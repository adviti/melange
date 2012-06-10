#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Downloads student forms.
"""


import optparse
import os
import shutil

import interactive


parser = optparse.OptionParser(usage="usage: %prog [options] app_id")
parser.add_option("-o", "--output", dest="outputdir", default="forms",
                  help="write files to target DIR", metavar="DIR")


def downloadStudentForms(options):
  from google.appengine.ext import db
  from soc.views.helper import lists as list_helper
  from soc.modules.gsoc.models.profile import GSoCStudentInfo


  q = lambda: GSoCStudentInfo.all().filter('number_of_projects', 1)

  outputdir = os.path.abspath(options.outputdir)

  if not os.path.exists(outputdir):
    os.mkdir(outputdir)

  if not os.path.isdir(outputdir):
    print "Could not create output dir: %s" % outputdir

  print "Fetching StudentInfo..."
  students = list(i for i in interactive.deepFetch(q) if i.tax_form)

  keys = list_helper.collectParentKeys(students)
  keys = list(set(keys))

  prefetched = {}

  print "Fetching Profile..."

  for i in xrange(0, len(keys), 100):
    chunk = keys[i:i+100]
    entities = db.get(chunk)
    prefetched.update(dict((i.key(), i) for i in entities if i))

  list_helper.distributeParentKeys(students, prefetched)

  countries = ['United States']
  us_students = [i for i in students if i.parent().res_country in countries]

  for student in us_students:
    form = student.tax_form
    _, ext = os.path.splitext(form.filename)
    path = os.path.join(outputdir, student.parent().link_id + ext)
    dst = open(path, "w")
    src = form.open()
    shutil.copyfileobj(src, dst)
    print "Downloading form to '%s'..." % path

  print "Done."


def main():
  options, args = parser.parse_args()

  if len(args) < 1:
    parser.error("Missing app_id")

  if len(args) > 1:
    parser.error("Too many arguments")

  interactive.setup()
  interactive.setupRemote(args[0])

  downloadStudentForms(options)


if __name__ == '__main__':
  main()

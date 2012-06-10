#!/usr/bin/env python2.5
#
# Copyright 2012 the Melange authors.
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
parser.add_option("-p", "--program", dest="program_path", default="",
                  help="scope path of the program", metavar="DIR")

def downloadStudentForms(options):
  from google.appengine.ext import db
  from soc.views.helper import lists as list_helper
  from soc.modules.gci.models.profile import GCIProfile
  from soc.modules.gci.models.profile import GCIStudentInfo
  from soc.modules.gci.models.program import GCIProgram
  from soc.modules.gci.models.score import GCIScore

  if not options.program_path:
    print "--program_path or -p option is required"
  program = GCIProgram.get_by_key_name(options.program_path)

  outputdir = os.path.abspath(options.outputdir)
  if not os.path.exists(outputdir):
    os.mkdir(outputdir)

  if not os.path.isdir(outputdir):
    print "Could not create output dir: %s" % outputdir

  q = lambda: GCIScore.all().filter("program =", program)
  print "Fetching GCIScore..."
  scores = list(i for i in interactive.deepFetch(q))

  keys = list_helper.collectParentKeys(scores)
  keys = list(set(keys))
  prefetched = {}

  print "Fetching Profile..."
  for i in xrange(0, len(keys), 100):
    chunk = keys[i:i+100]
    entities = db.get(chunk)
    prefetched.update(dict((i.key(), i) for i in entities if i))

  profiles = prefetched.values()
  list_helper.distributeParentKeys(scores, prefetched)

  keys = list_helper.collectKeys(GCIProfile.student_info, entities)
  keys = list(set(keys))
  prefetched = {}

  print "Fetching StudentInfo..."
  for i in xrange(0, len(keys), 100):
    chunk = keys[i:i+100]
    entities = db.get(chunk)
    prefetched.update(dict((i.key(), i) for i in entities if i))

  studentInfos = prefetched.values()
  list_helper.distributeKeys(GCIProfile.student_info, profiles, prefetched)

  i = 0
  while i < len(profiles):
    try:
      profile = profiles[i]
      consent_form = profile.student_info.consent_form
      student_id_form = profile.student_info.student_id_form
      if not consent_form or not student_id_form:
        print "At least one form missing from %s" % profile.link_id
      else:
        _saveForm(profile, consent_form, 'consent-form', outputdir)
        _saveForm(profile, consent_form, 'student-id-form', outputdir)
    except Exception, e:
      continue
    i += 1

  print "Done."


def _saveForm(profile, form, form_type, outputdir):
  _, ext = os.path.splitext(form.filename)
  filename = '-'.join([profile.link_id, form_type, ext])
  path = os.path.join(outputdir, filename)
  dst = open(path, "w")
  src = form.open()
  shutil.copyfileobj(src, dst)
  print "Downloading form to '%s'..." % path


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

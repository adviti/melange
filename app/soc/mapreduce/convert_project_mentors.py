#!/usr/bin/python2.5
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

"""Map reduce to merge mentor and co-mentors properties in GSoCProject.
"""


from google.appengine.ext.mapreduce import operation

from soc.modules.gsoc.models.project import GSoCProject


def process(project):
  mentor =  GSoCProject.mentor.get_value_for_datastore(project)
  mentors = [mentor]
  for am in project.additional_mentors:
    if am not in mentors:
      mentors.append(am)

  project.mentors = mentors

  yield operation.db.Put(project)
  yield operation.counters.Increment("projects_updated")


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


"""MapReduce to initialize the GCITask created_by and modified_by properties.
This was not being recorded for GCI 2011 program because it was not being
handled in the code before.
"""


from google.appengine.ext.mapreduce import operation

from soc.modules.gci.models.profile import GCIProfile


def process(task):
  org = task.org

  q = GCIProfile.all()
  q.filter('org_admin_for', org)

  # It is sufficient to fetch one org admin (and any one is fine).
  org_admin = q.get()

  if not task.created_by:
    task.created_by = org_admin

  if not task.modified_by:
    task.modified_by = org_admin

  yield operation.db.Put(task)
  yield operation.counters.Increment("task_authorship_updated")

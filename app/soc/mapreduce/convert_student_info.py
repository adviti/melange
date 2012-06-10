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

"""GSoCStudentInfo updating MapReduce.
"""


import logging

from google.appengine.ext import db
from google.appengine.ext.mapreduce import operation

from soc.models.user import User
from soc.modules.gsoc.models.profile import GSoCStudentInfo
from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.gsoc.models.project import GSoCProject


def process(student_info):
  logging.debug("Converting student_info '%r'" % student_info.key())
  proposals = GSoCProposal.all().ancestor(student_info.parent_key()).fetch(1000)
  projects = GSoCProject.all().ancestor(student_info.parent_key()).fetch(1000)

  proposals = [i for i in proposals if i.status != 'withdrawn']
  projects = [i for i in projects if i.status != 'withdrawn']

  nr_proposals = len(proposals)
  nr_projects = len(projects)

  orgs = [GSoCProject.org.get_value_for_datastore(i) for i in projects]

  student_info.number_of_proposals = nr_proposals
  student_info.number_of_projects = nr_projects
  student_info.project_for_orgs = orgs

  yield operation.db.Put(student_info)
  yield operation.counters.Increment("student_infos_converted")
  yield operation.counters.Increment("proposals_counted", delta=nr_proposals)
  yield operation.counters.Increment("projects_counted", delta=nr_projects)

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

"""The role conversion updates for GCI are defined in this module.
"""


from django import http

from soc.models.linkable import Linkable
from soc.tasks.updates import role_conversion

from soc.modules.gci.models.mentor import GCIMentor
from soc.modules.gci.models.org_admin import GCIOrgAdmin
from soc.modules.gci.models.profile import GCIProfile
from soc.modules.gci.models.student import GCIStudent
from soc.modules.gci.models.profile import GCIStudentInfo
from soc.modules.gci.models.task import GCITask


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/gci/role_conversion/update_mentors$',
        'soc.modules.gci.tasks.updates.role_conversion.updateMentors'),
      (r'^tasks/gci/role_conversion/update_org_admins$',
        'soc.modules.gci.tasks.updates.role_conversion.updateOrgAdmins'),
      (r'^tasks/gci/role_conversion/update_students$',
        'soc.modules.gci.tasks.updates.role_conversion.updateStudents'),
      (r'^tasks/gci/role_conversion/update_task_reference',
        'soc.modules.gci.tasks.updates.role_conversion.updateGCITaskReferences'),
  ]

  return patterns
  

class RoleUpdater(role_conversion.RoleUpdater):
  """Class which is responsible for updating entities in GCI.
  """

  POPULATED_PROFILE_PROPS = set(
      GCIProfile.properties()) - set(Linkable.properties())

  POPULATED_STUDENT_PROPS = GCIStudentInfo.properties()

  def _processStudentEntity(self, entity, properties):
    query = GCITask.all()
    query.filter('student', entity)
    query.filter('status', 'Closed')
    no_of_tasks = query.count()

    properties['number_of_tasks_completed'] = no_of_tasks


def updateMentors(request):
  """Starts an iterative task which updates mentors.
  """

  updater = RoleUpdater(GCIMentor, GCIProfile,
      GCIStudent, GCIStudentInfo, 'program', 'mentor_for')
  updater.run()
  return http.HttpResponse("Ok")


def updateOrgAdmins(request):
  """Starts an iterative task which updates org admins.
  """

  updater = RoleUpdater(GCIOrgAdmin, GCIProfile,
      GCIStudent, GCIStudentInfo, 'program', 'org_admin_for')
  updater.run()
  return http.HttpResponse("Ok")

def updateStudents(request):
  """Starts an iterative task which updates students.
  """

  updater = RoleUpdater(GCIStudent, GCIProfile,
      GCIStudent, GCIStudentInfo, 'scope')
  updater.run()
  return http.HttpResponse("Ok")

def updateGCITaskReferences(request):
  """Starts a bunch of iterative tasks which update references in
     GCITask.
  """ 
  
  updater = role_conversion.ReferenceUpdater(GCITask, GCIProfile,
      ['student', 'created_by', 'modified_by'], ['mentors'])
  updater.run()
  return http.HttpResponse("Ok")

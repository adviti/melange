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

"""The role conversion updates are defined in this module.
"""


import gae_django

from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.runtime import DeadlineExceededError

from django import http

from soc.models.host import Host
from soc.models.linkable import Linkable
from soc.models.mentor import Mentor
from soc.models.org_admin import OrgAdmin
from soc.models.role import StudentInfo

from soc.modules.gsoc.models.mentor import GSoCMentor
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.org_admin import GSoCOrgAdmin
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.gsoc.models.student import GSoCStudent
from soc.modules.gsoc.models.profile import GSoCStudentInfo
from soc.modules.gsoc.models.student_project import StudentProject
from soc.modules.gsoc.models.student_proposal import StudentProposal


ROLE_MODELS = [GSoCMentor, GSoCOrgAdmin, GSoCStudent]


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/role_conversion/update_references',
        'soc.tasks.updates.role_conversion.updateReferences'),
      (r'^tasks/role_conversion/update_project_references',
        'soc.tasks.updates.role_conversion.updateStudentProjectReferences'),
      (r'^tasks/role_conversion/update_proposal_references',
        'soc.tasks.updates.role_conversion.updateStudentProposalReferences'),
      (r'^tasks/role_conversion/update_roles$',
        'soc.tasks.updates.role_conversion.updateRoles'),
      (r'^tasks/role_conversion/update_mentors$',
        'soc.tasks.updates.role_conversion.updateMentors'),
      (r'^tasks/role_conversion/update_org_admins$',
        'soc.tasks.updates.role_conversion.updateOrgAdmins'),
      (r'^tasks/role_conversion/update_students$',
        'soc.tasks.updates.role_conversion.updateStudents'),
      (r'^tasks/role_conversion/update_hosts$',
        'soc.tasks.updates.role_conversion.updateHosts'),
      (r'^tasks/role_conversion/update_student_infos$',
        'soc.tasks.updates.role_conversion.updateStudentInfos'),
  ]

  return patterns


class HostUpdater(object):
  """Class which is responsible for updating Host entities.
  """

  def run(self, batch_size=25):
    """Starts the updater.
    """

    self._process(None, batch_size)

  def _process(self, start_key, batch_size):
    """Retrieves Host entities and updates them.
    """

    query = Host.all()
    if start_key:
      query.filter('__key__ > ', start_key)

    try:
      entities = query.fetch(batch_size)

      if not entities:
        # all entities has already been processed
        return

      for entity in entities:
        sponsor = entity.scope
        host_for = entity.user.host_for

        if not host_for:
          host_for = []

        user = entity.user
        if sponsor.key() not in host_for:
          host_for.append(sponsor.key())
        user.host_for = host_for

        db.put(user)

      # process the next batch of entities
      start_key = entities[-1].key()
      deferred.defer(self._process, start_key, batch_size)
    except DeadlineExceededError:
      # here we should probably be more careful
      deferred.defer(self._process, start_key, batch_size)


class RoleUpdater(object):
  """Class which is responsible for updating the entities.
  """

  POPULATED_PROFILE_PROPS = set(
      GSoCProfile.properties()) - set(Linkable.properties())

  POPULATED_STUDENT_PROPS = StudentInfo.properties()

  def __init__(self, model, profile_model, student_model,
               studentinfo_model, program_field, role_field=None):
    self.MODEL = model
    self.PROFILE_MODEL = profile_model
    self.PROGRAM_FIELD = program_field
    self.ROLE_FIELD = role_field
    self.STUDENT_MODEL = student_model
    self.STUDENTINFO_MODEL = studentinfo_model

  def run(self, batch_size=25):
    """Starts the updater.
    """

    self._process(None, batch_size)

  def _prcoessStudentEntity(self, entity, **properties):
    pass

  def _processEntity(self, entity):
    program = getattr(entity, self.PROGRAM_FIELD)
    user = entity.user

    # try to find an existing Profile entity or create a new one
    key_name = program.key().name() + '/' + user.link_id
    properties = {
        'link_id': entity.link_id,
        'scope_path': program.key().name(),
        'scope': program,
        'parent': user,
        'public_name': user.name,
        }
    for prop in self.POPULATED_PROFILE_PROPS:
      if hasattr(entity, prop):
        properties[prop] = getattr(entity, prop)

    profile = self.PROFILE_MODEL.get_or_insert(
        key_name=key_name, **properties)

    # do not update anything if the role is already in the profile
    if profile.student_info and self.MODEL == self.STUDENT_MODEL:
      return
    elif self.ROLE_FIELD:
      if entity.scope.key() in getattr(profile, self.ROLE_FIELD):
        return

    to_put = [profile]

    # a non-invalid role is found, we should re-populate the profile
    if profile.status == 'invalid' and entity.status != 'invalid':
      for prop_name in entity.properties():
        value = getattr(entity, prop_name)
        setattr(profile, prop_name, value)

      if profile.student_info:
        profile.student_info = None

    if self.ROLE_FIELD:
      # the role is either Mentor or OrgAdmin
      if self.ROLE_FIELD == 'org_admin_for':
        org_admin_for = list(set(profile.org_admin_for + [entity.scope.key()]))
        profile.org_admin_for = org_admin_for
        profile.is_org_admin = True

      mentor_for = list(set(profile.mentor_for + [entity.scope.key()]))
      profile.mentor_for = mentor_for
      profile.is_mentor = True
    else:
      # the role is certainly Student; we have to create a new StudentInfo
      properties = {}
      for prop in self.POPULATED_STUDENT_PROPS:
        if hasattr(entity, prop):
          properties[prop] = getattr(entity, prop)
      self._processStudentEntity(entity, properties)

      key_name = profile.key().name()
      student_info = self.STUDENTINFO_MODEL(key_name=key_name,
          parent=profile, **properties)
      profile.student_info = student_info
      profile.is_student = True
      to_put.append(student_info)

    db.run_in_transaction(db.put, to_put)

  def _process(self, start_key, batch_size):
    """Retrieves entities and creates or updates a corresponding
    Profile entity.
    """

    query = self.MODEL.all()
    if start_key:
      query.filter('__key__ > ', start_key)

    try:
      entities = query.fetch(batch_size)

      if not entities:
        # all entities has already been processed
        return

      for entity in entities:
        try:
          self._processEntity(entity)
        except db.Error, e:
          import logging
          logging.exception(e)
          logging.error("Broke on %s: %s" % (entity.key().name(), self.MODEL))

      # process the next batch of entities
      start_key = entities[-1].key()
      deferred.defer(self._process, start_key, batch_size)
    except DeadlineExceededError:
      # here we should probably be more careful
      deferred.defer(self._process, start_key, batch_size)


class StudentInfoUpdater(object):
  """Class which is responsible for creating GSoCStudentInfo based on
  the corresponding StudentInfo entities
  """

  def run(self, batch_size=25):
    """Starts the updater.
    """

    self._process(None, batch_size)

  def _processEntity(self, entity):
    profile = entity.parent()
    project = GSoCProject.all().ancestor(profile).get()

    properties = {
        'school_name': entity.school_name,
        'school_country': entity.school_country,
        'school_home_page': entity.school_home_page,
        'school_type': entity.school_type,
        'major': entity.major,
        'degree': entity.degree,
        'expected_graduation': entity.expected_graduation,
        'number_of_proposals': GSoCProposal.all().ancestor(profile).count(),
        'number_of_projects': 1 if project is not None else 0,
        'project_for_orgs': [project.org.key()] if project else []  
        }

    studentInfo = GSoCStudentInfo(key_name = profile.key().name(), 
        parent=profile, **properties)
    profile.student_info = studentInfo

    db.run_in_transaction(db.put, [profile, studentInfo])

  def _process(self, start_key, batch_size):
    """Retrieves entities and creates or updates a corresponding
    Profile entity.
    """

    query = StudentInfo.all()
    if start_key:
      query.filter('__key__ > ', start_key)

    try:
      entities = query.fetch(batch_size)

      if not entities:
        # all entities has already been processed
        return

      for entity in entities:
        try:
          self._processEntity(entity)
        except db.Error, e:
          import logging
          logging.exception(e)
          logging.error("Broke on %s: %s" % (entity.key().name(), 'StudentInfo'))

      # process the next batch of entities
      start_key = entities[-1].key()
      deferred.defer(self._process, start_key, batch_size)
    except DeadlineExceededError:
      # here we should probably be more careful
      deferred.defer(self._process, start_key, batch_size)


def updateHosts(request):
  """Starts a task which updates Host entities.
  """

  updater = HostUpdater()
  updater.run()
  return http.HttpResponse("Ok")


def updateStudentInfos(request):
  """Starts a task which updates StudentInfo entities
  """

  updater = StudentInfoUpdater()
  updater.run()
  return http.HttpResponse("Ok")


def updateRole(role_name):
  """Starts a task which updates a particular role.
  """

  if role_name == 'gsoc_mentor':
    updater = RoleUpdater(GSoCMentor, GSoCProfile,
        GSoCStudent, GSoCStudentInfo, 'program', 'mentor_for')
  elif role_name == 'gsoc_org_admin':
    updater = RoleUpdater(GSoCOrgAdmin, GSoCProfile,
        GSoCStudent, GSoCStudentInfo, 'program', 'org_admin_for')
  elif role_name == 'gsoc_student':
    updater = RoleUpdater(GSoCStudent, GSoCProfile,
        GSoCStudent, GSoCStudentInfo, 'scope')

  updater.run()
  return http.HttpResponse("Ok")

def updateRoles(request):
  """Starts a bunch of iterative tasks which update particular roles.

  In order to prevent issues with concurrent access to entities, we set
  ETA so that each role is processed in separation.
  """

  # update org admins
  #updateRole('gsoc_org_admin')

  # update mentors
  #updateRole('gsoc_mentor')

  # update students
  # we can assume that students cannot have any other roles, so we do not
  # need to set ETA
  updateRole('gsoc_student')

def updateMentors(request):
  """Starts an iterative task which update mentors.
  """

  return updateRole('gsoc_mentor')

def updateOrgAdmins(request):
  """Starts an iterative task which update org admins.
  """

  return updateRole('gsoc_org_admin')

def updateStudents(request):
  """Starts an iterative task which update students.
  """

  return updateRole('gsoc_student')

def _getProfileForRole(entity, profile_model):
  """Returns GSoCProfile or GCIProfile which corresponds to the specified
  entity.
  """

  if isinstance(entity, profile_model):
    return entity

  if isinstance(entity, OrgAdmin) or isinstance(entity, Mentor):
    key_name = entity.program.key().name() + '/' + entity.user.key().name()
  else:
    key_name = entity.key().name()

  parent = entity.user
  return profile_model.get_by_key_name(key_name, parent=parent)


def _getProfileKeyForRoleKey(key, profile_model):
  """Returns Key instance of the Profile which corresponds to the Role which
  is represented by the specified Key.
  """

  entity = db.get(key)
  profile = _getProfileForRole(entity, profile_model)
  return profile.key()

class ReferenceUpdater(object):
  """Class which is responsible for updating references to Profile in
  the specified model.
  """

  def __init__(self, model, profile_model, fields_to_update,
               lists_to_update=[]):
    self.MODEL = model
    self.PROFILE_MODEL = profile_model
    self.FIELDS_TO_UPDATE = fields_to_update
    self.LISTS_TO_UPDATE = lists_to_update

  def run(self, batch_size=25):
    """Starts the updater.
    """

    self._process(None, batch_size)

  def _process(self, start_key, batch_size):
    """Iterates through the entities and updates the references.
    """

    query = self.MODEL.all()
    if start_key:
      query.filter('__key__ > ', start_key)

    try:
      entities = query.fetch(batch_size)

      if not entities:
        # all entities has already been processed
        return

      for entity in entities:
        for field in self.FIELDS_TO_UPDATE:
          old_reference = getattr(entity, field)

          if not old_reference:
            continue

          # check if the field has not been updated
          if isinstance(old_reference, self.PROFILE_MODEL):
            continue

          profile = _getProfileForRole(old_reference, self.PROFILE_MODEL)
          setattr(entity, field, profile)

        for list_property in self.LISTS_TO_UPDATE:
          l = getattr(entity, list_property)
          new_l = []
          for key in l:
            new_l.append(_getProfileKeyForRoleKey(key, self.PROFILE_MODEL))
          setattr(entity, list_property, new_l)

      db.put(entities)
      start_key = entities[-1].key()
      deferred.defer(self._process, start_key, batch_size)
    except DeadlineExceededError:
      # here we should probably be more careful
      deferred.defer(self._process, start_key, batch_size)


def updateReferencesForModel(model):
  """Starts a task which updates references for a particular model.
  """

  if model == 'student_proposal':
    updater = ReferenceUpdater(StudentProposal, GSoCProfile,
        ['scope', 'mentor'], ['possible_mentors'])
  elif model == 'student_project':
    updater = ReferenceUpdater(StudentProject, GSoCProfile,
        ['mentor', 'student'], ['additional_mentors'])

  updater.run()
  return http.HttpResponse("Ok")


def updateStudentProjectReferences(request):
  """Starts a bunch of iterative tasks which update references in
  StudentProjects.
  """

  return updateReferencesForModel('student_project')


def updateStudentProposalReferences(request):
  """Starts a bunch of iterative tasks which update references in
  StudentProposals.
  """

  return updateReferencesForModel('student_proposal')


def updateReferences(request):
  """Starts a bunch of iterative tasks which update references to various roles.
  """

  # updates student proposals
  updateReferencesForModel('student_proposal')

  # updates student projects
  updateReferencesForModel('student_project')

  return http.HttpResponse("Ok")

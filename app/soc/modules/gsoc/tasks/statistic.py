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

"""Tasks related to collection of statistic for GSoC programs"""


from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.runtime import DeadlineExceededError

from django.utils import simplejson
from django.conf.urls.defaults import url

from soc.models import countries
from soc.models.statistic_info import StatisticInfo

from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.gsoc.models.statistic_data import GSoCStatisticData
from soc.modules.gsoc.models.statistic_info import GSoCStatisticInfo

from soc.modules.gsoc.statistics import mapping


PROFILE_SPECIFIC = [
    'profiles',
    'students',
    'students_per_country',
    'mentors',
    'mentors_per_country',
    'admins',
    'proposals_per_student',
    'students_with_proposals',
    'students_with_proposals_per_country'
    ]

PROPOSAL_SPECIFIC = [
    'proposals',
    'proposals_per_organization'
    ]


class NotImplementedStatistic(Exception):
  pass


class AbstractStatisticService(object):

  def __call__(self, request, *args, **kwargs):
    return self.processRequest(request, args, kwargs)

  def processRequest(self, request, args, kwargs):
    raise NotImplementedError('The process request method not implemented.')


class CreateStatisticInfoService(AbstractStatisticService):
  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/statistic_info/create$', self)]

  def processRequest(self, request, args, kwargs):
    statisticInfo = GSoCStatisticInfo.getInstance()

    # create Statistic instances based on mapping file
    # by default all the statistic will be hidden
    for statistic_name in mapping.STATISTIC_NAMES:
      statisticInfo.appendStatistic(
          StatisticInfo.Statistic(statistic_name, False))
    statisticInfo.put()

class CollectStatisticService(AbstractStatisticService):
  _model = None
  _model_specific = []
  _batch_size = 10
  _statistics = {}

  def initialize(self):
    entities = GSoCStatisticData.get_by_key_name(self._model_specific)
    for entity in entities:
      self._statistics[entity.key().name()] = {
          'entity': entity,
          'data': simplejson.loads(entity.data),
          'dirty': False
          }

  def finalize(self):
    to_put = []
    for statistic in self._statistics.itervalues():
      entity = statistic['entity']
      if statistic['dirty']:
        entity.data = simplejson.dumps(statistic['data'])
        to_put.append(entity)
    db.put(to_put)

  def processRequest(self, request, args, kwargs):
    # first, we need to create or clear statistic entities
    self._initializeStatistics()
    # start the first of the tasks which will collect the actual data
    deferred.defer(self._continue, None)

  def _initializeStatistics(self):
    raise NotImplementedError('Subclasses should implement this method.')

  def _processEntity(self, entity):
    raise NotImplementedError('The process entity method not implemented.')

  def _continue(self, start_key):
    self.initialize()
    query = self._model.all()
    if start_key:
      query.filter('__key__ > ', start_key)

    try:
      entities = query.fetch(self._batch_size)

      if not entities:
        # all the entities have been processed
        return

      for entity in entities:
        self._processEntity(entity)

      self.finalize()
      start_key = entity.key()
    except DeadlineExceededError:
      # nothing happens, we just try processing the same batch again
      pass

    # delegate work to the next task
    deferred.defer(self._continue, start_key)


class CreateStatisticService(AbstractStatisticService):
  _model_specific = []

  def __init__(self):
    self.programs = GSoCProgram.all().fetch(1000)

  def processRequest(self, request, args, kwargs):
    key_name = kwargs.get('key_name')
    # if specific key_name is not specified, initialize all statistic
    key_names = [key_name] if key_name else self._model_specific
    self._createStatistics(key_names)

  def createStatistics(self):
    self._createStatistics(self._model_specific)

  def _createStatistics(self, key_names):
    to_put = []
    for key_name in key_names:
      to_put.append(self._createStatistic(key_name))
    db.put(to_put)

  def _createStatistic(self, key_name):
    data = self._createInitialData(key_name)
    entity = GSoCStatisticData.get_by_key_name(key_name) 
    if not entity:
      entity = GSoCStatisticData(key_name=key_name, data=data)
    else:
      entity.data = data
    return entity

  def _createInitialData(self, key_name):
    raise NotImplementedError('Subclasses should implement this method.')

  def _createPerProgramInitialData(self):
    data = {}
    for program in self.programs:
      key_name = program.key().name()
      data[key_name] = 0
    return data

  def _createPerProgramPerCountryInitialData(self):
    data = {}
    for program in self.programs:
      key_name = program.key().name()
      data[key_name] = {}
      for country in countries.COUNTRIES_AND_TERRITORIES:
        data[key_name][country] = 0

    return data


class CreateProfileSpecificStatisticService(CreateStatisticService):
  _model_specific = PROFILE_SPECIFIC

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/statistic/create/profile$', self),
        url(r'^gsoc/statistic/create/profile/(?P<key_name>(\w+))$', self),
    ]

  def _createInitialData(self, key_name):
    if key_name == 'admins':
      data = self._createAdmins()
    elif key_name == 'profiles':
      data = self._createProfiles()
    elif key_name == 'mentors':
      data = self._createMentors()
    elif key_name == 'mentors_per_country':
      data = self._createMentorsPerCountry()
    elif key_name == 'proposals_per_student':
      data = self._createProposalsPerStudent()
    elif key_name == 'students':
      data = self._createStudents()
    elif key_name == 'students_per_country':
      data = self._createStudentsPerCountry()
    elif key_name == 'students_with_proposals':
      data = self._createStudentsWithProposals()
    elif key_name == 'students_with_proposals_per_country':
      data = self._createStudentsWithProposalsPerCountry()
    else:
      raise NotImplementedStatistic(
        'The statistic with name %s has not been defined.' % key_name)
    return simplejson.dumps(data)

  def _createAdmins(self):
    return self._createPerProgramInitialData()

  def _createMentors(self):
    return self._createPerProgramInitialData()

  def _createMentorsPerCountry(self):
    return self._createPerProgramPerCountryInitialData()

  def _createProfiles(self):
    return self._createPerProgramInitialData()

  def _createProposalsPerStudent(self):
    return self._createPerProgramPerCounter(25)

  def _createStudents(self):
    return self._createPerProgramInitialData()

  def _createStudentsPerCountry(self):
    return self._createPerProgramPerCountryInitialData()

  def _createStudentsWithProposals(self):
    return self._createPerProgramInitialData()

  def _createStudentsWithProposalsPerCountry(self):
    return self._createPerProgramPerCountryInitialData()

  def _createPerProgramPerCounter(self, limit):
    data = {}
    for program in self.programs:
      key_name = program.key().name()
      data[key_name] = {}
      for i in xrange(limit + 1):
        data[key_name][i] = 0
    return data


class CreateProposalSpecificStatisticService(CreateStatisticService):
  _model_specific = PROPOSAL_SPECIFIC

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/statistic/create/proposal$', self),
        url(r'^gsoc/statistic/create/proposal/(?P<key_name>(\w+))$', self),
    ]

  def _createInitialData(self, key_name):
    if key_name == 'proposals':
      data = self._createProposals()
    elif key_name == 'proposals_per_organization':
      data = self._createProposalsPerOrganization()
    else:
      raise NotImplementedStatistic(
        'The statistic with name %s has not been defined.' % key_name)
    return simplejson.dumps(data)

  def _createProposals(self):
    return self._createPerProgramInitialData()

  def _createProposalsPerOrganization(self):
    data = {}
    for program in self.programs:
      key_name = program.key().name()
      data[key_name] = {}

    return data    


class CollectProfileSpecificStatistics(CollectStatisticService):
  _model = GSoCProfile
  _model_specific = PROFILE_SPECIFIC

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/statistic/collect/profile$', self)
    ]
    
  def _initializeStatistics(self):
    CreateProfileSpecificStatisticService().createStatistics()

  def _processEntity(self, entity):
    # check if the profile is active
    if entity.status == 'invalid':
      return

    self._collectProfiles(entity)

    # check if the profile represents a student
    is_student = entity.student_info is not None
    if is_student:
      self._collectStudentSpecificStatistics(entity)
    elif entity.is_mentor or entity.is_org_admin:
      self._collectMentorSpecificStatistics(entity)
      if entity.is_org_admin:
        self._collectAdminSpecificStatistics(entity)


  def _collectAdmins(self, entity):
    self._collectPerProgramStatistic(entity, 'admins')

  def _collectMentors(self, entity):
    self._collectPerProgramStatistic(entity, 'mentors')

  def _collectMentorsPerCountry(self, entity):
    self._collectPerProgramPerCountryStatistic(entity, 'mentors_per_country')

  def _collectProfiles(self, entity):
    self._collectPerProgramStatistic(entity, 'profiles')

  def _collectProposalsPerStudent(self, entity):
    program_key_name = entity.scope.key().name()
    number = str(entity.student_info.number_of_proposals)
    statistic = self._statistics['proposals_per_student']
    statistic['data'][program_key_name][number] += 1

  def _collectStudents(self, entity):
    self._collectPerProgramStatistic(entity, 'students')

  def _collectStudentsPerCountry(self, entity):
    self._collectPerProgramPerCountryStatistic(entity, 'students_per_country')

  def _collectStudentsWithProposals(self, entity):
    self._collectPerProgramStatistic(entity, 'students_with_proposals')

  def _collectStudentsWithProposalsPerCountry(self, entity):
    self._collectPerProgramPerCountryStatistic(
        entity, 'students_with_proposals_per_country')

  def _collectAdminSpecificStatistics(self, entity):
    self._collectAdmins(entity)

  def _collectMentorSpecificStatistics(self, entity):
    self._collectMentors(entity)
    self._collectMentorsPerCountry(entity)

  def _collectStudentSpecificStatistics(self, entity):
    self._collectStudents(entity)
    self._collectStudentsPerCountry(entity)

    student_info = entity.student_info
    if student_info.number_of_proposals:
      self._collectStudentsWithProposals(entity)
      self._collectStudentsWithProposalsPerCountry(entity)

    self._collectProposalsPerStudent(entity)

  def _collectPerProgramStatistic(self, entity, key_name):
    program_key_name = entity.scope.key().name()
    statistic = self._statistics[key_name]
    statistic['data'][program_key_name] += 1
    statistic['dirty'] = True

  def _collectPerProgramPerCountryStatistic(self, entity, key_name): 
    program_key_name = entity.scope.key().name()
    country = entity.res_country
    statistic = self._statistics[key_name] 
    statistic['data'][program_key_name][country] += 1
    statistic['dirty'] = True

  def _collectPerProgramPerCounterStatistic(self, entity, key_name):
    program_key_name = entity.scope.key().name()


class CollectProposalSpecificStatistics(CollectStatisticService):
  _model = GSoCProposal
  _model_specific = PROPOSAL_SPECIFIC

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/statistic/collect/proposal$', self)
    ]

  def _initializeStatistics(self):
    CreateProposalSpecificStatisticService().createStatistics()

  def _processEntity(self, entity):

    self._collectProposals(entity)
    self._collectProposalsPerOrganization(entity)

  def _collectProposals(self, entity):
    self._collectPerProgramStatistic(entity, 'proposals')

  def _collectProposalsPerOrganization(self, entity):
    program_key_name = entity.program.key().name()
    org_key_name = entity.org.key().name()
    statistic = self._statistics['proposals_per_organization']

    if org_key_name in statistic['data'][program_key_name]:
      statistic['data'][program_key_name][org_key_name] += 1
    else:
      statistic['data'][program_key_name][org_key_name] = 1
    statistic['dirty'] = True

  def _collectPerProgramStatistic(self, entity, key_name):
    program_key_name = entity.program.key().name()
    statistic = self._statistics[key_name]
    statistic['data'][program_key_name] += 1
    statistic['dirty'] = True

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

"""The presentation module for GSoC statistics."""


from gviz import gviz_api
from django.utils import simplejson

from soc.models import countries
from soc.modules.gsoc.statistics import mapping
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.statistic_data import GSoCStatisticData


class AbstractPresenter(object):

  def _getDataSources(self, key_name):
    key_names = mapping.DEPENDENCIES[key_name]
    statistics = GSoCStatisticData.get_by_key_name(key_names)
    sources = {}
    for statistic in statistics:
      sources[statistic.key().name()] = simplejson.loads(statistic.data)

    if len(sources) != len(key_names):
      raise Exception('At least one of the dependencies cannot be loaded.')

    return sources

  def _getDataTableRows(self, key_name, sources):
    if key_name == 'admins':
      return self._getAdmins(key_name, sources)
    if key_name == 'profiles':
      return self._getProfiles(key_name, sources)
    if key_name == 'proposals_per_student':
      return self._getProposalsPerStudent(key_name, sources)
    if key_name == 'mentors':
      return self._getMentors(key_name, sources)
    if key_name == 'mentors_per_country':
      return self._getMentorsPerCountry(key_name, sources)
    if key_name == 'students':
      return self._getStudents(key_name, sources)
    if key_name == 'students_per_country':
      return self._getStudentsPerCountry(key_name, sources)

    raise Exception('Statistic %s not supported.' % key_name)

  def _getAdmins(self, key_name, sources):
    return self._getNumberPerProgramRows(key_name, sources)

  def _getMentors(self, key_name, sources):
    return self._getNumberPerProgramRows(key_name, sources)

  def _getMentorsPerCountry(self, key_name, sources):
    return self._getPerProgramPerCountryRows(key_name, sources)

  def _getProfiles(self, key_name, sources):
    return self._getNumberPerProgramRows(key_name, sources)

  def _getProposalsPerStudent(self, key_name, sources):
    values = range(21)
    return self._getPerProgramPerNumberRows(key_name, sources, values)

  def _getStudents(self, key_name, sources):
    return self._getNumberPerProgramRows(key_name, sources)

  def _getStudentsPerCountry(self, key_name, sources):
    return self._getPerProgramPerCountryRows(key_name, sources)

  def _getNumberPerProgramRows(self, key_name, sources):
    source = sources[key_name]

    rows = []
    for program, number in source.iteritems():
      program = GSoCProgram.get_by_key_name(program)
      rows.append([program.name, int(number)])

    return rows

  def _getPerProgramPerCountryRows(self, key_name, sources):
    source = sources[key_name]

    rows = []
    for country in countries.COUNTRIES_AND_TERRITORIES:
      rows.append([country] +
          [program.get(country, 0) for program in source.values()])
    return rows

  def _getPerProgramPerNumberRows(self, key_name, sources, values=None):
    source = sources[key_name]

    if not values:
      existingValues = set(i.keys() for i in source.itervalues())
      values = range(min(values), max(values) - 1)

    rows = []
    for value in values:
      rows.append([value] + 
          [program.get(str(value), 0) for program in source.values()])
    return rows

class JsonPresenter(AbstractPresenter):
  def get(self, key_name):
    statistic = GSoCStatisticData.get_by_key_name(key_name)
    return statistic.data if statistic else {}


_NUMBER_PER_PROGRAM_DESCRIPTION = [
    ('program', 'string', 'Program'),
    ('number', 'number', 'Number')]

class GvizPresenter(AbstractPresenter):
  def get(self, key_name):
    sources = self._getDataSources(key_name)
    description = self._getDataTableDescriptions(key_name, sources)
    rows = self._getDataTableRows(key_name, sources)

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(rows)

    json = data_table.ToJSon()
    return json

  def _getDataTableDescriptions(self, key_name, sources):
    if key_name in ['profiles', 'students', 'mentors', 'admins',
                    'students_with_proposals', 'students_with_projects']:
      return _NUMBER_PER_PROGRAM_DESCRIPTION
    if key_name in ['students_per_country', 'mentors_per_country']:
      columns = []
      columns.append(('country', 'string', 'Country'))
      source = sources[key_name]
      programs = GSoCProgram.get_by_key_name(source.keys())
      for program in programs:
        columns.append((program.key().name(), 'number', program.name))
      return columns
    if key_name in ['proposals_per_student']:
      columns = []
      columns.append(('proposals', 'number', 'Proposals'))
      source = sources[key_name]
      programs = GSoCProgram.get_by_key_name(source.keys())     
      for program in programs:
        columns.append((program.key().name(), 'number', program.name))
      return columns

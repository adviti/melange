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

"""The mapping module for GSoC statistics."""


_COUNTRY_PER_PROGRAM_DESCRIPTION = [
    ('program', 'string', 'Program'),
    ('number', 'number', 'Number')]


STATISTICS = [
    {'name': 'profiles',
     'human_name': 'Profiles Per Program',
     'dependencies': ['profiles'],
     'visualizations': ['table', 'piechart']},
    {'name': 'students',
     'human_name': 'Students Per Program',
     'dependencies': ['students'],
     'visualizations': ['table']},
    {'name': 'students_per_country',
     'human_name': 'Students Per Country',
     'dependencies': ['students_per_country'],
     'visualizations': ['table']},
    {'name': 'mentors',
     'human_name': 'Mentors Per Program',
     'dependencies': ['mentors'],
     'visualizations': ['table']},
    {'name': 'mentors_per_country',
     'human_name': 'Mentors Per Country',
     'dependencies': ['mentors_per_country'],
     'visualizations': ['table']},
    {'name': 'admins',
     'human_name': 'Admins Per Program',
     'dependencies': ['admins'],
     'visualizations': ['table']},
    {'name': 'proposals_per_student',
     'human_name': 'Proposals Per Students',
     'dependencies': ['proposals_per_student'],
     'visualizations': ['table']},
    {'name': 'students_with_proposals',
     'human_name': 'Students With Proposal Per Program',
     'dependencies': ['students_with_proposals'],
     'visualizations': ['table']},
    {'name': 'students_with_proposals_per_country',
     'human_name': 'Students With Proposals Per Country',
     'dependencies': ['students_with_proposals_per_country'],
     'visualizations': ['table']}]

STATISTIC_NAMES = [s['name'] for s in STATISTICS]
DEPENDENCIES = dict([[s['name'], s['dependencies']] for s in STATISTICS])
VISUALIZATIONS = dict([[s['name'], s['visualizations']] for s in STATISTICS])

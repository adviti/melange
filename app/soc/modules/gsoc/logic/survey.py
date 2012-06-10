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

"""Logic for Survey related models which stores evaluation survey for projects.
"""


from google.appengine.ext import db


def getSurveysForProgram(model, program, surveys, limit=1000):
  """Return the survey entity for a given program and the survey link id.

  Args:
    model: The Survey Model against which we need to query
    program: entity representing the program from which the featured
        projects should be fetched
    surveys: link id of the survey(s) which should be fetched
  """
  q = db.Query(model)
  q.filter('scope', program)
  link_id_operator = 'link_id'
  if isinstance(surveys, list):
    if len(surveys) > 1:
      link_id_operator += ' IN'
    else:
      surveys = surveys[0]

  q.filter(link_id_operator, surveys)

  return q.fetch(limit)

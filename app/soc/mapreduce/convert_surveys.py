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


"""Surveys model updating MapReduce.
"""


from google.appengine.ext.mapreduce import operation

from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gci.models.program import GCIProgram


def process(survey):
  survey.created_by = survey.author
  survey.program = survey.scope

  yield operation.db.Put(survey)
  yield operation.counters.Increment("survey_updated")

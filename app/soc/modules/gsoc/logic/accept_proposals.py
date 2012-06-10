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

"""Functions that help with accept proposals status.
"""


from google.appengine.ext import db

from soc.modules.gsoc.models.accept_proposals_status import \
    GSoCAcceptProposalsStatus


def getOrCreateStatusForProgram(program_entity):
  """Returns the AcceptProposalsStatus entity belonging to the given
  program or creates a new one.

  Args:
    program_entity: Program entity to get or create the
        AcceptProposalsStatus for.
  """
  q = GSoCAcceptProposalsStatus.all().filter('program', program_entity)
  aps_entity = q.get()

  if not aps_entity:
    aps_entity = GSoCAcceptProposalsStatus(program=program_entity)
    aps_entity.put()

  return aps_entity

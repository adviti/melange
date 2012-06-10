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

"""Functions that help with duplicate detection.
"""


from google.appengine.ext import db

from soc.modules.gsoc.models.proposal_duplicates import GSoCProposalDuplicate
from soc.modules.gsoc.models.proposal_duplicates_status import \
    GSoCProposalDuplicatesStatus


def getOrCreateStatusForProgram(program_entity):
  """Returns the ProposalDuplicatesStatus entity belonging to the given
  program or creates a new one.

  Args:
    program_entity: Program entity to get or create the 
        ProposalDuplicatesStatus for.
  """
  q = GSoCProposalDuplicatesStatus.all().filter('program', program_entity)
  pds_entity = q.get()

  if not pds_entity:
    pds_entity = GSoCProposalDuplicatesStatus(program=program_entity)
    pds_entity.put()

  return pds_entity

def deleteAllForProgram(program_entity, non_dupes_only=False):
  """Deletes all ProposalDuplicates for a given program.

  Args:
    program_entity: Program to delete the ProposalDuplicatesFor
    non_dupes_only: Iff True removes only the ones which have is_duplicate
      set to False. False by default.
  """

  q = GSoCProposalDuplicate.all()
  q.filter('program', program_entity)

  if non_dupes_only:
    q.filter('is_duplicate', False)

  # can not delete more then 500 entities in one call
  proposal_duplicates = q.fetch(500)
  while proposal_duplicates:
    db.delete(proposal_duplicates)
    proposal_duplicates = q.fetch(500)

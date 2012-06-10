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

"""GSOC logic for proposals.
"""


from soc.modules.gsoc.models.proposal import GSoCProposal


def getProposalsToBeAcceptedForOrg(org_entity, step_size=25):
  """Returns all StudentProposals which will be accepted into the program
  for the given organization.

  params:
    org_entity: the Organization for which the proposals should be checked
    step_size: optional parameter to specify the amount of Student Proposals
              that should be retrieved per roundtrip to the datastore

  returns:
    List with all StudentProposal which will be accepted into the program
  """

  # check if there are already slots taken by this org
  q = GSoCProposal.all()
  q.filter('org', org_entity)
  q.filter('status', 'accepted')

  slots_left_to_assign = max(0, org_entity.slots - q.count())
  if slots_left_to_assign == 0:
    # no slots left so return nothing
    return []

  q = GSoCProposal.all()
  q.filter('org', org_entity)
  q.filter('status', 'pending')
  q.filter('accept_as_project', True)
  q.filter('has_mentor', True)
  q.order('-score')

  # We are not putting this into the filter because order and != do not mix
  # in GAE.
  proposals = q.fetch(slots_left_to_assign)

  offset = slots_left_to_assign
  # retrieve as many additional proposals as needed in case the top
  # N do not have a mentor assigned
  while len(proposals) < slots_left_to_assign:
    new_proposals = q.fetch(step_size, offset=offset)

    if not new_proposals:
      # we ran out of proposals`
      break

    proposals += new_proposals
    offset += step_size

  # cut off any superfluous proposals
  return proposals[:slots_left_to_assign]

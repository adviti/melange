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

"""Logic for GSoC slot transfers.
"""


from soc.modules.gsoc.models.slot_transfer import GSoCSlotTransfer


def getSlotTransferEntitiesForOrg(org_entity, limit=1000):
  """Returns the slot transfer entity for the organization.

  params:
    org_entity: the Organization for which the slot transfer entity must be
        fetched

  returns:
    The slot transfer entity for the given organization
  """

  q = GSoCSlotTransfer.all().ancestor(org_entity)
  return q.fetch(limit=limit)

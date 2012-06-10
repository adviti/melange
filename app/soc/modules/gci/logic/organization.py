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

"""GCIOrganization logic methods.
"""


from soc.logic import organization as org_logic

from soc.modules.gci.models.organization import GCIOrganization
from soc.modules.gci.models.task import GCITask


def getRemainingTaskQuota(org):
  """Returns the number of remaining tasks that the organization can publish.

  While calculating the remaining quota we consider all the tasks that
  were published including the closed tasks but not the deleted tasks.

  Args:
    org: The organization entity for which the quota must be calculated

  Returns:
    An integer which is the number of tasks the organization can publish yet
  """
  # TODO(Madhu): Refactor to create Open Tasks and Closed tasks variables
  # count all the tasks the organization has published till now.
  # This excludes tasks in Unapproved, Unpublished and Invalid states.
  valid_status = ['Open', 'Reopened', 'ClaimRequested', 'Claimed',
                  'ActionNeeded', 'Closed', 'AwaitingRegistration',
                  'NeedsWork', 'NeedsReview']

  q = GCITask.all()
  q.filter('org', org)
  q.filter('status IN', valid_status)

  return org.task_quota_limit - q.count()


def participating(program):
  """Return a list of GCI organizations to display on GCI program homepage.

  Function that acts as a GCI module wrapper for fetching participating
  organizations.

  Args:
    program: GCIProgram entity for which the orgs need to be fetched.
  """
  return org_logic.participating(GCIOrganization, program)

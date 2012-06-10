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

"""GCI logic for profiles.
"""


from soc.tasks import mailer

from soc.modules.gci.logic.helper import notifications
from soc.modules.gci.models.profile import GCIProfile
from soc.modules.gci.models.task import GCITask


def queryAllMentorsForOrg(org, keys_only=False, limit=1000):
  """Returns a list of keys of all the mentors for the organization

  Args:
    org: the organization entity for which we need to get all the mentors
    keys_only: True if only the entity keys must be fetched instead of the
        entities themselves.
    limit: the maximum number of entities that must be fetched

  returns:
    List of all the mentors for the organization
  """

  # get all mentors keys first
  query = GCIProfile.all(keys_only=keys_only)
  query.filter('mentor_for', org)
  mentors = query.fetch(limit=limit)

  return mentors


def queryAllMentorsKeysForOrg(org, limit=1000):
  """Returns a list of keys of all the mentors for the organization

  Args:
    org: the organization entity for which we need to get all the mentors
    limit: the maximum number of entities that must be fetched

  returns:
    List of all the mentors for the organization
  """
  return queryAllMentorsForOrg(org, keys_only=True, limit=limit)


def sendFirstTaskConfirmationTxn(profile, task):
  """Returns a transaction which sends a confirmation email to a student who
  completes their first task.
  """

  if not profile.student_info:
    raise ValueError('Only students can be queried for closed tasks.')
  
  context = notifications.getFirstTaskConfirmationContext(profile)
  return mailer.getSpawnMailTaskTxn(context, parent=task)


def orgAdminsForOrg(org, limit=1000):
  """Returns the organization administrators for the given GCI Organization.

  Args:
    org: The GCIOrganization entity for which the admins should be found.
  """
  query = GCIProfile.all()
  query.filter('org_admin_for', org)

  return query.fetch(limit)


def queryProfileForUserAndProgram(user, program):
  """Returns the query to fetch GCIProfile entity for the specified user
  and program.

  Args:
    user: User entity for which the profile should be found
    program: GCIProgram entity for which the profile should be found
  """
  return GCIProfile.all().ancestor(user).filter('scope = ', program)

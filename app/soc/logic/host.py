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

"""Logic for Host Model.
"""


from soc.models.host import Host
from soc.models.program import Program
from soc.models.user import User


def getHostForUser(user_entity):
  """Returns the host entity for the given user.

  Args:
    user_entity: the user for whom the Host entity must be fetched.

  returns:
    The host entity for the given user_entity
  """

  q = Host.all().ancestor(user_entity)
  return q.get()


def getHostsForProgram(program_entity, limit=1000):
  """Returns all the host entities for the given program.

  Args:
    program_entity: The Program entity for which the hosts must be determined

  Returns:
    The list of host entities for the specified program entity
  """
  sponsor_key = Program.scope.get_value_for_datastore(
      program_entity)
  q = User.all()
  q.filter('host_for', sponsor_key)
  host_users = q.fetch(1000)

  # TODO(Madhu): to be simplified after host_for is moved from user entity
  # to host entity
  hosts = []
  for user in host_users:
    q = Host.all()
    q.ancestor(user)
    hosts.append(q.get())

  return hosts

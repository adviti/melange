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

"""Organization (Model) query functions.
"""


import datetime

from google.appengine.api import memcache


def _orgsWithLogoForQuery(query, batch_size=5):
  """Return the org entities for the given query and batch size which have
  Logo URL set.

  Args:
    query: Appengine query for which the entities must be fetched
    batch_size: number of entities that needs to be fetched
  """
  orgs = []
  for org in query:
    if org.logo_url:
      orgs.append(org)
      if len(orgs) == batch_size:
        break

  return orgs


def _orgWithLogoQuery(model, program):
  """Returns a query for Organizations in the specified program with logo.
  """
  q = model.all()
  q.filter('scope', program)
  q.filter('status', 'active')
  q.filter('logo_url >=', '')

  return q


def participating(model, program):
  """Return a list of organizations to display on program homepage.

  Args:
    program: program entity for which the orgs need to be fetched.
  """
  # expiry time to fetch the new organization entities
  # the current expiry time is 30 minutes.
  expiry_time = datetime.timedelta(seconds=1800)

  batch_size = 5

  q = _orgWithLogoQuery(model, program)

  # the cache stores a 3-tuple in the order list of org entities,
  # cursor and the last time the cache was updated

  key = 'participating_orgs_for' + program.key().name()
  po_cache = memcache.get(key)

  if po_cache:
    cached_orgs, cached_cursor, cached_time = po_cache
    if not datetime.datetime.now() > cached_time + expiry_time:
      return cached_orgs
    else:
      q.with_cursor(cached_cursor)

  orgs = _orgsWithLogoForQuery(q, batch_size)

  if len(orgs) < batch_size:
    q = _orgWithLogoQuery(model, program)
    extra_orgs = _orgsWithLogoForQuery(q, batch_size - len(orgs))

    # add only those orgs which are not already in the list
    orgs_keys = [o.key() for o in orgs]
    for org in extra_orgs:
      if org.key() not in orgs_keys:
        orgs.append(org)

  new_cursor = q.cursor()
  memcache.set(key, value=(orgs, new_cursor, datetime.datetime.now()))

  return orgs

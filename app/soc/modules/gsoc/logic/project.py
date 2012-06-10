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

"""Logic for GSoC Project Model.
"""


import datetime

from google.appengine.api import memcache
from google.appengine.ext import db

from soc.modules.gsoc.models.project import GSoCProject


def getFeaturedProject(current_timeline, program):
  """Return a featured project for a given program.

  Args:
    current_timeline: where we are currently on the program timeline
    program: entity representing the program from which the featured
        projects should be fetched
  """
  # expiry time to fetch the new featured project entity
  # the current expiry time is 2 hours.
  expiry_time = datetime.timedelta(seconds=7200)

  def queryForProject():
    query = GSoCProject.all()
    query.filter('is_featured', True)
    query.filter('program', program)
    if current_timeline == 'coding_period':
      project_status = 'accepted'
    else:
      project_status = 'completed'
    query.filter('status', project_status)
    return query

  q = queryForProject()

  # the cache stores a 3-tuple in the order student_project entity,
  # cursor and the last time the cache was updated
  fsp_cache = memcache.get('featured_gsoc_project')

  if fsp_cache:
    cached_project, cached_cursor, cache_expiry_time = fsp_cache
    if not datetime.datetime.now() > cache_expiry_time + expiry_time:
      return cached_project
    else:
      q.with_cursor(cached_cursor)
      if q.count() == 0:
        q = queryForProject()

  new_project = q.get()
  new_cursor = q.cursor()
  memcache.set(
    key='featured_gsoc_project',
    value=(new_project, new_cursor, datetime.datetime.now()))

  return new_project


def getProjectsQuery(keys_only=False, ancestor=None, **properties):
  """Returns the Appengine GSoCProject query object for the given set
  of properties.

  Args:
    ancestor: The student for which the accepted projects must be fetched.
    properties: keyword arguments containing the properties for which the
        query must be constructed.
  """
  q = db.Query(GSoCProject, keys_only=keys_only)

  if ancestor:
    q.ancestor(ancestor)

  for k, v in properties.items():
    q.filter(k, v)

  return q


def getAcceptedProjectsQuery(keys_only=False, ancestor=None, **properties):
  """Returns the Appengine GSoCProject query object for the given
  set of properties for accepted projects.

  Args:
    ancestor: The student for which the accepted projects must be fetched.
    properties: keyword arguments containing the properties for which the
        query must be constructed.
  """
  q = getProjectsQuery(keys_only, ancestor, **properties)
  q.filter('status', 'accepted')

  return q


def getAcceptedProjectsForOrg(org, limit=1000):
  """Returns all the accepted projects for a given organization.

  Args:
    org: The organization entity for which the accepted projects are accepted.
  """
  q = getAcceptedProjectsQuery(org=org)
  return q.fetch(limit)

def getAcceptedProjectsForStudent(student, limit=1000):
  """Returns all the accepted projects for a given student.

  Args:
    student: The student for whom the projects should be retrieved.
  """
  q = getAcceptedProjectsQuery(ancestor=student)
  return q.fetch(limit)

def getProjectsQueryForOrgs(orgs):
  """Returns the query corresponding to projects for the given organization(s).

  Args:
    orgs: The list of organization entities for which the projects
        should be queried.
  """
  q = getProjectsQuery()
  orgs = list(orgs)
  q.filter('org IN', orgs)
  return q


def getProjectsQueryForEval(keys_only=False, ancestor=None, **properties):
  """Returns the query corresponding to projects to be evaluated.

  This is a special query needed to build evaluation lists.
  """
  q = getProjectsQuery(keys_only, ancestor, **properties)
  q.filter('status IN', ['accepted', 'failed', 'completed'])
  return q


def getProjectsQueryForEvalForOrgs(orgs):
  """Returns the query corresponding to projects for the given organization(s).

  This is a special query needed to build evaluation lists.

  Args:
    orgs: The list of organization entities for which the projects
        should be queried.
  """
  q = getProjectsQueryForOrgs(orgs)
  q.filter('status IN', ['accepted', 'failed', 'completed'])
  return q


def getProjectsForOrgs(orgs, limit=1000):
  """Returns all the projects for the given organization(s).

  Unlike getAcceptedProjectsForOrg function, this returns all the projects
  for all the orgs listed

  Args:
    orgs: The list of organization entities for which the projects
        should be queried.
  """
  q = getProjectsQueryForOrgs(orgs)
  return q.fetch(limit)

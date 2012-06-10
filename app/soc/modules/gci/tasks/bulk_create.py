#!/usr/bin/python2.5
#
# Copyright 2010 the Melange authors.
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

"""Appengine Tasks related to GCI Task bulk create.
"""


import csv
import logging
import StringIO
import time

from django import http
from django.conf.urls.defaults import url
from django.utils import simplejson

from google.appengine.ext import db
from google.appengine.api import taskqueue
from google.appengine.runtime import DeadlineExceededError

from HTMLParser import HTMLParseError

from htmlsanitizer import HtmlSanitizer
from htmlsanitizer import safe_html

from soc.tasks.helper import error_handler
from soc.tasks.helper.timekeeper import Timekeeper

from soc.modules.gci.logic.organization import getRemainingTaskQuota
from soc.modules.gci.logic.helper import notifications
from soc.modules.gci.models.bulk_create_data import GCIBulkCreateData
from soc.modules.gci.models.profile import GCIProfile
from soc.modules.gci.models.task import DIFFICULTIES
from soc.modules.gci.models.task import GCITask


BULK_CREATE_URL = '/tasks/gci/task/bulk_create'

DATA_HEADERS = ['title', 'description', 'time_to_complete', 'mentors',
                'difficulty', 'task_type', 'arbit_tag']


class BulkCreateTask(object):
  """Request handlers for bulk creating GCITasks.
  """

  def djangoURLPatterns(self):
    """Returns the URL patterns for the tasks in this module
    """
    patterns = [
        url(r'^tasks/gci/task/bulk_create$', self.bulkCreateTasks,
            name='gci_bulk_create_task'),
        ]
    return patterns

  def bulkCreateTasks(self, request, *args, **kwargs):
    """Task that creates GCI Tasks from bulk data specified in the POST dict.

    The POST dict should have the following information present:
        bulk_create_key: the key of the bulk_create entity
    """
    import settings

    # keep track of our own timelimit (20 seconds)
    timelimit = 20000
    timekeeper = Timekeeper(timelimit)

    post_dict = request.POST

    bulk_create_key = post_dict.get('bulk_create_key')
    if not bulk_create_key:
      return error_handler.logErrorAndReturnOK(
                 'Not all POST data specified in: %s' % post_dict)

    bulk_data = GCIBulkCreateData.get(bulk_create_key)
    if not bulk_data:
      return error_handler.logErrorAndReturnOK(
                 'No valid data found for key: %s' % bulk_create_key)

    # note that we only query for the quota once
    org_admin = bulk_data.created_by
    org = bulk_data.org
    task_quota = getRemainingTaskQuota(org)

    # TODO(ljvderijk): Add transactions

    tasks = bulk_data.tasks
    while len(tasks) > 0:
      try:
        # check if we have time
        timekeeper.ping()

        if settings.GCI_TASK_QUOTA_LIMIT_ENABLED and task_quota <= 0:
          return error_handler.logErrorAndReturnOK(
              'Task quota reached for %s' %(org.name))

        # remove the first task
        task_as_string = tasks.pop(0)

        loaded_task = simplejson.loads(task_as_string)
        task = {}
        for key, value in loaded_task.iteritems():
          # If we don't do this python will complain about kwargs not being
          # strings when we try to save the new task.
          task[key.encode('UTF-8')] = value

        logging.info('Uncleaned task: %s' %task)
        # clean the data
        errors = self._cleanTask(task, org)

        if errors:
          logging.warning(
              'Invalid task data uploaded, the following errors occurred: %s'
              %errors)
          bulk_data.errors.append(db.Text(
              'The task in row %i contains the following errors.\n %s' \
              %(bulk_data.tasksRemoved(), '\n'.join(errors))))

        # at-most-once semantics for creating tasks
        bulk_data.put()

        if errors:
          # do the next task
          continue

        # set other properties
        task['org'] = org
        task['program'] = org_admin.scope
        task['status'] = 'Unpublished'
        task['created_by'] = org_admin
        task['modified_by'] = org_admin

        subscribers_entities = task['mentor_entities'] + [org_admin]
        task['subscribers'] = list(set([ent.key() for ent in
            subscribers_entities if ent.automatic_task_subscription]))

        # create the new task
        logging.info('Creating new task with fields: %s' %task)
        task_entity = GCITask(**task)
        task_entity.put()
        task_quota = task_quota - 1
      except DeadlineExceededError:
        # time to bail out
        break

    if len(tasks) == 0:
      # send out a message
      notifications.sendBulkCreationCompleted(bulk_data)
      bulk_data.delete()
    else:
      # there is still work to be done, do a non 500 response and requeue
      task_params = {
          'bulk_create_key': bulk_data.key()
          }
      new_task = taskqueue.Task(params=task_params,
                                url=BULK_CREATE_URL)
      # add to the gci queue
      new_task.add(queue_name='gci-update')

    # we're done here
    return http.HttpResponse('OK')

  def _cleanTask(self, task, org):
    """Cleans the data given so that it can be safely stored as a task.

      Args:
        task: Dictionary as constructed by the csv.DictReader().
        org: the GCIOrganization for which the task is created.

      Returns:
          A list of error messages if any have occurred.
    """

    errors = []

    # check title
    if not task['title']:
      errors.append('No valid title present.')

    # clean description
    try:
      cleaner = HtmlSanitizer.Cleaner()
      cleaner.string = task['description']
      cleaner.clean()
      task['description'] = cleaner.string.strip().replace('\r\n', '\n')
    except (HTMLParseError, safe_html.IllegalHTML, TypeError), e:
      logging.warning('Cleaning of description failed with: %s' %e)
      errors.append(
          'Failed to clean the description, do not use naughty HTML such as '
          '<script>.')

    # clean time to complete
    try:
      task['time_to_complete'] = int(task['time_to_complete'])
    except (ValueError, TypeError), e:
      errors.append('No valid time to completion found, given was: %s.'
                    % task['time_to_complete'])

    # clean mentors
    mentor_ids = set(task['mentors'].split(','))

    mentors = []
    mentor_entities = []
    for mentor_id in mentor_ids:
      q = GCIProfile.all()
      q.filter('link_id', mentor_id.strip())
      q.filter('mentor_for', org)
      q.filter('status', 'active')
      mentor = q.get()
      if mentor:
        mentors.append(mentor.key())
        mentor_entities.append(mentor)
      else:
        errors.append('%s is not a mentor.' % mentor_id)

    task['mentors'] = mentors
    task['mentor_entities'] = mentor_entities

    program_entity = org.scope

    # clean task difficulty
    difficulty = task['difficulty'].strip()
    if not difficulty or difficulty not in DIFFICULTIES:
      # no valid difficulty found
      errors.append('No valid task difficulty found, given %s.' % difficulty)
    else:
      task['difficulty_level'] = difficulty

    # clean task types
    types = []
    for task_type in set(task['task_type'].split(',')):
      task_type = task_type.strip()
      if task_type in program_entity.task_types:
        types.append(task_type)
      else:
        errors.append('%s is not a valid task type.' % task_type)
    task['types'] = types

    # clean task tags
    tags = []
    for tag in set(task['arbit_tag'].split(',')):
      tags.append(tag.strip())
    task['tags'] = tags

    return errors


def spawnBulkCreateTasks(data, org, org_admin):
  """Spawns a task to bulk post the given data.

  The data given to this method should be in CSV format with the following
  columns:
      title, description, time_to_complete, mentors, difficulty, task_type,
      arbit_tag

  Fields where multiple values are allowed should be comma separated as well.
  These fields are task_type, arbit_tag and mentors. Rows of data which can not
  be properly resolved to form a valid Task will be safely ignored.

  Args:
    data: string with data in csv format
    org: GCIOrganization for which the tasks are created
    org_admin: GCIProfile of the org admin uploading these tasks
  """
  data = StringIO.StringIO(data.encode('UTF-8'))
  tasks = csv.DictReader(data, fieldnames=DATA_HEADERS, restval="")

  task_list = []
  for task in tasks:
    # pop any extra columns
    task.pop(None,None)
    task_list.append(db.Text(simplejson.dumps(task)))

  bulk_data = GCIBulkCreateData(
      tasks=task_list, org=org, created_by=org_admin,
      total_tasks=len(task_list))
  bulk_data.put()

  task_params = {
      'bulk_create_key': bulk_data.key()
      }

  logging.info('Enqueued bulk_create with: %s' % task_params)
  new_task = taskqueue.Task(params=task_params,
                            url=BULK_CREATE_URL)
  new_task.add()

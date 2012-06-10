#!/usr/bin/env python2.5
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

"""Tasks related to Calculating duplicate proposals.
"""


import datetime

from google.appengine.api import taskqueue
from google.appengine.ext import db

from django import http
from django.conf.urls.defaults import url as django_url

from soc.tasks.helper import error_handler

from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.logic import proposal as proposal_logic
from soc.modules.gsoc.logic import duplicates as duplicates_logic
from soc.modules.gsoc.models.proposal_duplicates import GSoCProposalDuplicate


# TODO(ljvderijk): General purpose task responses such as retry(), abort() and
# error message can be defined in a parent class of this object.
class ProposalDuplicatesTask(object):
  """Request handler for Proposal Duplicates view.
  """
  def djangoURLPatterns(self):
    """Returns the URL patterns for the tasks in this module.
    """
    patterns = [
        django_url(r'^tasks/gsoc/proposal_duplicates/start$',
                   self.start, name='proposal_duplicates_task_start'),
        django_url(r'^tasks/gsoc/proposal_duplicates/calculate$',
                   self.calculate, name='proposal_duplicates_task_calculate'),
        ]
    return patterns

  def start(self, request, *args, **kwargs):
    """Starts the task to find all duplicate proposals which are about to be
    accepted for a single GSoCProgram.

    Expects the following to be present in the POST dict:
      program_key: Specifies the program key name for which to find the
                   duplicate proposals
      repeat: Specifies if a new task that must be performed again an hour
              later, with the same POST data

    Args:
      request: Django Request object
    """

    from soc.logic.helper import timeline as timeline_helper

    post_dict = request.POST

    # retrieve the program_key and repeat option from POST data
    program_key = post_dict.get('program_key')
    repeat = post_dict.get('repeat')

    if not (program_key and repeat):
      # invalid task data, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid task data: %s' % post_dict)

    # get the program for the given keyname
    program_entity = GSoCProgram.get_by_key_name(program_key)

    if not program_entity:
      # invalid program specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid program specified: %s' % program_key)

    # obtain the proposal duplicate status
    pds_entity = duplicates_logic.getOrCreateStatusForProgram(program_entity)

    if pds_entity.status == 'idle':
      # delete all old duplicates
      duplicates_logic.deleteAllForProgram(program_entity)

      # pass these data along params as POST to the new task
      task_params = {'program_key': program_key}
      task_url = '/tasks/gsoc/proposal_duplicates/calculate'

      new_task = taskqueue.Task(params=task_params, url=task_url)

      def txn():
        # add a new task that performs duplicate calculation per
        # organization
        new_task.add(transactional=True)

        # update the status of the PDS entity to processing
        pds_entity.status = 'processing'
        pds_entity.put()

      db.RunInTransaction(txn)

    # Add a new clone of this task that must be performed an hour later because
    # the current task is part of the task that repeatedly runs but repeat
    # it before accepted students are announced only.
    if repeat == 'yes' and timeline_helper.isBeforeEvent(
        program_entity.timeline, 'accepted_students_announced_deadline'):
      # pass along these params as POST to the new task
      task_params = {'program_key': program_key,
                     'repeat': 'yes'}
      task_url = '/tasks/gsoc/proposal_duplicates/start'

      new_task = taskqueue.Task(params=task_params, url=task_url,
                                countdown=3600)
      new_task.add()

    # return OK
    return http.HttpResponse()


  def calculate(self, request, *args, **kwargs):
    """Calculates the duplicate proposals in a given program for
    a student on a per Organization basis.

    Expects the following to be present in the POST dict:
      program_key: Specifies the program key name for which to find the
                   duplicate proposals
      org_cursor: Specifies the organization datastore cursor from which to
                  start the processing of finding the duplicate proposals

    Args:
      request: Django Request object
    """
    post_dict = request.POST

    program_key = post_dict.get('program_key')
    if not program_key:
      # invalid task data, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid program key: %s' % post_dict)

    program_entity = GSoCProgram.get_by_key_name(program_key)
    if not program_entity:
      # invalid program specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid program specified: %s' % program_key)

    # get the organization and update the cursor if possible
    q = GSoCOrganization.all()
    q.filter('status', 'active')
    q.filter('scope', program_entity)
    q.filter('slots >', 0)

    # retrieve the org_cursor from POST data
    org_cursor = post_dict.get('org_cursor')

    if org_cursor:
      org_cursor = str(org_cursor)
      q.with_cursor(org_cursor)

    org_entity = q.get()
    # update the cursor
    org_cursor = q.cursor()

    if org_entity:
      # get all the proposals likely to be accepted in the program
      accepted_proposals = proposal_logic.getProposalsToBeAcceptedForOrg(org_entity)

      for ap in accepted_proposals:
        student_entity = ap.parent()

        q = GSoCProposalDuplicate.all()
        q.filter('student', student_entity)
        proposal_duplicate = q.get()

        if proposal_duplicate and ap.key() not in proposal_duplicate.duplicates:
          # non-counted (to-be) accepted proposal found
          proposal_duplicate.duplicates = proposal_duplicate.duplicates + \
                                          [ap.key()]
          proposal_duplicate.is_duplicate = \
              len(proposal_duplicate.duplicates) >= 2
          if org_entity.key() not in proposal_duplicate.orgs:
            proposal_duplicate.orgs = proposal_duplicate.orgs + [org_entity.key()]
        else:
          pd_fields  = {
              'program': program_entity,
              'student': student_entity,
              'orgs':[org_entity.key()],
              'duplicates': [ap.key()],
              'is_duplicate': False
              }
          proposal_duplicate = GSoCProposalDuplicate(**pd_fields)

        proposal_duplicate.put()

      # Adds a new task that performs duplicate calculation for
      # the next organization.
      task_params = {'program_key': program_key,
                     'org_cursor': unicode(org_cursor)}
      task_url = '/tasks/gsoc/proposal_duplicates/calculate'

      new_task = taskqueue.Task(params=task_params, url=task_url)
      new_task.add()
    else:
      # There aren't any more organizations to process. So delete
      # all the proposals for which there are not more than one
      # proposal for duplicates property.
      duplicates_logic.deleteAllForProgram(program_entity, non_dupes_only=True)

      # update the proposal duplicate status and its timestamp
      pds_entity = duplicates_logic.getOrCreateStatusForProgram(program_entity)
      pds_entity.status = 'idle'
      pds_entity.calculated_on = datetime.datetime.now()
      pds_entity.put()

    # return OK
    return http.HttpResponse()

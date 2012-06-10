#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""Tasks related to Grading Survey Groups and Records.
"""


import datetime
import logging

from google.appengine.api import taskqueue
from google.appengine.ext import db

from django import http
from django.conf.urls.defaults import url

from soc.logic import mail_dispatcher
from soc.logic import site
from soc.tasks.helper import error_handler

from soc.modules.gsoc.logic import grading_record
from soc.modules.gsoc.models.grading_record import GSoCGradingRecord
from soc.modules.gsoc.models.grading_survey_group import GSoCGradingSurveyGroup
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.project import GSoCProject


class GradingRecordTasks(object):
  """Tasks that are involved in dealing with GradingRecords.
  """

  # batch size to use when going through StudentProjects
  DEF_BATCH_SIZE = 25

  def djangoURLPatterns(self):
    """Returns the URL patterns for the tasks in this module.
    """
    patterns = [
        url(r'tasks/gsoc/grading_record/update_records$',
            self.updateRecordsForSurveyGroup),
        url(r'tasks/gsoc/grading_record/update_projects$',
            self.updateProjectsForSurveyGroup),
        url(r'tasks/gsoc/grading_record/mail_result',
            self.sendMailAboutGradingRecordResult)]
    return patterns

  def updateRecordsForSurveyGroup(self, request, *args, **kwargs):
    """Updates or creates GradingRecords for the given GradingSurveyGroup.

    Expects the following to be present in the POST dict:
      group_key: Specifies the GradingSurveyGroup key name.
      cursor: optional to specify where the query should continue from.

    Args:
      request: Django Request object
    """
    post_dict = request.POST

    group_key = post_dict.get('group_key')

    if not group_key:
      # invalid task data, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid updateRecordForSurveyGroup data: %s' % post_dict)

    # get the GradingSurveyGroup for the given key
    survey_group = GSoCGradingSurveyGroup.get_by_id(int(group_key))

    if not survey_group:
      # invalid GradingSurveyGroup specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid GradingSurveyGroup specified: %s' % group_key)

    q = GSoCProject.all()
    q.filter('program', survey_group.program)
    q.filter('status', 'accepted')

    if 'cursor' in post_dict:
      q.with_cursor(post_dict['cursor'])

    # get the first batch_size number of StudentProjects
    projects = q.fetch(self.DEF_BATCH_SIZE)

    if not projects:
      # task completed, update timestamp for last update complete
      survey_group.last_update_complete = datetime.datetime.now()
      survey_group.put()
      return http.HttpResponse()

    # update/create and batch put the new GradingRecords
    grading_record.updateOrCreateRecordsFor(survey_group, projects)

    # pass along these params as POST to the new task
    task_params = {'group_key': group_key,
                   'cursor': q.cursor()}

    new_task = taskqueue.Task(params=task_params, url=request.path)
    new_task.add()

    # task completed, return OK
    return http.HttpResponse('OK')

  def updateProjectsForSurveyGroup(self, request, *args, **kwargs):
    """Updates each StudentProject for which a GradingRecord is found.

    Expects the following to be present in the POST dict:
      group_key: Specifies the GradingSurveyGroup key name.
      cursor: Optional, specifies the cursor for the GadingRecord query.
      send_mail: Optional, if this string evaluates to True mail will be send
                 for each GradingRecord that's processed.

    Args:
      request: Django Request object
    """
    post_dict = request.POST

    group_key = post_dict.get('group_key')
    if not group_key:
      # invalid task data, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid updateRecordForSurveyGroup data: %s' % post_dict)

    # get the GradingSurveyGroup for the given keyname
    survey_group = GSoCGradingSurveyGroup.get_by_id(int(group_key))

    if not survey_group:
      # invalid GradingSurveyGroup specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid GradingSurveyGroup specified: %s' % group_key)

    q = GSoCGradingRecord.all()
    q.filter('grading_survey_group', survey_group)

    if 'cursor' in post_dict:
      q.with_cursor(post_dict['cursor'])

    # get the first batch_size number of GradingRecords
    records = q.fetch(self.DEF_BATCH_SIZE)

    if not records:
      # we are done
      return http.HttpResponse()

    grading_record.updateProjectsForGradingRecords(records)

    # check if we need to send an email for each GradingRecord
    send_mail = post_dict.get('send_mail', '')

    if send_mail:
      # enqueue a task to send mail for each GradingRecord
      for record in records:
        # pass along these params as POST to the new task
        task_params = {'record_key': str(record.key())}
        task_url = '/tasks/gsoc/grading_record/mail_result'

        mail_task = taskqueue.Task(params=task_params, url=task_url)
        mail_task.add('mail')

    # pass along these params as POST to the new task
    task_params = {'group_key': group_key,
                   'cursor': q.cursor(),
                   'send_mail': send_mail}

    new_task = taskqueue.Task(params=task_params, url=request.path)
    new_task.add()

    # task completed, return OK
    return http.HttpResponse('OK')

  def sendMailAboutGradingRecordResult(self, request, *args, **kwargs):
    """Sends out a mail about the result of one GradingRecord.

    Expects the following to be present in the POST dict:
      record_key: Specifies the key for the record to process.

    Args:
      request: Django Request object
    """
    post_dict = request.POST

    record_key = post_dict.get('record_key')

    if not record_key:
      # no GradingRecord key specified, log and return OK
      error_handler.logErrorAndReturnOK(
          'No valid record_key specified in POST data: %s' % request.POST)

    record = GSoCGradingRecord.get(db.Key(record_key))

    if not record:
      # no valid GradingRecord key specified, log and return OK
      error_handler.logErrorAndReturnOK(
          'No valid GradingRecord key specified: %s' % record_key)

    survey_group_entity = record.grading_survey_group
    project_entity = record.parent()
    student_entity = project_entity.parent()
    org_entity = project_entity.org
    site_entity = site.singleton()

    mail_context = {
      'survey_group': survey_group_entity,
      'grading_record': record,
      'project': project_entity,
      'organization': org_entity,
      'site_name': site_entity.site_name,
      'to_name': student_entity.name()
    }

    # set the sender
    (_, sender_address) = mail_dispatcher.getDefaultMailSender()
    mail_context['sender'] = sender_address
  
    # set the receiver and subject
    mail_context['to'] = student_entity.email
    mail_context['cc'] = []
    mail_context['subject'] = '%s results processed for %s' %(
        survey_group_entity.name, project_entity.title)

    q = GSoCProfile.all()
    q.filter('org_admin_for', org_entity)
    org_admins = q.fetch(1000)

    # collect all mentors
    mentors = db.get(project_entity.mentors)

    # add them all to the cc list
    for org_member in org_admins + mentors:
      mail_context['cc'].append(org_member.email)

    # send out the email using a template
    mail_template = 'modules/gsoc/grading_record/mail/result.html'
    mail_dispatcher.sendMailFromTemplate(mail_template, mail_context)

    # return OK
    return http.HttpResponse()

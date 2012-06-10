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

"""Tasks related to sending out survey reminders.
"""


import logging

from google.appengine.api import taskqueue
from google.appengine.ext import db

from django import http
from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse

from soc.logic import mail_dispatcher
from soc.logic import system
from soc.logic import site
from soc.tasks.helper import error_handler

from soc.modules.gsoc.models.grading_project_survey import GradingProjectSurvey
from soc.modules.gsoc.models.grading_project_survey_record import \
    GSoCGradingProjectSurveyRecord
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.models.project_survey import ProjectSurvey
from soc.modules.gsoc.models.project_survey_record import \
    GSoCProjectSurveyRecord


class SurveyReminderTask(object):
  """Tasks that send out reminders for ProjectSurey and GradingProjectSurveys.
  """

  BATCH_SIZE = 25

  def djangoURLPatterns(self):
    """Returns the URL patterns for the tasks in this module.
    """
    patterns = [url(r'tasks/gsoc/surveys/send_reminder/spawn$',
                    self.spawnRemindersForProjectSurvey,
                    name='spawn_survey_reminders'),
                url(r'tasks/gsoc/surveys/send_reminder/send$',
                    self.sendSurveyReminderForProject)]
    return patterns

  def spawnRemindersForProjectSurvey(self, request, *args, **kwargs):
    """Spawns tasks for each StudentProject in the given Program.

    Expects the following to be present in the POST dict:
      program_key: Specifies the program key name for which to loop over all the
                   StudentProjects for
      survey_key: specifies the key name for the ProjectSurvey to send reminders
                  for
      survey_type: a string which is project or grading depending on the type of
                   Survey.
      cursor: optional query cursor to indicate how far along we are.

    Args:
      request: Django Request object
    """
    post_dict = request.POST

    # retrieve the program_key and survey_key from POST data
    program_key = post_dict.get('program_key')
    survey_key = post_dict.get('survey_key')
    survey_type = post_dict.get('survey_type')

    if not (program_key and survey_key and survey_type):
      # invalid task data, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid spawnRemindersForProjectSurvey data: %s' % post_dict)

    program_entity = GSoCProgram.get_by_key_name(program_key)

    if not program_entity:
      # invalid program specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid program specified: %s' % program_key)

    q = GSoCProject.all()
    q.filter('status', 'accepted')
    q.filter('program', program_entity)

    if 'cursor' in post_dict:
      q.with_cursor(post_dict['cursor'])

    projects = q.fetch(self.BATCH_SIZE)

    if not projects:
      # we are done, return OK
      return http.HttpResponse()

    for project in projects:
      task_params = {'survey_key': survey_key,
                     'survey_type': survey_type,
                     'project_key': str(project.key())}
      task_url = '/tasks/gsoc/surveys/send_reminder/send'

      new_task = taskqueue.Task(params=task_params, url=task_url)
      new_task.add('mail')

    # pass along these params as POST to the new task
    task_params = {'program_key': program_key,
                   'survey_key': survey_key,
                   'survey_type': survey_type,
                   'cursor': q.cursor()}
    task_url = request.path
    new_task = taskqueue.Task(params=task_params, url=task_url)
    new_task.add()

    # return OK
    return http.HttpResponse()

  def sendSurveyReminderForProject(self, request, *args, **kwargs):
    """Sends a reminder mail for a given StudentProject and Survey.

    A reminder is only send if no record is on file for the given Survey and 
    StudentProject.

    Expects the following to be present in the POST dict:
      survey_key: specifies the key name for the ProjectSurvey to send reminders
                  for
      survey_type: either project or grading depending on the type of Survey
      project_key: encoded Key which specifies the project to send a reminder 
                   for

    Args:
      request: Django Request object
    """
    post_dict = request.POST

    project_key = post_dict.get('project_key')
    survey_key = post_dict.get('survey_key')
    survey_type = post_dict.get('survey_type')

    if not (project_key and survey_key and survey_type):
      # invalid task data, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid sendSurveyReminderForProject data: %s' % post_dict)

    # set model depending on survey type specified in POST
    if survey_type == 'project':
      survey_model = ProjectSurvey
      record_model = GSoCProjectSurveyRecord
    elif survey_type == 'grading':
      survey_model = GradingProjectSurvey
      record_model = GSoCGradingProjectSurveyRecord
    else:
      return error_handler.logErrorAndReturnOK(
          '%s is an invalid survey_type' %survey_type)

    # retrieve the project and survey
    project_key = db.Key(project_key)
    project = GSoCProject.get(project_key)
    if not project:
      # no existing project found, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid project specified %s:' % project_key)

    survey = survey_model.get_by_key_name(survey_key)
    if not survey:
      # no existing survey found, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid survey specified %s:' % survey_key)

    # try to retrieve an existing record
    q = record_model.all()
    q.filter('project', project)
    q.filter('survey', survey)
    record = q.get()

    if not record:
      # send reminder email because we found no record
      student_profile = project.parent()
      site_entity = site.singleton()

      if survey_type == 'project':
        url_name = 'gsoc_take_student_evaluation'

        to_name = student_profile.name()
        to_address = student_profile.email
        mail_template = 'v2/modules/gsoc/reminder/student_eval_reminder.html'
      elif survey_type == 'grading':
        url_name = 'gsoc_take_mentor_evaluation'

        mentors = db.get(project.mentors)
        to_address = [m.email for m in mentors]
        to_name = 'mentor(s) for project "%s"' %(project.title)
        mail_template = \
            'v2/modules/gsoc/reminder/mentor_eval_reminder.html'

      program = project.program
      hostname = system.getHostname()
      url_kwargs = {
          'sponsor': program.scope.link_id,
          'program': program.link_id,
          'survey': survey.link_id,
          'user': student_profile.link_id,
          'id': str(project.key().id()),
          }
      url = reverse(url_name, kwargs=url_kwargs)
      survey_url = '%s://%s%s' % ('http', hostname, url)

      # set the context for the mail template
      mail_context = {
          'student_name': student_profile.name(),
          'project_title': project.title,
          'survey_url': survey_url,
          'survey_end': survey.survey_end,
          'to_name': to_name,
          'site_name': site_entity.site_name,
          'sender_name': "The %s Team" % site_entity.site_name,
      }

      # set the sender
      (_, sender_address) = mail_dispatcher.getDefaultMailSender()
      mail_context['sender'] = sender_address
      # set the receiver and subject
      mail_context['to'] = to_address
      mail_context['subject'] = \
          'Evaluation Survey "%s" Reminder' %(survey.title)

      # find all org admins for the project's organization
      org = project.org

      q = GSoCProfile.all()
      q.filter('status', 'active')
      q.filter('org_admin_for', org)
      org_admins = q.fetch(1000)

      # collect email addresses for all found org admins
      org_admin_addresses = []

      for org_admin in org_admins:
        org_admin_addresses.append(org_admin.email)

      if org_admin_addresses:
        mail_context['cc'] = org_admin_addresses

      # send out the email
      mail_dispatcher.sendMailFromTemplate(mail_template, mail_context)

    # return OK
    return http.HttpResponse()

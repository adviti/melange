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

"""Notifications for the GCI module.
"""


from django.template import loader
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext

from soc.logic import accounts
from soc.logic import dicts
from soc.logic import mail_dispatcher
from soc.logic import site
from soc.logic import system
from soc.logic.helper import notifications
from soc.tasks import mailer


DEF_BULK_CREATE_COMPLETE_SUBJECT = ugettext(
    'Bulk creation of tasks completed')

DEF_BULK_CREATE_COMPLETE_TEMPLATE = 'v2/modules/gci/reminder/bulk_create.html'

DEF_FIRST_TASK_CONFIRMATION_SUBJECT = ugettext(
    'You have completed your first task in Google Code In program')

DEF_FIRST_TASK_CONFIRMATION_TEMPLATE = \
    'v2/modules/gci/notification/first_task_confirmation.html'

DEF_TASK_REQUEST_SUBJECT = ugettext(
    'A new task has been requested from your organization')

DEF_TASK_REQUEST_TEMPLATE = \
    'modules/gci/notification/messages/task_request.html'

DEF_PARENTAL_FORM_SUBJECT = ugettext(
    '[%(program_name)s]: Parental Consent Form - Please Respond')

DEF_NEW_TASK_COMMENT_SUBJECT = ugettext(
    '[%(program_name)s] New comment on %(task_title)s')

DEF_NEW_TASK_COMMENT_NOTIFICATION_TEMPLATE = \
    'v2/modules/gci/notification/new_task_comment.html'


def sendMail(to_user, subject, message_properties, template):
  """Sends an email with the specified properties and mail content

  Args:
    to_user: user entity to whom the mail should be sent
    subject: subject of the mail
    message_properties: contains those properties that need to be
                        customized
    template: template that holds the content of the mail
  """

  from soc.logic import site

  site_entity = site.singleton()
  site_name = site_entity.site_name

  # get the default mail sender
  default_sender = mail_dispatcher.getDefaultMailSender()

  if not default_sender:
    # no valid sender found, abort
    return
  else:
    (sender_name, sender) = default_sender

  to = accounts.denormalizeAccount(to_user.account).email()

  # create the message contents
  new_message_properties = {
      'to_name': to_user.name,
      'sender_name': sender_name,
      'to': to,
      'sender': sender,
      'site_name': site_name,
      'subject': force_unicode(subject)
      }

  messageProperties = dicts.merge(message_properties, new_message_properties)

  # send out the message using the default new notification template
  mail_dispatcher.sendMailFromTemplate(template, messageProperties)

def sendTaskUpdateMail(subscriber, subject, message_properties=None):
  """Sends an email to a user about an update to a Task.

    Args:
      subscriber: The user entity to whom the message must be sent
      subject: Subject of the mail
      message_properties: The mail message properties
      template: Optional django template that is used to build the message body
  """

  template = 'modules/gci/task/update_notification.html'

  # delegate sending mail to the helper function
  sendMail(subscriber, subject, message_properties, template)

def sendBulkCreationCompleted(bulk_data):
  """Sends out a notification that the bulk creation of tasks has been
  completed.

  Any error messages that have been generated are also added to the notification.

  Args:
    bulk_data: GCIBulkCreateData entity containing information needed to
               populate the notification.
  """
  message_properties = {
      'bulk_data' : bulk_data
      }

  subject = DEF_BULK_CREATE_COMPLETE_SUBJECT
  template = DEF_BULK_CREATE_COMPLETE_TEMPLATE

  sendMail(bulk_data.created_by.user, subject, message_properties, template)

def sendParentalConsentFormRequired(user_entity, program_entity):
  """Sends out a notification to the student who completed first task that
  a parent consent form is necessary to receive prizes.

  Args:
    user_entity: User entity who completed his/her first task
    program_entity: The entity for the program for which the task
                    was completed.
  """
  subject = DEF_PARENTAL_FORM_SUBJECT % {
      'program_name': program_entity.name
      }
  template = 'modules/gci/notification/messages/parental_form_required.html'

  # delegate sending mail to the helper function
  sendMail(user_entity, subject, {}, template)

def sendRequestTaskNotification(org_admins, message):
  """Sends notifications to org admins that there is a student who requested
  more tasks from them.

  Args:
    org_admins: a list of org admins who the notification should be sent to
    message: a short message that will be included to the notification
  """

  from soc.logic import site

  # get the default mail sender
  default_sender = mail_dispatcher.getDefaultMailSender()

  if not default_sender:
    # no valid sender found, abort
    return
  else:
    (sender_name, sender) = default_sender

  # get site name
  site_entity = site.singleton()
  template = DEF_TASK_REQUEST_TEMPLATE

  properties = {
      'message': message,
      'sender_name': sender_name,
      }

  for org_admin in org_admins:
    to = org_admin.user
    properties['to'] = to
    properties['to_name'] = to.name

    notifications.sendNotification(to, None, properties, subject, template)

def getFirstTaskConfirmationContext(student):
  """Sends notification to the GCI student, when he or she completes their
  first task.
  
  Args:
    student: the student who should receive the confirmation
  """

  user = student.parent()
  to = accounts.denormalizeAccount(user.account).email()

  subject = DEF_FIRST_TASK_CONFIRMATION_SUBJECT

  program = student.scope

  kwargs = {
      'sponsor': program.scope_path,
      'program': program.link_id
  }
  url = reverse('gci_student_form_upload', kwargs=kwargs)

  protocol = 'http'
  hostname = system.getHostname()

  context = {
      'student_forms_link': '%s://%s%s' % (protocol, hostname, url),
      }

  template = DEF_FIRST_TASK_CONFIRMATION_TEMPLATE
  body = loader.render_to_string(template, context)

  return mailer.getMailContext(to=to, subject=subject, html=body, bcc=[])

def getTaskCommentContext(task, comment, to_emails):
  """Sends out notifications to the subscribers.

  Args:
    task: task entity that comment made on.
    comment: comment entity.
    to_emails: list of recepients for the notification.
  """
  url_kwargs = {
    'sponsor': task.program.scope_path,
    'program': task.program.link_id,
    'id': task.key().id(),
  }

  task_url = 'http://%(host)s%(task)s' % {
      'host': system.getHostname(),
      'task': reverse('gci_view_task', kwargs=url_kwargs)}

  commented_by = comment.created_by.name if comment.created_by else "Melange"

  message_properties = {
      'commented_by': commented_by,
      'comment_title': comment.title,
      'comment_content': comment.content,
      'group': task.org.name,
      'program_name': task.program.name,
      'sender_name': 'The %s Team' % site.singleton().site_name,
      'task_title': task.title,
      'task_url': task_url,
  }

  subject = DEF_NEW_TASK_COMMENT_SUBJECT % message_properties
  template = DEF_NEW_TASK_COMMENT_NOTIFICATION_TEMPLATE
  body = loader.render_to_string(template, dictionary=message_properties)

  return mailer.getMailContext(to=[], subject=subject, html=body, bcc=to_emails)

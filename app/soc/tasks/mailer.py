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

"""Task to send out an email message.
"""


import logging

from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import OverQuotaError
from google.appengine.runtime.apiproxy_errors import DeadlineExceededError

from django.conf.urls.defaults import url as django_url
from django.utils import simplejson

from soc.logic import system
from soc.models import email
from soc.tasks import responses
from soc.tasks.helper import error_handler


SEND_MAIL_URL = '/tasks/mail/send_mail'


def getMailContext(to, subject, html, sender=None, bcc=None):
  """Constructs a mail context for the specified arguments.
  """
  if not sender:
    sender = system.getApplicationNoReplyEmail()

  context = {
      'subject': subject,
      'html': html,
      'sender': sender,
  }

  if to:
    context['to'] = to

  if bcc:
    context['bcc'] = bcc

  return context


def getSpawnMailTaskTxn(context, parent=None, transactional=True):
  """Spawns a new Task that sends out an email with the given dictionary.
  """
  if not (context.get('to') or context.get('bcc')):
    context['body'] = context.get('body', '')[:10]
    logging.debug("Not sending email: '%s'" % context)
    # no-one cares :(
    return lambda: None

  mail_entity = email.Email(context=simplejson.dumps(context), parent=parent)

  def txn():
    """Transaction to ensure that a task get enqueued for each mail stored.
    """
    mail_entity.put()

    task_params = {'mail_key': str(mail_entity.key())}
    # Setting a countdown because the mail_entity might not be stored to
    # all the replicas yet.
    new_task = taskqueue.Task(params=task_params, url=SEND_MAIL_URL,
                              countdown=5)
    new_task.add(queue_name='mail', transactional=transactional)

  return txn


class MailerTask(object):
  """Request handler for mailer.
  """

  def djangoURLPatterns(self):
    """Returns the URL patterns for the tasks in this module.
    """
    return [
        django_url(r'^tasks/mail/send_mail$', self.sendMail,
                   name='send_email_task'),
    ]

  def sendMail(self, request):
    """Sends out an email that is stored in the datastore.

    The POST request should contain the following entries:
      mail_key: Datastore key for an Email entity.
    """
    post_dict = request.POST

    mail_key = post_dict.get('mail_key', None)

    if not mail_key:
      return error_handler.logErrorAndReturnOK('No email key specified')

    mail_entity = db.get(mail_key)

    if not mail_entity:
      return error_handler.logErrorAndReturnOK(
          'No email entity found for key %s' % mail_key)

    # construct the EmailMessage from the given context
    loaded_context = simplejson.loads(mail_entity.context)

    context = {}
    for key, value in loaded_context.iteritems():
      # If we don't do this python will complain about kwargs not being
      # strings.
      context[str(key)] = value

    logging.info('Sending %s' %context)
    message = mail.EmailMessage(**context)

    try:
      message.check_initialized()
    except Exception, e:
      logging.exception(e)
      context['body'] = context.get('body', '')[:10]
      logging.error('This message was not properly initialized: "%s"' % context)
      mail_entity.delete()
      return responses.terminateTask()

    def txn():
      """Transaction that ensures the deletion of the Email entity only if
      the mail has been successfully sent.
      """
      mail_entity.delete()
      message.send()

    try:
      db.RunInTransaction(txn)
    except mail.Error, exception:
      # shouldn't happen because validate has been called, keeping the Email
      # entity for study purposes.
      return error_handler.logErrorAndReturnOK(exception)
    except (OverQuotaError, DeadlineExceededError), e:
      return responses.repeatTask()

    # mail successfully sent
    return responses.terminateTask()

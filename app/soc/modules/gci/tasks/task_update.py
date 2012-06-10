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

"""Appengine Tasks related to GCI Task handling.
"""


from google.appengine.api import taskqueue
from google.appengine.ext import db

from django import http
from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext

from soc.logic import system
from soc.tasks.helper import error_handler

from soc.modules.gci.logic import task as task_logic
from soc.modules.gci.models.comment import GCIComment
from soc.modules.gci.models.task import GCITask
from soc.modules.gci.models.task_subscription import GCITaskSubscription


class TaskUpdate(object):
  """Tasks that are involved in dealing with GCITasks.
  """

  DEF_TASK_UPDATE_SUBJECT = ugettext(
      '[%(program_name)s Task Update] %(title)s')

  def djangoURLPatterns(self):
    """Returns the URL patterns for the tasks in this module.
    """
    patterns = [
        url(r'^tasks/gci/task/update/(?P<id>(\d+))$', self.updateGCITask,
            name='task_update_GCI_task'),
        url(r'^tasks/gci/task/mail/comment', self.sendCommentNotificationMail,
            name='task_create_GCI_comment_notification')
        ]
    return patterns

  def updateGCITask(self, request, id, *args, **kwargs):
    """Method executed by Task Queue API to update a GCI Task to
    relevant state.

    Args:
      request: the standard Django HTTP request object
    """
    id = int(id)

    task = GCITask.get_by_id(id)

    if not task:
      # invalid task data, log and return OK
      return error_handler.logErrorAndReturnOK(
          'No GCITask found for id: %s' % id)

    task_logic.updateTaskStatus(task)

    return http.HttpResponse()

  def sendCommentNotificationMail(self, request, *args, **kwargs):
    """Appengine task that sends mail to the subscribed users.

    Expects the following to be present in the POST dict:
      comment_key: Specifies the comment id for which to send the notifications

    Args:
      request: Django Request object
    """
    # TODO(ljvderijk): If all mails are equal we can sent one big bcc mail

    # set default batch size
    batch_size = 10

    post_dict = request.POST

    comment_key = post_dict.get('comment_key')

    if not comment_key:
      # invalid task data, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid createNotificationMail data: %s' % post_dict)

    comment_key = db.Key(comment_key)
    comment = GCIComment.get(comment_key)

    if not comment:
      # invalid comment specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid comment specified: %s' % (comment_key))

    task = comment.parent()
    subscription = GCITaskSubscription.all().ancestor(task).fetch(1)

    # check and retrieve the subscriber_start_key that has been done last
    idx = int(post_dict.get('subscriber_start_index', 0))
    subscribers = db.get(subscription.subscribers[idx:idx+batch_size])

    url_kwargs = {
      'sponsor': task.program.scope_path,
      'program': task.program.link_id,
      'id': task.key().id_or_name(),
    }
    task_url = "http://%(host)s%(task)s" % {
        'host': system.getHostname(),
        'task': reverse('gci_view_task', kwargs=url_kwargs)
        }

    # create the data for the mail to be sent
    message_properties = {
        'task_url': task_url,
        'redirect_url': "%(task_url)s#c%(cid)d" % {
            'task_url': task_url,
            'cid': comment.key().id_or_name()
            },
        'comment_entity': comment,
        'task_entity': task,
    }

    subject = self.DEF_TASK_UPDATE_SUBJECT % {
        'program_name': task.program.short_name,
        'title': task.title,
        }

    for subscriber in subscribers:
      # TODO(ljvderijk): enable sending of mail after template fixes
      #gci_notifications.sendTaskUpdateMail(subscriber, subject,
      #                                      message_properties)
      pass

    if len(subscribers) == batch_size:
      # spawn task for sending out notifications to next set of subscribers
      next_start = idx + batch_size

      task_params = {
          'comment_key': str(comment_key),
          'subscriber_start_index': next_start
          }
      task_url = '/tasks/gci/task/mail/comment'

      new_task = taskqueue.Task(params=task_params, url=task_url)
      new_task.add('mail')

    # return OK
    return http.HttpResponse()


def spawnUpdateTask(entity, transactional=False):
  """Spawns a task to update the state of the task.
  """
  update_url = '/tasks/gci/task/update/%s' %entity.key().id()
  new_task = taskqueue.Task(eta=entity.deadline,
                            url=update_url)
  new_task.add('gci-update', transactional=transactional)


def spawnCreateNotificationMail(comment):
  """Spawns a task to send mail to the user who has subscribed to the specific
  task.

  Args:
    comment: The Comment entity for which mails must be sent
  """
  task_params = {
      'comment_key': str(comment.key())
      }
  task_url = '/tasks/gci/task/mail/comment'

  new_task = taskqueue.Task(params=task_params, url=task_url)
  new_task.add('mail')

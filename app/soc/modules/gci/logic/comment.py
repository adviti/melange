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

"""GCIComment logic methods.
"""


from google.appengine.ext import db

from soc.tasks import mailer

from soc.modules.gci.logic.helper import notifications
from soc.modules.gci.models.profile import GCIProfile


def storeAndNotify(comment):
  """Stores and notifies those that are subscribed about a comment on a task.

  Args:
    comment: A GCIComment instance
  """
  db.run_in_transaction(storeAndNotifyTxn(comment))


def storeAndNotifyTxn(comment):
  """Returns a method to be run in a transaction to notify subscribers.
  """
  task = comment.parent()

  to_emails = []
  profiles = GCIProfile.get(task.subscribers)
  for profile in profiles:
    if ((not comment.created_by) or
        profile.user.key() != comment.created_by.key()):
      to_emails.append(profile.email)

  context = notifications.getTaskCommentContext(task, comment, to_emails)
  sub_txn = mailer.getSpawnMailTaskTxn(context, parent=task)
  def txn():
    sub_txn()
    comment.put()

  return txn

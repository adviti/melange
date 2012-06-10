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

"""Module containing logic function for invitations.
"""


from google.appengine.ext import db

from soc.logic.helper import notifications

from soc.tasks import mailer


def acceptInvite(request_data):
  """Accepts an invitation.
  """
  invite = request_data.invite

  invite_key = invite.key()
  profile_key = request_data.profile.key()
  organization_key = invite.org.key()

  def accept_invitation_txn():
    invite = db.get(invite_key)
    profile = db.get(profile_key)

    invite.status = 'accepted'

    if invite.role != 'mentor':
      profile.is_org_admin = True
      profile.org_admin_for.append(organization_key)
      profile.org_admin_for = list(set(profile.org_admin_for))

    profile.is_mentor = True
    profile.mentor_for.append(organization_key)
    profile.mentor_for = list(set(profile.mentor_for))

    invite.put()
    profile.put()

  accept_invitation_txn()
  # TODO(SRabbelier): run in txn as soon as we make User Request's parent
  # db.run_in_transaction(accept_invitation_txn)

def rejectInvite(request_data):
  """Rejects a invitation. 
  """
  invite_key = request_data.invite.key()

  def reject_invite_txn():
    invite = db.get(invite_key)
    invite.status = 'rejected'
    invite.put()

  db.run_in_transaction(reject_invite_txn)

def withdrawInvite(request_data):
  """Withdraws an invitation.
  """
  invite_key = request_data.invite.key()

  def withdraw_invite_txn():
    invite = db.get(invite_key)
    invite.status = 'withdrawn'
    invite.put()

    context = notifications.handledInviteContext(request_data)
    sub_txn = mailer.getSpawnMailTaskTxn(context, parent=invite)
    sub_txn()

  db.run_in_transaction(withdraw_invite_txn)

def resubmitInvite(request_data):
  """Resubmits an invitation. 
  """
  invite_key = request_data.invite.key()

  def resubmit_invite_txn():
    invite = db.get(invite_key)
    invite.status = 'pending'
    invite.put()

    context = notifications.handledInviteContext(request_data)
    sub_txn = mailer.getSpawnMailTaskTxn(context, parent=invite)
    sub_txn()

  db.run_in_transaction(resubmit_invite_txn)

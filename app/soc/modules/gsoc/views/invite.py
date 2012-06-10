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

"""Module containing the view for GSoC invitation page.
"""


from google.appengine.ext import db
from google.appengine.api import users

from django import forms as djangoforms
from django.utils.translation import ugettext

from soc.logic import accounts
from soc.logic import cleaning
from soc.logic.helper import notifications
from soc.models.request import Request
from soc.models.user import User
from soc.views.helper import url_patterns
from soc.views.helper.access_checker import isSet
from soc.tasks import mailer

from soc.modules.gsoc.views.base import RequestHandler

from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.views import forms as gsoc_forms
from soc.modules.gsoc.views.helper.url_patterns import url


DEF_STATUS_FOR_USER_MSG = ugettext(
    'You are now %s for this organization.')

DEF_STATUS_FOR_ADMIN_MSG = ugettext(
    'This user is now %s with your organization.')


class InviteForm(gsoc_forms.GSoCModelForm):
  """Django form for the invite page.
  """

  link_id = gsoc_forms.CharField(label='Link ID/Email')

  class Meta:
    model = Request
    css_prefix = 'gsoc_intivation'
    fields = ['message']

  def __init__(self, request_data, *args, **kwargs):
    super(InviteForm, self).__init__(*args, **kwargs)

    # store request object to cache results of queries
    self.request_data = request_data

    # reorder the fields so that link_id is the first one
    field = self.fields.pop('link_id')
    self.fields.insert(0, 'link_id', field)
    field.help_text = ugettext(
        'The link_id or email address of the invitee, '
        ' separate multiple values with a comma')
    
  def clean_link_id(self):
    """Accepts link_id of users which may be invited.
    """

    assert isSet(self.request_data.organization)

    link_ids = self.cleaned_data.get('link_id', '').split(',')

    self.request_data.invited_user = []

    for link_id in link_ids:
      self.cleaned_data['link_id'] = link_id.strip()
      self._clean_one_link_id()

  def _clean_one_link_id(self):
    invited_user = None

    link_id_cleaner = cleaning.clean_link_id('link_id')

    try:
      link_id = link_id_cleaner(self)
    except djangoforms.ValidationError, e:
      if e.code != 'invalid':
        raise

      email_cleaner = cleaning.clean_email('link_id')

      try:
        email_address = email_cleaner(self)
      except djangoforms.ValidationError, e:
        if e.code != 'invalid':
          raise
        msg = ugettext(u'Enter a valid link_id or email address.')
        raise djangoforms.ValidationError(msg, code='invalid')

      account = users.User(email_address)
      user_account = accounts.normalizeAccount(account)
      invited_user = User.all().filter('account', user_account).get()

      if not invited_user:
        raise djangoforms.ValidationError(
            'There is no user with that email address')

    # get the user entity that the invitation is to
    if not invited_user:
      existing_user_cleaner = cleaning.clean_existing_user('link_id')
      invited_user = existing_user_cleaner(self)

    self.request_data.invited_user.append(invited_user)
    
    # check if the organization has already sent an invitation to the user
    query = db.Query(Request)
    query.filter('type', 'Invitation')
    query.filter('user', invited_user)
    query.filter('role', self.request_data.kwargs['role'])
    query.filter('org', self.request_data.organization)
    if query.get():
      raise djangoforms.ValidationError(
          'An invitation to this user has already been sent.')

    # check if the user that is invited does not have the role
    key_name = '/'.join([
        self.request_data.program.key().name(),
        invited_user.link_id])
    profile = self.request_data.invite_profile = GSoCProfile.get_by_key_name(
        key_name, parent=invited_user)

    if not profile:
      msg = ('The specified user has a User account (the link_id is valid), '
             'but they do not yet have a profile for this %s. '
             'You cannot invite them until they create a profile.')
      raise djangoforms.ValidationError(msg % self.request_data.program.name)

    if profile.student_info:
      raise djangoforms.ValidationError('That user is a student')

    if self.request_data.kwargs['role'] == 'org_admin':
      role_for = profile.org_admin_for
    else:
      role_for = set(profile.org_admin_for + profile.mentor_for)

    if self.request_data.organization.key() in role_for:
      raise djangoforms.ValidationError('That user already has this role.')

    
class InvitePage(RequestHandler):
  """Encapsulate all the methods required to generate Invite page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/invite/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'invite/%s$' % url_patterns.INVITE,
            self, name='gsoc_invite')
    ]

  def checkAccess(self):
    """Access checks for GSoC Invite page.
    """

    self.check.isProgramVisible()
    self.check.isOrgAdmin()

  def context(self):
    """Handler to for GSoC Invitation Page HTTP get request.
    """

    role = 'Org Admin' if self.data.kwargs['role'] == 'org_admin' else 'Mentor'

    invite_form = InviteForm(self.data, self.data.POST or None)

    return {
        'logout_link': self.data.redirect.logout(),
        'page_name': 'Invite a new %s' % role,
        'program': self.data.program,
        'invite_form': invite_form
    }

  def _createFromForm(self):
    """Creates a new invitation based on the data inserted in the form.

    Returns:
      a newly created Request entity or None
    """

    assert isSet(self.data.organization)

    invite_form = InviteForm(self.data, self.data.POST)
    
    if not invite_form.is_valid():
      return None

    assert isSet(self.data.invited_user)
    assert self.data.invited_user

    # create a new invitation entity

    invite_form.cleaned_data['org'] = self.data.organization
    invite_form.cleaned_data['role'] = self.data.kwargs['role']
    invite_form.cleaned_data['type'] = 'Invitation'

    def create_invite_txn():
      invite = invite_form.create(commit=True)
      context = notifications.inviteContext(self.data, invite)
      sub_txn = mailer.getSpawnMailTaskTxn(context, parent=invite)
      sub_txn()
      return invite

    for user in self.data.invited_user:
      invite_form.instance = None
      invite_form.cleaned_data['user'] = user
      db.run_in_transaction(create_invite_txn)

    return True

  def post(self):
    """Handler to for GSoC Invitation Page HTTP post request.
    """

    if self._createFromForm():
      self.redirect.invite()
      self.redirect.to('gsoc_invite')
    else:
      self.get()


class ShowInvite(RequestHandler):
  """Encapsulate all the methods required to generate Show Invite page.
  """

  ACTIONS = {
      'accept': 'Accept',
      'reject': 'Reject',
      'resubmit': 'Resubmit',
      'withdraw': 'Withdraw',
      }

  def templatePath(self):
    return 'v2/soc/request/base.html'


  def djangoURLPatterns(self):
    return [
        url(r'invitation/%s$' % url_patterns.ID, self,
            name='gsoc_invitation')
    ]

  def checkAccess(self):
    self.check.isProfileActive()
    
    invite_id = int(self.data.kwargs['id'])
    self.data.invite = Request.get_by_id(invite_id)
    self.check.isInvitePresent(invite_id)

    self.data.organization = self.data.invite.org
    self.data.invited_user = self.data.invite.user

    if self.data.POST:
      self.data.action = self.data.POST['action']

      if self.data.action == self.ACTIONS['accept']:
        self.check.canRespondToInvite()
      elif self.data.action == self.ACTIONS['reject']:
        self.check.canRespondToInvite()
      elif self.data.action == self.ACTIONS['resubmit']:
        self.check.canResubmitInvite()
    else:
      self.check.canViewInvite()

    self.mutator.canRespondForUser()

    if self.data.user.key() == self.data.invited_user.key():
      self.data.invited_profile = self.data.profile
      return

    key_name = '/'.join([
        self.data.program.key().name(),
        self.data.invited_user.link_id])
    self.data.invited_profile = GSoCProfile.get_by_key_name(
        key_name, parent=self.data.invited_user)

  def context(self):
    """Handler to for GSoC Show Invitation Page HTTP get request.
    """

    assert isSet(self.data.invite)
    assert isSet(self.data.can_respond)
    assert isSet(self.data.organization)
    assert isSet(self.data.invited_user)
    assert isSet(self.data.invited_profile)
    assert self.data.invited_profile

    # This code is dupcliated between request and invite
    status = self.data.invite.status

    can_accept = can_reject = can_withdraw = can_resubmit = False

    if self.data.can_respond:
      # invitee speaking
      if status == 'pending':
        can_accept = True
        can_reject = True
      if status == 'rejected':
        can_accept = True
    else:
      # admin speaking
      if status == 'withdrawn':
        can_resubmit = True
      if status == 'pending':
        can_withdraw = True

    show_actions = can_accept or can_reject or can_withdraw or can_resubmit

    org_key = self.data.organization.key()
    status_msg = None

    if self.data.invited_profile.key() == self.data.profile.key():
      if org_key in self.data.invited_profile.org_admin_for:
        status_msg =  DEF_STATUS_FOR_USER_MSG % 'an organization administrator'
      elif org_key in self.data.invited_profile.mentor_for:
        status_msg =  DEF_STATUS_FOR_USER_MSG % 'a mentor'
    else:
      if org_key in self.data.invited_profile.org_admin_for:
        status_msg = DEF_STATUS_FOR_ADMIN_MSG % 'an organization administrator'
      elif org_key in self.data.invited_profile.mentor_for:
        status_msg = DEF_STATUS_FOR_ADMIN_MSG % 'a mentor'

    return {
        'request': self.data.invite,
        'page_name': 'Invite',
        'org': self.data.organization,
        'actions': self.ACTIONS,
        'status_msg': status_msg,
        'user_name': self.data.invited_profile.name(),
        'user_link_id': self.data.invited_user.link_id,
        'user_email': accounts.denormalizeAccount(
            self.data.invited_user.account).email(),
        'show_actions': show_actions,
        'can_accept': can_accept,
        'can_reject': can_reject,
        'can_withdraw': can_withdraw,
        'can_resubmit': can_resubmit,
        } 

  def post(self):
    """Handler to for GSoC Show Invitation Page HTTP post request.
    """

    assert self.data.action
    assert self.data.invite

    if self.data.action == self.ACTIONS['accept']:
      self._acceptInvitation()
    elif self.data.action == self.ACTIONS['reject']:
      self._rejectInvitation()
    elif self.data.action == self.ACTIONS['resubmit']:
      self._resubmitInvitation()
    elif self.data.action == self.ACTIONS['withdraw']:
      self._withdrawInvitation()

    self.redirect.dashboard()
    self.redirect.to()

  def _acceptInvitation(self):
    """Accepts an invitation.
    """

    assert isSet(self.data.organization)

    if not self.data.profile:
      self.redirect.program()
      self.redirect.to('edit_gsoc_profile')

    invite_key = self.data.invite.key()
    profile_key = self.data.profile.key()
    organization_key = self.data.organization.key()

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

  def _rejectInvitation(self):
    """Rejects a invitation. 
    """
    assert isSet(self.data.invite)
    invite_key = self.data.invite.key()

    def reject_invite_txn():
      invite = db.get(invite_key)
      invite.status = 'rejected'
      invite.put()

    db.run_in_transaction(reject_invite_txn)

  def _resubmitInvitation(self):
    """Resubmits a invitation. 
    """
    assert isSet(self.data.invite)
    invite_key = self.data.invite.key()

    def resubmit_invite_txn():
      invite = db.get(invite_key)
      invite.status = 'pending'
      invite.put()

      context = notifications.handledInviteContext(self.data)
      sub_txn = mailer.getSpawnMailTaskTxn(context, parent=invite)
      sub_txn()

    db.run_in_transaction(resubmit_invite_txn)

  def _withdrawInvitation(self):
    """Withdraws an invitation.
    """
    assert isSet(self.data.invite)
    invite_key = self.data.invite.key()

    def withdraw_invite_txn():
      invite = db.get(invite_key)
      invite.status = 'withdrawn'
      invite.put()

      context = notifications.handledInviteContext(self.data)
      sub_txn = mailer.getSpawnMailTaskTxn(context, parent=invite)
      sub_txn()

    db.run_in_transaction(withdraw_invite_txn)

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

"""Module containing the view for GCI invitation page.
"""


import logging

from django.utils.translation import ugettext

from google.appengine.api import users
from google.appengine.ext import db

from soc.logic import accounts
from soc.logic import cleaning
from soc.logic import invite as invite_logic
from soc.logic.exceptions import AccessViolation
from soc.logic.exceptions import BadRequest
from soc.logic.exceptions import NotFound
from soc.logic.helper import notifications

from soc.models.user import User

from soc.views.helper import lists
from soc.views.helper import url_patterns
from soc.views.helper.access_checker import isSet
from soc.views.template import Template

from soc.tasks import mailer

from soc.modules.gci.models.profile import GCIProfile
from soc.modules.gci.models.request import GCIRequest

from soc.modules.gci.views import forms as gci_forms
from soc.modules.gci.views.base import RequestHandler
from soc.modules.gci.views.helper import url_names
from soc.modules.gci.views.helper.url_patterns import url


USER_DOES_NOT_EXIST = ugettext('User %s not found.')
USER_ALREADY_INVITED = ugettext(
    'User %s has already been invited to become %s.')
USER_HAS_NO_PROFILE = ugettext(
    'User %s must create a profile for this program.')
USER_IS_STUDENT = ugettext('User %s is a student for this program.')
USER_ALREADY_HAS_ROLE = ugettext(
     'User %s already has %s role for this program.')

class InviteForm(gci_forms.GCIModelForm):
  """Django form for the invite page.
  """

  identifiers = gci_forms.CharField(label='Username/Email')

  class Meta:
    model = GCIRequest
    css_prefix = 'gci_intivation'
    fields = ['message']

  def __init__(self, request_data, *args, **kwargs):
    super(InviteForm, self).__init__(*args, **kwargs)

    # store request object to cache results of queries
    self.request_data = request_data

    # reorder the fields so that link_id is the first one
    field = self.fields.pop('identifiers')
    self.fields.insert(0, 'identifiers', field)
    field.help_text = ugettext(
        "Comma separated usernames or emails of the people to invite.")
    
  def clean_identifiers(self):
    """Accepts link_ids or email addresses of users which may be invited.
    """

    assert isSet(self.request_data.organization)

    users_to_invite = []
    identifiers = self.cleaned_data.get('identifiers', '').split(',')

    for identifier in identifiers:
      self.cleaned_data['identifier'] = identifier.strip()
      user = self._clean_identifier(identifier)
      users_to_invite.append(user)

    self.request_data.users_to_invite = users_to_invite

  def _clean_identifier(self, identifier):
    user_to_invite = None

    # first check if the field represents a valid link_id
    try:
      existing_user_cleaner = cleaning.clean_existing_user('identifier')
      user_to_invite = existing_user_cleaner(self)
    except gci_forms.ValidationError, e:
      if e.code != 'invalid':
        raise

      # otherwise check if the field represents a valid email address
      email_cleaner = cleaning.clean_email('identifier')
      try:
        email = email_cleaner(self)
      except gci_forms.ValidationError, e:
        if e.code != 'invalid':
          raise
        msg = ugettext(u'Enter a valid link_id or email address.')
        raise gci_forms.ValidationError(msg, code='invalid')

      account = users.User(email)
      user_account = accounts.normalizeAccount(account)
      user_to_invite = User.all().filter('account', user_account).get()

    # check if the user entity has been found
    if not user_to_invite:
      raise gci_forms.ValidationError(USER_DOES_NOT_EXIST % (identifier))

    # check if the organization has already sent an invitation to the user
    query = self._getQueryForExistingRequests(user_to_invite)
    if query.get():
      role = self.request_data.kwargs['role']
      raise gci_forms.ValidationError(
          USER_ALREADY_INVITED % (identifier, role))

    # check if the user that is invited does not have the role
    # TODO(dhans): in the ideal world, we want to invite Users with no profiles
    profile = self.request_data.invite_profile \
        = self._getProfile(user_to_invite)

    if not profile:
      raise gci_forms.ValidationError(USER_HAS_NO_PROFILE % identifier)

    if profile.student_info:
      raise gci_forms.ValidationError(USER_IS_STUDENT % identifier)

    if self.request_data.kwargs['role'] == 'org_admin':
      role_for = profile.org_admin_for
    else:
      role_for = set(profile.org_admin_for + profile.mentor_for)

    if self.request_data.organization.key() in role_for:
      role = self.request_data.kwargs['role']
      raise gci_forms.ValidationError(
          USER_ALREADY_HAS_ROLE % (identifier, role))

    return user_to_invite

  def _getQueryForExistingRequests(self, user_to_invite):
    query = db.Query(GCIRequest, keys_only=True)
    query.filter('type', 'Invitation')
    query.filter('user', user_to_invite)
    query.filter('role', self.request_data.kwargs['role'])
    query.filter('org', self.request_data.organization)
    return query
  
  def _getProfile(self, user_to_invite):
    key_name = '/'.join([
        self.request_data.program.key().name(), user_to_invite.link_id])
    return GCIProfile.get_by_key_name(key_name, parent=user_to_invite)


class ManageInviteForm(gci_forms.GCIModelForm):
  """Django form for the manage invitation page.
  """

  class Meta:
    model = GCIRequest
    css_prefix = 'gci_intivation'
    fields = ['message']


class InvitePage(RequestHandler):
  """Encapsulate all the methods required to generate Invite page.
  """

  def templatePath(self):
    return 'v2/modules/gci/invite/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'invite/%s$' % url_patterns.INVITE,
            self, name=url_names.GCI_SEND_INVITE)
    ]

  def checkAccess(self):
    """Access checks for GCI Invite page.
    """

    self.check.isProgramVisible()
    self.check.isOrgAdmin()

  def context(self):
    """Handler to for GCI Invitation Page HTTP get request.
    """

    role = 'Org Admin' if self.data.kwargs['role'] == 'org_admin' else 'Mentor'

    invite_form = InviteForm(self.data, self.data.POST or None)

    return {
        'logout_link': self.data.redirect.logout(),
        'page_name': 'Invite a new %s' % role,
        'program': self.data.program,
        'forms': [invite_form]
    }

  def validate(self):
    """Creates new invitation based on the data inserted in the form.

    Returns:
      True if the new invitations have been successfully saved; False otherwise
    """

    assert isSet(self.data.organization)

    invite_form = InviteForm(self.data, self.data.POST)
    
    if not invite_form.is_valid():
      return False

    assert isSet(self.data.users_to_invite)
    assert len(self.data.users_to_invite)

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

    for user in self.data.users_to_invite:
      invite_form.instance = None
      invite_form.cleaned_data['user'] = user
      db.run_in_transaction(create_invite_txn)

    return True

  def post(self):
    """Handler to for GCI Invitation Page HTTP post request.
    """
    if not self.validate():
      self.get()
      return

    self.redirect.dashboard().to()


class ManageInvite(RequestHandler):
  """View to manage the invitation by organization admins.
  """

  def templatePath(self):
    return 'v2/modules/gci/invite/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'invite/manage/%s$' % url_patterns.ID, self,
            name=url_names.GCI_MANAGE_INVITE)
    ]

  def checkAccess(self):
    self.check.isProfileActive()
    
    invite_id = int(self.data.kwargs['id'])
    self.data.invite = GCIRequest.get_by_id(invite_id)
    self.check.isInvitePresent(invite_id)

    # get invited user and check if it is not deleted
    self.data.invited_user = self.data.invite.user
    if not self.data.invited_user:
      logging.warning(
          'User entity does not exist for request with id %s', invite_id)
      raise NotFound('Invited user does not exist')

    # get the organization and check if the current user can manage the invite
    self.data.organization = self.data.invite.org
    self.check.isOrgAdmin()

    if self.data.POST:
      if 'withdraw' in self.data.POST:
        self.check.canInviteBeWithdrawn()
      elif 'resubmit' in self.data.POST:
        self.check.canInviteBeResubmitted()
      else:
        raise BadRequest('No action specified in manage_gci_invite request.')

  def context(self):
    page_name = self._constructPageName()

    form = ManageInviteForm(
        self.data.POST or None, instance=self.data.invite)

    button_name = self._constructButtonName()
    button_value = self._constructButtonValue()

    return {
        'page_name': page_name,
        'forms': [form],
        'button_name': button_name,
        'button_value': button_value
        }

  def post(self):
    # it is needed to handle notifications
    self.data.invited_profile = self._getInvitedProfile()

    if 'withdraw' in self.data.POST:
      invite_logic.withdrawInvite(self.data)
    elif 'resubmit' in self.data.POST:
      invite_logic.resubmitInvite(self.data)

    self.redirect.id().to(url_names.GCI_MANAGE_INVITE)

  def _constructPageName(self):
    invite = self.data.invite
    return "%s Invite For %s" % (invite.role, self.data.invited_user.name)

  def _constructButtonName(self):
    invite = self.data.invite
    if invite.status == 'pending':
      return 'withdraw'
    if invite.status in ['withdrawn', 'rejected']:
      return 'resubmit'

  def _constructButtonValue(self):
    invite = self.data.invite
    if invite.status == 'pending':
      return 'Withdraw'
    if invite.status in ['withdrawn', 'rejected']:
      return 'Resubmit'

  def _getInvitedProfile(self):
    key_name = '/'.join([
        self.data.program.key().name(),
        self.data.invited_user.link_id])
    return GCIProfile.get_by_key_name(key_name, parent=self.data.invited_user)


class RespondInvite(RequestHandler):
  """View to respond to the invitation by the user.
  """

  def templatePath(self):
    return 'v2/modules/gci/invite/show.html'

  def djangoURLPatterns(self):
    return [
        url(r'invite/respond/%s$' % url_patterns.ID, self,
            name=url_names.GCI_RESPOND_INVITE)
    ]

  def checkAccess(self):
    self.check.isUser()

    invite_id = int(self.data.kwargs['id'])
    self.data.invite = GCIRequest.get_by_id(invite_id)
    self.check.isInvitePresent(invite_id)

    self.check.canRespondInvite()
    self.data.is_respondable = self.data.invite.status == 'pending'

    # actual response may be sent only to pending requests
    if self.data.POST:
      if 'accept' not in self.data.POST and 'reject' not in self.data.POST:
        raise BadRequest('Valid action is not specified in the request.')
      self.check.isInviteRespondable()

  def context(self):
    page_name = self._constructPageName()
    return {
        'is_respondable': self.data.is_respondable,
        'page_name': page_name,
        'request': self.data.invite
        }

  def post(self):
    if 'accept' in self.data.POST:
      if not self.data.profile:
        self.redirect.program()
        self.redirect.to('edit_gci_profile')

      invite_logic.acceptInvite(self.data)
    else: # reject
      invite_logic.rejectInvite(self.data)

    self.redirect.id().to(url_names.GCI_RESPOND_INVITE)

  def _constructPageName(self):
    invite = self.data.invite
    return "%s Invite" % (invite.role.capitalize())


class UserInvitesList(Template):
  """Template for list of invites that have been sent to the current user.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data
    r = data.redirect

    list_config = lists.ListConfiguration()
    list_config.addColumn('org', 'From',
        lambda entity, *args: entity.org.name)
    list_config.addSimpleColumn('status', 'Status')
    list_config.setRowAction(
        lambda e, *args: r.id(e.key().id())
            .urlOf(url_names.GCI_RESPOND_INVITE))

    self._list_config = list_config

  def getListData(self):
    q = GCIRequest.all()
    q.filter('type', 'Invitation')
    q.filter('user', self.data.user)

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, lists.keyStarter)

    return response_builder.build()

  def context(self):
    invite_list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0)

    return {
        'lists': [invite_list],
    }

  def templatePath(self):
    return 'v2/modules/gci/invite/_invite_list.html'


class ListUserInvitesPage(RequestHandler):
  """View for the page that lists all the invites which have been sent to
  the current user.
  """

  def templatePath(self):
    return 'v2/modules/gci/invite/invite_list.html'

  def djangoURLPatterns(self):
    return [
        url(r'invite/list_user/%s$' % url_patterns.PROGRAM, self,
            name=url_names.GCI_LIST_INVITES),
    ]

  def checkAccess(self):
    self.check.isProfileActive()

  def jsonContext(self):
    list_content = UserInvitesList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation('You do not have access to this data')

    return list_content.content()

  def context(self):
    return {
        'page_name': 'Invitations to you',
        'invite_list': UserInvitesList(self.request, self.data),
    }

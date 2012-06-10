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

"""Module containing the view for GSoC request page.
"""


from google.appengine.ext import db

from soc.logic import accounts
from soc.logic.exceptions import AccessViolation
from soc.logic.helper import notifications
from soc.views.helper import url_patterns
from soc.views.helper.access_checker import isSet
from soc.tasks import mailer

from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.request import GSoCRequest
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.base_templates import LoggedInMsg
from soc.modules.gsoc.views.forms import GSoCModelForm
from soc.modules.gsoc.views.helper.url_patterns import url


class RequestForm(GSoCModelForm):
  """Django form for the request page.
  """
  class Meta:
    model = GSoCRequest
    css_prefix = 'gsoc_request'
    fields = ['message']


class RequestPage(RequestHandler):
  """Encapsulate all the methods required to generate Request page.
  """
  def templatePath(self):
    return 'v2/modules/gsoc/invite/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'request/%s$' % url_patterns.ORG,
            self, name='gsoc_request')
    ]

  def checkAccess(self):
    """Access checks for GSoC Invite page.
    """
    self.check.isProgramVisible()

    # check if the current user has a profile, but is not a student
    self.check.notStudent()

    # check if the organization exists
    self.check.isOrganizationInURLActive()

    # check if the user is not already mentor role for the organization
    self.check.notMentor()

    # check if there is already a request
    query = db.Query(GSoCRequest)
    query.filter('type = ', 'Request')
    query.filter('user = ', self.data.user)
    query.filter('org = ', self.data.organization)
    if query.get():
      raise AccessViolation(
          'You have already sent a request to this organization.')

  def context(self):
    """Handler for GSoC Request Page HTTP get request.
    """
    request_form = RequestForm(self.data.POST or None)

    return {
        'logged_in_msg': LoggedInMsg(self.data, apply_link=False),
        'page_name': 'Request to become a mentor',
        'program': self.data.program,
        'invite_form': request_form
    }

  def post(self):
    """Handler for GSoC Request Page HTTP post request.
    """
    request = self._createFromForm()
    if request:
      self.redirect.id(request.key().id())
      self.redirect.to('show_gsoc_request')
    else:
      self.get()

  def _createFromForm(self):
    """Creates a new request based on the data inserted in the form.

    Returns:
      a newly created Request entity or None
    """
    assert isSet(self.data.organization)

    request_form = RequestForm(self.data.POST)

    if not request_form.is_valid():
      return None

    # create a new invitation entity
    request_form.cleaned_data['user'] = self.data.user
    request_form.cleaned_data['org'] = self.data.organization
    request_form.cleaned_data['role'] = 'mentor'
    request_form.cleaned_data['type'] = 'Request'

    q = GSoCProfile.all().filter('org_admin_for', self.data.organization)
    q = q.filter('status', 'active').filter('notify_new_requests', True)
    admins = q.fetch(1000)
    admin_emails = [i.email for i in admins]

    def create_request_txn():
      request = request_form.create(commit=True)
      context = notifications.requestContext(self.data, request, admin_emails)
      sub_txn = mailer.getSpawnMailTaskTxn(context, parent=request)
      sub_txn()
      return request

    return db.run_in_transaction(create_request_txn)


class ShowRequest(RequestHandler):
  """Encapsulate all the methods required to generate Show Request page.
  """
  # maps actions with button names
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
        url(r'request/%s$' % url_patterns.ID, self,
            name='show_gsoc_request')
    ]

  def checkAccess(self):
    self.check.isProfileActive()

    request_id = int(self.data.kwargs['id'])
    self.data.invite = self.data.request_entity = GSoCRequest.get_by_id(
        request_id)
    self.check.isRequestPresent(request_id)

    self.data.organization = self.data.request_entity.org
    self.data.invited_user = self.data.requester = self.data.request_entity.user

    if self.data.POST:
      self.data.action = self.data.POST['action']

      if self.data.action == self.ACTIONS['accept']:
        self.check.canRespondToRequest()
      elif self.data.action == self.ACTIONS['reject']:
        self.check.canRespondToRequest()
      elif self.data.action == self.ACTIONS['resubmit']:
        self.check.canResubmitRequest()
      # withdraw action
    else:
      self.check.canViewRequest()

    self.mutator.canRespondForUser()

    key_name = '/'.join([
        self.data.program.key().name(),
        self.data.requester.link_id])
    self.data.requester_profile = GSoCProfile.get_by_key_name(
        key_name, parent=self.data.requester)

  def context(self):
    """Handler to for GSoC Show Request Page HTTP get request.
    """
    assert isSet(self.data.request_entity)
    assert isSet(self.data.can_respond)
    assert isSet(self.data.organization)
    assert isSet(self.data.requester)

    # This code is dupcliated between request and invite
    status = self.data.request_entity.status

    can_accept = can_reject = can_withdraw = can_resubmit = False

    if self.data.can_respond:
      # admin speaking
      if status == 'pending':
        can_accept = True
        can_reject = True
      if status == 'rejected':
        can_accept = True
    else:
      # requester speaking
      if status == 'withdrawn':
        can_resubmit = True
      if status == 'pending':
        can_withdraw = True

    show_actions = can_accept or can_reject or can_withdraw or can_resubmit

    org_key = self.data.organization.key()
    status_msg = None

    if self.data.requester_profile.key() == self.data.profile.key():
      if org_key in self.data.requester_profile.org_admin_for:
        status_msg = "You are now an organization administrator for this organization."
      elif org_key in self.data.requester_profile.mentor_for:
        status_msg = "You are now a mentor for this organization."
    else:
      if org_key in self.data.requester_profile.org_admin_for:
        status_msg = "This user is now an organization administrator with your organization."
      elif org_key in self.data.requester_profile.mentor_for:
        status_msg = "This user is now a mentor with your organization."

    return {
        'page_name': "Request to become a mentor",
        'request': self.data.request_entity,
        'org': self.data.organization,
        'actions': self.ACTIONS,
        'status_msg': status_msg,
        'user_name': self.data.requester_profile.name(),
        'user_link_id': self.data.requester.link_id,
        'user_email': accounts.denormalizeAccount(
            self.data.requester.account).email(),
        'show_actions': show_actions,
        'can_accept': can_accept,
        'can_reject': can_reject,
        'can_withdraw': can_withdraw,
        'can_resubmit': can_resubmit,
        }

  def post(self):
    """Handler to for GSoC Show Request Page HTTP post request.
    """
    assert isSet(self.data.action)
    assert isSet(self.data.request_entity)

    if self.data.action == self.ACTIONS['accept']:
      self._acceptRequest()
    elif self.data.action == self.ACTIONS['reject']:
      self._rejectRequest()
    elif self.data.action == self.ACTIONS['resubmit']:
      self._resubmitRequest()
    elif self.data.action == self.ACTIONS['withdraw']:
      self._withdrawRequest()

    self.redirect.program()
    self.redirect.to('gsoc_dashboard')

  def _acceptRequest(self):
    """Accepts a request.
    """
    assert isSet(self.data.organization)
    assert isSet(self.data.requester_profile)

    request_key = self.data.request_entity.key()
    profile_key = self.data.requester_profile.key()
    organization_key = self.data.organization.key()

    def accept_request_txn():
      request = db.get(request_key)
      profile = db.get(profile_key)

      request.status = 'accepted'
      profile.is_mentor = True
      profile.mentor_for.append(organization_key)
      profile.mentor_for = list(set(profile.mentor_for))

      profile.put()
      request.put()

      context = notifications.handledRequestContext(self.data, request.status)
      sub_txn = mailer.getSpawnMailTaskTxn(context, parent=request)
      # TODO(SRabbelier): just call as soon as we make User Request's parent
      db.run_in_transaction(sub_txn)

    accept_request_txn()
    # TODO(SRabbelier): run in txn as soon as we make User Request's parent
    # db.run_in_transaction(accept_request_txn)

  def _rejectRequest(self):
    """Rejects a request. 
    """
    assert isSet(self.data.request_entity)
    request_key = self.data.request_entity.key()

    def reject_request_txn():
      request = db.get(request_key)
      request.status = 'rejected'
      request.put()

      context = notifications.handledRequestContext(self.data, request.status)
      sub_txn = mailer.getSpawnMailTaskTxn(context, parent=request)
      sub_txn()

    db.run_in_transaction(reject_request_txn)

  def _resubmitRequest(self):
    """Resubmits a request.
    """
    assert isSet(self.data.request_entity)
    request_key = self.data.request_entity.key()

    def resubmit_request_txn():
      request = db.get(request_key)
      request.status = 'pending'
      request.put()

    db.run_in_transaction(resubmit_request_txn)

  def _withdrawRequest(self):
    """Withdraws an invitation.
    """
    assert isSet(self.data.request_entity)
    request_key = self.data.request_entity.key()

    def withdraw_request_txn():
      request = db.get(request_key)
      request.status = 'withdrawn'
      request.put()

    db.run_in_transaction(withdraw_request_txn)

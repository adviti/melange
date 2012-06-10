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

"""Module containing the AccessChecker class that contains helper functions
for checking access.
"""


from django.utils.translation import ugettext

from google.appengine.api import users
from google.appengine.ext import db

from soc.logic import host as host_logic
from soc.logic.exceptions import LoginRequest
from soc.logic.exceptions import RedirectRequest
from soc.logic.exceptions import BadRequest
from soc.logic.exceptions import NotFound
from soc.logic.exceptions import AccessViolation
from soc.logic.exceptions import GDocsLoginRequest
from soc.models.org_app_record import OrgAppRecord
from soc.models.org_app_survey import OrgAppSurvey
from soc.models.request import INVITATION_TYPE
from soc.models.request import REQUEST_TYPE
from soc.models.user import User
from soc.views.helper.gdata_apis import oauth as oauth_helper


DEF_AGREE_TO_TOS = ugettext(
    'You must agree to the <a href="%(tos_link)s">site-wide Terms of'
    ' Service</a> in your <a href="/user/edit_profile">User Profile</a>'
    ' in order to view this page.')

DEF_ALREADY_ADMIN = ugettext(
    'You cannot be a organization administrator for %s to access this page.')

DEF_ALREADY_MENTOR = ugettext(
    'You cannot be a mentor for %s to access this page.')

DEF_ALREADY_PARTICIPATING = ugettext(
    'You cannot become a Student because you are already participating '
    'in this program.')

DEF_ALREADY_PARTICIPATING_AS_STUDENT = ugettext(
    'You cannot register as a %s since you are already a '
    'student in %s.')

DEF_CANNOT_ACCESS_ORG_APP = ugettext(
    'You do not have access to this organization application.')

DEF_CANNOT_UPDATE_ENTITY = ugettext(
    'This %(model)s cannot be updated.')

DEF_DEV_LOGOUT_LOGIN = ugettext(
    'Please <a href="%%(sign_out)s">sign out</a>'
    ' and <a href="%%(sign_in)s">sign in</a>'
    ' again as %(role)s to view this page.')

DEF_ENTITY_DOES_NOT_BELONG_TO_YOU = ugettext(
    'This %(model)s entity does not belong to you.')

DEF_HAS_ALREADY_ROLE_FOR_ORG = ugettext(
    'You already have %(role)s role for %(org)s.')

DEF_ID_BASED_ENTITY_INVALID = ugettext(
    '%(model)s entity, whose id is %(id)s, is invalid at this time.')

DEF_ID_BASED_ENTITY_NOT_EXISTS = ugettext(
    '%(model)s entity, whose id is %(id)s, is does not exist.')

DEF_INVITE_DOES_NOT_EXIST = ugettext(
    'There is no invite with id %s.')

DEF_INVITE_CANNOT_BE_RESUBMITTED = ugettext(
    'Only withdrawn invitations may be resubmitted.')

DEF_INVITE_CANNOT_BE_ACCESSED = ugettext(
    'This invite cannot be accessed from this account.')

DEF_INVITE_CANNOT_BE_WITHDRAWN = ugettext(
    'Only pending invitations may be withdrawn.')

DEF_INVITE_CANNOT_BE_RESPONDED = ugettext(
    'This invite cannot be responded at this moment')

DEF_INVITE_ACCEPTED = ugettext(
    'This invite has been accepted.')

DEF_INVITE_REJECTED = ugettext(
    'This invite has been rejected.')

DEF_INVITE_WITHDRAWN = ugettext(
    'This invite has been withdrawn.')

DEF_REQUEST_DOES_NOT_EXIST = ugettext(
    'There is no request with id %s.')

DEF_REQUEST_CANNOT_BE_ACCESSED = ugettext(
    'This request cannot be accessed from this account.')

DEF_ACCEPTED_REQUEST_CANNOT_BE_MANAGED = ugettext(
    'This request cannot be managed because it is already been accepted.')

DEF_REQUEST_CANNOT_BE_WITHDRAWN = ugettext(
    'This %s request cannot be withdrawn.')

DEF_REQUEST_CANNOT_BE_RESUBMITTED = ugettext(
    'This %s request cannot be resubmitted.')

DEF_IS_NOT_STUDENT = ugettext(
    'This page is inaccessible because you do not have a student role '
    'in the program.')

DEF_HAS_NO_PROJECT = ugettext(
    'This page is inaccessible because you do not have an accepted project '
    'in the program.')

DEF_IS_STUDENT = ugettext(
    'This page is inaccessible because you are registered as a student.')

DEF_NO_DOCUMENT = ugettext(
    'The document was not found')

DEF_NO_LINK_ID = ugettext(
    'Link ID should not be empty')

DEF_NO_ORG_APP = ugettext(
    'The organization application for the program %s does not exist.')

DEF_NO_SLOT_TRANSFER = ugettext(
    'This page is inaccessible at this time. It is accessible only after '
    'the program administrator has made the slot allocations available and '
    'before %s')

DEF_NO_SUCH_PROGRAM = ugettext(
    'The url is wrong (no program was found).')

DEF_NO_SURVEY_ACCESS = ugettext (
    'You cannot take this survey because this survey is not created for'
    'your role in the program.')

DEF_NO_USER_LOGIN = ugettext(
    'Please create <a href="/user/create">User Profile</a>'
    ' in order to view this page.')

DEF_NO_USER_PROFILE = ugettext(
    'You must not have a User profile to visit this page.')

DEF_NO_USER = ugettext(
    'User with the Link ID %s does not exist.')

DEF_NOT_ADMIN = ugettext(
    'You need to be a organization administrator for %s to access this page.')

DEF_NOT_DEVELOPER = ugettext(
    'You need to be a site developer to access this page.')

DEF_NOT_HOST = ugettext(
    'You need to be a program adminstrator to access this page.')

DEF_NOT_MENTOR = ugettext(
    'You need to be a mentor for %s to access this page.')

DEF_NOT_PARTICIPATING = ugettext(
    'You are not participating in this program and have no access.')

DEF_NOT_PROPOSER = ugettext(
    'You are not allowed to perform this action since you are not the'
    'author(proposer) for this proposal.')

DEF_NOT_PUBLIC_DOCUMENT = ugettext(
    'This document is not publically readable.')

DEF_NOT_VALID_INVITATION = ugettext(
    'This is not a valid invitation.')

DEF_NOT_VALID_REQUEST = ugettext(
    'This is not a valid request.')

DEF_ORG_DOES_NOT_EXISTS = ugettext(
    'Organization, whose link_id is %(link_id)s, does not exist in '
    '%(program)s.')

DEF_ORG_NOT_ACTIVE = ugettext(
    'Organization %(name)s is not active in %(program)s.')

DEF_PAGE_INACTIVE = ugettext(
    'This page is inactive at this time.')

DEF_PAGE_INACTIVE_BEFORE = ugettext(
    'This page is inactive before %s')

DEF_PAGE_INACTIVE_OUTSIDE = ugettext(
    'This page is inactive before %s and after %s.')

DEF_PROGRAM_NOT_VISIBLE = ugettext(
    'This page is inaccessible because %s is not visible at this time.')

DEF_PROGRAM_NOT_RUNNING = ugettext(
    'This page is inaccessible because %s is not running at this time.')

DEF_PROPOSAL_IGNORED_MESSAGE = ugettext(
    'An organization administrator has flagged this proposal to be '
    'ignored. If you think this is incorrect, contact an organization '
    'administrator to resolve the situation.')

DEF_PROPOSAL_MODIFICATION_REQUEST = ugettext(
    'If you would like to update this proposal, request your organization '
    'to which this proposal belongs, to grant permission to modify the '
    'proposal.')

DEF_PROPOSAL_NOT_PUBLIC = ugettext(
    'This proposal is not made public, '
    'and you are not the student who submitted the proposal, '
    'nor are you a mentor for the organization it was submitted to.')

DEF_PROFILE_INACTIVE = ugettext(
    'This page is inaccessible because your profile is inactive in '
    'the program at this time.')

DEF_NO_PROFILE = ugettext(
    'This page is inaccessible because you do not have a profile '
    'in the program at this time.')

DEF_SCOPE_INACTIVE = ugettext(
    'The scope for this request is not active.')

DEF_ID_BASED_ENTITY_NOT_EXISTS = ugettext(
    'The requested %(model)s entity whose id is %(id)s does not exist.')

DEF_STATISTIC_DOES_NOT_EXIST = ugettext(
    'The statistic whose name is %(key_name)s does not exist.')

DEF_KEYNAME_BASED_ENTITY_NOT_EXISTS = ugettext(
    'The requested %(model)s entity whose keyname is %(key_name)s does not exist.')

DEF_KEYNAME_BASED_ENTITY_INVALID = ugettext(
    '%(model)s entity, whose keyname is %(key_name)s, is invalid at this time.')

unset = object()


def isSet(value):
  """Returns true iff value is not unset.
  """
  return value is not unset


class Mutator(object):
  """Helper class for access checking.

  Mutates the data object as requested.
  """

  def __init__(self, data):
    self.data = data
    self.unsetAll()

  def unsetAll(self):
    self.data.action = unset
    self.data.can_respond = unset
    self.data.document = unset
    self.data.invited_user = unset
    self.data.invited_profile = unset
    self.data.invite = unset
    self.data.key_name = unset
    self.data.request_entity = unset
    self.data.requester = unset
    self.data.scope_path = unset
    self.data.url_profile = unset
    self.data.url_student_info = unset
    self.data.url_user = unset

  def documentKeyNameFromKwargs(self):
    """Returns the document key fields from kwargs.

    Returns False if not all fields were supplied/consumed.
    """
    from soc.models.document import Document

    fields = []
    kwargs = self.data.kwargs.copy()

    prefix = kwargs.pop('prefix', None)
    fields.append(prefix)

    if prefix in ['gsoc_program', 'gsoc_org', 'gci_program', 'gci_org']:
      fields.append(kwargs.pop('sponsor', None))
      fields.append(kwargs.pop('program', None))

    if prefix in ['gsoc_org', 'gci_org']:
      fields.append(kwargs.pop('organization', None))

    fields.append(kwargs.pop('document', None))

    if any(kwargs.values()):
      raise BadRequest("Unexpected value for document url")

    if not all(fields):
      raise BadRequest("Missing value for document url")

    self.data.scope_path = '/'.join(fields[1:-1])
    self.data.key_name = '/'.join(fields)
    self.data.document = Document.get_by_key_name(self.data.key_name)

  def profileFromKwargs(self, profile_model):
    """Retrieves a profile from kwargs.

    Args:
      profile_model: The datastore model class
    """
    key_name = self.data.kwargs['user']
    self.data.url_user = User.get_by_key_name(key_name)

    if not self.data.url_user:
      raise NotFound('Requested user does not exist')

    fields = ['sponsor', 'program', 'user']
    key_name = '/'.join(self.data.kwargs[i] for i in fields)

    self.data.url_profile = profile_model.get_by_key_name(
        key_name, parent=self.data.url_user)

    if not self.data.url_profile:
      raise NotFound('Requested user does not have a profile')

  def studentFromKwargs(self):
    self.profileFromKwargs()
    self.data.url_student_info = self.data.url_profile.student_info

    if not self.data.url_student_info:
      raise NotFound('Requested user is not a student')

  def canRespondForUser(self):
    assert isSet(self.data.invited_user)
    assert isSet(self.data.invite)

    if self.data.invited_user.key() != self.data.user.key():
      # org admins may see the invitations and can respond to requests
      self.data.can_respond = self.data.invite.type == 'Request'
    else:
      # user that the entity refers to may only respond if it is a Request
      self.data.can_respond = self.data.invite.type == 'Invitation'

  def commentVisible(self):
    assert isSet(self.data.url_user)

    self.data.public_comments_visible = False
    self.data.private_comments_visible = False

    # if the user is not logged in, no comments can be made
    if not self.data.user:
      return

    # if the current user is the proposer, he or she may access public comments
    if self.data.user.key() == self.data.url_user.key():
      self.data.public_comments_visible = True
      return

    # All the mentors and org admins from the organization may access public
    # and private comments.
    if self.data.mentorFor(self.data.proposal_org):
      self.data.public_comments_visible = True
      self.data.private_comments_visible = True
      return

  def host(self):
    assert isSet(self.data.user)

    self.data.host = host_logic.getHostForUser(self.data.user)
    if self.data.host or self.data.user.host_for:
      self.data.is_host = True

  def orgAppFromKwargs(self, raise_not_found=True):
    """Sets the organization application in RequestData object.

    Args:
      raise_not_found: iff False do not send 404 response.
    """
    assert self.data.program

    q = OrgAppSurvey.all()
    q.filter('program', self.data.program)
    self.data.org_app = q.get()

    if raise_not_found and not self.data.org_app:
      raise NotFound(DEF_NO_ORG_APP % self.data.program.name)

  def orgAppRecordIfIdInKwargs(self):
    """Sets the organization application in RequestData object.
    """
    assert self.data.org_app

    self.data.org_app_record = None

    id = self.data.kwargs.get('id')
    if id:
      self.data.org_app_record = OrgAppRecord.get_by_id(int(id))

      if not self.data.org_app_record:
        raise NotFound(DEF_NO_ORG_APP % self.data.program.name)


class DeveloperMutator(Mutator):
  def canRespondForUser(self):
    self.data.can_respond = True

  def commentVisible(self):
    self.data.public_comments_visible = True
    self.data.private_comments_visible = True

  def hostFromKwargs(self):
    """Set the host entity for the given user in the kwargs.
    """
    self.data.host_user_key = None

    key_name = self.data.kwargs.get('link_id', '')
    if not key_name:
      self.host()
      if self.data.is_host:
        return
      else:
        raise NotFound(DEF_NO_LINK_ID)

    user_key = db.Key.from_path('User', key_name)

    if not user_key:
      raise NotFound(DEF_NO_USER % key_name)

    self.data.host_user_key = user_key
    self.data.host = host_logic.getHostForUser(user_key)


class BaseAccessChecker(object):
  """Helper class for access checking.

  Should contain all access checks that apply to both regular users
  and developers.
  """

  def __init__(self, data):
    """Initializes the access checker object.
    """
    self.data = data
    self.gae_user = users.get_current_user()

  def fail(self, message):
    """Raises an AccessViolation with the specified message.
    """
    raise AccessViolation(message)

  def isLoggedIn(self):
    """Ensures that the user is logged in.
    """

    if self.gae_user:
      return

    raise LoginRequest()

  def isLoggedOut(self):
    """Ensures that the user is logged out.
    """

    if not self.gae_user:
      return

    raise RedirectRequest(self.data.logout_url)

  def isUser(self):
    """Checks if the current user has an User entity.
    """
    self.isLoggedIn()

    if self.data.user:
      return

    raise AccessViolation(DEF_NO_USER_LOGIN)

  def isNotUser(self):
    """Checks if the current user does not have an User entity.

    To perform this check a User must be logged in.
    """
    self.isLoggedIn()

    if not self.data.user:
      return

    raise AccessViolation(DEF_NO_USER_PROFILE)


  def isDeveloper(self):
    """Checks if the current user is a Developer.
    """
    self.isUser()

    if self.data.user.is_developer:
      return

    if users.is_current_user_admin():
      return

    raise AccessViolation(DEF_NOT_DEVELOPER)

  def hasProfile(self):
    """Checks if the user has a profile for the current program.
    """
    self.isLoggedIn()

    if self.data.profile:
      return

    raise AccessViolation(DEF_NO_PROFILE)

  def isProfileActive(self):
    """Checks if the profile of the current user is active.
    """
    self.hasProfile()

    if self.data.profile.status == 'active':
      return

    raise AccessViolation(DEF_PROFILE_INACTIVE)

  def isInvitePresent(self, invite_id):
    """Checks if the invite entity is not None.
    """
    assert isSet(self.data.invite)

    if self.data.invite is None:
      raise AccessViolation(DEF_INVITE_DOES_NOT_EXIST % invite_id)

    if self.data.invite.type != INVITATION_TYPE:
      raise AccessViolation(DEF_INVITE_DOES_NOT_EXIST % invite_id)

  def isRequestPresent(self, request_id):
    """Checks if the invite entity is not None.
    """
    assert isSet(self.data.request_entity)

    if self.data.request_entity is None:
      raise AccessViolation(DEF_REQUEST_DOES_NOT_EXIST % request_id)

    if self.data.request_entity.type != REQUEST_TYPE:
      raise AccessViolation(DEF_REQUEST_DOES_NOT_EXIST % request_id)

  def canAccessGoogleDocs(self):
    """Checks if user has a valid access token to access Google Documents.
    """
    self.isUser()
    access_token = oauth_helper.getAccessToken(self.data.user)
    if not access_token: #TODO(orc.avs):check token is valid
      next = self.data.request.get_full_path()
      raise GDocsLoginRequest(next)


class DeveloperAccessChecker(BaseAccessChecker):
  """Helper class for access checking.

  Allows most checks.
  """

  def __getattr__(self, name):
    return lambda *args, **kwargs: None


class AccessChecker(BaseAccessChecker):
  """Helper class for access checking.
  """

  def isHost(self):
    """Checks whether the current user has a host role.
    """
    self.isLoggedIn()

    if self.data.is_host:
      return

    raise AccessViolation(DEF_NOT_HOST)

  def isProgramRunning(self):
    """Checks whether the program is running now by making sure the current 
    data is between program start and end and the program is visible to 
    normal users.
    """
    if not self.data.program:
      raise NotFound(DEF_NO_SUCH_PROGRAM)

    self.isProgramVisible()

    if self.data.timeline.programActive():
      return

    raise AccessViolation(
        DEF_PROGRAM_NOT_RUNNING % self.data.program.name)

  def isProgramVisible(self):
    """Checks whether the program exists and is visible to the user. 
    Visible programs are either in the visible.

    Programs are always visible to hosts.
    """
    if not self.data.program:
      raise NotFound(DEF_NO_SUCH_PROGRAM)

    if self.data.program.status == 'visible':
      return

    try:
      self.isHost()
      return
    except AccessViolation:
      pass

    raise AccessViolation(
        DEF_PROGRAM_NOT_VISIBLE % self.data.program.name)

  def acceptedOrgsAnnounced(self):
    """Checks if the accepted orgs have been announced.
    """
    self.isProgramVisible()

    if self.data.timeline.orgsAnnounced():
      return

    period = self.data.timeline.orgsAnnouncedOn()
    raise AccessViolation(DEF_PAGE_INACTIVE_BEFORE % period)

  def acceptedStudentsAnnounced(self):
    """Checks if the accepted students have been announced.
    """
    self.isProgramVisible()

    if self.data.timeline.studentsAnnounced():
      return

    period = self.data.timeline.studentsAnnouncedOn()
    raise AccessViolation(DEF_PAGE_INACTIVE_BEFORE % period)

  def canApplyNonStudent(self, role, edit_url):
    """Checks if the user can apply as a mentor or org admin.
    """
    self.isLoggedIn()

    if self.data.profile and not self.data.profile.student_info:
      raise RedirectRequest(edit_url)

    if not self.data.profile:
      return

    raise AccessViolation(DEF_ALREADY_PARTICIPATING_AS_STUDENT % (
        role, self.data.program.name))

  def isActiveStudent(self):
    """Checks if the user is an active student.
    """
    self.isProfileActive()

    if self.data.student_info:
      return

    raise AccessViolation(DEF_IS_NOT_STUDENT)

  def isStudentWithProject(self):
    self.isActiveStudent()

    if self.data.student_info.number_of_projects > 0:
      return

    raise AccessViolation(DEF_HAS_NO_PROJECT)

  def notStudent(self):
    """Checks if the current user has a non-student profile.
    """
    self.isProfileActive()

    if not self.data.student_info:
      return

    raise AccessViolation(DEF_IS_STUDENT)

  def notOrgAdmin(self):
    """Checks if the user is not an admin.
    """
    self.isProfileActive()
    assert isSet(self.data.organization)

    if self.data.organization.key() not in self.data.profile.org_admin_for:
      return

    raise AccessViolation(DEF_ALREADY_ADMIN % self.data.organization.name)

  def notMentor(self):
    """Checks if the user is not a mentor.
    """
    self.isProfileActive()
    assert isSet(self.data.organization)

    if not self.data.mentorFor(self.data.organization):
      return

    raise AccessViolation(DEF_ALREADY_MENTOR % self.data.organization.name)

  def isOrgAdmin(self):
    """Checks if the user is an org admin.
    """
    assert isSet(self.data.organization)
    self.isOrgAdminForOrganization(self.data.organization)

  def isMentor(self):
    """Checks if the user is a mentor.
    """
    assert isSet(self.data.organization)
    self.isMentorForOrganization(self.data.organization)

  def isOrgAdminForOrganization(self, org):
    """Checks if the user is an admin for the specified organiztaion.
    """
    self.isProfileActive()

    if self.data.orgAdminFor(org):
      return

    raise AccessViolation(DEF_NOT_ADMIN % org.name)

  def isMentorForOrganization(self, org):
    """Checks if the user is a mentor for the specified organiztaion.
    """
    self.isProfileActive()

    if self.data.mentorFor(org):
      return

    raise AccessViolation(DEF_NOT_MENTOR % org.name)

  def isOrganizationInURLActive(self):
    """Checks if the organization in URL exists and if its status is active.
    """
    assert isSet(self.data.organization)

    if not self.data.organization:
      error_msg = DEF_ORG_DOES_NOT_EXISTS % {
          'link_id': self.data.kwargs['organization'],
          'program': self.data.program.name
          }
      raise AccessViolation(error_msg)

    if self.data.organization.status != 'active':
      error_msg = DEF_ORG_NOT_ACTIVE % {
          'name': self.data.organization.name,
          'program': self.data.program.name
          }
      raise AccessViolation(error_msg)

  def isProposalInURLValid(self):
    """Checks if the proposal in URL exists.
    """
    assert isSet(self.data.proposal)

    if not self.data.proposal:
      error_msg = DEF_ID_BASED_ENTITY_NOT_EXISTS % {
          'model': 'GSoCProposal',
          'id': self.data.kwargs['id']
          }
      raise AccessViolation(error_msg)

    if self.data.proposal.status == 'invalid':
      error_msg = DEF_ID_BASED_ENTITY_INVALID % {
          'model': 'GSoCProposal',
          'id': self.data.kwargs['id'],
          }
      raise AccessViolation(error_msg)

  def studentSignupActive(self):
    """Checks if the student signup period is active.
    """
    self.isProgramVisible()

    if self.data.timeline.studentSignup():
      return

    raise AccessViolation(DEF_PAGE_INACTIVE_OUTSIDE %
        self.data.timeline.studentsSignupBetween())

  def canStudentUpdateProposalPostSignup(self):
    """Checks if the student signup deadline has passed.
    """
    self.isProgramVisible()

    if (self.data.timeline.afterStudentSignupEnd() and
        self.data.proposal.is_editable_post_deadline):
      return

    violation_message = '%s %s'% ((DEF_PAGE_INACTIVE_OUTSIDE %
        self.data.timeline.studentsSignupBetween()),
        DEF_PROPOSAL_MODIFICATION_REQUEST)
    raise AccessViolation(violation_message)

  def canStudentUpdateProposal(self):
    """Checks if the student is eligible to submit a proposal.
    """
    assert isSet(self.data.proposal)

    self.isActiveStudent()
    self.isProposalInURLValid()

    # check if the timeline allows updating proposals
    try:
      self.studentSignupActive()
    except AccessViolation:
      self.canStudentUpdateProposalPostSignup()

    # check if the proposal belongs to the current user
    expected_profile = self.data.proposal.parent()
    if expected_profile.key().name() != self.data.profile.key().name():
      error_msg = DEF_ENTITY_DOES_NOT_BELONG_TO_YOU % {
          'model': 'GSoCProposal'
          }
      raise AccessViolation(error_msg)

    # check if the status allows the proposal to be updated
    status = self.data.proposal.status
    if status == 'ignored':
      raise AccessViolation(DEF_PROPOSAL_IGNORED_MESSAGE)
    elif status in ['invalid', 'accepted', 'rejected']:
      raise AccessViolation(DEF_CANNOT_UPDATE_ENTITY % {
          'model': 'GSoCProposal'
          })

    # determine what can be done with the proposal
    if status == 'new' or status == 'pending':
      self.data.is_pending = True
    elif status == 'withdrawn':
      self.data.is_pending = False

  def canRespondToInvite(self):
    """Checks if the current user can accept/reject the invitation.
    """
    assert isSet(self.data.invite)
    assert isSet(self.data.invited_user)

    # check if the entity represents an invitation
    if self.data.invite.type != 'Invitation':
      raise AccessViolation(DEF_NOT_VALID_INVITATION)

    # check if the entity can be responded
    if self.data.invite.status not in ['pending', 'rejected']:
      raise AccessViolation(DEF_NOT_VALID_INVITATION)

    # check if the entity is addressed to the current user
    if self.data.invited_user.key() != self.data.user.key():
      error_msg = DEF_ENTITY_DOES_NOT_BELONG_TO_YOU % {
          'model': 'Request'
          }
      raise AccessViolation(error_msg)

    # check if the user does not have this role
    if self.data.invite.role == 'org_admin':
      self.notOrgAdmin()
    else:
      self.notMentor()

  def canResubmitInvite(self):
    """Checks if the current user can resubmit the invitation.
    """

    assert isSet(self.data.invite)

    # check if the entity represents an invitation
    if self.data.invite.type != INVITATION_TYPE:
      raise AccessViolation(DEF_INVITE_DOES_NOT_EXIST)

    # only withdrawn requests may be resubmitted
    if self.data.invite.status != 'withdrawn':
      raise AccessViolation(DEF_NOT_VALID_REQUEST)

    # check if the user is an admin for the organization
    self.isOrgAdmin()

  def canInviteBeResubmitted(self):
    """Checks if the invitation may be resubmitted.
    """

    assert isSet(self.data.invite)

    # check if the entity represents an invitation
    if self.data.invite.type != INVITATION_TYPE:
      raise AccessViolation(DEF_INVITE_DOES_NOT_EXIST)

    # only withdrawn requests may be resubmitted
    if self.data.invite.status != 'withdrawn':
      raise AccessViolation(DEF_INVITE_CANNOT_BE_RESUBMITTED)

    #TODO(dhans): actually it needs to be checked if the user has not accepted
    # a request in the meantime.

  def canInviteBeWithdrawn(self):
    """Checks if the invitation may be withdrawn.
    """

    assert isSet(self.data.invite)

    # check if the entity represents an invitation
    if self.data.invite.type != INVITATION_TYPE:
      raise AccessViolation(DEF_INVITE_DOES_NOT_EXIST)

    # only pending requests may be withdrawn
    if self.data.invite.status != 'pending':
      raise AccessViolation(DEF_INVITE_CANNOT_BE_WITHDRAWN)

  def canRespondInvite(self):
    """Checks if the current user may respond to invite entity.
    """
    assert isSet(self.data.invite)

    # check if the entity represents an invitation
    if self.data.invite.type != INVITATION_TYPE:
      raise AccessViolation(DEF_INVITE_DOES_NOT_EXIST)

    # only the invited user may respond to the invitation
    if self.data.user.key() != self.data.invite.user.key():
      raise AccessViolation(DEF_INVITE_CANNOT_BE_ACCESSED)

  def isInviteRespondable(self):
    """Checks if the invite may be responded at this moment.
    """
    assert isSet(self.data.invite)

    # only pending invites may be responded
    if self.data.invite.status == 'accepted':
      raise AccessViolation(DEF_INVITE_ACCEPTED)
    if self.data.invite.status == 'rejected':
      raise AccessViolation(DEF_INVITE_REJECTED)
    if self.data.invite.status == 'withdrawn':
      raise AccessViolation(DEF_INVITE_WITHDRAWN)

  def canManageRequest(self):
    """Checks if the current user may manage the specified request.
    """
    assert isSet(self.data.request_entity)

    # only the author may manage their request
    if self.data.user.key() != self.data.request_entity.user.key():
      raise AccessViolation(DEF_REQUEST_CANNOT_BE_ACCESSED)

    # accepted requests cannot be managed
    if self.data.request_entity.status == 'accepted':
      raise AccessViolation(DEF_ACCEPTED_REQUEST_CANNOT_BE_MANAGED)

  def isRequestManageable(self):
    """Checks if the request may be managed with the specified action.
    """
    assert isSet(self.data.request_entity)
    current_status = self.data.request_entity.status

    if 'withdraw' in self.data.POST and current_status != 'pending':
      raise AccessViolation(DEF_REQUEST_CANNOT_BE_WITHDRAWN % current_status)

    if 'resubmit' in self.data.POST and \
        current_status not in ['rejected', 'withdrawn']:
      raise AccessViolation(DEF_REQUEST_CANNOT_BE_RESUBMITTED % current_status)
       
  def canRespondToRequest(self):
    """Checks if the current user can accept/reject the request.
    """
    assert isSet(self.data.request_entity)
    assert isSet(self.data.requester)

    # check if the entity represents an invitation
    if self.data.request_entity.type != 'Request':
      raise AccessViolation(DEF_NOT_VALID_REQUEST)

    # check if the entity can be responded
    if self.data.request_entity.status not in ['pending', 'rejected']:
      raise AccessViolation(DEF_NOT_VALID_REQUEST)

    # check if the user is an admin for the organization
    self.isOrgAdmin()

  def canResubmitRequest(self):
    """Checks if the current user can resubmit the request.
    """

    assert isSet(self.data.request_entity) 
    assert isSet(self.data.requester)

    # check if the entity represents an invitation
    if self.data.request_entity.type != 'Request':
      raise AccessViolation(DEF_NOT_VALID_REQUEST)

    # only withdrawn requests may be resubmitted
    if self.data.request_entity.status != 'withdrawn':
      raise AccessViolation(DEF_NOT_VALID_REQUEST)

    # check if the request belongs to the current user
    if self.data.requester.key() != self.data.user.key():
      error_msg = DEF_ENTITY_DOES_NOT_BELONG_TO_YOU % {
          'model': 'Request'
          }
      raise AccessViolation(error_msg)

  def canViewInvite(self):
    """Checks if the current user can see the invitation.
    """
    assert isSet(self.data.organization)
    assert isSet(self.data.invite)
    assert isSet(self.data.invited_user)

    self._canAccessRequestEntity(
        self.data.invite, self.data.invited_user, self.data.organization)

  def canViewRequest(self):
    """Checks if the current user can see the request.
    """
    assert isSet(self.data.organization)
    assert isSet(self.data.request_entity)
    assert isSet(self.data.requester)

    self._canAccessRequestEntity(
        self.data.request_entity, self.data.requester, self.data.organization)

  def _canAccessRequestEntity(self, entity, user, org):
    """Checks if the current user is allowed to access a Request entity.
    
    Args:
      entity: an entity which belongs to Request model
      user: user entity that the Request refers to
      org: organization entity that the Request refers to
    """
    # check if the entity is addressed to the current user
    if user.key() != self.data.user.key():
      # check if the current user is an org admin for the organization
      self.isOrgAdmin()

  def canAccessProposalEntity(self):
    """Checks if the current user is allowed to access a Proposal entity.
    """

    assert isSet(self.data.proposal)
    assert isSet(self.data.proposal_org)
    assert isSet(self.data.url_user)

    # if the proposal is public, everyone may access it
    if self.data.proposal.is_publicly_visible:
      return

    if not self.data.user:
      raise AccessViolation(DEF_PROPOSAL_NOT_PUBLIC)

    self.isProfileActive()
    # if the current user is the proposer, he or she may access it
    if self.data.user.key() == self.data.url_user.key():
      return

    # all the mentors and org admins from the organization may access it
    if self.data.mentorFor(self.data.proposal_org):
      return

    raise AccessViolation(DEF_PROPOSAL_NOT_PUBLIC)

  def canEditDocument(self):
    self.isHost()

  def canViewDocument(self):
    """Checks if the specified user can see the document.
    """
    assert isSet(self.data.document)

    if not self.data.document:
      raise NotFound(DEF_NO_DOCUMENT)

    if self.data.document.read_access == 'public':
      return

    raise AccessViolation(DEF_NOT_PUBLIC_DOCUMENT)

  def isProposer(self):
    """Checks if the current user is the author of the proposal.
    """
    self.isProgramVisible()
    self.isProfileActive()

    assert isSet(self.data.proposer)

    if self.data.proposer.key() == self.data.profile.key():
      return

    raise AccessViolation(DEF_NOT_PROPOSER)

  def isSlotTransferActive(self):
    """Checks if the slot transfers are active at the time.
    """
    assert isSet(self.data.program)
    assert isSet(self.data.timeline)

    if (self.data.program.allocations_visible and
        self.data.timeline.beforeStudentsAnnounced()):
      return

    raise AccessViolation(DEF_NO_SLOT_TRANSFER % (
        self.data.timeline.studentsAnnouncedOn()))

  def isProjectInURLValid(self):
    """Checks if the project in URL exists.
    """
    assert isSet(self.data.project)

    if not self.data.project:
      error_msg = DEF_ID_BASED_ENTITY_NOT_EXISTS % {
          'model': 'GSoCProject',
          'id': self.data.kwargs['id']
          }
      raise AccessViolation(error_msg)

    if self.data.project.status == 'invalid':
      error_msg = DEF_ID_BASED_ENTITY_INVALID % {
          'model': 'GSoCProject',
          'id': self.data.kwargs['id'],
          }
      raise AccessViolation(error_msg)

  def canStudentUpdateProject(self):
    """Checks if the student can edit the project details.
    """
    assert isSet(self.data.program)
    assert isSet(self.data.timeline)
    assert isSet(self.data.project)
    assert isSet(self.data.project_owner)

    self.isProjectInURLValid()

    # check if the timeline allows updating project
    self.isProgramVisible()
    self.acceptedStudentsAnnounced()

    # check if the project belongs to the current user
    expected_profile_key = self.data.project.parent_key()
    if expected_profile_key != self.data.profile.key():
      error_msg = DEF_ENTITY_DOES_NOT_BELONG_TO_YOU % {
          'model': 'GSoCProject'
          }
      raise AccessViolation(error_msg)

    # check if the status allows the project to be updated
    if self.data.project.status in ['invalid', 'withdrawn', 'failed']:
      raise AccessViolation(DEF_CANNOT_UPDATE_ENTITY % {
          'model': 'GSoCProject'
          })

  def isSurveyActive(self, survey, show_url=None):
    """Checks if the survey in the request data is active.

    Args:
      survey: the survey entity for which the access must be checked
      show_url: The survey show page url to which the user must be
          redirected to
    """
    assert isSet(self.data.program)
    assert isSet(self.data.timeline)

    if self.data.timeline.surveyPeriod(survey):
      return

    if self.data.timeline.afterSurveyEnd(survey) and show_url:
      raise RedirectRequest(show_url)

    raise AccessViolation(DEF_PAGE_INACTIVE_OUTSIDE %
        (survey.survey_start, survey.survey_end))

  def canUserTakeSurvey(self, survey, taking_access='user'):
    """Checks if the user with the given profile can take the survey.

    Args:
      survey: the survey entity for which the access must be checked
    """
    assert isSet(self.data.program)
    assert isSet(self.data.timeline)

    self.isProjectInURLValid()

    if taking_access == 'student':
      self.isActiveStudent()
      return
    elif taking_access == 'org':
      assert isSet(self.data.organization)

      self.isMentor()
      return
    elif taking_access == 'user':
      self.isUser()
      return

    raise AccessViolation(DEF_NO_SURVEY_ACCESS)

  def isStatisticValid(self):
    """Checks if the URL refers to an existing statistic.
    """
    assert isSet(self.data.statistic)
    # check if the statistic exist
    if not self.data.statistic:
      error_msg = DEF_STATISTIC_DOES_NOT_EXIST % {
          'key_name': self.data.kwargs['id']
          }
      raise AccessViolation(error_msg)

  def canRetakeOrgApp(self):
    """Checks if the user can edit the org app record.
    """
    assert isSet(self.data.org_app_record)

    self.isUser()

    allowed_keys = [self.data.org_app_record.main_admin.key(),
                    self.data.org_app_record.backup_admin.key()]
    if self.data.user.key() not in allowed_keys:
      raise AccessViolation(DEF_CANNOT_ACCESS_ORG_APP)

  def canViewOrgApp(self):
    """Checks if the user can view the org app record. Only the org admins and
    hosts are allowed to view.
    """
    assert isSet(self.data.org_app_record)

    try:
      self.canRetakeOrgApp()
      return
    except AccessViolation:
      pass

    self.isHost()

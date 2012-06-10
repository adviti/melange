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

"""Module containing the RequestData object that will be created for each
request in the GSoC module.
"""


import datetime

from google.appengine.api import users
from google.appengine.ext import db

from django.core.urlresolvers import reverse

from soc.logic import system
from soc.logic import site
from soc.logic import user
from soc.views.helper.access_checker import isSet


def isBefore(date):
  """Returns True iff date is before utcnow().

  Returns False if date is not set.
  """
  return date and datetime.datetime.utcnow() < date


def isAfter(date):
  """Returns True iff date is after utcnow().

  Returns False if date is not set.
  """
  return date and date < datetime.datetime.utcnow()


def isBetween(start, end):
  """Returns True iff utcnow() is between start and end.
  """
  return isAfter(start) and isBefore(end)


class TimelineHelper(object):
  """Helper class for the determination of the currently active period.

  Methods ending with "On", "Start", or "End" return a date.
  Methods ending with "Between" return a tuple with two dates.
  Methods ending with neither return a Boolean.
  """

  def __init__(self, timeline, org_app):
    self.timeline = timeline
    self.org_app = org_app

  def currentPeriod(self):
    """Return where we are currently on the timeline.
    """
    pass

  def nextDeadline(self):
    """Determines the next deadline on the timeline.
    """
    pass

  def orgsAnnouncedOn(self):
    return self.timeline.accepted_organization_announced_deadline

  def beforeProgramStart(self):
    return isBefore(self.timeline.program_start)

  def programActiveBetween(self):
    return (self.timeline.program_start, self.timeline.program_end)

  def orgSignupStart(self):
    return self.org_app.survey_start if self.org_app else None

  def orgSignupEnd(self):
    return self.org_app.survey_end if self.org_app else None

  def orgSignupBetween(self):
    return (self.org_app.survey_start, self.org_app.survey_end) if \
        self.org_app else (None, None)

  def studentSignupStart(self):
    return self.timeline.student_signup_start

  def studentSignupEnd(self):
    return self.timeline.student_signup_end

  def studentsSignupBetween(self):
    return (self.timeline.student_signup_start,
            self.timeline.student_signup_end)

  def programActive(self):
    start, end = self.programActiveBetween()
    return isBetween(start, end)

  def beforeOrgSignupStart(self):
    return self.org_app and isBefore(self.orgSignupStart())

  def afterOrgSignupStart(self):
    return self.org_app and isAfter(self.orgSignupStart())

  def orgSignup(self):
    if not self.org_app:
      return False
    start, end = self.orgSignupBetween()
    return isBetween(start, end)

  def orgsAnnounced(self):
    return isAfter(self.orgsAnnouncedOn())

  def beforeStudentSignupStart(self):
    return isBefore(self.studentSignupStart())

  def afterStudentSignupStart(self):
    return isAfter(self.studentSignupStart())

  def studentSignup(self):
    start, end = self.studentsSignupBetween()
    return isBetween(start, end)

  def afterStudentSignupEnd(self):
    return isAfter(self.studentSignupEnd())

  def surveyPeriod(self, survey):
    start = survey.survey_start
    end = survey.survey_end
    return isAfter(start) and isBefore(end)

  def afterSurveyStart(self, survey):
    return isAfter(survey.survey_start)

  def afterSurveyEnd(self, survey):
    return isAfter(survey.survey_end)


class RequestData(object):
  """Object containing data we query for each request.

  Fields:
    site: the Site entity
    user: the user entity (if logged in)
    request: the request object (as provided by django)
    args: the request args (as provided by djang)
    kwargs: the request kwargs (as provided by django)
    path: the url of the current query, encoded as utf-8 string
    full_path: same as path, but including any GET args
    login_url: login url that redirects to the current path
    logout_url: logout url that redirects to the current path
    GET: the GET dictionary (from the request object)
    POST: the POST dictionary (from the request object)
    is_developer: is the current user a developer
    gae_user: the Google Appengine user object
  """

  def __init__(self):
    """Constructs an empty RequestData object.
    """
    self.site = None
    self.user = None
    self.request = None
    self.args = []
    self.kwargs = {}
    self.GET = None
    self.POST = None
    self.path = None
    self.full_path = None
    self.is_developer = False
    self.gae_user = None
    self.css_path = 'gsoc'
    self._login_url = None
    self._logout_url = None
    self._ds_write_disabled = None

  @property
  def login_url(self):
    """Memoizes and returns the login_url for the current path.
    """
    if not self._login_url:
      self._login_url = users.create_login_url(self.full_path)
    return self._login_url

  @property
  def logout_url(self):
    """Memoizes and returns the logout_url for the current path.
    """
    if not self._logout_url:
      self._logout_url = users.create_logout_url(self.full_path)
    return self._logout_url

  @property
  def ds_write_disabled(self):
    """Memoizes and returns whether datastore writes are disabled.
    """
    if self._ds_write_disabled is not None:
      return self._ds_write_disabled

    if self.request.method == 'GET':
      val= self.request.GET.get('dsw_disabled', '')

      if val.isdigit() and int(val) == 1:
        self._ds_write_disabled = True
        return True

    self._ds_write_disabled = not db.WRITE_CAPABILITY.is_enabled()
    return self._ds_write_disabled

  def populate(self, redirect, request, args, kwargs):
    """Populates the fields in the RequestData object.

    Args:
      request: Django HTTPRequest object.
      args & kwargs: The args and kwargs django sends along.
    """
    self.redirect = redirect
    self.request = request
    self.args = args
    self.kwargs = kwargs
    self.GET = request.GET
    self.POST = request.POST
    self.path = request.path.encode('utf-8')
    self.full_path = request.get_full_path().encode('utf-8')
    # XSRF middleware already retrieved it for us
    if not hasattr(request, 'site'):
      request.site = site.singleton()
    self.site = request.site
    self.user = user.current()
    if users.is_current_user_admin():
      self.is_developer = True
    if self.user and self.user.is_developer:
      self.is_developer = True
    self.gae_user = users.get_current_user()

  def _requestQuery(self, organization):
    """Returns a query to retrieve a Request for this user.
    """
    if isinstance(organization, db.Model):
      organization = organization.key()

    from soc.models.request import Request
    query = Request.all()
    query.filter('user', self.user)
    query.filter('org', organization)

    return query

  def appliedTo(self, organization):
    """Returns true iff the user has applied for the specified organization.

    Organization may either be a key or an organization instance.
    """
    query = self._requestQuery(organization)
    query.filter('type', 'Request')
    return bool(query.get())

  def invitedTo(self, organization):
    """Returns the role the user has been invited to,.

    Organization may either be a key or an organization instance.
    Returns None if no invite was sent.
    """
    query = self._requestQuery(organization)
    query.filter('type', 'Invitation')
    invite = query.get()
    return invite.role if invite else None


class RedirectHelper(object):
  """Helper for constructing redirects.
  """

  def __init__(self, data, response):
    """Initializes the redirect helper.
    """
    self._data = data
    self._response = response
    self._clear()

  def _clear(self):
    """Clears the internal state.
    """
    self._no_url = False
    self._url_name = None
    self._url = None
    self.args = []
    self.kwargs = {}

  def sponsor(self, program=None):
    """Sets kwargs for an url_patterns.SPONSOR redirect.
    """
    if not program:
      assert isSet(self._data.program)
      program = self._data.program
    self._clear()
    self.kwargs['sponsor'] = program.scope_path
    return self

  def program(self, program=None):
    """Sets kwargs for an url_patterns.PROGRAM redirect.
    """
    if not program:
      assert isSet(self._data.program)
      program = self._data.program
    self.sponsor(program)
    self.kwargs['program'] = program.link_id
    return self

  def organization(self, organization=None):
    """Sets the kwargs for an url_patterns.ORG redirect.
    """
    if not organization:
      assert isSet(self._data.organization)
      organization = self._data.organization
    self.program()
    self.kwargs['organization'] = organization.link_id
    return self

  def id(self, id=None):
    """Sets the kwargs for an url_patterns.ID redirect.
    """
    if not id:
      assert 'id' in self._data.kwargs
      id = self._data.kwargs['id']
    self.program()
    self.kwargs['id'] = id
    return self

  def key(self, key=None):
    """Sets the kwargs for an url_patterns.KEY redirect.
    """
    if not key:
      assert 'key' in self._data.kwargs
      key = self._data.kwargs['key']
    self.program()
    self.kwargs['key'] = key
    return self

  def createProfile(self, role):
    """Sets args for an url_patterns.CREATE_PROFILE redirect.
    """
    self.program()
    self.kwargs['role'] = role
    return self

  def profile(self, user=None):
    """Sets args for an url_patterns.PROFILE redirect.
    """
    if not user:
      assert 'user' in self._data.kwargs
      user = self._data.kwargs['user']
    self.program()
    self.kwargs['user'] = user
    return self

  def document(self, document):
    """Sets args for an url_patterns.DOCUMENT redirect.

    If document is not set, a call to url() will return None.
    """
    self._clear()
    if not document:
      self._no_url = True
      return self

    if isinstance(document, db.Model):
      key = document.key()
    else:
      key = document

    self.args = key.name().split('/')

    return self

  def urlOf(self, name, full=False, secure=False, cbox=False, extra=[]):
    """Returns the resolved url for name.

    Uses internal state for args and kwargs.
    """
    if self.args:
      url = reverse(name, args=self.args)
    elif self.kwargs:
      url = reverse(name, kwargs=self.kwargs)
    else:
      url = reverse(name)

    url = self._appendGetArgs(url, cbox=cbox, extra_get_args=extra)

    return self._fullUrl(url, full, secure)

  def url(self, full=False, secure=False):
    """Returns the url of the current state.
    """
    if self._no_url:
      return None
    assert self._url or self._url_name
    if self._url:
      return self._fullUrl(self._url, full, secure)
    return self.urlOf(self._url_name, full=full, secure=secure)

  def _fullUrl(self, url, full, secure):
    """Returns the full version of the url iff full.

    The full version starts with http:// and includes getHostname().
    """
    if (not full) and (system.isLocal() or not secure):
      return url

    if secure:
      protocol = 'https'
      hostname = system.getSecureHostname()
    else:
      protocol = 'http'
      hostname = system.getHostname(self._data)

    return '%s://%s%s' % (protocol, hostname, url)

  def _appendGetArgs(self, url, cbox=False, validated=False,
      extra_get_args=[]):
    """Appends GET arguments to the specified URL.
    """
    get_args = extra_get_args[:]
    if cbox:
      get_args.append('cbox=true')

    if validated:
      get_args.append('validated')

    if get_args:
      # check if the url has already a question mark
      if url.find('?') == -1:
        url = url + '?'
      else:
        url = url + '&'

      # append all the GET arguments at the end of the URL
      if get_args:
        url = url + '&'.join(get_args)

    return url

  def to(self, name=None, validated=False, full=False, secure=False,
         cbox=False, extra=[]):
    """Redirects to the resolved url for name.

    Uses internal state for args and kwargs.

    Args:
      name: Name of the URL pattern
      validated: If set to True will add &validated to GET arguments
      full: Whether the URL should include the protocol
      secure: Whether the protocol of the URL should be set to HTTPS
      cbox: If set to True will add &cbox=true to GET arguments
      extra: List of additional arguments that will be added as GET arguments
    """
    if self._url:
      url = self._url
    else:
      assert name or self._url_name
      url = self.urlOf(name or self._url_name)

    url = self._appendGetArgs(url, cbox=cbox, validated=validated,
        extra_get_args=extra)

    self.toUrl(url, full=full, secure=secure)

  def toUrl(self, url, full=False, secure=False):
    """Redirects to the specified url.
    """
    from django.utils.encoding import iri_to_uri
    url = self._fullUrl(url, full, secure)
    self._response.status_code = 302
    self._response["Location"] = iri_to_uri(url)

  def login(self):
    """Sets the _url to the login url.
    """
    self._clear()
    self._url = self._data.login_url
    return self

  def logout(self):
    """Sets the _url to the logout url.
    """
    self._clear()
    self._url = self._data.logout_url
    return self

  def acceptedOrgs(self):
    """Sets the _url_name to the list of all accepted orgs.
    """
    self.program()
    return self

  def homepage(self):
    """Sets the _url_name for the homepage of the current program.
    """
    self.program()
    return self

  def searchpage(self):
    """Sets the _url_name for the searchpage of the current program.
    """
    self.program()
    return self

  def orgHomepage(self, link_id):
    """Sets the _url_name for the specified org homepage
    """
    self.program()
    self.kwargs['organization'] = link_id
    return self

  def dashboard(self):
    """Sets the _url_name for dashboard page of the current program.
    """
    self.program()
    return self

  def events(self):
    """Sets the _url_name for the events page, if it is set.
    """
    self.program()
    return self

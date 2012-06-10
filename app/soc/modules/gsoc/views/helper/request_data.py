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


from google.appengine.ext import db

from soc.logic.exceptions import NotFound
from soc.views.helper.access_checker import isSet
from soc.views.helper import request_data

from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.timeline import GSoCTimeline


class TimelineHelper(request_data.TimelineHelper):
  """Helper class for the determination of the currently active period.

  Methods ending with "On", "Start", or "End" return a date.
  Methods ending with "Between" return a tuple with two dates.
  Methods ending with neither return a Boolean.
  """

  def currentPeriod(self):
    """Return where we are currently on the timeline.
    """
    if not self.programActive():
      return 'offseason'

    if self.beforeOrgSignupStart():
      return 'kickoff_period'

    if self.afterStudentSignupStart():
      return 'student_signup_period'

    if self.afterOrgSignupStart():
      return 'org_signup_period'

    if self.studentsAnnounced():
      return 'coding_period'

    return 'offseason'

  def nextDeadline(self):
    """Determines the next deadline on the timeline.

    Returns:
      A two-tuple containing deadline text and the datetime object for
      the next deadline
    """
    if self.beforeOrgSignupStart():
      return ("Org Application Starts", self.orgSignupStart())

    # we do not have deadlines for any of those programs that are not active
    if not self.programActive():
      return ("", None)

    if self.orgSignup():
      return ("Org Application Deadline", self.orgSignupEnd())

    if request_data.isBetween(self.orgSignupEnd(), self.orgsAnnouncedOn()):
      return ("Accepted Orgs Announced In", self.orgsAnnouncedOn())

    if self.orgsAnnounced() and self.beforeStudentSignupStart():
      return ("Student Application Opens", self.studentSignupStart())

    if self.studentSignup():
      return ("Student Application Deadline", self.studentSignupEnd())

    if request_data.isBetween(self.studentSignupEnd(), self.applicationMatchedOn()):
      return ("Proposal Matched Deadline", self.applicationMatchedOn())

    if request_data.isBetween(self.applicationMatchedOn(), self.applicationReviewEndOn()):
      return ("Proposal Scoring Deadline", self.applicationReviewEndOn())

    if request_data.isBetween(self.applicationReviewEndOn(), self.studentsAnnouncedOn()):
      return ("Accepted Students Announced", self.studentsAnnouncedOn())

    return ('', None)

  def studentsAnnouncedOn(self):
    return self.timeline.accepted_students_announced_deadline

  def studentsAnnounced(self):
    return request_data.isAfter(self.studentsAnnouncedOn())

  def beforeStudentsAnnounced(self):
    return request_data.isBefore(self.studentsAnnouncedOn())

  def applicationReviewEndOn(self):
    return self.timeline.application_review_deadline

  def applicationMatchedOn(self):
    return self.timeline.student_application_matched_deadline

  def mentorSignup(self):
    return self.programActiveBetween() and self.orgsAnnounced()

  def afterFirstSurveyStart(self, surveys):
    """Returns True if we are past at least one survey has start date.

    Args:
      surveys: List of survey entities for which we need to determine if
        at least one of them have started
    """
    first_survey_start = min([s.survey_start for s in surveys])
    return request_data.isAfter(first_survey_start)


class RequestData(request_data.RequestData):
  """Object containing data we query for each request in the GSoC module.

  The only view that will be exempt is the one that creates the program.

  Fields:
    site: The Site entity
    user: The user entity (if logged in)
    css_path: a part of the css to fetch the GSoC specific CSS resources
    program: The GSoC program entity that the request is pointing to
    programs: All GSoC programs.
    program_timeline: The GSoCTimeline entity
    timeline: A TimelineHelper entity
    is_host: is the current user a host of the program
    is_mentor: is the current user a mentor in the program
    is_student: is the current user a student in the program
    is_org_admin: is the current user an org admin in the program
    org_map: map of retrieved organizations
    org_admin_for: the organizations the current user is an admin for
    mentor_for: the organizations the current user is a mentor for
    student_info: the StudentInfo for the current user and program
    organization: the GSoCOrganization for the current url

  Raises:
    out_of_band: 404 when the program does not exist
  """

  def __init__(self):
    """Constructs an empty RequestData object.
    """
    super(RequestData, self).__init__()
    # module wide fields
    self.css_path = 'gsoc'

    # program wide fields
    self._programs = None
    self.program = None
    self.program_timeline = None
    self.org_app = None

    # user profile specific fields
    self.profile = None
    self.is_host = False
    self.is_mentor = False
    self.is_student = False
    self.is_org_admin = False
    self.org_map = {}
    self.mentor_for = []
    self.org_admin_for = []
    self.student_info = None
    self.organization = None

  @property
  def programs(self):
    """Memoizes and returns a list of all programs.
    """
    from soc.modules.gsoc.models.program import GSoCProgram
    if not self._programs:
      self._programs = list(GSoCProgram.all())

    return self._programs

  def getOrganization(self, org_key):
    """Retrieves the specified organization.
    """
    if org_key not in self.org_map:
      org = db.get(org_key)
      self.org_map[org_key] = org

    return self.org_map[org_key]

  def orgAdminFor(self, organization):
    """Returns true iff the user is admin for the specified organization.

    Organization may either be a key or an organization instance.
    """
    if self.is_host:
      return True
    if isinstance(organization, db.Model):
      organization = organization.key()

    return organization in [i.key() for i in self.org_admin_for]

  def mentorFor(self, organization):
    """Returns true iff the user is mentor for the specified organization.

    Organization may either be a key or an organization instance.
    """
    if self.is_host:
      return True
    if isinstance(organization, db.Model):
      organization = organization.key()
    return organization in [i.key() for i in self.mentor_for]

  def isPossibleMentorForProposal(self, mentor_profile=None):
    """Checks if the user is a possible mentor for the proposal in the data.
    """
    assert isSet(self.profile)
    assert isSet(self.proposal)

    profile = mentor_profile if mentor_profile else self.profile

    return profile.key() in self.proposal.possible_mentors

  def populate(self, redirect, request, args, kwargs):
    """Populates the fields in the RequestData object.

    Args:
      request: Django HTTPRequest object.
      args & kwargs: The args and kwargs django sends along.
    """
    super(RequestData, self).populate(redirect, request, args, kwargs)

    if kwargs.get('sponsor') and kwargs.get('program'):
      program_key_name = "%s/%s" % (kwargs['sponsor'], kwargs['program'])
      program_key = db.Key.from_path('GSoCProgram', program_key_name)
    else:
      from soc.models.site import Site
      program_key = Site.active_program.get_value_for_datastore(self.site)
      program_key_name = program_key.name()
      import logging
      logging.error("No program specified")

    timeline_key = db.Key.from_path('GSoCTimeline', program_key_name)

    org_app_key_name = 'gsoc_program/%s/orgapp' % program_key_name
    org_app_key = db.Key.from_path('OrgAppSurvey', org_app_key_name)

    keys = [program_key, timeline_key, org_app_key]

    self.program, self.program_timeline, self.org_app = db.get(keys)

    if not self.program:
      raise NotFound("There is no program for url '%s'" % program_key_name)

    self.timeline = TimelineHelper(self.program_timeline, self.org_app)

    if kwargs.get('organization'):
      fields = [self.program.key().id_or_name(), kwargs.get('organization')]
      org_key_name = '/'.join(fields)
      self.organization = GSoCOrganization.get_by_key_name(org_key_name)
      if not self.organization:
        raise NotFound("There is no organization for url '%s'" % org_key_name)

    if self.user:
      key_name = '%s/%s' % (self.program.key().name(), self.user.link_id)
      self.profile = GSoCProfile.get_by_key_name(
          key_name, parent=self.user)

      from soc.modules.gsoc.models.program import GSoCProgram
      host_key = GSoCProgram.scope.get_value_for_datastore(self.program)
      self.is_host = host_key in self.user.host_for

    if self.profile:
      org_keys = set(self.profile.mentor_for + self.profile.org_admin_for)

      prop = GSoCProfile.student_info
      student_info_key = prop.get_value_for_datastore(self.profile)

      if student_info_key:
        self.student_info = db.get(student_info_key)
        self.is_student = True
      else:
        orgs = db.get(org_keys)

        org_map = self.org_map = dict((i.key(), i) for i in orgs)

        self.mentor_for = org_map.values()
        self.org_admin_for = [org_map[i] for i in self.profile.org_admin_for]

    self.is_org_admin = self.is_host or bool(self.org_admin_for)
    self.is_mentor = self.is_org_admin or bool(self.mentor_for)


class RedirectHelper(request_data.RedirectHelper):
  """Helper for constructing redirects.
  """

  def review(self, id=None, student=None):
    """Sets the kwargs for an url_patterns.REVIEW redirect.
    """
    if not student:
      assert 'user' in self._data.kwargs
      student = self._data.kwargs['user']
    self.id(id)
    self.kwargs['user'] = student
    return self

  def invite(self, role=None):
    """Sets args for an url_patterns.INVITE redirect.
    """
    if not role:
      assert 'role' in self._data.kwargs
      role = self._data.kwargs['role']
    self.organization()
    self.kwargs['role'] = role
    return self

  def orgApp(self, survey=None):
    """Sets kwargs for an url_patterns.SURVEY redirect for org application.
    """
    if not survey:
      assert 'survey' in self._data.kwargs
      survey = self._data.kwargs['survey']
    self.organization()
    self.kwargs['survey'] = survey

  def document(self, document):
    """Override this method to set GSoC specific _url_name.
    """
    super(RedirectHelper, self).document(document)
    self._url_name = 'show_gsoc_document'
    return self
 
  def acceptedOrgs(self):
    """Sets the _url_name to the list all the accepted orgs.
    """
    super(RedirectHelper, self).acceptedOrgs()
    self._url_name = 'gsoc_accepted_orgs'
    return self

  def allProjects(self):
    """Sets the _url_name to list all GSoC projects.
    """
    self.program()
    self._url_name = 'gsoc_accepted_projects'
    return self

  def homepage(self):
    """Sets the _url_name for the homepage of the current GSOC program.
    """
    super(RedirectHelper, self).homepage()
    self._url_name = 'gsoc_homepage'
    return self

  def searchpage(self):
    """Sets the _url_name for the searchpage of the current GSOC program.
    """
    super(RedirectHelper, self).searchpage()
    self._url_name = 'search_gsoc'
    return self

  def orgHomepage(self, link_id):
    """Sets the _url_name for the specified org homepage
    """
    super(RedirectHelper, self).orgHomepage(link_id)
    self._url_name = 'gsoc_org_home'
    return self

  def dashboard(self):
    """Sets the _url_name for dashboard page of the current GSOC program.
    """
    super(RedirectHelper, self).dashboard()
    self._url_name = 'gsoc_dashboard'
    return self

  def events(self):
    """Sets the _url_name for the events page, if it is set.
    """
    from soc.modules.gsoc.models.program import GSoCProgram
    key = GSoCProgram.events_page.get_value_for_datastore(self._data.program)

    if not key:
      self._clear()
      self._no_url = True

    self.program()
    self._url_name = 'gsoc_events'
    return self

  def request(self, request):
    """Sets the _url_name for a request.
    """
    assert request
    self.id(request.key().id())
    if request.type == 'Request':
      self._url_name = 'show_gsoc_request'
    else:
      self._url_name = 'gsoc_invitation'
    return self

  def comment(self, comment, full=False, secure=False):
    """Creates a direct link to a comment.
    """
    review = comment.parent()
    self.review(review.key().id_or_name(), review.parent().link_id)
    url = self.urlOf('review_gsoc_proposal', full=full, secure=secure)
    return "%s#c%s" % (url, comment.key().id())

  def project(self, id=None, student=None):
    """Returns the URL to the Student Project.

    Args:
      student: entity which represents the user for the student
    """
    if not student:
      assert 'user' in self._data.kwargs
      student = self._data.kwargs['user']
    self.id(id)
    self.kwargs['user'] = student
    return self

  def survey(self, survey=None):
    """Sets kwargs for an url_patterns.SURVEY redirect.

    Args:
      survey: the survey's link_id
    """
    self.program()

    if not survey:
      assert 'survey' in self._data.kwargs
      survey = self._data.kwargs['survey']
    self.kwargs['survey'] = survey

    return self

  def survey_record(self, survey=None, id=None, student=None):
    """Returns the redirector object with the arguments for survey record

    Args:
      survey: the survey's link_id
    """
    self.program()
    self.project(id, student)
    if not survey:
      assert 'survey' in self._data.kwargs
      survey = self._data.kwargs['survey']
    self.kwargs['survey'] = survey

    return self

  def grading_record(self, record):
    """Returns the redirector object with the arguments for grading record

    Args:
      record: the grading record entity
    """
    self.program()

    project = record.parent()
    self.project(project.key().id(), project.parent().link_id)

    self.kwargs['group'] = record.grading_survey_group.key().id_or_name()
    self.kwargs['record'] = record.key().id()

    return self

  def editProfile(self, profile):
    """Returns the URL for the edit profile page for the given profile.
    """
    self.program()
    self._url_name = 'edit_gsoc_profile'

    return self

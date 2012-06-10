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

"""Module for the admin pages.
"""


import logging
import math

from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import db

from django import forms as djangoforms
from django import http
from django.utils import simplejson
from django.utils.dateformat import format
from django.utils.translation import ugettext

from soc.logic import accounts
from soc.logic import cleaning
from soc.logic.exceptions import AccessViolation
from soc.logic.exceptions import BadRequest
from soc.models.user import User
from soc.views.dashboard import Dashboard
from soc.views.dashboard import DashboardUserActions
from soc.views.helper import lists
from soc.views.helper import url_patterns
from soc.views.template import Template

from soc.modules.gsoc.logic.project import getAcceptedProjectsQuery
from soc.modules.gsoc.logic.proposal import getProposalsToBeAcceptedForOrg
from soc.modules.gsoc.models.grading_project_survey import GradingProjectSurvey
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.models.project_survey import ProjectSurvey
from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.gsoc.models.proposal_duplicates import GSoCProposalDuplicate
from soc.modules.gsoc.views import forms as gsoc_forms
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper.url_patterns import url


class LookupForm(gsoc_forms.GSoCModelForm):
  """Django form for the lookup profile page.
  """

  class Meta:
    model = None

  def __init__(self, request_data, *args):
    super(LookupForm, self).__init__(*args)
    self.request_data = request_data

  email = djangoforms.CharField(label='Email')

  def clean_email(self):
    email_cleaner = cleaning.clean_email('email')

    try:
      email_address = email_cleaner(self)
    except djangoforms.ValidationError, e:
      if e.code != 'invalid':
        raise
      msg = ugettext(u'Enter a valid email address.')
      raise djangoforms.ValidationError(msg, code='invalid')

    account = users.User(email_address)
    user_account = accounts.normalizeAccount(account)
    user = User.all().filter('account', user_account).get()

    if not user:
      raise djangoforms.ValidationError(
          "There is no user with that email address")

    self.cleaned_data['user'] = user

    q = GSoCProfile.all()
    q.filter('scope', self.request_data.program)
    q.ancestor(user)
    self.cleaned_data['profile'] = q.get()


class UserActions(DashboardUserActions):
  """Template to render the left side user actions.
  """

  def actionURL(self):
    r = self.data.redirect
    r.program()

    return r.urlOf('gsoc_admin_dashboard')


class DashboardPage(RequestHandler):
  """Dashboard for admins.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/%s$' % url_patterns.PROGRAM,
         self, name='gsoc_admin_dashboard'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/admin/base.html'

  def context(self):
    """Context for dashboard page.
    """
    dashboards = []

    dashboards.append(MainDashboard(self.request, self.data))
    dashboards.append(ProgramSettingsDashboard(self.request, self.data))
    dashboards.append(ManageOrganizationsDashboard(self.request, self.data))
    dashboards.append(EvaluationsDashboard(self.request, self.data))
    dashboards.append(MentorEvaluationsDashboard(self.request, self.data))
    dashboards.append(StudentEvaluationsDashboard(self.request, self.data))
    dashboards.append(EvaluationGroupDashboard(self.request, self.data))

    dashboards.append(TrackingsDashboard(self.request, self.data))
    dashboards.append(ShipmentInfoDashboard(self.request, self.data))

    return {
        'colorbox': self.data.GET.get('colorbox'),
        'dashboards': dashboards,
        'page_name': 'Admin dashboard',
        'user_actions': UserActions(self.data)
    }

  def post(self):
    """Handles a post request.

    Do nothing, since toggle button posting to this handler
    without expecting any response.
    """
    return False


class MainDashboard(Dashboard):
  """Dashboard for admin's main-dashboard
  """

  def __init__(self, request, data):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    super(MainDashboard, self).__init__(request, data)

  def context(self):
    """Returns the context of main dashboard.
    """
    r = self.data.redirect
    r.program()

    manage_orgs = ManageOrganizationsDashboard(self.request, self.data)
    program_settings = ProgramSettingsDashboard(self.request, self.data)
    evaluations = EvaluationsDashboard(self.request, self.data)
    trackings = TrackingsDashboard(self.request, self.data)

    subpages = [
        {
            'name': 'lookup_profile',
            'description': ugettext(
                'Lookup profile of mentor or student from various program.'),
            'title': 'Lookup profile',
            'link': r.urlOf('lookup_gsoc_profile')
        },
        {
            'name': 'allocate_slots',
            'description': ugettext(
                'Allocate slots (number of acceptable projects) per '
                'organization'),
            'title': 'Allocate slots',
            'link': r.urlOf('gsoc_slots')
        },
        {
            'name': 'slots_transfer',
            'description': ugettext(
                'Transfer slots for organizations'),
            'title': 'Slots transfer',
            'link': r.urlOf('gsoc_admin_slots_transfer')
        },
        {
            'name': 'duplicates',
            'description': ugettext(
                'Calculate how many duplicate proposals, students that have '
                'accepted proposals more than one'),
            'title': 'Duplicates',
            'link': r.urlOf('gsoc_view_duplicates')
        },
        {
            'name': 'accept_proposals',
            'description': ugettext(
                'Start proposals into projects conversion'),
            'title': 'Accept proposals',
            'link': r.urlOf('gsoc_accept_proposals')
        },
        {
            'name': 'withdraw_projects',
            'description': ugettext(
                'Withdraw accepted projects or accept withdrawn projects'),
            'title': 'Withdraw projects',
            'link': r.urlOf('gsoc_withdraw_projects')
        },
        {
            'name': 'manage_organizations',
            'description': ugettext(
                'Manage organizations from active program. You can allocate '
                'slots for organizations, manage invitations for '
                'org admin/mentors, and withdraw/accept students/mentors '
                'from various organizations'),
            'title': 'Manage organizations',
            'link': '',
            'subpage_links': manage_orgs.getSubpagesLink(),
        },
        {
            'name': 'evaluations',
            'description': ugettext(
                'Send reminder, evaluation group, create, edit, '
                'view evaluations for mentors and students'),
            'title': 'Evaluations',
            'link': '',
            'subpage_links': evaluations.getSubpagesLink(),
        },
        {
            'name': 'program_settings',
            'description': ugettext(
                'Edit program settings and timeline'),
            'title': 'Program settings',
            'link': '',
            'subpage_links': program_settings.getSubpagesLink(),
        },
        {
            'name': 'participant_locations',
            'description': ugettext(
                'Show all participants (students and mentors) in a '
                'clusterer map. You can also view a single profile map '
                'after clicking the marker.'),
            'title': 'Participant Locations',
            'link': '#'
        },
        {
            'name': 'report_statistic',
            'description': ugettext(
                'Reports and statistics of program'),
            'title': 'Report/statistic',
            'link': '#'
        },
        {
            'name': 'trackings',
            'description': ugettext(
                'Shipment and payment trackings for students'),
            'title': 'Tracking Information',
            'link': '',
            'subpage_links': trackings.getSubpagesLink(),
        },
    ]

    return {
        'title': 'Admin Dashboard',
        'name': 'main',
        'subpages': self._divideSubPages(subpages),
        'enabled': True
    }


class ProgramSettingsDashboard(Dashboard):
  """Dashboard for admin's program-settings-dashboard
  """

  def __init__(self, request, data):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    r = data.redirect
    r.program()

    subpages = [
        {
            'name': 'edit_program',
            'description': ugettext(
                'Edit your program settings such as information, slots, '
                'documents, etc.'),
            'title': 'Edit program',
            'link': r.urlOf('edit_gsoc_program')
        },
        {
            'name': 'edit_timeline',
            'description': ugettext(
                'Edit your program timeline such as program start/end date, '
                'student signup start/end date, etc.'),
            'title': 'Edit timeline',
            'link': r.urlOf('edit_gsoc_timeline')
        },
        {
            'name': 'documents',
            'description': ugettext(
                'List of documents from various program.'),
            'title': 'List of documents',
            'link': r.urlOf('list_gsoc_documents')
        },
    ]

    super(ProgramSettingsDashboard, self).__init__(request, data, subpages)

  def context(self):
    """Returns the context of program settings dashboard.
    """
    subpages = self._divideSubPages(self.subpages)

    return {
        'title': 'Program Settings',
        'name': 'program_settings',
        'backlinks': [
            {
                'to': 'main',
                'title': 'Admin dashboard'
            },
        ],
        'subpages': subpages
    }


class ManageOrganizationsDashboard(Dashboard):
  """Dashboard for admin's manage-organizations-dashboard
  """

  def __init__(self, request, data):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    r = data.redirect
    r.program()

    subpages = [
        {
            'name': 'slots_allocation',
            'description': ugettext(
                'Allocate slots (number of acceptable projects) for '
                'organizations'),
            'title': 'Slots allocation',
            'link': r.urlOf('gsoc_slots')
        },
        {
            'name': 'manage_proposals',
            'description': ugettext(
                'Proposals submitted by student to organizations'),
            'title': 'Proposals',
            'link': r.urlOf('gsoc_proposals_orgs')
        },
        {
            'name': 'manage_projects',
            'description': ugettext(
                'Projects by students'),
            'title': 'Projects',
            'link': r.urlOf('gsoc_projects_orgs')
        }
    ]

    super(ManageOrganizationsDashboard, self).__init__(request, data, subpages)

  def context(self):
    """Returns the context of manage organizations dashboard.
    """
    subpages = self._divideSubPages(self.subpages)

    return {
        'title': 'Manage Organizations',
        'name': 'manage_organizations',
        'backlinks': [
            {
                'to': 'main',
                'title': 'Admin dashboard'
            },
        ],
        'subpages': subpages
    }


class EvaluationsDashboard(Dashboard):
  """Dashboard for admin's evaluations-dashboard
  """

  def __init__(self, request, data):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    mentor_evaluations = MentorEvaluationsDashboard(request, data)
    student_evaluations = StudentEvaluationsDashboard(request, data)
    evaluation_group = EvaluationGroupDashboard(request, data)

    r = data.redirect
    r.program()

    subpages = [
        {
            'name': 'reminder_emails',
            'description': ugettext(
                'Send reminder emails for evaluations.'),
            'title': 'Send reminder',
            'link': r.urlOf('gsoc_survey_reminder_admin')
        },
        {
            'name': 'evaluation_group',
            'description': ugettext(
                'Create and view evaluation group'),
            'title': 'Evaluation group',
            'link': '',
            'subpage_links': evaluation_group.getSubpagesLink(),
        },
        {
            'name': 'mentor_evaluations',
            'description': ugettext(
                'Create, edit and view evaluations for mentors'),
            'title': 'Mentor Evaluations',
            'link': '',
            'subpage_links': mentor_evaluations.getSubpagesLink(),
        },
        {
            'name': 'student_evaluations',
            'description': ugettext(
                'Create, edit and view evaluations for students'),
            'title': 'Student Evaluations',
            'link': '',
            'subpage_links': student_evaluations.getSubpagesLink(),
        },
    ]

    super(EvaluationsDashboard, self).__init__(request, data, subpages)

  def context(self):
    """Returns the context of manage organizations dashboard.
    """
    subpages = self._divideSubPages(self.subpages)

    return {
        'title': 'Evaluations',
        'name': 'evaluations',
        'backlinks': [
            {
                'to': 'main',
                'title': 'Admin dashboard'
            },
        ],
        'subpages': subpages
    }


class MentorEvaluationsDashboard(Dashboard):
  """Dashboard for mentor's evaluations
  """

  def __init__(self, request, data):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    r = data.redirect
    r.survey('midterm')

    subpages = [
        {
            'name': 'edit_mentor_evaluation',
            'description': ugettext('Create or edit midterm evaluation for '
                'mentors in active program'),
            'title': 'Create or Edit Midterm',
            'link': r.urlOf('gsoc_edit_mentor_evaluation')
        },
        {
            'name': 'preview_mentor_evaluation',
            'description': ugettext('Preview midterm evaluation to be '
                'administered mentors.'),
            'title': 'Preview Midterm Evaluation',
            'link': r.urlOf('gsoc_preview_mentor_evaluation')
        },
        {
            'name': 'view_mentor_evaluation',
            'description': ugettext('View midterm evaluation for mentors'),
            'title': 'View Midterm Records',
            'link': r.urlOf('gsoc_list_mentor_eval_records')
        },
    ]

    r.survey('final')
    subpages += [
        {
            'name': 'edit_mentor_evaluation',
            'description': ugettext('Create or edit midterm evaluation for '
                'mentors in active program'),
            'title': 'Create or Edit Final Evaluation',
            'link': r.urlOf('gsoc_edit_mentor_evaluation')
        },
        {
            'name': 'preview_mentor_evaluation',
            'description': ugettext('Preview final evaluation to be '
                'administered mentors.'),
            'title': 'Preview Final Evaluation',
            'link': r.urlOf('gsoc_preview_mentor_evaluation')
        },
        {

            'name': 'view_mentor_evaluation',
            'description': ugettext('View final evaluation for mentors'),
            'title': 'View Final Evaluation Records',
            'link': r.urlOf('gsoc_list_mentor_eval_records')
        },
    ]

    super(MentorEvaluationsDashboard, self).__init__(request, data, subpages)

  def context(self):
    """Returns the context of mentor evaluations dashboard.
    """
    subpages = self._divideSubPages(self.subpages)

    return {
        'title': 'Mentor Evaluations',
        'name': 'mentor_evaluations',
        'backlinks': [
            {
                'to': 'main',
                'title': 'Admin dashboard'
            },
            {
                'to': 'evaluations',
                'title': 'Evaluations'
            },
        ],
        'subpages': subpages
    }


class StudentEvaluationsDashboard(Dashboard):
  """Dashboard for student's evaluations
  """

  def __init__(self, request, data):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    r = data.redirect
    r.survey('midterm')

    subpages = [
        {
            'name': 'edit_student_evaluation',
            'description': ugettext('Create or edit midterm evaluation for '
                'students in active program'),
            'title': 'Create or Edit Midterm',
            'link': r.urlOf('gsoc_edit_student_evaluation')
        },
        {
            'name': 'preview_student_evaluation',
            'description': ugettext('Preview midterm evaluation to be '
                'administered to the students.'),
            'title': 'Preview Midterm Evaluation',
            'link': r.urlOf('gsoc_preview_student_evaluation')
        },
        {
            'name': 'view_student_evaluation',
            'description': ugettext('View midterm evaluation for students'),
            'title': 'View Midterm Records',
            'link': r.urlOf('gsoc_list_student_eval_records')
        },
    ]

    r.survey('final')
    subpages += [
        {
            'name': 'edit_student_evaluation',
            'description': ugettext('Create or edit final evaluation for '
                'students in active program'),
            'title': 'Create or Edit Final Evaluation',
            'link': r.urlOf('gsoc_edit_student_evaluation')
        },
        {
            'name': 'preview_student_evaluation',
            'description': ugettext('Preview final evaluation to be '
                'administered to the students.'),
            'title': 'Preview Final Evaluation',
            'link': r.urlOf('gsoc_preview_student_evaluation')
        },
        {
            'name': 'view_student_evaluation',
            'description': ugettext('View final evaluation for students'),
            'title': 'View Final Evaluation Records',
            'link': r.urlOf('gsoc_list_student_eval_records')
        },
    ]

    super(StudentEvaluationsDashboard, self).__init__(request, data, subpages)

  def context(self):
    """Returns the context of student evaluations dashboard.
    """
    subpages = self._divideSubPages(self.subpages)

    return {
        'title': 'Student Evaluations',
        'name': 'student_evaluations',
        'backlinks': [
            {
                'to': 'main',
                'title': 'Admin dashboard'
            },
            {
                'to': 'evaluations',
                'title': 'Evaluations'
            },
        ],
        'subpages': subpages
    }


class EvaluationGroupDashboard(Dashboard):
  """Dashboard for evaluation group
  """

  def __init__(self, request, data):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    subpages = [
        {
            'name': 'edit_evaluation_group',
            'description': ugettext('Create evaluation group'),
            'title': 'Create',
            'link': '#'
        },
        {
            'name': 'view_evaluation_group',
            'description': ugettext('View evaluation group'),
            'title': 'View',
            'link': '#'
        },
    ]

    super(EvaluationGroupDashboard, self).__init__(request, data, subpages)

  def context(self):
    """Returns the context of evaluation group dashboard.
    """
    subpages = self._divideSubPages(self.subpages)

    return {
        'title': 'Evaluation Group',
        'name': 'evaluation_group',
        'backlinks': [
            {
                'to': 'main',
                'title': 'Admin dashboard'
            },
            {
                'to': 'evaluations',
                'title': 'Evaluations'
            },
        ],
        'subpages': subpages
    }


class TrackingsDashboard(Dashboard):
  """Dashboard for trackings.
  """

  def __init__(self, request, data):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    r = data.redirect
    r.program()

    shipment_info = ShipmentInfoDashboard(request, data)

    subpages = [
        {
            'name': 'shipment_infos',
            'description': ugettext('Manage Shipment Information'),
            'title': 'Shipment Information',
            'link': '',
            'subpage_links': shipment_info.getSubpagesLink(),
        },
        {
            'name': 'sync_data',
            'description': ugettext('Sync Data'),
            'title': 'Sync Data',
            'link': r.urlOf('trackings_sync_data'),
        },
    ]

    super(TrackingsDashboard, self).__init__(request, data, subpages)

  def context(self):
    """Returns the context of trackings dashboard.
    """
    subpages = self._divideSubPages(self.subpages)

    return {
        'title': 'Tracking Information',
        'name': 'trackings',
        'backlinks': [
            {
                'to': 'main',
                'title': 'Admin dashboard'
            },
        ],
        'subpages': subpages
    }


class ShipmentInfoDashboard(Dashboard):
  """Dashboard for shipment infos.
  """

  def __init__(self, request, data):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    r = data.redirect
    r.program()

    subpages = [
        {
            'name': 'create_shipment_info',
            'description': ugettext('Create shipment information'),
            'title': 'Create',
            'link': r.urlOf('create_shipment_info'),
        },
        {
            'name': 'edit_shipment_infos',
            'description': ugettext('Edit shipment informations'),
            'title': 'Edit',
            'link': r.urlOf('shipment_info_records'),
        },
    ]

    super(ShipmentInfoDashboard, self).__init__(request, data, subpages)

  def context(self):
    """Returns the context of shipment infos dashboard.
    """
    subpages = self._divideSubPages(self.subpages)

    return {
        'title': 'Shipment Information',
        'name': 'shipment_infos',
        'backlinks': [
            {
                'to': 'main',
                'title': 'Admin dashboard'
            },
            {
                'to': 'trackings',
                'title': 'Tracking Information'
            }
        ],
        'subpages': subpages
    }


class LookupLinkIdPage(RequestHandler):
  """View for the participant profile.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/lookup/%s$' % url_patterns.PROGRAM,
         self, name='lookup_gsoc_profile'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/admin/lookup.html'

  def post(self):
    self.get()

  def context(self):
    form = LookupForm(self.data, self.data.POST or None)
    error = bool(form.errors)

    forms = [form]
    profile = None

    if not form.errors and self.data.request.method == 'POST':
      profile = form.cleaned_data.get('profile')

    if profile:
      cbox = False
      if self.data.GET.get('cbox'):
        cbox = True

      self.redirect.profile(profile.link_id)
      self.redirect.to('gsoc_profile_admin', cbox=cbox)

    return {
      'forms': forms,
      'error': error,
      'posted': error,
      'page_name': 'Lookup profile',
    }


class AcceptedOrgsList(Template):
  """Template for list of accepted organizations
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data

    list_config = lists.ListConfiguration()
    list_config.addColumn('name', 'Name',
        (lambda e, *args: e.short_name.strip()), width=75)
    list_config.addSimpleColumn('link_id', 'Link ID', hidden=True)

    list_config = self.extraColumn(list_config)
    self._list_config = list_config

  def extraColumn(self, list_config):
    return list_config

  def context(self):
    description = 'List of organizations accepted into %s' % (
            self.data.program.name)

    list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0, description)

    return {
        'lists': [list],
    }

  def getListData(self):
    idx = lists.getListIndex(self.request)
    if idx != 0:
      return None

    q = GSoCOrganization.all().filter('scope', self.data.program)

    starter = lists.keyStarter

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, starter)

    return response_builder.build()

  def templatePath(self):
    return "v2/modules/gsoc/admin/_accepted_orgs_list.html"


class ProposalsAcceptedOrgsList(AcceptedOrgsList):
  """Template for list of accepted organizations
  """

  def extraColumn(self, list_config):
    use_cbox = False
    if self.request.GET.get('cbox'):
      use_cbox = True

    r = self.data.redirect
    list_config.setRowAction(
        lambda e, *args: r.organization(e).urlOf('gsoc_proposals_org',
            cbox=use_cbox))
    list_config.addSimpleColumn('slots_desired', 'min', width=20)
    list_config.addSimpleColumn('max_slots_desired', 'max', width=20)
    list_config.addSimpleColumn('slots', 'Slots', width=20)

    return list_config

  def context(self):
    description = 'List of organizations accepted into %s. Click on '\
                  'a organization to see the submitted proposals.' % (
                      self.data.program.name)

    list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0, description)

    return {
        'lists': [list],
    }


class ProposalsAcceptedOrgsPage(RequestHandler):
  """View for accepted orgs.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/proposals/%s$' % url_patterns.PROGRAM,
         self, name='gsoc_proposals_orgs'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/admin/proposals.html'

  def jsonContext(self):
    list_content = ProposalsAcceptedOrgsList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')

    return list_content.content()

  def context(self):
    return {
      'page_name': 'Proposal page',
      'list': ProposalsAcceptedOrgsList(self.request, self.data),
    }


class ProjectsAcceptedOrgsList(AcceptedOrgsList):
  """Template for list of accepted organizations
  """

  def extraColumn(self, list_config):
    list_config.addColumn('name', 'Name',
        (lambda e, *args: e.short_name.strip()), width=75)
    list_config.addSimpleColumn('link_id', 'Link ID', hidden=True)

    use_cbox = False
    if self.request.GET.get('cbox'):
      use_cbox = True

    r = self.data.redirect
    list_config.setRowAction(
        lambda e, *args: r.organization(e).urlOf('gsoc_projects_org',
            cbox=use_cbox))
    list_config.addSimpleColumn('slots_desired', 'min', width=20)
    list_config.addSimpleColumn('max_slots_desired', 'max', width=20)
    list_config.addSimpleColumn('slots', 'Slots', width=20)

    def getTotalProjects(ent):
      q = GSoCProject.all()
      q.filter('program', self.data.program)
      q.filter('org', ent)
      return q.count()

    list_config.addColumn('projects', 'Projects',
        lambda ent, *a: getTotalProjects(ent))

    return list_config

  def context(self):
    description = 'List of organizations accepted into %s. Click on ' \
                  'a organization to see the accepted projects.' % (
                      self.data.program.name)

    list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0, description)

    return {
        'lists': [list],
    }


class ProjectsAcceptedOrgsPage(RequestHandler):
  """View for accepted orgs.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/projects/%s$' % url_patterns.PROGRAM,
         self, name='gsoc_projects_orgs'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/admin/projects.html'

  def jsonContext(self):
    list_content = ProjectsAcceptedOrgsList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')

    return list_content.content()

  def context(self):
    return {
      'page_name': 'Projects page',
      'list': ProjectsAcceptedOrgsList(self.request, self.data),
    }


class ProposalsList(Template):
  """Template for listing all the proposals sent to org.
  """

  def __init__(self, request, data):
    """Initializes this proposals list.
    """
    self.request = request
    self.data = data

    r = data.redirect
    list_config = lists.ListConfiguration(add_key_column=False)
    list_config.addColumn('key', 'Key', (lambda ent, *args: "%s/%s" % (
        ent.parent().key().name(), ent.key().id())), hidden=True)
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn(
        'email', 'Student Email',
        (lambda ent, *args: ent.parent().email), hidden=True)
    list_config.addSimpleColumn('score', 'Score')
    list_config.addSimpleColumn('nr_scores', '#scores', hidden=True)
    def getAverage(ent):
      if not ent.nr_scores:
        return float(0)

      average = float(ent.score)/float(ent.nr_scores)
      return float("%.2f" % average)

    list_config.addColumn(
        'average', 'Average', lambda ent, *a: getAverage(ent))

    def getStatusOnDashboard(proposal, accepted, duplicates):
      """Method for determining which status to show on the dashboard.
      """
      if proposal.status == 'pending':
          if proposal.accept_as_project and (
              not GSoCProposal.mentor.get_value_for_datastore(proposal)):
            return """<strong><font color="red">No mentor assigned</font></strong>"""
          elif proposal.key() in duplicates:
            return """<strong><font color="red">Duplicate</font></strong>"""
          elif proposal.key() in accepted:
            return """<strong><font color="green">Pending acceptance</font><strong>"""
      # not showing duplicates or proposal doesn't have an interesting state
      return proposal.status
    options = [
        ('(pending|accepted|rejected|duplicate|mentor)', 'Valid'),
        ('(duplicate|mentor)', 'Needs attention'),
        ('(duplicate)', 'Duplicate'),
        ('(accepted)', 'Accepted'),
        ('(rejected)', 'Rejected'),
        ('(mentor)', 'No mentor assigned'),
        ('', 'All'),
        ('(invalid|withdrawn|ignored)', 'Invalid'),
    ]
    list_config.addColumn('status', 'Status', getStatusOnDashboard, options=options)

    list_config.addColumn(
        'last_modified_on', 'Last modified',
        lambda ent, *args: format(ent.last_modified_on, 'Y-m-d H:i:s'))
    list_config.addColumn(
        'created_on', 'Created on',
        (lambda ent, *args: format(ent.created_on, 'Y-m-d H:i:s')),
        hidden=True)
    list_config.addColumn(
        'student', 'Student',
        lambda ent, *args: ent.parent().name())
    list_config.addSimpleColumn('accept_as_project', 'Should accept')

    # hidden keys
    list_config.addColumn(
        'full_proposal_key', 'Full proposal key',
        (lambda ent, *args: str(ent.key())), hidden=True)
    list_config.addColumn(
        'org_key', 'Organization key',
        (lambda ent, *args: ent.org.key().name()), hidden=True)

    list_config.setDefaultSort('last_modified_on', 'desc')

    self._list_config = list_config

  def templatePath(self):
    return'v2/modules/gsoc/admin/_proposals_list.html'

  def context(self):
    description = 'List of proposals submitted into %s' % self.data.organization.name

    list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=0, description=description)
    return {
        'name': 'proposals_submitted',
        'title': 'PROPOSALS SUBMITTED TO MY ORGS',
        'lists': [list],
        }

  def getListData(self):
    idx = lists.getListIndex(self.request)
    if idx != 0:
      return None

    org = self.data.organization
    program = self.data.program

    # Hold all the accepted projects for orgs where this user is a member of
    accepted = []
    # Hold all duplicates for either the entire program or the orgs of the user.
    duplicates = []
    dupQ = GSoCProposalDuplicate.all()
    dupQ.filter('is_duplicate', True)
    dupQ.filter('org', org)
    dupQ.filter('program', program)

    accepted.extend([p.key() for p in getProposalsToBeAcceptedForOrg(org)])

    duplicate_entities = dupQ.fetch(1000)
    for dup in duplicate_entities:
      duplicates.extend(dup.duplicates)

    q = GSoCProposal.all()
    q.filter('org', org)
    q.filter('program', program)

    starter = lists.keyStarter
    prefetcher = lists.modelPrefetcher(GSoCProposal, ['org'], parent=True)

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, starter, prefetcher=prefetcher)
    return response_builder.build(accepted, duplicates)


class ProposalsPage(RequestHandler):
  """View for proposals for particular org.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/proposals/%s$' % url_patterns.ORG,
         self, name='gsoc_proposals_org'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/admin/proposals.html'

  def jsonContext(self):
    list_content = ProposalsList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')

    return list_content.content()

  def post(self):
    """Handler for POST requests.
    """
    proposals_list = ProposalsList(self.request, self.data)

    if not proposals_list.post():
      raise AccessViolation(
          'You cannot change this data')

  def context(self):
    return {
      'page_name': 'Proposal page',
      'list': ProposalsList(self.request, self.data),
    }


class ProjectsList(Template):
  """Template for listing all projects of particular org.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data

    list_config = lists.ListConfiguration(add_key_column=False)
    list_config.addColumn('key', 'Key', (lambda ent, *args: "%s/%s" % (
        ent.parent().key().name(), ent.key().id())), hidden=True)
    list_config.addColumn('student', 'Student',
                          lambda entity, *args: entity.parent().name())
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn('org', 'Organization',
                          lambda entity, *args: entity.org.name)
    list_config.addColumn(
        'mentors', 'Mentor',
        lambda entity, m, *args: [m[i].name() for i in entity.mentors])
    list_config.setDefaultPagination(False)
    list_config.setDefaultSort('student')

    self._list_config = list_config

  def context(self):
    list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=0,
        description='List of projects under %s that ' \
            'accepted into %s' % (
            self.data.organization.name, self.data.program.name))

    return {
        'lists': [list],
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == 0:
      list_query = getAcceptedProjectsQuery(
          program=self.data.program, org=self.data.organization)

      starter = lists.keyStarter
      prefetcher = lists.listModelPrefetcher(
          GSoCProject, ['org'], ['mentors'], parent=True)

      response_builder = lists.RawQueryContentResponseBuilder(
          self.request, self._list_config, list_query,
          starter, prefetcher=prefetcher)
      return response_builder.build()
    else:
      return None

  def templatePath(self):
    return "v2/modules/gsoc/admin/_projects_list.html"


class ProjectsPage(RequestHandler):
  """View for projects of particular org.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/projects/%s$' % url_patterns.ORG,
         self, name='gsoc_projects_org'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/admin/projects.html'

  def jsonContext(self):
    list_content = ProjectsList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')

    return list_content.content()

  def post(self):
    """Handler for POST requests.
    """
    projects_list = ProjectsList(self.request, self.data)

    if not projects_list.post():
      raise AccessViolation(
          'You cannot change this data')

  def context(self):
    return {
      'page_name': 'Projects page',
      'list': ProjectsList(self.request, self.data),
    }


class SlotsList(AcceptedOrgsList):
  """Template for list of accepted organizations.
  """

  def extraColumn(self, list_config):
    list_config.addColumn('name', 'Name',
        (lambda e, *args: e.short_name.strip()), width=75)
    list_config.addSimpleColumn('link_id', 'Link ID', hidden=True)
    options = [('', 'All'), ('true', 'New'), ('false', 'Veteran')]
    list_config.addSimpleColumn('new_org', 'New', width=25, options=options)
    list_config.addSimpleColumn('slots_desired', 'min', width=25)
    list_config.addSimpleColumn('max_slots_desired', 'max', width=25)
    list_config.addSimpleColumn('slots', 'Slots', width=50)
    list_config.setColumnEditable('slots', True)
    list_config.setColumnSummary('slots', 'sum', "<b>Total: {0}</b>")
    list_config.addSimpleColumn('note', 'Note')
    list_config.setColumnEditable('note', True) #, edittype='textarea')
    list_config.setDefaultPagination(False)
    list_config.setDefaultSort('name')
    list_config.addPostEditButton('save', "Save", "", [], refresh="none")

    return list_config

  def post(self):
    idx = lists.getListIndex(self.request)
    if idx != 0:
      return False

    data = self.data.POST.get('data')

    if not data:
      raise BadRequest("Missing data")

    parsed = simplejson.loads(data)

    for key_name, properties in parsed.iteritems():
      note = properties.get('note')
      slots = properties.get('slots')

      if 'note' not in properties and 'slots' not in properties:
        logging.warning("Neither note or slots present in '%s'" % properties)
        continue

      if 'slots' in properties:
        if not slots.isdigit():
          logging.warning("Non-int value for slots: '%s'" % slots)
          properties.pop('slots')
        else:
          slots = int(slots)

      def update_org_txn():
        org = GSoCOrganization.get_by_key_name(key_name)
        if not org:
          logging.warning("Invalid org_key '%s'" % key_name)
          return
        if 'note' in properties:
          org.note = note
        if 'slots' in properties:
          org.slots = slots
        org.put()

      db.run_in_transaction(update_org_txn)

    return True


class SlotsPage(RequestHandler):
  """View for the participant profile.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/slots/%s$' % url_patterns.PROGRAM,
         self, name='gsoc_slots'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/admin/slots.html'

  def jsonContext(self):
    list_content = SlotsList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')

    return list_content.content()

  def post(self):
    slots_list = SlotsList(self.request, self.data)

    if not slots_list.post():
      raise AccessViolation(
          'You cannot change this data')

  def context(self):
    return {
      'page_name': 'Slots page',
      'slots_list': SlotsList(self.request, self.data),
    }


class SurveyReminderPage(RequestHandler):
  """Page to send out reminder emails to fill out a Survey.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/survey_reminder/%s$' % url_patterns.PROGRAM,
            self, name='gsoc_survey_reminder_admin'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/admin/survey_reminder.html'

  def post(self):
    post_dict = self.request.POST

    task_params = {
        'program_key': self.data.program.key().id_or_name(),
        'survey_key': post_dict['key'],
        'survey_type': post_dict['type']
    }

    task = taskqueue.Task(url=self.data.redirect.urlOf('spawn_survey_reminders'),
                          params=task_params)
    task.add()

    self.response = http.HttpResponseRedirect(
        self.request.path+'?msg=Reminders are being sent')
    return

  def context(self):
    q = GradingProjectSurvey.all()
    q.filter('scope', self.data.program)
    mentor_surveys = q.fetch(1000)

    q = ProjectSurvey.all()
    q.filter('scope', self.data.program)
    student_surveys = q.fetch(1000)

    return {
      'page_name': 'Sending Evaluation Reminders',
      'mentor_surveys': mentor_surveys,
      'student_surveys': student_surveys,
      'msg': self.request.GET.get('msg', '')
    }

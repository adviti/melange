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

"""Module for the GCI participant dashboard.
"""

from google.appengine.ext import db

from django.utils.dateformat import format
from django.utils.translation import ugettext

from soc.logic import user as user_logic
from soc.logic.exceptions import AccessViolation

from soc.models.org_app_record import OrgAppRecord
from soc.views.dashboard import Component
from soc.views.dashboard import Dashboard
from soc.views.helper import lists
from soc.views.helper import url_patterns

from soc.modules.gci.logic import org_app as org_app_logic
from soc.modules.gci.logic import ranking as scores_logic
from soc.modules.gci.logic.task import queryAllTasksClosedByStudent
from soc.modules.gci.models.request import GCIRequest
from soc.modules.gci.models.organization import GCIOrganization
from soc.modules.gci.models.profile import GCIProfile
from soc.modules.gci.models.score import GCIScore
from soc.modules.gci.models.profile import GCIStudentInfo
from soc.modules.gci.models.task import GCITask
from soc.modules.gci.views.base import RequestHandler
from soc.modules.gci.views.helper import url_names
from soc.modules.gci.views.helper.url_patterns import url


BACKLINKS_TO_MAIN = {'to': 'main', 'title': 'Main dashboard'}
BIRTHDATE_FORMAT = 'd-m-Y'
DATETIME_FORMAT = 'Y-m-d H:i:s'


class MainDashboard(Dashboard):
  """Dashboard for user's main-dashboard
  """

  def __init__(self, request, data):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    super(MainDashboard, self).__init__(request, data)
    self.subpages = []

  def context(self):
    """Returns the context of main dashboard.
    """
    return {
        'title': 'Participant dashboard',
        'name': 'main',
        'subpages': self._divideSubPages(self.subpages),
        'enabled': True
    }

  def addSubpages(self, subpage):
    self.subpages.append(subpage)


class ComponentsDashboard(Dashboard):
  """Dashboard that holds component list
  """

  def __init__(self, request, data, component_property):
    """Initializes the dashboard.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
      component_property: Component property
    """
    super(ComponentsDashboard, self).__init__(request, data)
    self.name = component_property.get('name')
    self.title = component_property.get('title')
    self.components = [component_property.get('component'),]
    self.backlinks = [component_property.get('backlinks'),]

  def context(self):
    """Returns the context of components dashboard.
    """
    return {
        'title': self.title,
        'name': self.name,
        'backlinks': self.backlinks,
        'components': self.components,
    }


class DashboardPage(RequestHandler):
  """View for the participant dashboard.
  """

  def djangoURLPatterns(self):
    """The URL pattern for the dashboard.
    """
    return [
        url(r'dashboard/%s$' % url_patterns.PROGRAM, self,
            name='gci_dashboard')]

  def checkAccess(self):
    """Denies access if you are not logged in.
    """
    self.check.isLoggedIn()

  def templatePath(self):
    """Returns the path to the template.
    """
    return 'v2/modules/gci/dashboard/base.html'

  def populateDashboards(self):
    """Populates the various dashboard subpages and components for each subpage.
    """
    # dashboard container, will hold each component list
    dashboards = []

    # main container that contains all component list
    main = MainDashboard(self.request, self.data)

    # retrieve active links and add it to the main dashboard
    links = self.links()
    for link in links:
      main.addSubpages(link)

    # retrieve active component(s) for currently logged-in user
    components = self.components()

    # add components as children of main dashboard and treat the component
    # as dashboard element
    for component in components:
      c = {
          'name': component.context().get('name'),
          'description': component.context().get('description'),
          'title': component.context().get('title'),
          'component_link': True,
          }
      main.addSubpages(c)

      dashboards.append(ComponentsDashboard(self.request, self.data, {
          'name': component.context().get('name'),
          'title': component.context().get('title'),
          'component': component,
          'backlinks': BACKLINKS_TO_MAIN,
          }))

    dashboards.append(main)

    return dashboards

  def shouldSubmitForms(self):
    """Checks if the current user should submit the student forms
    """
    student_id_form = False
    consent_form = False

    if not self.data.student_info:
      return False, False, False

    query = queryAllTasksClosedByStudent(self.data.profile, keys_only=True)

    # If the current user is not a student or if he is a student and has
    # not completed even a single task successfully he/she need not submit
    # any forms.
    if query.count() < 1:
      return False, False, False

    has_completed_task = True

    if not self.data.student_info.student_id_form:
      student_id_form = True

    if not self.data.student_info.consent_form:
      consent_form = True

    return has_completed_task, student_id_form, consent_form

  def context(self):
    """Handler for default HTTP GET request.
    """
    context = {
        'page_name': self.data.program.name,
        'user_name': self.data.user.name if self.data.user else None,
        }

    # Check if the student should submit either of the forms
    has_completed_task, student_id_form, consent_form = self.shouldSubmitForms()
    context['student_id_form'] = student_id_form
    context['consent_form'] = consent_form

    if has_completed_task:
      context['student_forms_link'] = self.redirect.program().urlOf(
          'gci_student_form_upload')

    context['dashboards'] = self.populateDashboards()

    return context

  def jsonContext(self):
    """Handler for JSON requests.
    """
    components = self.components()

    list_content = None
    for component in components:
      list_content = component.getListData()
      if list_content:
        break

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def components(self):
    """Returns the list components that are active on the page.
    """
    components = []

    if self.data.student_info:
      components += self._getStudentComponents()
    elif self.data.is_org_admin:
      components += self._getOrgAdminComponents()
      components += self._getMentorComponents()
    elif self.data.is_mentor:
      components += self._getMentorComponents()
    else:
      components += self._getLoneUserComponents()

    if self.data.is_host or user_logic.isDeveloper():
      components += self._getHostComponents()

    return components

  def _getHostComponents(self):
    """Get the dashboard components for a host.
    """
    components = []

    components.append(AllStudentsList(self.request, self.data))

    return components

  def _getStudentComponents(self):
    """Get the dashboard components for a student.
    """
    components = []

    return components

  def _getMentorComponents(self):
    """Get the dashboard components for Organization members.
    """
    components = []

    component = self._getMyOrgApplicationsComponent()
    if component:
      components.append(component)

    components.append(MyOrgsTaskList(self.request, self.data))

    # add org list just before creating task and invitation, so mentor can
    # choose which organization the task or invitite will be created for
    components.append(MyOrgsListBeforeCreateTask(self.request, self.data))

    # add request to become mentor component
    components.append(AllOrgsListBeforeRequestRole(self.request, self.data))

    return components

  def _getOrgAdminComponents(self):
    """Get the dashboard components for org admins.
    """
    components = []

    # add list of mentors component
    components.append(MyOrgsMentorsList(self.request, self.data))

    # add invite mentors component
    components.append(MyOrgsListBeforeInviteMentor(self.request, self.data))

    # add invite org admins component
    components.append(MyOrgsListBeforeInviteOrgAdmin(self.request, self.data))

    # add list of all the invitations
    components.append(OrgAdminInvitesList(self.request, self.data))

    # add list of all the requests
    components.append(OrgAdminRequestsList(self.request, self.data))

    # add bulk create tasks component 
    components.append(MyOrgsListBeforeBulkCreateTask(self.request, self.data))

    # add edit org profile component
    components.append(MyOrgsListBeforeOrgProfile(self.request, self.data))

    return components

  def _getLoneUserComponents(self):
    """Get the dashboard components for users without any role.
    """
    components = []

    component = self._getMyOrgApplicationsComponent()
    if component:
      components.append(component)

    # add request to become mentor component
    components.append(AllOrgsListBeforeRequestRole(self.request, self.data))

    return components

  def _getMyOrgApplicationsComponent(self):
    """Returns MyOrgApplicationsComponent iff this user is main_admin or
    backup_admin in an application.
    """
    survey = org_app_logic.getForProgram(self.data.program)

    # Test if this user is main admin or backup admin
    q = OrgAppRecord.all()
    q.filter('survey', survey)
    q.filter('main_admin', self.data.user)

    record = q.get()

    q = OrgAppRecord.all()
    q.filter('survey', survey)
    q.filter('backup_admin', self.data.user)

    if record or q.get():
      # add a component showing the organization application of the user
      return MyOrgApplicationsComponent(self.request, self.data, survey)

    return None

  def links(self):
    """Returns additional links of main dashboard that are active on the page.
    """
    links = []

    if self.data.student_info:
      links += self._getStudentLinks()
    if self.data.is_org_admin:
      links += self._getOrgAdminLinks()
    if self.data.is_mentor:
      links += self._getMentorLinks()
    links += self._getLoneUserLinks()

    return links

  def _getStudentLinks(self):
    """Get the main dashboard links for student.
    """
    links = []

    return links

  def _getOrgAdminLinks(self):
    """Get the main dashboard links for org-admin.
    """
    links = []
    return links

  def _getMentorLinks(self):
    """Get the main dashboard links for mentor.
    """
    links = []
    return links

  def _getLoneUserLinks(self):
    """Get the main dashboard links for users without any role.
    """
    links = []

    link = self._getAddNewOrgAppLink()
    if link:
      links.append(link)

    # add link to my invitations list
    links.append(self._getMyInvitationsLink())

    return links

  def _getAddNewOrgAppLink(self):
    """Get the link for org admins to take organization application survey.
    """
    survey = org_app_logic.getForProgram(self.data.program)
    if not survey or not self.data.timeline.surveyPeriod(survey):
      return []

    r = self.data.redirect
    r.program()

    return {
        'name': 'take_org_app',
        'description': ugettext(
            'Take organization application survey.'),
        'title': 'Take organization application',
        'link': r.urlOf('gci_take_org_app')
        }

  def _getMyInvitationsLink(self):
    """Get the link of incoming invitations list (invitations sent to me).
    """
    r = self.data.redirect
    r.program()

    return {
        'name': 'list_invites',
        'description': ugettext(
            'List of all invites which have been sent to me.'),
        'title': 'Invites to me',
        'link': r.urlOf(url_names.GCI_LIST_INVITES)
        }

  def _getMyOrgInvitationsLink(self):
    """Get the link of outgoing invitations list (invitations sent by my orgs).
    """
    r = self.data.redirect
    r.program()

    return {
        'name': 'list_org_invites',
        'description': ugettext(
            'List of all invites which have been sent by my organizations.'),
        'title': 'My organization outgoing invitations',
        'link': r.urlOf(url_names.GCI_LIST_ORG_INVITES)
        }


class MyOrgApplicationsComponent(Component):
  """Component for listing the Organization Applications of the current user.
  """

  def __init__(self, request, data, survey):
    """Initializes the component.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
      survey: the OrgApplicationSurvey entity
    """
    super(MyOrgApplicationsComponent, self).__init__(request, data)

    # passed in so we don't have to do double queries
    self.survey = survey

    list_config = lists.ListConfiguration()

    list_config.addSimpleColumn('name', 'Name')
    list_config.addSimpleColumn('org_id', 'Organization ID')
    list_config.addColumn(
        'created', 'Created On',
        lambda ent, *args: format(ent.created, DATETIME_FORMAT))
    list_config.addColumn(
        'modified', 'Last Modified On',
        lambda ent, *args: format(ent.modified, DATETIME_FORMAT))

    if self.data.timeline.surveyPeriod(survey):
      url_name = 'gci_retake_org_app'
    else:
      url_name = 'gci_show_org_app'

    list_config.setRowAction(
        lambda e, *args: data.redirect.id(e.key().id()).
            urlOf(url_name))

    self._list_config = list_config

    super(MyOrgApplicationsComponent, self).__init__(request, data)

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return 'v2/modules/gci/dashboard/list_component.html'

  def context(self):
    """Returns the context of this component.
    """
    list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=0, preload_list=False)

    return {
        'name': 'org_app',
        'title': 'My organization applications',
        'lists': [list],
        'description': ugettext('My organization applications'),
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    if lists.getListIndex(self.request) != 0:
      return None

    q = OrgAppRecord.all()
    q.filter('survey', self.survey)
    q.filter('main_admin', self.data.user)

    records = q.fetch(1000)

    q = OrgAppRecord.all()
    q.filter('survey', self.survey)
    q.filter('backup_admin', self.data.user)

    records.extend(q.fetch(1000))

    response = lists.ListContentResponse(self.request, self._list_config)

    for record in records:
      response.addRow(record)
    response.next = 'done'

    return response

class MyOrgsTaskList(Component):
  """Component for listing the tasks of the orgs of the current user.
  """

  def __init__(self, request, data):
    """Initializes the component.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    super(MyOrgsTaskList, self).__init__(request, data)

    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn(
        'org', 'Organization',
        lambda ent, *args: ent.org.name)

    list_config.addColumn('time_to_complete', 'Time to complete',
                          lambda entity, *args: entity.taskTimeToComplete())

    list_config.addColumn(
        'mentors', 'Mentors',
        lambda entity, mentors, *args: ', '.join(
            mentors[i].name() for i in entity.mentors))

    list_config.addSimpleColumn('description', 'Description', hidden=True)
    list_config.addColumn(
        'student', 'Student',
        lambda ent, *args: ent.student.name() if ent.student else '',
        hidden=True)
    list_config.addColumn(
        'created_by', 'Created by',
        lambda entity, *args: entity.created_by.name() \
            if entity.created_by else '',
        hidden=True)
    list_config.addColumn(
        'modified_by', 'Modified by',
        lambda entity, *args: entity.modified_by.name() \
            if entity.modified_by else '',
        hidden=True)
    list_config.addColumn(
        'created_on', 'Created on',
        lambda entity, *args: format(entity.created_on, DATETIME_FORMAT) \
            if entity.created_on else '',
        hidden=True)
    list_config.addColumn(
        'modified_on', 'Modified on',
        lambda entity, *args: format(entity.modified_on, DATETIME_FORMAT) \
            if entity.modified_on else '',
        hidden=True)
    list_config.addColumn('closed_on', 'Closed on',
        lambda entity, *args: format(
            entity.closed_on, DATETIME_FORMAT) if entity.closed_on else '',
        hidden=True)
    list_config.addSimpleColumn('status', 'Status')

    # TODO (madhu): Super temporary solution until the pretty lists are up.
    list_config.addColumn('edit', 'Edit',
        lambda entity, *args: (
          '<a href="%s" style="color:#0000ff;text-decoration:underline;">'
          'Edit</a>' % (data.redirect.id(entity.key().id()).urlOf(
              'gci_edit_task'))))

    list_config.setRowAction(
        lambda e, *args: data.redirect.id(e.key().id()).
            urlOf('gci_view_task'))

    self._list_config = list_config

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return'v2/modules/gci/dashboard/list_component.html'

  def context(self):
    """Returns the context of this component.
    """
    list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=1, preload_list=False)

    return {
        'name': 'all_org_tasks',
        'title': 'All tasks for my organizations',
        'lists': [list],
        'description': ugettext('List of all tasks for my organization'),
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    if lists.getListIndex(self.request) != 1:
      return None

    q = GCITask.all()
    q.filter('program', self.data.program)
    q.filter('org IN', self.data.mentor_for)

    starter = lists.keyStarter
    prefetcher = lists.listModelPrefetcher(
        GCITask, ['org', 'student', 'created_by', 'modified_by'], ['mentors'])

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, starter, prefetcher=prefetcher)

    return response_builder.build()


class MyOrgsList(Component):
  """Component for listing the orgs of the current user.

  Since mentor_for is a list of orgs, we need to give org selection first
  """

  def __init__(self, request, data):
    """Initializes the component.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    super(MyOrgsList, self).__init__(request, data)

    list_config = lists.ListConfiguration()

    list_config.addSimpleColumn('name', 'Organization Name')

    self._list_config = list_config

    self._setRowAction(request, data)

    self._setIdx()

  def _setIdx(self):
    raise NotImplemented

  def _setRowAction(self, request, data):
    """Since setRowAction can be vary, it must be implemented individually.
    """
    raise NotImplemented
    
  def _getContext(self):
    raise NotImplemented

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return'v2/modules/gci/dashboard/list_component.html'

  def context(self):
    """Returns the context of this component.
    """
    return self._getContext()

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    if lists.getListIndex(self.request) != self.idx:
      return None

    response = lists.ListContentResponse(self.request, self._list_config)

    for org in self.data.mentor_for:
      response.addRow(org)

    response.next = 'done'

    return response


class MyOrgsListBeforeCreateTask(MyOrgsList):
  """Component for listing the orgs of the current user, just before creating
  task.
  """

  def _setIdx(self):
    self.idx = 2

  def _getContext(self):
    org_list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=self.idx, preload_list=False)

    return {
        'name': 'create_tasks',
        'title': 'Create Task',
        'lists': [org_list],
        'description': ugettext('Create task for students. Since you may '
            'belong to more than one organizations, you need to choose one '
            'organization you will create the task for.')}

  def _setRowAction(self, request, data):
    self._list_config.setRowAction(
        lambda e, *args: data.redirect.organization(e).
            urlOf('gci_create_task'))


class MyOrgsListBeforeBulkCreateTask(MyOrgsList):
  """Component for listing the orgs of the current user, just before creating
  task.
  """

  def _setIdx(self):
    self.idx = 3

  def _getContext(self):
    org_list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=self.idx, preload_list=False)

    return {
        'name': 'bulk_create_tasks',
        'title': 'Bulk Upload Tasks',
        'lists': [org_list],
        'description': ugettext('Bulk upload tasks. Since you may '
            'belong to more than one organizations, you need to choose one '
            'organization you will upload the tasks for.')}

  def _setRowAction(self, request, data):
    self._list_config.setRowAction(
        lambda e, *args: data.redirect.organization(e).
            urlOf('gci_bulk_create'))


class MyOrgsListBeforeInviteMentor(MyOrgsList):
  """Component for listing the orgs of the current user, just before creating
  invite.
  """

  def _setIdx(self):
    self.idx = 4

  def _getContext(self):
    org_list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=self.idx, preload_list=False)

    return {
        'name': 'invite_mentor',
        'title': 'Invite Mentor',
        'lists': [org_list],
        'description': ugettext('Invite mentors to be part of your '
            'organization.')}

  def _setRowAction(self, request, data):
    r = data.redirect

    self._list_config.setRowAction(
        lambda e, *args: r.invite('mentor', e)
            .urlOf(url_names.GCI_SEND_INVITE))


class MyOrgsListBeforeInviteOrgAdmin(MyOrgsList):
  """Component for listing the organizations of the current user, just before
  he or she creates a new org admin invite.
  """

  def _setIdx(self):
    self.idx = 5

  def _getContext(self):
    org_list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=self.idx, preload_list=False)

    return {
        'name': 'invite_org_admin',
        'title': 'Invite Org Admin',
        'lists': [org_list],
        'description': ugettext('Invite org admins to be part of your '
            'organization. Please note that once they accept your invitation, '
            'they will become mentors too.')}

  def _setRowAction(self, request, data):
    r = data.redirect

    self._list_config.setRowAction(
        lambda e, *args: r.invite('org_admin', e)
            .urlOf(url_names.GCI_SEND_INVITE))


class MyOrgsMentorsList(Component):
  """Component for listing the mentors of the orgs of the current user.
  """

  def __init__(self, request, data):
    """Initializes the component.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    super(MyOrgsMentorsList, self).__init__(request, data)

    list_config = lists.ListConfiguration()

    list_config.addSimpleColumn('public_name', 'Name')
    list_config.addSimpleColumn('link_id', 'Username')
    list_config.addSimpleColumn('email', 'Email')

    self._list_config = list_config

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return'v2/modules/gci/dashboard/list_component.html'

  def context(self):
    """Returns the context of this component.
    """
    list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=6, preload_list=False)

    return {
        'name': 'all_orgs_mentors',
        'title': 'All mentors for my organizations',
        'lists': [list],
        'description': ugettext('List of all mentors for my organizations'),
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    if lists.getListIndex(self.request) != 6:
      return None

    q = GCIProfile.all()
    q.filter('mentor_for IN', self.data.org_admin_for)

    starter = lists.keyStarter

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, starter)

    return response_builder.build()


class MyOrgsListBeforeOrgProfile(MyOrgsList):
  """Component for listing the orgs of the current user, just before
  create/edit org's profile.
  """

  def _setIdx(self):
    self.idx = 7

  def _getContext(self):
    org_list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=self.idx, preload_list=False)

    return {
        'name': 'edit_org_profile',
        'title': 'Edit organization profile',
        'lists': [org_list],
        'description': ugettext('Edit organization profile. Since you may '
            'belong to more than one organizations, you need to choose one '
            'organization you will edit the profile for.')}

  def _setRowAction(self, request, data):
    self._list_config.setRowAction(
        lambda e, *args: data.redirect.organization(e).
            urlOf(url_names.EDIT_GCI_ORG_PROFILE))


class AllOrgsListBeforeRequestRole(MyOrgsList):
  """Component for listing all the organizations that the current user may
  request to become mentor for.
  """

  def _setIdx(self):
    self.idx = 8

  def _setRowAction(self, request, data):
    self._list_config.setRowAction(
        lambda e, *args: data.redirect.invite('mentor', e)
            .urlOf(url_names.GCI_SEND_REQUEST))

  def getListData(self):
    if lists.getListIndex(self.request) != self.idx:
      return None

    q = GCIOrganization.all()
    q.filter('scope', self.data.program)
    q.filter('status IN', ['new', 'active'])

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, lists.keyStarter)

    return response_builder.build()

  def _getContext(self):
    org_list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=self.idx, preload_list=False)

    return {
        'name': 'request_to_become_mentor',
        'title': 'Request to become a mentor',
        'lists': [org_list],
        'description': ugettext('Request to become a mentor for one of '
            'the participating organizations.')}


class OrgAdminInvitesList(Component):
  """Template for list of invites that have been sent by the organizations
  that the current user is organization admin for.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data
    r = data.redirect

    list_config = lists.ListConfiguration()
    list_config.addColumn('to', 'To',
        lambda entity, *args: entity.user.name)
    list_config.addSimpleColumn('status', 'Status')

    # organization column should be added only if the user is an administrator
    # for more than one organization
    if len(self.data.org_admin_for) > 1:
      list_config.addColumn('org', 'From',
        lambda entity, *args: entity.org.name)

    list_config.setRowAction(
        lambda e, *args: r.id(e.key().id())
            .urlOf(url_names.GCI_MANAGE_INVITE))

    self.idx = 9
    self._list_config = list_config

  def getListData(self):
    if lists.getListIndex(self.request) != self.idx:
      return None

    q = GCIRequest.all()
    q.filter('type', 'Invitation')
    q.filter('org IN', [e.key() for e in self.data.org_admin_for])

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, lists.keyStarter)

    return response_builder.build()

  def context(self):
    invite_list = lists.ListConfigurationResponse(
        self.data, self._list_config, self.idx)

    return {
        'name': 'outgoing_invitations',
        'title': 'Outgoing Invitations',
        'lists': [invite_list],
        'description': ugettext(
            'See all the invitations that have been sent '
            'by your organizations.')
    }

  def templatePath(self):
    return 'v2/modules/gci/dashboard/list_component.html'


class OrgAdminRequestsList(Component):
  """Template for list of requests that have been sent to the organizations
  that the current user is organization admin for.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data
    r = data.redirect

    list_config = lists.ListConfiguration()
    list_config.addColumn('from', 'From',
        lambda entity, *args: entity.user.name)
    list_config.addSimpleColumn('status', 'Status')

    # organization column should be added only if the user is an administrator
    # for more than one organization
    if len(self.data.org_admin_for) > 1:
      list_config.addColumn('org', 'Organization',
        lambda entity, *args: entity.org.name)

    list_config.setRowAction(
        lambda e, *args: r.id(e.key().id())
            .urlOf(url_names.GCI_RESPOND_REQUEST))

    self.idx = 10
    self._list_config = list_config

  def getListData(self):
    if lists.getListIndex(self.request) != self.idx:
      return None

    q = GCIRequest.all()
    q.filter('type', 'Request')
    q.filter('org IN', [e.key() for e in self.data.org_admin_for])

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, lists.keyStarter)

    return response_builder.build()

  def context(self):
    request_list = lists.ListConfigurationResponse(
        self.data, self._list_config, self.idx)

    return {
        'name': 'incoming_requests',
        'title': 'Incoming Requests',
        'lists': [request_list],
        'description': ugettext(
            'See all the requests that have been sent to '
            'your organizations.')
    }

  def templatePath(self):
    return 'v2/modules/gci/dashboard/list_component.html'


class AllStudentsList(Component):
  """Component for the list of all the students who have completed at least
  one task in the program.
  """

  """The default index number for this component.
  """
  COMPONTENT_IDX = 11

  def __init__(self, request, data):
    self.request = request
    self.data = data
    r = data.redirect

    list_config = lists.ListConfiguration(add_key_column=False)
    list_config.addColumn('key', 'Key', (lambda entity, *args: "%s" % (
        entity.parent().key().id_or_name())), hidden=True)
    list_config.addColumn('name', 'Student name',
        lambda entity, *args: entity.parent().name())
    list_config.addColumn('student_id', 'Student ID',
        lambda entity, *args: 'Yes' 
            if entity.parent().student_info.student_id_form else 'No')
    list_config.addColumn('consent_form', 'Parental Consent',
        lambda entity, *args: 'Yes' 
            if entity.parent().student_info.consent_form else 'No')
    list_config.addColumn('number_of_tasks', 'Number of tasks',
        lambda entity, *args: len(entity.tasks))
    list_config.addColumn('email', 'Email',
        lambda entity, *args: entity.parent().email,
        hidden=True)
    list_config.addColumn('street', 'Street',
        lambda entity, *args: entity.parent().res_street + ' ' +
            str(entity.parent().res_street_extra or ''),
        hidden=True)
    list_config.addColumn('city', 'City',
        lambda entity, *args: entity.parent().res_city,
        hidden=True)
    list_config.addColumn('state', 'State/Province',
        lambda entity, *args: entity.parent().res_state,
        hidden=True)
    list_config.addColumn('postalcode', 'Postal Code',
        lambda entity, *args: entity.parent().res_postalcode,
        hidden=True)
    list_config.addColumn('country', 'Country',
        lambda entity, *args: entity.parent().res_country,
        hidden=True)   

    self.idx = self.COMPONTENT_IDX
    self._list_config = list_config

  def getListData(self):
    if lists.getListIndex(self.request) != self.idx:
      return None

    query = scores_logic.allScoresForProgramQuery(self.data.program)

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, query, lists.keyStarter)

    return response_builder.build()

  def context(self):
    request_list = lists.ListConfigurationResponse(
        self.data, self._list_config, self.idx)

    return {
        'name': 'all_students_with_tasks',
        'title': 'All students',
        'lists': [request_list],
        'description': ugettext(
            'See all the students who have completed at least one task.')
    }

  def templatePath(self):
    return 'v2/modules/gci/dashboard/list_component.html'

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

"""Module containing the view for GSoC project details page.
"""


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.logic.exceptions import BadRequest
from soc.views.helper.access_checker import isSet
from soc.views.template import Template
from soc.views.toggle_button import ToggleButtonTemplate

from soc.modules.gsoc.logic import profile as profile_logic
from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.views import assign_mentor
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.forms import GSoCModelForm
from soc.modules.gsoc.views.helper import url_patterns
from soc.modules.gsoc.views.helper.url_patterns import url


class ProjectDetailsForm(GSoCModelForm):
  """Constructs the form to edit the project details
  """

  class Meta:
    model = GSoCProject
    css_prefix = 'gsoc_project'
    fields = ['title', 'abstract', 'public_info',
              'additional_info', 'feed_url']


class ProjectDetailsUpdate(RequestHandler):
  """Encapsulate the methods required to generate Project Details update form.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/project_details/update.html'

  def djangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    return [
        url(r'project/update/%s$' % url_patterns.PROJECT, self,
            name='gsoc_update_project')
    ]

  def checkAccess(self):
    """Access checks for GSoC project details page.
    """
    self.check.isLoggedIn()
    self.check.isActiveStudent()
    self.mutator.projectFromKwargs()
    self.check.canStudentUpdateProject()

  def context(self):
    """Handler to for GSoC project details page HTTP get request.
    """
    project_details_form = ProjectDetailsForm(self.data.POST or None,
                                              instance=self.data.project)

    context = {
        'page_name': 'Update project details',
        'project': self.data.project,
        'forms': [project_details_form],
        'error': project_details_form.errors,
    }

    return context

  def validate(self):
    """Validate the form data and save if valid.
    """
    project_details_form = ProjectDetailsForm(self.data.POST or None,
                                              instance=self.data.project)

    if not project_details_form.is_valid():
      return False

    project_details_form.save()
    return True

  def post(self):
    """Post handler for the project details update form.
    """
    if self.validate():
      self.redirect.project()
      self.redirect.to('gsoc_project_details')
    else:
      self.get()


class UserActions(Template):
  """Template to render the left side user actions.
  """

  DEF_FEATURED_PROJECT_HELP = ugettext(
      'Choosing Yes features this project on program home page. The '
      'project is featured when Yes is displayed in bright orange.')

  def __init__(self, data):
    super(UserActions, self).__init__(data)
    self.toggle_buttons = []

  def context(self):
    assert isSet(self.data.project)

    r = self.data.redirect.project()

    featured_project = ToggleButtonTemplate(
        self.data, 'on_off', 'Featured', 'project-featured',
        r.urlOf('gsoc_featured_project'),
        checked=self.data.project.is_featured,
        help_text=self.DEF_FEATURED_PROJECT_HELP,
        labels={
            'checked': 'Yes',
            'unchecked': 'No'})
    self.toggle_buttons.append(featured_project)

    context = {
        'title': 'Project Actions',
        'toggle_buttons': self.toggle_buttons,
        }

    r = self.data.redirect
    all_mentors_keys = profile_logic.queryAllMentorsKeysForOrg(
        self.data.project.org)
    context['assign_mentor'] = assign_mentor.AssignMentorFields(
        self.data, self.data.project.mentors,
        r.project().urlOf('gsoc_project_assign_mentors'),
        all_mentors=all_mentors_keys, mentor_required=True)

    return context

  def templatePath(self):
    return "v2/modules/gsoc/project_details/_user_action.html"


class ProjectDetails(RequestHandler):
  """Encapsulate all the methods required to generate GSoC project
  details page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/project_details/base.html'

  def djangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    return [
        url(r'project/%s$' % url_patterns.PROJECT, self,
            name='gsoc_project_details')
    ]

  def checkAccess(self):
    """Access checks for GSoC project details page.
    """
    self.mutator.projectFromKwargs()

  def context(self):
    """Handler to for GSoC project details page HTTP get request.
    """
    project = self.data.project

    r = self.redirect

    context = {
        'page_name': 'Project details',
        'project': project,
        'org_home_link': r.organization(project.org).urlOf('gsoc_org_home'),
    }

    if self.data.orgAdminFor(self.data.project.org):
      context['user_actions'] = UserActions(self.data)

    user_is_owner = self.data.user and \
        (self.data.user.key() == self.data.project_owner.parent_key())
    if user_is_owner:
      context['update_link'] = r.project().urlOf('gsoc_update_project')

    return context


class AssignMentors(RequestHandler):
  """View which handles assigning mentor to a project.
  """

  def djangoURLPatterns(self):
    return [
         url(r'project/assign_mentors/%s$' % url_patterns.PROJECT,
         self, name='gsoc_project_assign_mentors'),
    ]

  def checkAccess(self):
    self.mutator.projectFromKwargs()
    assert isSet(self.data.project.org)
    self.check.isOrgAdminForOrganization(self.data.project.org)

  def assignMentors(self, mentor_keys):
    """Assigns the mentor to the project.

    Args:
      mentor_keys: List of mentor profile keys to to be assigned
          to the project.
    """
    assert isSet(self.data.project)

    project_key = self.data.project.key()

    def assign_mentor_txn():
      project = db.get(project_key)

      project.mentors = mentor_keys

      db.put(project)

    db.run_in_transaction(assign_mentor_txn)

  def validate(self):
    str_mentor_keys = self.data.POST.getlist('assign_mentor')

    if str_mentor_keys:
      org = self.data.project.org

      # need the list to set conversion and back to list conversion
      # to ensure that same mentor doesn't get assigned to the
      # project more than once
      mentor_keys = set([db.Key(k) for k in str_mentor_keys if k])
      if mentor_keys < set(
          profile_logic.queryAllMentorsKeysForOrg(org)):
        return list(mentor_keys)

      raise BadRequest("Invalid post data.")

    return None

  def post(self):
    assert isSet(self.data.project)

    mentor_keys = self.validate()
    if mentor_keys:
      self.assignMentors(mentor_keys)

    project_owner = self.data.project.parent()

    self.redirect.project(self.data.project.key().id(),
                          project_owner.link_id)
    self.redirect.to('gsoc_project_details')

  def get(self):
    """Special Handler for HTTP GET request since this view only handles POST.
    """
    self.error(405)


class FeaturedProject(RequestHandler):
  """View which handles making the project featured by toggle button.
  """

  def djangoURLPatterns(self):
    return [
         url(r'project/featured/%s$' % url_patterns.PROJECT,
         self, name='gsoc_featured_project'),
    ]

  def checkAccess(self):
    self.mutator.projectFromKwargs()
    assert isSet(self.data.project.org)
    self.check.isOrgAdminForOrganization(self.data.project.org)

  def toggleFeatured(self, value):
    """Makes the project featured.

    Args:
      value: can be either "checked" or "unchecked".
    """
    assert isSet(self.data.project)

    if value != 'checked' and value != 'unchecked':
      raise BadRequest("Invalid post data.")

    if value == 'checked' and not self.data.project.is_featured:
      raise BadRequest("Invalid post data.")
    if value == 'unchecked' and self.data.project.is_featured:
      raise BadRequest("Invalid post data.")

    project_key = self.data.project.key()

    def make_featured_txn():
      # transactionally get latest version of the proposal
      project = db.get(project_key)
      if value == 'unchecked':
        project.is_featured = True
      elif value == 'checked':
        project.is_featured = False

      db.put(project)

    db.run_in_transaction(make_featured_txn)

  def post(self):
    value = self.data.POST.get('value')
    self.toggleFeatured(value)

  def get(self):
    """Special Handler for HTTP GET request since this view only handles POST.
    """
    self.error(405)

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

"""Module for the GCI organization profile page.
"""


from soc.views import forms

from django import forms as django_forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic.exceptions import RedirectRequest
from soc.views.helper import url_patterns
from soc.views import org_profile

from soc.modules.gci.models.organization import GCIOrganization
from soc.modules.gci.views.base import RequestHandler
from soc.modules.gci.views import forms as gci_forms
from soc.modules.gci.views.helper import url_names
from soc.modules.gci.views.helper.url_patterns import url

PROFILE_EXCLUDE = org_profile.PROFILE_EXCLUDE + [
    'task_quota_limit',
]

class OrgProfileForm(org_profile.OrgProfileForm):
  """Django form for the organization profile.
  """

  def __init__(self, *args, **kwargs):
    super(OrgProfileForm, self).__init__(
        gci_forms.GCIBoundField, *args, **kwargs)

  class Meta:
    model = GCIOrganization
    css_prefix = 'gci_org_page'
    exclude = PROFILE_EXCLUDE

  def templatePath(self):
    return gci_forms.TEMPLATE_PATH


class OrgCreateProfileForm(OrgProfileForm):
  """Django form to create the organization profile.
  """

  class Meta:
    model = GCIOrganization
    css_prefix = 'gci_org_page'
    exclude = PROFILE_EXCLUDE


class OrgProfilePage(RequestHandler):
  """View for the Organization Profile page.
  """

  def djangoURLPatterns(self):
    return [
         url(r'profile/organization/%s$' % url_patterns.PROGRAM,
         self, name=url_names.CREATE_GCI_ORG_PROFILE),
         url(r'profile/organization/%s$' % url_patterns.ORG,
         self, name=url_names.EDIT_GCI_ORG_PROFILE),
    ]

  def checkAccess(self):
    self.check.isLoggedIn()
    self.check.isProgramVisible()

    if 'organization' in self.data.kwargs:
      self.check.isProfileActive()
      self.check.isOrgAdminForOrganization(self.data.organization)
      #probably check if the org is active
    else:
      self.data.organization = None
      self.mutator.orgAppFromOrgId()
      self.check.canCreateNewOrg()

  def templatePath(self):
    return 'v2/modules/gci/org_profile/base.html'

  def context(self):
    if not self.data.organization:
      form = OrgCreateProfileForm(self.data.POST or None)
    else:
      form = OrgProfileForm(self.data.POST or None,
                            instance=self.data.organization)

    context = {
        'page_name': "Organization profile",
        'forms': [form],
        'error': bool(form.errors),
        }

    if self.data.organization:
      r = self.data.redirect.organization()
      context['org_home_page_link'] = r.urlOf('gci_org_home')

    return context

  def post(self):
    org_profile = self.createOrgProfileFromForm()
    if org_profile:
      self.redirect.organization(org_profile)
      self.redirect.to('edit_gci_org_profile', validated=True)
    else:
      self.get()

  def createOrgProfileFromForm(self):
    """Creates a new organization based on the data inserted in the form.

    Returns:
      a newly created organization entity or None
    """

    if self.data.organization:
      form = OrgProfileForm(self.data.POST, instance=self.data.organization)
    else:
      form = OrgCreateProfileForm(self.data.POST)

    if not form.is_valid():
      return None

    if not self.data.organization:
      org_id = self.data.GET['org_id']
      form.cleaned_data['founder'] = self.data.user
      form.cleaned_data['scope'] = self.data.program
      form.cleaned_data['scope_path'] = self.data.program.key().name() 
      form.cleaned_data['link_id'] = org_id
      key_name = '%s/%s' % (self.data.program.key().name(), org_id)
      entity = form.create(key_name=key_name)
      self.data.profile.org_admin_for.append(entity.key())
      self.data.profile.mentor_for.append(entity.key())
      self.data.profile.is_mentor = True
      self.data.profile.is_org_admin = True
      self.data.profile.put()
    else:
      entity = form.save()

    return entity

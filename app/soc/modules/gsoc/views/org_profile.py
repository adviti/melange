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

"""Module for the GSoC organization profile page.
"""


from soc.views import forms

from django import forms as django_forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.views.helper import url_patterns
from soc.views import org_profile

from soc.modules.gsoc.logic import cleaning as gsoc_cleaning
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.base_templates import LoggedInMsg
from soc.modules.gsoc.views import forms as gsoc_forms
from soc.modules.gsoc.views.helper.url_patterns import url

PROFILE_EXCLUDE = org_profile.PROFILE_EXCLUDE + [
    'proposal_extra',
]

class OrgProfileForm(org_profile.OrgProfileForm):
  """Django form for the organization profile.
  """

  def __init__(self, *args, **kwargs):
    super(OrgProfileForm, self).__init__(
        gsoc_forms.GSoCBoundField, *args, **kwargs)

    instance = self.instance

    field = self.fields['nonreq_proposal_extra']
    field.group = ugettext("4. Organization Preferences")
    field.initial = ', '.join(instance.proposal_extra) if instance else ''

  class Meta:
    model = GSoCOrganization
    css_prefix = 'gsoc_org_page'
    exclude = PROFILE_EXCLUDE
    widgets = forms.choiceWidgets(GSoCOrganization,
        ['contact_country', 'shipping_country'])

  nonreq_proposal_extra = django_forms.CharField(
      label='Extra columns', required=False)
  nonreq_proposal_extra.help_text = ugettext('Comma separated list of values.')

  tags = django_forms.CharField(label='Tags')
  clean_tags = gsoc_cleaning.cleanTagsList(
      'tags', gsoc_cleaning.COMMA_SEPARATOR)

  def clean_nonreq_proposal_extra(self):
    values = self.cleaned_data['nonreq_proposal_extra']
    splitvalues = values.split(',')

    for value in splitvalues:
      if ' ' not in value.strip():
        continue

      raise django_forms.ValidationError(
          "Spaces not allowed in extra column mames.")

    return values

  def clean(self):
    if 'nonreq_proposal_extra' not in self.cleaned_data:
      return

    value = self.cleaned_data['nonreq_proposal_extra']

    if not value:
      self.cleaned_data['proposal_extra'] = []
    else:
      cols = [i.strip() for i in value.split(',') if i.strip()]
      self.cleaned_data['proposal_extra'] = cols

    return self.cleaned_data

  def clean_max_score(self):
    max_score = self.cleaned_data['max_score']
    if 1 <= max_score <= 12:
      return max_score
    raise django_forms.ValidationError("Specify a value between 1 and 12.")

  def templatePath(self):
    return gsoc_forms.TEMPLATE_PATH


class OrgCreateProfileForm(OrgProfileForm):
  """Django form to create the organization profile.
  """

  class Meta:
    model = GSoCOrganization
    css_prefix = 'gsoc_org_page'
    exclude = PROFILE_EXCLUDE
    widgets = forms.choiceWidgets(GSoCOrganization,
        ['contact_country', 'shipping_country'])


class OrgProfilePage(RequestHandler):
  """View for the Organization Profile page.
  """

  def djangoURLPatterns(self):
    return [
         url(r'profile/organization/%s$' % url_patterns.PROGRAM,
         self, name='create_gsoc_org_profile'),
         url(r'profile/organization/%s$' % url_patterns.ORG,
         self, name='edit_gsoc_org_profile'),
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
      self.check.fail("Org creation is not supported at this time")

  def templatePath(self):
    return 'v2/modules/gsoc/org_profile/base.html'

  def context(self):
    if not self.data.organization:
      form = OrgCreateProfileForm(self.data.POST or None)
    else:
      form = OrgProfileForm(self.data.POST or None,
                            instance=self.data.organization)

    if self.data.organization.org_tag:
      tags = self.data.organization.tags_string(self.data.organization.org_tag)
      form.fields['tags'].initial = tags

    context = {
        'page_name': "Organization profile",
        'form_top_msg': LoggedInMsg(self.data, apply_link=False),
        'forms': [form],
        'error': bool(form.errors),
        }

    r = self.data.redirect.organization()
    context['org_home_page_link'] = r.urlOf('gsoc_org_home')
    if (self.data.program.allocations_visible and
          self.data.timeline.beforeStudentsAnnounced()):
      context['slot_transfer_page_link'] = r.urlOf('gsoc_slot_transfer')

    return context

  def post(self):
    org_profile = self.createOrgProfileFromForm()
    if org_profile:
      self.redirect.organization(org_profile)
      self.redirect.to('edit_gsoc_org_profile', validated=True)
    else:
      self.get()

  def putWithOrgTags(self, form, entity):
    fields = form.cleaned_data

    entity.org_tag = {
        'tags': fields['tags'],
        'scope': entity.scope if entity else fields['scope']
    }

    entity.put()

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
      form.cleaned_data['founder'] = self.data.user
      form.cleaned_data['scope'] = self.data.program
      form.cleaned_data['scope_path'] = self.data.program.key().name() 
      key_name = '%s/%s' % (
          self.data.program.key().name(),
          form.cleaned_data['link_id']
          )
      entity = form.create(commit=False, key_name=key_name)
      self.putWithOrgTags(form, entity)
      self.data.profile.org_admin_for.append(entity.key())
      self.data.profile.put()
    else:
      entity = form.save(commit=False)
      self.putWithOrgTags(form, entity)

    return entity

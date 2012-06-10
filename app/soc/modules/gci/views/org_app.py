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

"""Module for the GCI Organization application.
"""


import logging

from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic.exceptions import BadRequest
from soc.models.org_app_record import OrgAppRecord
from soc.views import org_app
from soc.views.helper import access_checker
from soc.views.helper import url_patterns

from soc.modules.gci.logic import org_app as org_app_logic
from soc.modules.gci.views import forms as gci_forms
from soc.modules.gci.views.base import RequestHandler
from soc.modules.gci.views.helper.url_patterns import url


class GCIOrgAppEditPage(RequestHandler):
  """View for creating/editing organization application.
  """

  def djangoURLPatterns(self):
    return [
         url(r'org/application/edit/%s$' % url_patterns.PROGRAM,
             self, name='gci_edit_org_app'),
    ]

  def checkAccess(self):
    self.check.isHost()
    self.mutator.orgAppFromKwargs(raise_not_found=False)

  def templatePath(self):
    return 'v2/modules/gci/org_app/edit.html'

  def context(self):
    if self.data.org_app:
      form = gci_forms.OrgAppEditForm(
          self.data.POST or None, instance=self.data.org_app)
    else:
      form = gci_forms.OrgAppEditForm(self.data.POST or None)

    if self.data.org_app:
      page_name = ugettext('Edit - %s' % (self.data.org_app.title))
    else:
      page_name = 'Create new organization application'

    context = {
        'page_name': page_name,
        'post_url': self.redirect.program().urlOf('gci_edit_org_app'),
        'forms': [form],
        'error': bool(form.errors),
        }

    return context

  def orgAppFromForm(self):
    """Create/edit the organization application entity from form.

    Returns:
      a newly created or updated organization application entity or None.
    """
    if self.data.org_app:
      form = gci_forms.OrgAppEditForm(
          self.data.POST, instance=self.data.org_app)
    else:
      form = gci_forms.OrgAppEditForm(self.data.POST)

    if not form.is_valid():
      return None

    form.cleaned_data['modified_by'] = self.data.user

    if not self.data.org_app:
      form.cleaned_data['created_by'] = self.data.user
      form.cleaned_data['program'] = self.data.program
      key_name = 'gci_program/%s/orgapp' % self.data.program.key().name()
      entity = form.create(key_name=key_name, commit=True)
    else:
      entity = form.save(commit=True)

    return entity

  def post(self):
    org_app = self.orgAppFromForm()
    if org_app:
      r = self.redirect.program()
      r.to('gci_edit_org_app', validated=True)
    else:
      self.get()


class GCIOrgAppPreviewPage(RequestHandler):
  """View for organizations to submit their application.
  """

  def djangoURLPatterns(self):
    return [
         url(r'org/application/preview/%s$' % url_patterns.PROGRAM,
             self, name='gci_preview_org_app'),
    ]

  def checkAccess(self):
    self.check.isHost()
    self.mutator.orgAppFromKwargs(raise_not_found=False)

  def templatePath(self):
    return 'v2/modules/gci/org_app/take.html'

  def context(self):
    form = gci_forms.OrgAppTakeForm(
        self.data.org_app, self.data.program.org_admin_agreement.content)

    context = {
        'page_name': '%s' % (self.data.org_app.title),
        'forms': [form],
        'error': bool(form.errors),
        }

    return context


class GCIOrgAppTakePage(RequestHandler):
  """View for organizations to submit their application.
  """

  def djangoURLPatterns(self):
    return [
         url(r'org/application/%s$' % url_patterns.PROGRAM,
             self, name='gci_take_org_app'),
         url(r'org/application/%s$' % url_patterns.ID,
             self, name='gci_retake_org_app'),
    ]

  def checkAccess(self):
    self.mutator.orgAppFromKwargs()
    self.mutator.orgAppRecordIfIdInKwargs()
    assert access_checker.isSet(self.data.org_app)

    # FIXME: There will never be organization in kwargs
    show_url = None
    if 'organization' in self.kwargs:
      show_url = self.data.redirect.organization().urlOf('gci_show_org_app')

    self.check.isSurveyActive(self.data.org_app, show_url)

    if self.data.org_app_record:
      self.check.canRetakeOrgApp()
    else:
      self.check.canTakeOrgApp()

  def templatePath(self):
    return 'v2/modules/gci/org_app/take.html'

  def _getTOSContent(self):
    return self.data.program.org_admin_agreement.content if \
        self.data.program.org_admin_agreement else ''

  def context(self):
    if self.data.org_app_record:
      form = gci_forms.OrgAppTakeForm(self.data.org_app, self._getTOSContent(),
          self.data.POST or None, instance=self.data.org_app_record)
    else:
      form = gci_forms.OrgAppTakeForm(self.data.org_app, self._getTOSContent(),
          self.data.POST or None)

    context = {
        'page_name': '%s' % (self.data.org_app.title),
        'forms': [form],
        'error': bool(form.errors),
        }

    return context

  def recordOrgAppFromForm(self):
    """Create/edit a new student evaluation record based on the form input.

    Returns:
      a newly created or updated evaluation record entity or None
    """
    if self.data.org_app_record:
      form = gci_forms.OrgAppTakeForm(
          self.data.org_app, self._getTOSContent(),
          self.data.POST, instance=self.data.org_app_record)
    else:
      form = gci_forms.OrgAppTakeForm(
          self.data.org_app, self._getTOSContent(), self.data.POST)

    if not form.is_valid():
      return None

    if not self.data.org_app_record:
      form.cleaned_data['user'] = self.data.user
      form.cleaned_data['main_admin'] = self.data.user
      form.cleaned_data['survey'] = self.data.org_app
      entity = form.create(commit=True)
    else:
      entity = form.save(commit=True)

    return entity

  def post(self):
    org_app_record = self.recordOrgAppFromForm()
    if org_app_record:
      r = self.redirect.id(org_app_record.key().id())
      r.to('gci_retake_org_app', validated=True)
    else:
      self.get()


class GCIOrgAppRecordsList(org_app.OrgAppRecordsList, RequestHandler):
  """View for listing all records of a GCI Organization application.
  """

  def __init__(self, *args, **kwargs):
    RequestHandler.__init__(self, *args, **kwargs)
    org_app.OrgAppRecordsList.__init__(self, 'gci_show_org_app')

  def djangoURLPatterns(self):
    return [
         url(
             r'org/application/records/%s$' % url_patterns.PROGRAM,
             self, name='gci_list_org_app_records')
         ]

  def post(self):
    """Edits records from commands received by the list code.
    """
    post_data = self.request.POST

    if not post_data.get('button_id', None) == 'save':
      raise BadRequest('No valid POST data found')

    data = self.data.POST.get('data')
    if not data:
      raise BadRequest('Missing data')

    parsed = simplejson.loads(data)
    self.data.redirect.program()
    url = self.data.redirect.urlOf('create_gci_org_profile', full=True)

    for id, properties in parsed.iteritems():
      record = OrgAppRecord.get_by_id(long(id))

      if not record:
        logging.warning('%s is an invalid OrgAppRecord ID' %id)
        continue

      if record.survey.key() != self.data.org_app.key():
        logging.warning('%s is not a record for the Org App in the URL' %record.key())
        continue

      new_status = properties['status']
      org_app_logic.setStatus(self.data, record, new_status, url)

    self.response.set_status(200)


class OrgAppReadOnlyTemplate(org_app.OrgAppReadOnlyTemplate):
  """Template to construct readonly organization application record.
  """

  template_path = 'v2/modules/gci/org_app/readonly_template.html'


class GCIOrgAppShowPage(RequestHandler):
  """View to display the readonly page for organization application.
  """

  def djangoURLPatterns(self):
    return [
        url(r'org/application/show/%s$' % url_patterns.ID,
            self, name='gci_show_org_app'),
    ]

  def checkAccess(self):
    self.mutator.orgAppFromKwargs()
    self.mutator.orgAppRecordIfIdInKwargs()
    assert access_checker.isSet(self.data.org_app_record)

    self.check.canViewOrgApp()

  def templatePath(self):
    return 'v2/modules/gci/org_app/show.html'

  def context(self):
    record = self.data.org_app_record

    context = {
        'page_name': 'Organization application - %s' % (record.name),
        'organization': record.name,
        'css_prefix': OrgAppReadOnlyTemplate.Meta.css_prefix,
        }

    if record:
      context['record'] = OrgAppReadOnlyTemplate(record)

    return context

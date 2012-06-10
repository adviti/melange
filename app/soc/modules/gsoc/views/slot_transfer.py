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

"""Module for the GSoC slot transfer page.
"""


from google.appengine.ext import db

from django import forms as django_forms

from soc.logic import cleaning
from soc.logic import host as host_logic
from soc.logic.exceptions import RedirectRequest
from soc.logic.helper import notifications
from soc.tasks import mailer
from soc.views import forms
from soc.views import readonly_template
from soc.views.helper import url_patterns

from soc.modules.gsoc.models.slot_transfer import GSoCSlotTransfer

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper.url_patterns import url


class SlotTransferForm(forms.ModelForm):
  """Django form for the slot transfer page.
  """

  def __init__(self, max_slots, *args, **kwargs):
    super(SlotTransferForm, self).__init__(*args, **kwargs)
    choices = [('None', self.fields['nr_slots'].label)] + [
        (i, i) for i in range(1, max_slots + 1)]
    self.fields['nr_slots'].widget = django_forms.widgets.Select(
        choices=choices)

  class Meta:
    model = GSoCSlotTransfer
    css_prefix = 'gsoc_slot_transfer'
    exclude = ['status', 'created_on', 'last_modified_on',
               'program', 'admin_remarks']

  clean_remarks = cleaning.clean_html_content('remarks')


class SlotTransferReadOnlyTemplate(readonly_template.ModelReadOnlyTemplate):
  """Template to display readonly information from previous requests.
  """

  template_path = 'v2/modules/gsoc/slot_transfer/_readonly_template.html'

  def __init__(self, counter, *args, **kwargs):
    super(SlotTransferReadOnlyTemplate, self).__init__(*args, **kwargs)
    self.counter = counter

  class Meta:
    model = GSoCSlotTransfer
    css_prefix = 'gsoc_slot_transfer'
    exclude = ['program']


class SlotTransferPage(RequestHandler):
  """View for transferring the slots.
  """

  def djangoURLPatterns(self):
    return [
        url(r'slots/transfer/%s$' % url_patterns.ORG,
            self, name='gsoc_slot_transfer'),
    ]

  def checkAccess(self):
    self.check.isLoggedIn()
    self.check.isProgramVisible()
    self.check.isOrganizationInURLActive()
    self.check.isOrgAdminForOrganization(self.data.organization)

    self.check.isSlotTransferActive()
    self.mutator.slotTransferEntities()
    if not self.data.slot_transfer_entities:
      if 'new' not in self.data.kwargs:
        r = self.data.redirect
        new_url = r.organization().urlOf('gsoc_update_slot_transfer')
        raise RedirectRequest(new_url)

  def templatePath(self):
    return 'v2/modules/gsoc/slot_transfer/base.html'

  def context(self):
    requests = []
    require_new_link = True
    for i, ent in enumerate(self.data.slot_transfer_entities):
      requests.append(SlotTransferReadOnlyTemplate(i, instance=ent))
      if ent.status == 'pending':
        require_new_link = False

    context = {
        'page_name': 'Transfer slots to pool',
        'requests': requests,
        }

    if (self.data.program.allocations_visible and
        self.data.timeline.beforeStudentsAnnounced()):
      r = self.data.redirect.organization()
      edit_url = r.urlOf('gsoc_update_slot_transfer')
      if require_new_link:
        context['new_slot_transfer_page_link'] = edit_url
      else:
        context['edit_slot_transfer_page_link'] = edit_url

    return context


class UpdateSlotTransferPage(RequestHandler):
  """View for transferring the slots.
  """

  def djangoURLPatterns(self):
    return [
        url(r'slots/transfer/update/%s$' % url_patterns.ORG,
            self, name='gsoc_update_slot_transfer'),
    ]

  def checkAccess(self):
    self.check.isLoggedIn()
    self.check.isProgramVisible()
    self.check.isOrganizationInURLActive()
    self.check.isOrgAdminForOrganization(self.data.organization)

    self.check.isSlotTransferActive()
    self.mutator.slotTransferEntities()

  def templatePath(self):
    return 'v2/modules/gsoc/slot_transfer/form.html'

  def context(self):
    slots = self.data.organization.slots

    if self.data.POST:
      slot_transfer_form = SlotTransferForm(slots, self.data.POST)
    else:
      slot_transfer_form = SlotTransferForm(slots)

    for ent in self.data.slot_transfer_entities:
      if ent.status == 'pending':
        if self.data.POST:
          slot_transfer_form = SlotTransferForm(slots, self.data.POST,
                                                instance=ent)
        else:
          slot_transfer_form = SlotTransferForm(slots,
                                                instance=ent)

    context = {
        'page_name': 'Transfer slots to pool',
        'form_header_msg': 'Transfer the slots to the pool',
        'forms': [slot_transfer_form],
        }

    r = self.data.redirect.organization()
    context['org_home_page_link'] = r.urlOf('gsoc_org_home')
    context['slot_transfer_page_link'] = r.urlOf('gsoc_slot_transfer')

    return context

  def createOrUpdateFromForm(self):
    """Creates a new proposal based on the data inserted in the form.

    Returns:
      a newly created proposal entity or None
    """
    slot_transfer_entity = None

    slot_transfer_form = SlotTransferForm(self.data.organization.slots,
                                          self.data.POST)

    if not slot_transfer_form.is_valid():
      return None

    slot_transfer_form.cleaned_data['program'] = self.data.program

    for ent in self.data.slot_transfer_entities:
      if ent.status == 'pending':
        slot_transfer_entity = ent
        break

    host_entities = host_logic.getHostsForProgram(self.data.program)
    to_emails = [i.parent().account.email() for i in host_entities
                 if i.notify_slot_transfer]

    def create_or_update_slot_transfer_trx():
      update = False
      if slot_transfer_entity:
        slot_transfer = db.get(slot_transfer_entity.key())
        slot_transfer_form.instance = slot_transfer
        slot_transfer = slot_transfer_form.save(commit=True)

        update = True
      else:
        slot_transfer = slot_transfer_form.create(
            commit=True, parent=self.data.organization)

      context = notifications.createOrUpdateSlotTransferContext(
          self.data, slot_transfer,
          to_emails, update)
      sub_txn = mailer.getSpawnMailTaskTxn(
          context, parent=slot_transfer.parent())
      sub_txn()

      return slot_transfer

    return db.run_in_transaction(create_or_update_slot_transfer_trx)

  def post(self):
    """Handler for HTTP POST request.
    """

    slot_transfer_entity = self.createOrUpdateFromForm()
    if slot_transfer_entity:
      self.redirect.organization(self.data.organization)
      self.redirect.to('gsoc_update_slot_transfer', validated=True)
    else:
      self.get()

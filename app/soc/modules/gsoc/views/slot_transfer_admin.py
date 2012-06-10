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

"""Module for the GSoC slot transfer admin page.
"""


import logging

from google.appengine.ext import db

from django.utils import simplejson

from soc.logic.exceptions import AccessViolation
from soc.logic.exceptions import BadRequest
from soc.views.helper import lists
from soc.views.helper import url_patterns
from soc.views.template import Template

from soc.modules.gsoc.models.slot_transfer import GSoCSlotTransfer
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper.url_patterns import url


class SlotsTransferAdminList(Template):
  """Template for list of slot transfer requests.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data

    list_config = lists.ListConfiguration()
    # hidden key
    list_config.addColumn(
        'full_transfer_key', 'Full slot transfer key',
        (lambda ent, *args: str(ent.key())), hidden=True)
    list_config.addColumn(
        'org', 'Organization',
        (lambda e, *args: e.parent().short_name.strip()), width=75)
    options = [('', 'All'), ('pending', 'Pending'),
               ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    list_config.addSimpleColumn('status', 'Status', width=40, options=options)
    list_config.addSimpleColumn('remarks', 'Remarks', width=75)
    list_config.addSimpleColumn('nr_slots', 'Returned slots', width=50)
    list_config.setColumnEditable('nr_slots', True)
    list_config.addSimpleColumn('admin_remarks', 'Admin remarks')
    list_config.setColumnEditable('admin_remarks', True) #, edittype='textarea')
    list_config.addColumn(
        'slots_desired', 'Min desired', 
        (lambda e, *args: e.parent().slots_desired), width=25, hidden=True)
    list_config.addColumn(
        'max_slots_desired', 'Max desired',
        (lambda e, *args: e.parent().max_slots_desired), width=25, hidden=True)
    list_config.addColumn(
        'slots', 'Slots',
        (lambda e, *args: e.parent().slots), width=50, hidden=True)
    list_config.setDefaultPagination(False)
    list_config.setDefaultSort('org')
    list_config.addPostEditButton('save', "Save", "",
                                  ['full_transfer_key'], refresh="none")

    bounds = [1,'all']
    keys = ['key', 'full_transfer_key']
    list_config.addPostButton('accept', "Accept", "", bounds, keys)
    list_config.addPostButton('reject', "Reject", "", bounds, keys)

    self._list_config = list_config

  def context(self):
    description = 'List of slot transfer requests for the program %s' % (
            self.data.program.name)

    list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0, description)

    return {
        'lists': [list],
    }

  def post(self):
    idx = lists.getListIndex(self.request)
    if idx != 0:
      return False

    data = self.data.POST.get('data')

    button_id = self.data.POST.get('button_id')

    if not data:
      raise BadRequest("Missing data")

    parsed = simplejson.loads(data)

    if button_id == 'accept':
      return self.postAccept(parsed, True)

    if button_id == 'reject':
      return self.postAccept(parsed, False)
  
    if button_id == 'save':
      return self.postSave(parsed)

  def postAccept(self, data, accept):
    for properties in data:
      if 'full_transfer_key' not in properties:
        logging.warning("Missing key in '%s'" % properties)
        continue

      slot_transfer_key = properties['full_transfer_key']
      def accept_slot_transfer_txn():
        slot_transfer = db.get(slot_transfer_key)

        if not slot_transfer:
          logging.warning("Invalid slot_transfer_key '%s'" % 
                          slot_transfer_key)
          return

        org = slot_transfer.parent()
        if not org:
          logging.warning("No organization present for the slot transfer %s" %
                          slot_transfer_key)
          return

        if accept:
          if slot_transfer.status == 'accepted':
            return

          slot_transfer.status = 'accepted'

          if slot_transfer.nr_slots < 0:
            logging.warning("Organization %s is trying to trick us to "
                "gain more slots by using a negative number %s" %
                (org.name, slot_transfer.nr_slots))
            return

          org.slots -= slot_transfer.nr_slots
          if org.slots < 0:
            org.slots = 0

          org.put()
        else:
          if slot_transfer.status == 'rejected':
            return
          slot_transfer.status = 'rejected'
        slot_transfer.put()

      db.run_in_transaction(accept_slot_transfer_txn)

    return True

  def postSave(self, parsed):

    for key_name, properties in parsed.iteritems():
      admin_remarks = properties.get('admin_remarks')
      nr_slots = properties.get('nr_slots')
      full_transfer_key = properties.get('full_transfer_key')

      if not full_transfer_key:
        logging.warning(
            "key for the slot transfer request is not present '%s'" %
            properties)
        continue

      if 'admin_remarks' not in properties and 'nr_slots' not in properties:
        logging.warning(
            "Neither admin remarks or number of slots present in '%s'" %
            properties)
        continue

      if 'nr_slots' in properties:
        if not nr_slots.isdigit():
          logging.warning("Non-int value for slots: '%s'" %nr_slots)
          properties.pop('nr_slots')
        else:
          nr_slots = int(nr_slots)

      def update_org_txn():
        slot_transfer =  db.get(full_transfer_key)
        if not slot_transfer:
          logging.warning("Invalid slot_transfer_key '%s'" % key_name)
          return
        if 'admin_remarks' in properties:
          slot_transfer.admin_remarks = admin_remarks
        if 'nr_slots' in properties:
          slot_transfer.nr_slots = nr_slots
        slot_transfer.put()

      db.run_in_transaction(update_org_txn)

    return True

  def getListData(self):
    idx = lists.getListIndex(self.request)
    if idx != 0:
      return None

    q = GSoCSlotTransfer.all().filter('program', self.data.program)

    starter = lists.keyStarter
    prefetcher = lists.modelPrefetcher(GSoCSlotTransfer, [], parent=True)

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, starter, prefetcher=prefetcher)

    return response_builder.build()

  def templatePath(self):
    return "v2/modules/gsoc/slot_transfer_admin/_list.html"


class SlotsTransferAdminPage(RequestHandler):
  """View for the the list of slot transfer requests.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/slots/transfer/%s$' % url_patterns.PROGRAM,
         self, name='gsoc_admin_slots_transfer'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/slot_transfer_admin/base.html'

  def jsonContext(self):
    list_content = SlotsTransferAdminList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')

    return list_content.content()

  def post(self):
    slots_list = SlotsTransferAdminList(self.request, self.data)

    if not slots_list.post():
      raise AccessViolation(
          'You cannot change this data')

  def context(self):
    return {
      'page_name': 'Slots transfer action page',
      'slot_transfer_list': SlotsTransferAdminList(self.request, self.data),
    }

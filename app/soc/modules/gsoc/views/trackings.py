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

"""Module contains forms and views for shipment and payment trackings.
"""

__authors__ = [
    '"Orcun Avsar" <orc.avs@gmail.com>',
  ]


from google.appengine.api import taskqueue

from django.utils import simplejson
from django.utils.dateformat import format

from soc.modules.gsoc.views import forms
from soc.views.helper import lists
from soc.views.template import Template
from soc.logic.exceptions import AccessViolation
from soc.views.helper.gdata_apis import oauth as oauth_helper
from soc.views.helper.gdata_apis import docs as gdocs_helper

from soc.modules.gsoc.views.base import RequestHandler
from soc.views.helper import url_patterns
from soc.modules.gsoc.views.helper.url_patterns import url
from soc.modules.gsoc.models.trackings import ShipmentInfo
from soc.modules.gsoc.tasks.trackings import ShipmentSyncTask


DATETIME_FORMAT = 'jS F Y H:i:s'


class ShipmentInfoForm(forms.GSoCModelForm):
  """Form for editing ShipmentInfo objects.
  """

  class Meta:
    model = ShipmentInfo
    exclude = ['status', 'last_sync_time']


class EditShipmentInfo(RequestHandler):
  """Admin view for editing shipment info.
  """

  def __init__(self, *args, **kwargs):
    super(EditShipmentInfo, *args, **kwargs)

    self._shipment_info = None

  def djangoURLPatterns(self):
    return [
        url(r'admin/trackings/shipment_info/edit/%s' %
            url_patterns.namedIdBasedPattern(['sponsor', 'program']),
            self, name='edit_shipment_info')
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/form_base.html'

  def _getShipmentInfo(self):
    if not self._shipment_info:
      id = int(self.data.kwargs['id'])
      self._shipment_info= ShipmentInfo.get_by_id(
          id, parent=self.data.program)

    return self._shipment_info

  def context(self):
    shipment_info = self._getShipmentInfo()
    form = ShipmentInfoForm(self.data.POST or None, instance=shipment_info)
    error = bool(form.errors)

    context = {
        'forms': [form],
        'page_name': 'Update Shipment Information',
        'error': error,
    }
    return context

  def post(self):
    shipment_info = self._getShipmentInfo()
    form = ShipmentInfoForm(
        self.data.POST, instance=shipment_info)
    error = bool(form.errors)
    if not error:
      shipment_info = form.save(commit=True)
      self.redirect.id(shipment_info.key().id())
      self.redirect.to('edit_shipment_info')
    else:
      self.get()


class CreateShipmentInfo(RequestHandler):
  """Admin view for creating a shipment info.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/trackings/shipment_info/create/%s$' % \
            url_patterns.PROGRAM,
            self, name='create_shipment_info'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/form_base.html'

  def context(self):
    form = ShipmentInfoForm(self.data.POST or None)
    error = bool(form.errors)
    context = {
        'forms': [form],
        'page_name': 'Create Shipment Information',
        'error': error,
    }
    return context

  def post(self):
    form = ShipmentInfoForm(self.data.POST)
    error = bool(form.errors)
    if not error:
      shipment_info = form.create(commit=True,
                                  parent=self.data.program)

    self.redirect.id(shipment_info.key().id())
    self.redirect.to('edit_shipment_info')


class ShipmentInfoList(Template):
  """Template for the list of ShipmentInfo objects.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data

    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('name', 'Name')
    list_config.addSimpleColumn('status', 'Status')
    list_config.addColumn(
        'last_sync_time', 'Last Sync Time',
        lambda ent, *args: format(
          ent.last_sync_time, DATETIME_FORMAT) if \
          ent.last_sync_time else 'N/A')

    self._list_config = list_config

    def rowAction(entity, *args):
      entity_id = entity.key().id()
      url = data.redirect.id(entity_id).urlOf('edit_shipment_info')
      return url

    self._list_config.setRowAction(rowAction)

  def templatePath(self):
    return 'v2/modules/gsoc/admin/trackings/_list.html'

  def context(self):
    description = 'List of shipment informations for %s' % \
                  self.data.program.name

    list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0, description)
    return {
        'list_name': 'Shipment Informations',
        'lists': [list],
    }

  def getListData(self):
    idx = lists.getListIndex(self.request)
    if idx != 0:
      return None

    q = ShipmentInfo.all().ancestor(self.data.program)
    starter = lists.keyStarter
    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q, starter)

    return response_builder.build()


class ShipmentInfoListPage(RequestHandler):
  """Admin view for listing all shipment infos for a specific program.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/trackings/shipment_info/records/%s' %
            url_patterns.PROGRAM,
            self, name='shipment_info_records'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/admin/trackings/records.html'

  def context(self):
    context = {
        'page_name': 'Shipment informations for %s' % self.data.program.name,
        'list': ShipmentInfoList(self.request, self.data),
    }
    return context

  def jsonContext(self):
    list_content = ShipmentInfoList(self.request, self.data).getListData()
    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()


class SyncData(RequestHandler):
  """Admin view that shows syncing tasks.
  """

  DEF_BATCH_SIZE = 100

  def djangoURLPatterns(self):
    return [
        url(r'admin/trackings/sync_data/%s$' % url_patterns.PROGRAM,
            self, name='trackings_sync_data'),
    ]

  def checkAccess(self):
    self.check.isHost()
    self.check.canAccessGoogleDocs()

  def templatePath(self):
    return 'v2/modules/gsoc/admin/trackings/sync_data.html'

  def context(self):
    query = ShipmentInfo.all().ancestor(self.data.program)
    shipment_infos = query.fetch(self.DEF_BATCH_SIZE)
    self.redirect.program()
    return {
        'page_name': 'Sync Trackings Data for %s' % self.data.program.name,
        'shipment_infos': shipment_infos,
        'start_shipment_sync_url': self.redirect.urlOf('start_shipment_sync'),
    }


class StartShipmentSync(RequestHandler):
  """Start a sync task for the specified shipment info.

  Uses user's access token to export target spreadsheet. Then, starts
  the task with the exported content.
  """

  def djangoURLPatterns(self):
    return [
        url(r'admin/trackings/start_shipment_sync/%s$' % url_patterns.PROGRAM,
            self, name='start_shipment_sync'),
    ]

  def checkAccess(self):
    self.check.isHost()
    self.check.canAccessGoogleDocs()

  def post(self):
    service = oauth_helper.createDocsServiceWithAccessToken(self.data)

    shipment_info_id = self.data.POST['id']
    shipment_info = ShipmentInfo.get_by_id(
        int(shipment_info_id), parent=self.data.program)

    link = shipment_info.spreadsheet_link
    resource_key = gdocs_helper.get_resource_key_from_document_link(link)
    resource_id = 'spreadsheet:%s' % resource_key

    #get sheet content for USA students
    usa_sheet_content = gdocs_helper.get_content(
        service, resource_id, return_as='csv', gid=0)

    #get sheet content for international students
    intl_sheet_content = gdocs_helper.get_content(
        service, resource_id, return_as='csv', gid=3)

    task_start_url = self.redirect.urlOf('shipment_sync_task_start')

    #start task for USA students
    params = {
        'program_key': str(self.data.program.key()),
        'sheet_content': simplejson.dumps(usa_sheet_content),
        'sheet_type': 'usa',
        'shipment_info_id': shipment_info_id,
    }
    taskqueue.add(url=task_start_url, params=params)

    #start task for international students
    params = {
        'program_key': str(self.data.program.key()),
        'sheet_content': simplejson.dumps(intl_sheet_content),
        'sheet_type': 'intl',
        'shipment_info_id': shipment_info_id,
    }
    taskqueue.add(url=task_start_url, params=params)

    #return back to sync data page
    self.redirect.program()
    self.redirect.to('trackings_sync_data')

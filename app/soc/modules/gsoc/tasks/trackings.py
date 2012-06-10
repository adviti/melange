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

"""Tasks related to syncing shipment and payment trackings data.
"""

__authors__ = [
  '"Orcun Avsar" <orc.avs@gmail.com>',
  ]


import re
import datetime
import logging
import StringIO
import csv

from django import http
from django.utils import simplejson
from django.conf.urls.defaults import url as django_url

from google.appengine.api import taskqueue
from google.appengine.ext import db
from google.appengine.runtime import DeadlineExceededError

from soc.logic import dicts
from soc.logic.exceptions import Error
from soc.tasks import responses
from soc.tasks.helper.timekeeper import Timekeeper
from soc.views.helper.request_data import RedirectHelper

from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.trackings import ShipmentInfo
from soc.modules.gsoc.models.shipment import StudentShipment


DATE_SHIPPED_FORMAT = '%Y-%m-%d'


class ColumnNotFoundError(Error):
  """Error to be raised when an expected column is not found in the row.
  """

  pass


class SyncTask(object):
  """Base class for sync tasks.
  """

  def findColumnIndexes(self, first_row, expected_columns):
    """Find column indexes in the first row for expected columns.

    Args:
      first_row: List for raw header row data of the sheet. Each element
                 of the list will be turned into variable like names.
                 e.g. 'Shipment Address 2 (35)' turns to 'shipment_address_2'
      expected_columns: List of expected columns in the first row. All
                        elements of the list are expected to be found in the
                        first row.
    """
    column_indexes = {}

    #sluggify first row elements (columns) into variable like names
    new_first_row = []
    for column_name in first_row:
      #lower characters: 'Shipment Address 2' > 'shipment address 2 (35)'
      column_name = column_name.lower()
      #remove paranthesis: 'address 2 (35)' > 'address 2'
      column_name = re.sub(r'[(].*[)]', '', column_name).strip()
      #remove unwanted characters
      column_name = re.sub(r'[^a-z1-9_ ]', '', column_name).strip()
      #replace whitespaces with '_': 'address 2' > 'address_2'
      column_name = re.sub(r'[ ]', '_', column_name)

      new_first_row.append(column_name)

    first_row = new_first_row

    for column_name in expected_columns:
      try:
        column_index = first_row.index(column_name)
      except ValueError:
        msg = '%s not found in %s' % (str(column_name), str(first_row))
        raise ColumnNotFoundError, msg
      column_indexes[column_name] = column_index

    return column_indexes


  def getRowData(self, row, column_indexes):
    data = {}
    for column_name, column_index in column_indexes.items():
      data[column_name] = row[column_index]

    return data


class ShipmentSyncTask(SyncTask):
  """Request handlers syncing shipments trackings data.
  """

  #Expected columns for USA and international student sheets
  USA_EXPECTED_COLUMNS = ['link_id', 'tracking', 'date_shipped', 'notes',
                          'address_1', 'address_2', 'city', 'state', 'zip']

  INTL_EXPECTED_COLUMNS = ['link_id', 'tracking', 'date_shipped', 'notes',
                           'address_1', 'address_2', 'city', 'zippostal_code',
                           'country']

  def __init__(self, *args, **kwargs):
    super(ShipmentSyncTask, self).__init__()

    self.__program = None
    self.__shipment_info = None

  def djangoURLPatterns(self):
    """Returns the URL patterns for the tasks in this module
    """
    patterns = [
        django_url(r'^tasks/gsoc/trackings/sync/shipment/start$',
                   self.startShipmentSync,
                   name='shipment_sync_task_start'),
        django_url(r'^tasks/gsoc/trackings/sync/shipment/continue$',
                   self.continueShipmentSync,
                   name='shipment_sync_task_continue'),
    ]
    return patterns

  def setProgram(self, program_key):
    self.__program = db.get(db.Key(program_key))

  def setShipmentInfo(self, shipment_info_id):
    self.__shipment_info = ShipmentInfo.get_by_id(shipment_info_id,
                                                  parent=self.__program)

  def setShipmentInfoStatusToError(self):
    """Fallback function that sets shipment info status to 'error'.
    """
    shipment_info = self.__shipment_info
    if shipment_info:
      shipment_info.status = 'error'
      shipment_info.put()

  def startShipmentSync(self, request, *args, **kwargs):
    """Run _startShipmentSync while presuming an error for the fallback.
    """
    try:
      return self._startShipmentSync(request, *args, **kwargs)
    except Exception:
      self.setShipmentInfoStatusToError()
      raise

  def _startShipmentSync(self, request, *args, **kwargs):
    """Start syncing shipment data.

    POST Args:
      program_key: the key of the program which task is runnig for.
      sheet_content: sheet content data in JSON format.
      sheet_type: 'usa' or 'intl'
      shipment_info_id: id of the shipment info object that task is running 
                        for.
    """
    params = dicts.merge(request.POST, request.GET)
    redirect = RedirectHelper(None, None)

    if 'program_key' not in params:
      logging.error("missing program_key in params: '%s'" % params)
      return responses.terminateTask()

    if 'sheet_content' not in params:
      logging.error("missing sheet_content in params: '%s'" % params)
      return responses.terminateTask()

    if 'sheet_type' not in params:
      logging.error("missing sheet_type in params: '%s'" % params)
      return responses.terminateTask()

    if 'shipment_info_id' not in params:
      logging.error("missing shipment_info_id in params: '%s'" % params)
      return responses.terminateTask()

    self.setProgram(params['program_key'])
    self.setShipmentInfo(int(params['shipment_info_id']))

    self.__shipment_info.status = 'syncing'
    self.__shipment_info.put()

    sheet_content = StringIO.StringIO(
        simplejson.loads(params['sheet_content']))
    sheet_type = params['sheet_type']

    sheet_rows = [row for row in csv.reader(sheet_content)]

    if sheet_type == 'usa':
      column_indexes = self.findColumnIndexes(
          sheet_rows[0], self.USA_EXPECTED_COLUMNS)

    elif sheet_type == 'intl':
      column_indexes = self.findColumnIndexes(
          sheet_rows[0], self.INTL_EXPECTED_COLUMNS)

    params = {
        'program_key': params['program_key'],
        'shipment_info_id': params['shipment_info_id'],
        'column_indexes': simplejson.dumps(column_indexes),
        'sheet_rows': simplejson.dumps(sheet_rows[1:]),
    }

    taskqueue.add(url=redirect.urlOf('shipment_sync_task_continue'),
                  params=params)
    return responses.terminateTask()

  def continueShipmentSync(self, request, *args, **kwargs):
    """Run _continueShipmentSync while presuming an error for the fallback.
    """
    try:
      return self._continueShipmentSync(request, *args, **kwargs)
    except Exception:
      self.setShipmentInfoStatusToError()
      raise

  def _continueShipmentSync(self, request, *args, **kwargs):
    """Continue syncing shipment data.

    POST Args:
      program_key: the key of the program which sync is being done for.
      shipment_info_id: id of the shipment info object that task is running
                        for.
      column_indexes: column indexes for specific columns in JSON format.
      sheet_rows: spreadsheets CSV chunk data in JSON format.
    """
    timekeeper = Timekeeper(20000)
    params = dicts.merge(request.POST, request.GET)
    redirect = RedirectHelper(None, None)

    if 'program_key' not in params:
      logging.error("missing program_key in params: '%s'" % params)
      return responses.terminateTask()

    if 'shipment_info_id' not in params:
      logging.error("missing shipment_info_id in params: '%s'" % params)
      return responses.terminateTask()

    self.setProgram(params['program_key'])
    self.setShipmentInfo(int(params['shipment_info_id']))

    if 'sheet_rows' not in params:
      logging.error("missing sheet_rows data in params: '%s'" % params)
      return responses.terminateTask()

    if 'column_indexes' not in params:
      logging.error("missing column_indexes data in params: '%s'" % params)
      return responses.terminateTask()

    column_indexes = simplejson.loads(params['column_indexes'])
    sheet_rows = simplejson.loads(params['sheet_rows'])

    try:
      for remain, row in timekeeper.iterate(sheet_rows):

        if len(row) < len(column_indexes):
          row.extend((len(column_indexes) - len(row)) * [''])
        data = self.getRowData(row, column_indexes)
        link_id = data['link_id']

        q = GSoCProfile.all().filter('scope', self.__program)
        q.filter('link_id', link_id)
        profile = q.get()

        if not profile:
          logging.error("Profile link_id '%s' for program '%s' is not found" %
                        (link_id, self.__program.name))
          continue #continue to next row

        if not profile.is_student:
          logging.error("Profile link_id '%s' is not a student" %
                        link_id)
          continue

        tracking = data['tracking']
        date_shipped = data['date_shipped']
        notes = data['notes']
        full_address = " ".join([
          data['address_1'], data['address_2'], data['city'],
          data.get('state', ''), data.get('zip', ''),
          data.get('zippostal_code', ''), data.get('country', '')
        ])
        self.updateShipmentDataForStudent(
            profile, tracking, date_shipped, notes, full_address)

    except DeadlineExceededError:
      if remain:
        remaining_rows = sheet_rows[(-1 * remain):]
        params = {
            'program_key': params.get('program_key'),
            'sheet_rows': simplejson.dumps(remaining_rows),
            'column_indexes': params.get('column_indexes'),
            'shipment_info_id': params.get('shipment_info_id'),
        }
        taskqueue.add(
            url=redirect.urlOf('shipment_sync_task_continue'), params=params)
        return responses.terminateTask()

    self.finishSync()
    return responses.terminateTask()

  def finishSync(self):
    shipment_info = self.__shipment_info
    shipment_info.last_sync_time = datetime.datetime.now()

    if shipment_info.status == 'syncing':
      shipment_info.status = 'half-complete'

    elif shipment_info.status == 'half-complete':
      shipment_info.status = 'idle'

    shipment_info.put()

  def updateShipmentDataForStudent(self, profile, tracking, date_shipped,
                                   notes, full_address):
    shipment_info = self.__shipment_info

    q = StudentShipment.all()
    q.filter('shipment_info', shipment_info)
    q.ancestor(profile)
    student_shipment = q.get()

    if not student_shipment:
      student_shipment = StudentShipment(shipment_info=shipment_info,
                                         parent=profile)

    student_shipment.tracking = tracking
    student_shipment.date_shipped = datetime.datetime.strptime(
        date_shipped, DATE_SHIPPED_FORMAT).date()
    student_shipment.notes = notes
    student_shipment.full_address = full_address
    student_shipment.put()

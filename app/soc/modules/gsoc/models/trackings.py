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

"""Module contains models for shipment and payment trackings information.
"""

__authors__ = [
  '"Orcun Avsar" <orc.avs@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext


class ShipmentInfo(db.Model):
  """Model for storing shipment infos created by program admin.

  Stores Google spreadsheets link that is used for syncing.
  """

  #: string property field for storing shipment name
  name = db.StringProperty(required=True,
                           verbose_name=ugettext('Name Of Shipment'))

  #: Google spreadsheet link for student shipments tracking
  spreadsheet_link = db.LinkProperty(
      required=True,
      verbose_name=ugettext('Spreadsheet Link'))
  spreadsheet_link.help_text = ugettext(
      'Link to your Google spreadsheet that holds shipment data.')

  #: status property for syncing
  status = db.StringProperty(required=True,
                             choices=['idle', 'syncing',
                                      'half-complete', 'error'],
                             default='idle')

  #: datetime property for storing last sync time
  last_sync_time = db.DateTimeProperty(required=False)

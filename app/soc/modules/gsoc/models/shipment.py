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

"""This module contains models for student shipments.
"""

__authors__ = [
  '"Orcun Avsar" <orc.avs@gmail.com>',
]


from google.appengine.ext import db

from soc.modules.gsoc.models.trackings import ShipmentInfo


class StudentShipment(db.Model):
  """Model for storing shipments for students.

  Parent is Profile entity of the student for whom shipment is sent.
  """

  #: string property indicates which shipment info this entity belongs to
  shipment_info = db.ReferenceProperty(reference_class=ShipmentInfo,
                                       required=True)

  #: string property holds tracking (number) property
  tracking = db.StringProperty(required=False)

  #: string property shows date of shipment
  date_shipped = db.DateProperty(required=False)

  #: string property holds notes about shipment
  notes = db.StringProperty(required=False)

  #: string property that holds shipment's full address that joins different
  #: address related columns of the spreadsheet row.
  full_address = db.TextProperty(required=False)

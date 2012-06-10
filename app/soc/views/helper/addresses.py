#!/usr/bin/env python2.5
#
# Copyright 2012 the Melange authors.
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

"""Module that contains utility functions associated with addresses.
"""

def addAddressColumns(list_config):
  """Adds address columns to the specified list config.

  Columns added:
    * res_street
    * res_street_extra
    * res_city
    * res_state
    * res_country
    * res_postalcode
    * phone
    * ship_name
    * ship_street
    * ship_street_extra
    * ship_city
    * ship_state
    * ship_country
    * ship_postalcode
    * tshirt_style
    * tshirt_size
  """
  list_config.addSimpleColumn('res_street', "res_street", hidden=True)
  list_config.addSimpleColumn('res_street_extra', "res_street_extra", hidden=True)
  list_config.addSimpleColumn('res_city', "res_city", hidden=True)
  list_config.addSimpleColumn('res_state', "res_state", hidden=True)
  list_config.addSimpleColumn('res_country', "res_country", hidden=True)
  list_config.addSimpleColumn('res_postalcode', "res_postalcode", hidden=True)
  list_config.addSimpleColumn('phone', "phone", hidden=True)
  list_config.addColumn(
      'ship_name', "ship_name",
      (lambda e, *args: e.shipping_name()), hidden=True)
  list_config.addColumn(
      'ship_street', "ship_street",
      (lambda e, *args: e.shipping_street()), hidden=True)
  list_config.addColumn(
      'ship_street_extra', "ship_street_extra",
      (lambda e, *args: e.shipping_street_extra()), hidden=True)
  list_config.addColumn(
      'ship_city', "ship_city",
      (lambda e, *args: e.shipping_city()), hidden=True)
  list_config.addColumn(
      'ship_state', "ship_state",
      (lambda e, *args: e.shipping_state()), hidden=True)
  list_config.addColumn(
      'ship_country', "ship_country",
      (lambda e, *args: e.shipping_country()), hidden=True)
  list_config.addColumn(
      'ship_postalcode', "ship_postalcode",
      (lambda e, *args: e.shipping_postalcode()), hidden=True)
  list_config.addSimpleColumn('tshirt_style', "tshirt_style", hidden=True)
  list_config.addSimpleColumn('tshirt_size', "tshirt_size", hidden=True)

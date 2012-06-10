#!/usr/bin/env python2.5
#
# Copyright 2008 the Melange authors.
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

"""This module contains the Model for Host."""


from google.appengine.ext import db

from django.utils.translation import ugettext


class Host(db.Model):
  """Model containing host specific data.

  The User entity corresponding to this host will be the parent of this entity.
  """

  notify_slot_transfer = db.BooleanProperty(required=False, default=True,
      verbose_name=ugettext('Notify of slot transfer updates'))
  notify_slot_transfer.help_text = ugettext(
      'Whether to send an email notification when slot transfer requests '
      'are made or updated.')
  notify_slot_transfer.group = ugettext("1. Notification settings")

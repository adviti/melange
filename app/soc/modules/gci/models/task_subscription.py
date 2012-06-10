#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""This module contains the GCI Task Subscription Model.
"""


from google.appengine.ext import db


class GCITaskSubscription(db.Model):
  """GCI Subscription model for tasks.

  Parent:
    soc.modules.gci.models.task.GCITask
  """
  # Property holding the list of users who are subscribed to the task.
  subscribers = db.ListProperty(item_type=db.Key, default=[])

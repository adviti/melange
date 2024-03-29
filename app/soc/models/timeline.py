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

"""This module contains the Timeline Model.
"""


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models import linkable


class Timeline(linkable.Linkable):
  """The Timeline Model, representing the timeline for a Program.
  """

  program_start = db.DateTimeProperty(
      verbose_name=ugettext('Program Start date'))

  program_end = db.DateTimeProperty(
      verbose_name=ugettext('Program End date'))

  accepted_organization_announced_deadline = db.DateTimeProperty(
      verbose_name=ugettext('Accepted Organizations Announced Deadline'))

  student_signup_start  = db.DateTimeProperty(
      verbose_name=ugettext('Student Signup Start date'))

  student_signup_end = db.DateTimeProperty(
      verbose_name=ugettext('Student Signup End date'))

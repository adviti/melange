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

"""This module contains the  GCIProfile Model."""


from google.appengine.ext import db
from google.appengine.ext import blobstore

from django.utils.translation import ugettext

from soc.modules.gci.models import avatars

import soc.models.role


class GCIProfile(soc.models.role.Profile):
  """GCIProfile Model.
  """
  automatic_task_subscription = db.BooleanProperty(
      required=False, default=True,
      verbose_name=ugettext('Automatic task subscription'))
  automatic_task_subscription.help_text = ugettext(
      'Whether to subscribe to tasks of interest automatically. These are '
      'tasks which you have claimed or are mentoring.')
  automatic_task_subscription.group = ugettext("6. Notification settings")

  # Avatar figure chosen by student and mentor
  avatar = db.StringProperty(
      required=False, verbose_name=ugettext('Avatar'))
  avatar.group = ugettext("1. Public Info")


class GCIStudentInfo(soc.models.role.StudentInfo):
  """GCIStudentInfo Model.

  Parent:
    soc.modules.gci.models.profile.GCIProfile
  """
  #: number of tasks completed
  number_of_tasks_completed = db.IntegerProperty(default=0)

  #: Property determining whether the student has closed at least one task
  task_closed = db.BooleanProperty(default=False)

  #: Set to True if the reminder mail to upload parental consent
  #: form is sent to students
  parental_form_mail = db.BooleanProperty(default=False)

  #: Property pointing to the consent form
  consent_form = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Parental Consent Form'))
  consent_form.help_text = ugettext(
      'A signed Parental Consent Form from your legal parent or guardian')

  #: Property pointing to the second page of the consent form
  #: (Deprecated since GCI2011)
  consent_form_two = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Parental Consent Form (page 2)'))
  consent_form_two.help_text = ugettext(
      'Page two of the Parental Consent Form (if applicable)')

  #: Property pointing to the student id form
  student_id_form = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Student ID form'))
  student_id_form.help_text = ugettext(
      'A scan of your student ID to verify your student status and birthday.')

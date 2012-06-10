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

"""This module contains the  GSoCProfile Model."""


from google.appengine.ext import db
from google.appengine.ext import blobstore

from django.utils.translation import ugettext

from soc.models import role


class GSoCProfile(role.Profile):
  """GSoCProfile Model.
  """

  notify_new_proposals = db.BooleanProperty(required=False, default=True,
      verbose_name=ugettext('Notify of new proposals'))
  notify_new_proposals.help_text = ugettext(
      'Whether to send an email notification when new proposals are submitted.')
  notify_new_proposals.group = ugettext("6. Notification settings")

  notify_proposal_updates = db.BooleanProperty(required=False, default=True,
      verbose_name=ugettext('Notify of proposal updates'))
  notify_proposal_updates.help_text = ugettext(
      'Whether to send an email notification when a proposal is updated.')
  notify_proposal_updates.group = ugettext("6. Notification settings")

  notify_public_comments = db.BooleanProperty(required=False, default=True,
      verbose_name=ugettext('Notify of new public comments'))
  notify_public_comments.help_text = ugettext(
      'Whether to send an email notification for new public comment.')
  notify_public_comments.group = ugettext("6. Notification settings")

  notify_private_comments = db.BooleanProperty(required=False, default=True,
      verbose_name=ugettext('Notify of new private comments'))
  notify_private_comments.help_text = ugettext(
      'Whether to send an email notification for new private comment.')
  notify_private_comments.group = ugettext("6. Notification settings")


class GSoCStudentInfo(role.StudentInfo):
  """GSoCStudentInfo Model.

  Parent:
    soc.modules.gsoc.models.profile.Profile
  """

  #: number of proposals 
  number_of_proposals = db.IntegerProperty(default=0)

  #: number of projects
  number_of_projects = db.IntegerProperty(default=0)

  #: number of passed evaluations
  passed_evaluations = db.IntegerProperty(default=0)

  #: number of failed evaluations
  failed_evaluations = db.IntegerProperty(default=0)

  #: organizations the user has a project for
  project_for_orgs = db.ListProperty(item_type=db.Key, default=[])

  #: Property pointing to the tax form
  tax_form = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Tax Form'))
  tax_form.help_text = ugettext(
      'A signed tax form')

  #: Property pointing to the proof of enrollment form
  enrollment_form = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Proof of Enrollment Form'))
  enrollment_form.help_text = ugettext(
      'A proof of enrollment form')

  #: School home page URL, not required here but enforced in the form for
  #: backwards compatibility.
  school_home_page = db.LinkProperty(
      required=False, verbose_name=ugettext("School Home Page URL"))
  school_home_page.group = ugettext("5. Education")

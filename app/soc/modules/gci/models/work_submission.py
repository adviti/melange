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

"""This module contains the GCI WorkSubmission Model.
"""


from google.appengine.ext import blobstore
from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.user

from soc.modules.gci.models import organization as gci_org_model
from soc.modules.gci.models import program as gci_program_model


class GCIWorkSubmission(db.Model):
  """Model for work submissions for a task by students.

  Parent:
    soc.modules.gci.models.task.GCITask
  """

  #: User who submitted this work
  user = db.ReferenceProperty(reference_class=soc.models.user.User,
                              required=True,
                              collection_name='work_submissions')

  #: Organization to which this work belongs to
  org = db.ReferenceProperty(
      reference_class=gci_org_model.GCIOrganization,
      required=True, collection_name='work_submissions')

  #: Program to which this work belongs to
  program = db.ReferenceProperty(
      reference_class=gci_program_model.GCIProgram,
      required=True, collection_name='work_submissions')

  #: Property allowing you to store information about your work
  information = db.TextProperty(
      required=False, verbose_name=ugettext('Info'))
  information.help_text = ugettext(
      'Information about the work you submit for this task')

  #: Property containing an URL to this work or more information about it
  url_to_work = db.LinkProperty(
      required=False, verbose_name=ugettext('URL to your Work'))
  url_to_work.help_text = ugettext(
      'URL to a resource containing your work or more information about it')

  #: Property pointing to the work uploaded as a file or archive
  upload_of_work = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Upload of Work'))
  upload_of_work.help_text = ugettext(
      'Your work uploaded as a single file or as archive')

  #: Property containing the date when the work was submitted
  submitted_on = db.DateTimeProperty(required=True, auto_now_add=True,
                                     verbose_name=ugettext('Submitted on'))

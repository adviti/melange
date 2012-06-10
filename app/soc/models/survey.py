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

"""This module contains the Survey models.

Survey describes meta-information and permissions.
SurveyContent contains the fields (questions) and their metadata.
"""


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models.program import Program
from soc.models.user import User


class Survey(db.Model):
  """Model of a Survey.

  This model describes meta-information and permissions.
  The actual questions of the survey are contained
  in the SurveyContent entity.
  """

  # TODO(Madhu): Conversion script for existing surveys to convert scope
  # to program
  #: Required N:1 relationship indicating the program to which the survey
  #: belongs to
  program = db.ReferenceProperty(reference_class=Program, required=False,
                                 collection_name="program_surveys")

# TODO(Madhu): Get rid of this property once the conversion is done
  scope = db.ReferenceProperty(required=False,
      collection_name='links', verbose_name=ugettext('Link Scope'))
  scope.help_text = ugettext(
      'Reference to another Linkable entity that defines the "scope" of'
      ' this Linkable entity.')

  #: Required field indicating the "title" of the work, which may have
  #: different uses depending on the specific type of the work. Works
  #: can be indexed, filtered, and sorted by 'title'.
  title = db.StringProperty(required=True,
      verbose_name=ugettext('Title'))
  title.help_text = ugettext(
      'title of the document; often used in the window title')

  #: short name used in places such as the sidebar menu and breadcrumb trail
  #: (optional: title will be used if short_name is not present)
  short_name = db.StringProperty(verbose_name=ugettext('Short name'))
  short_name.help_text = ugettext(
      'short name used, for example, in the sidebar menu')

  #: Required db.TextProperty containing the contents of the Work.
  #: The content is only to be displayed to Persons in Roles eligible to
  #: view them (which may be anyone, for example, with the site front page).
  content = db.TextProperty(verbose_name=ugettext('Content'))

  #: date when the work was created
  created = db.DateTimeProperty(auto_now_add=True)

  # TODO(Madhu): Conversion from author to created_by
  #: Required 1:1 relationship indicating the User who initially created the
  #: survey (this relationship is needed to keep track of lifetime document
  #: creation limits, used to prevent spamming, etc.).
  created_by = db.ReferenceProperty(reference_class=User, required=False,
                                    collection_name="created_surveys",
                                    verbose_name=ugettext('Created by'))

  # TODO(Madhu): Remove after conversion
  author = db.ReferenceProperty(reference_class=User, required=False,
                                collection_name="authors",
                                verbose_name=ugettext('Created by'))

  #: date when the work was last modified
  modified = db.DateTimeProperty(auto_now=True)

  # indicating wich user last modified the work. Used in displaying Work
  modified_by = db.ReferenceProperty(reference_class=User, required=True,
                                     collection_name="modified_surveys",
                                     verbose_name=ugettext('Modified by'))

  #: Date at which the survey becomes available for taking.
  survey_start = db.DateTimeProperty(
      required=False,
      verbose_name=ugettext('Survey start date and time'))
  survey_start.help_text = ugettext(
      'Indicates a date before which this survey'
      ' cannot be taken or displayed.')

  #: Deadline for taking survey.
  survey_end = db.DateTimeProperty(
      required=False,
      verbose_name=ugettext('Survey end date and time'))
  survey_end.help_text = ugettext(
      'Indicates a date after which this survey'
      ' cannot be taken.')

  #: Stores the schema for the survey form
  schema = db.TextProperty(required=False)

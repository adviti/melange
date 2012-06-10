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

"""This module contains the GSoC Proposal Model.
"""


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.modules.gsoc.models.organization
import soc.modules.gsoc.models.profile
import soc.modules.gsoc.models.program


class GSoCProposal(db.Model):
  """Model for a student proposal used in the GSoC workflow.

  Parent:
    soc.modules.gsoc.models.profile.Profile
  """

  #: Required field indicating the "title" of the proposal
  title = db.StringProperty(required=True,
      verbose_name=ugettext('Project Title'))
  title.help_text = ugettext('Title of the proposal')

  #: required, text field used for different purposes,
  #: depending on the specific type of the proposal
  abstract = db.TextProperty(required=True,
      verbose_name=ugettext('Short Description'))
  abstract.help_text = ugettext(
      'Short abstract, summary, or snippet;'
      ' 500 characters or less, plain text displayed publicly')

  #: Text field for storing Google document entry in "name:id" format
  #: To be used for syncing proposal
  google_document = db.StringProperty(
      verbose_name=ugettext('Sync with Google Documents'))
  google_document.help_text = ugettext(
      ('Type your Google document\'s name to search '
       'and select your document before start syncing.'))

  #: Required field containing the content of the proposal.
  content = db.TextProperty(required=True,
      verbose_name=ugettext('Content'))
  content.help_text = ugettext('This contains your actual proposal')

  #: an URL linking to more information about this students proposal
  additional_info = db.URLProperty(required=False,
      verbose_name=ugettext('Additional Info'))
  additional_info.help_text = ugettext(
      'Link to a resource containing more information about your proposal')

  #: indicates whether the proposal's content may be publicly seen or not
  is_publicly_visible = db.BooleanProperty(required=False, default=False,
      verbose_name=ugettext('Publicly visible'))
  is_publicly_visible.help_text = ugettext(
      'If you check here, the content of your proposal will be visible '
      'for others. Please note that they still will not be able to see '
      'any public comments and reviews of the proposal. '
      'Also note that your proposal is always visible to the organization '
      'that you are applying to, regardless of whether you check this box.')

  #: A property containing which mentor has assigned himself to this proposal.
  #: Only a proposal with an assigned mentor can be turned into
  #: a accepted proposal. A proposal can only have one mentor.
  mentor = db.ReferenceProperty(
      reference_class=soc.modules.gsoc.models.profile.GSoCProfile,
      required=False,
      collection_name='proposals')

  #: true iff a proposal has a mentor
  has_mentor = db.BooleanProperty(default=False)

  #: A property containing a list of possible Mentors for this proposal
  possible_mentors = db.ListProperty(item_type=db.Key, default=[])

  #: the current score of this proposal, used to determine which proposals
  #: should be assigned a project slot.
  score = db.IntegerProperty(required=True, default=0)

  #: the amount of score of this proposal has had
  nr_scores = db.IntegerProperty(required=True, default=0)

  #: Whether the org admin has decided that this proposal should be accepted.
  #: Whether or not the proposal is actually converted into a project depends
  #: on the amount of slots the organization has available.
  accept_as_project = db.BooleanProperty(default=False)

  #: the status of this proposal
  #: pending: the proposal is in the process of being ranked/scored
  #: accepted: the proposal has been assigned a project slot
  #: rejected: the proposal has not been assigned a slot
  #: invalid: the student or org admin marked this as an invalid proposal.
  #: withdrawn: the proposal has been withdrawn by the student
  #: ignored: the org admin has ignored the proposal may be because it is spam
  status = db.StringProperty(required=True, default='pending',
      choices=['pending', 'accepted', 'rejected', 'invalid',
               'withdrawn', 'ignored'])

  #: organization to which this proposal is directed
  org = db.ReferenceProperty(
      reference_class=soc.modules.gsoc.models.organization.GSoCOrganization,
      required=False,
      collection_name='proposals')

  #: program in which this proposal has been created
  program = db.ReferenceProperty(
      reference_class=soc.modules.gsoc.models.program.GSoCProgram,
      required=True,
      collection_name='proposals')

  #: indicates whether the proposal's content may be publicly seen or not
  is_editable_post_deadline = db.BooleanProperty(
      required=False, default=False,
      verbose_name=ugettext('Publicly visible'))
  is_editable_post_deadline.help_text = ugettext(
      'Clicking this button enables the student to modify this proposal '
      'irrespective of the proposal submission deadline.')

  #: date when the proposal was created
  created_on = db.DateTimeProperty(required=True, auto_now_add=True)

  #: date when the proposal was last modified, should be set manually on edit
  last_modified_on = db.DateTimeProperty(required=True, auto_now=True)

  #: JSON field storing extra data by the org
  extra = db.TextProperty(required=False,
      verbose_name=ugettext('Extra content'))

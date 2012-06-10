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

"""GCI module cleaning methods.
"""


from django import forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import validate

from soc.modules.gci.logic.models.task import logic as gci_task_logic


def cleanTaskComment(comment_field, action_field, ws_ext_field,
                     ws_upld_field, extended_deadline_field):
  """Cleans the comment form and checks to see if there is either
  action or comment content.

  Raises ValidationError if:
    -There is no action taking place and no comment present
    -The action is needs_review and there is no comment or work submission
     present
  """

  def wrapper(self):
    """Decorator wrapper method.
    """

    cleaned_data = self.cleaned_data
    content = cleaned_data.get(comment_field)
    action = cleaned_data.get(action_field)
    ws_ext = cleaned_data.get(ws_ext_field)
    extended_deadline = cleaned_data.get(extended_deadline_field)

    # not using cleaned data because this is separately handled by
    # Appengine's blobstore APIs
    ws_upld = self.data.get(ws_upld_field)

    if action == 'noaction' and not content:
      raise forms.ValidationError(
          ugettext('You cannot have comment field empty with no action.'))

    if action == 'needs_review' and not (content or ws_ext or ws_upld):
      raise forms.ValidationError(
          ugettext('You cannot have all the three fields: comment, '
                   'and two work submission fields empty'))

    if action == 'needs_work' and extended_deadline <= 0:
      raise forms.ValidationError(
          ugettext('Some time extension must be given to the student '
                   'when more work on the task is expected.'))

    if ws_upld:
      cleaned_data[ws_upld_field] = ws_upld

    return cleaned_data

  return wrapper


def cleanMentorsList(field_name):
  """Clean method to check and validate list of mentor's link_ids.
  """

  @cleaning.check_field_is_empty(field_name)
  def wrapper(self):
    """Decorator wrapped method.
    """

    from soc.modules.gci.logic.models.mentor import logic as gci_mentor_logic

    mentors_list_str = cleaning.str2set(field_name)(self)

    fields = {
        'scope_path': self.cleaned_data.get('scope_path'),
        'status': 'active'
        }

    mentors = []
    for link_id in mentors_list_str:

      if not validate.isLinkIdFormatValid(link_id):
        raise forms.ValidationError(
            "%s is not a valid link ID." % link_id)

      fields['link_id'] = link_id

      mentor = gci_mentor_logic.getFromKeyFields(fields)
      if not mentor:
        raise forms.ValidationError(
            'link_id "%s" is not a valid Mentor.' % link_id)

      mentors.append(mentor.key())

    return mentors
  return wrapper

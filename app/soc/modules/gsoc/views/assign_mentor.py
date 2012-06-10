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

"""Module containing the views for assigning mentors to GSoC Proposals
and Projects.
"""


from google.appengine.ext import db

from soc.views.template import Template


def getMentorsChoicesToAssign(mentors, current_mentor=None):
  """Returns a list of tuple containing the mentor key and mentor name.

  Args:
    mentors: List of potential mentor entities whose Django style choices
        must be returned
    current_mentor: Key of currently assigned mentor key
    
  """

  # construct a choice list for all the mentors in possible mentors list
  mentors_choices = []
  for m in mentors:
    m_key = m.key()
    choice = {
        'key': m_key,
        'name': m.name(),
        }
    if current_mentor and m_key == current_mentor:
      choice['selected'] = True

    mentors_choices.append(choice)

  return mentors_choices

class AssignMentorFields(Template):
  """Template to render the fields necessary to assign a mentor to a proposal.
  """

  def __init__(self, data, current_mentors, action,
               all_mentors=None, possible_mentors=None,
               mentor_required=False):
    """Instantiates the template for Assign mentor buttons for org admin.

    data: The request data object
    current_mentors: List of Keys of currently assigned mentors to the project
    action: The form action URL to which the form should be posted
    all_mentors: Set of all the mentors that can be assigned to this entity
    possible_mentors: List of possible mentors that can be assigned to
        this entity.
    mentor_required: True if org admin is not allowed to unassign a mentor
    """
    super(AssignMentorFields, self).__init__(data)
    self.current_mentors = current_mentors
    self.action = action
    self.all_mentors = all_mentors
    self.possible_mentors = possible_mentors
    self.mentor_required = mentor_required

  def _getMentorContext(self, current_mentor=None):
    """Returns the context for assigning mentors along with the current state.

    Args:
      current_mentor: Currently assigned mentor key to be set as initial value
    """
    mentor_context = {}
    if self.possible_mentors:
      possible_mentors = db.get(self.possible_mentors)
      possible_mentor_choices = getMentorsChoicesToAssign(
          possible_mentors, current_mentor)
      mentor_context['possible_mentors'] = sorted(
          possible_mentor_choices, key=lambda c: c.get('name', ''))

    if self.all_mentors:
      if self.possible_mentors:
        self.all_mentors = set(self.all_mentors) - set(self.possible_mentors)
      all_mentors = db.get(self.all_mentors)
      all_mentor_choices = getMentorsChoicesToAssign(
          all_mentors, current_mentor)
      mentor_context['all_mentors'] = sorted(
          all_mentor_choices, key=lambda c: c.get('name', ''))

    return mentor_context

  def context(self):
    mentors = []

    # add a select drop down context for each assigned mentor with that
    # mentor set as initial value
    for m in self.current_mentors:
      mentors.append(self._getMentorContext(current_mentor=m))

    # if there are no mentors assigned at all render a single drop down
    # without any initial mentor set
    if not self.current_mentors:
      mentors.append(self._getMentorContext())

    return {
        'action': self.action,
        'mentor_required': self.mentor_required,
        'mentors': mentors,
        }

  def templatePath(self):
    return 'v2/modules/gsoc/_assign_mentor/base.html'

#!/usr/bin/python2.5
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


"""MapReduce to populate the changes property to the action comments for
GCI 2011 comments.

Initially when GCI 2011 started we did not have the concept of rendering
Changelog for the GCITasks. So it was not really necessary to differentiate
between the actual comments posted by the users and the comments that were
recorded as part of some action performed by users. However for rendering
the changelog this becomes necessary.

The initial thought was to separate the actions out to a separate GCIAction
model, but then merge-sorting the GCIComment and GCIAction lists while
rendering the changelog would be an additional overhead. For this reason
and to be consistent with what we did during GCI 2010, we populate the
changes property in the GCIComment model itself. So that way, the comment
entities with a value for the changes property are actions and others are
regular comments.

So all this mapreduce is trying to do is inferring the changes for the
comments from the comment title. We may have problems if some mentor or
student has used the same title as one of these action-comments to their
regular comments. But we are assuming that effect is not disastrous. If
some one notices such a thing has happened, we can easily revert it by
unsetting the changes property.
"""


from google.appengine.ext.mapreduce import context
from google.appengine.ext.mapreduce import operation

from django.utils.translation import ugettext

from soc.modules.gci.models.program import GCIProgram


ACTION_TITLES = {
    'Task Claimed': [ugettext('User-Student'),
                     ugettext('Action-Claim Requested'),
                     ugettext('Status-ClaimRequested')],
    'Task Assigned': [ugettext('User-Mentor'),
                      ugettext('Action-Claim Accepted'),
                      ugettext('Status-Claimed')],
    'Claim Removed': [ugettext('User-Student'),
                      ugettext('Action-Withdrawn'),
                      ugettext('Status-Reopened')],
    'Ready for review': [ugettext('User-Student'),
                         ugettext('Action-Submitted work'),
                         ugettext('Status-NeedsReview')],
    'Task Needs More Work': [ugettext('User-Mentor'),
                             ugettext('Action-Requested more work'),
                             ugettext('Status-NeedsWork')],
    'Initial Deadline passed': [ugettext('User-MelangeAutomatic'),
                                ugettext('Action-Warned for action'),
                                ugettext('Status-ActionNeeded')],
    'No more Work can be submitted': [ugettext('User-MelangeAutomatic'),
                                      ugettext('Action-Deadline passed'),
                                      ugettext('Status-NeedsReview')],
    'Task Closed': [ugettext('User-Mentor'),
                    ugettext('Action-Closed the task'),
                    ugettext('Status-Closed')],
    'Deadline extended': [ugettext('User-Mentor'),
                          ugettext('Action-Deadline extended')],
    # User can be either mentor or melange automatic system
    # Action can be one of Claim Rejected from ClaimRequested/Reopened
    # from other states/Forcibly Reopened from NeedsWork and Claimed
    'Task Reopened': [ugettext('Action-Task Reopened'),
                      ugettext('Status-Reopened')
                      ]
    }


def process(comment):
  ctx = context.get()
  params = ctx.mapreduce_spec.mapper.params
  program_key = params['program_key']

  program = GCIProgram.get_by_key_name(program_key)

  if comment.parent().program.key() != program.key():
    yield operation.counters.Increment("prev_program_comment_not_converted")
    return

  if comment.title not in ACTION_TITLES:
    yield operation.counters.Increment("user_comment_not_converted")
    return

  comment_title = ACTION_TITLES[comment.title]

  changes = ACTION_TITLES[comment_title]
  # Task reopening is a special case which could have been performed
  # either by a mentor or by the automated system after the passing of
  # the deadline. So additional inference of the user has to be made.
  if comment_title == 'Task Reopened':
    if comment.created_by:
      user_info = ugettext('User-Mentor')
    else:
      user_info = ugettext('MelangeAutomatic')
    changes = [user_info] + changes

  comment.changes = changes

  yield operation.db.Put(comment)
  yield operation.counters.Increment("action_comment_converted")

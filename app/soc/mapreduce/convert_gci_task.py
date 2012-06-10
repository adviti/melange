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

"""GCI Task updating MapReduce.
"""


from google.appengine.ext import db
from google.appengine.ext.mapreduce import operation

from soc.models.host import Host
from soc.models.role import Role

from soc.modules.gci.logic import task as task_logic
from soc.modules.gci.models.comment import GCIComment
from soc.modules.gci.models.mentor import GCIMentor
from soc.modules.gci.models.org_admin import GCIOrgAdmin
from soc.modules.gci.models.profile import GCIProfile
from soc.modules.gci.models.student import GCIStudent
from soc.modules.gci.models.task import GCITask
from soc.modules.gci.models.task_subscription import GCITaskSubscription
from soc.modules.gci.models.work_submission import GCIWorkSubmission


TASK_PROPERTIES = GCITask.properties()
# We do not want history property in the new entities in any more because
# we are not using it
TASK_PROPERTIES.pop('scope', 'history')

COMMENT_PROPERTIES = GCIComment.properties()
WORK_SUBMISSION_PROPERTIES = GCIWorkSubmission.properties()


def process_task(task):
  """Conversion to make GCI Tasks ID based and getting rid of unnecessary
  properties.
  """
  if task.key().name():
    # Get the values for all the properties in the GCITask model from the
    # old entity to create the new entity.
    new_task_properties = {}
    for prop in TASK_PROPERTIES:
      new_task_properties[prop] = getattr(task, prop)
      new_task_properties['org'] = task.scope

    new_task = GCITask(**new_task_properties)
    new_task_key = new_task.put()

    if new_task_key:
      # Update all the comments with the new task as the parent
      comments = GCIComment.all().ancestor(task).fetch(1000)
      for c in comments:
        new_comm_properties = {}
        for c_prop in COMMENT_PROPERTIES:
          new_comm_properties[c_prop] = getattr(c, c_prop)
        new_comment = GCIComment(parent=new_task_key, **new_comm_properties)

        # set these fields to behave like last_modified_on/by
        new_comment.modified_on = new_comment.created_on
        new_comment.modified_by = new_comment.created_by

        yield operation.db.Put(new_comment)
        yield operation.counters.Increment("comment_updated")

      # Update all the work submission entities with the new task as the parent
      work_submissions = GCIWorkSubmission.all().ancestor(task).fetch(1000)
      for ws in work_submissions:
        new_ws_properties = {}
        for ws_prop in WORK_SUBMISSION_PROPERTIES:
          new_ws_properties[ws_prop] = getattr(ws, ws_prop)
        new_ws = GCIWorkSubmission(parent=new_task_key, **new_ws_properties)
        yield operation.db.Put(new_ws)
        yield operation.counters.Increment("work_submission_updated")

      yield operation.counters.Increment("task_updated")


def new_task_for_old(task):
  q = GCITask.all(keys_only=True)
  q.filter('org', task.scope)
  q.filter('link_id', task.link_id)
  return q.get()


def process_tag(tag):
  """Replace all the references to the list of old tasks to the new tasks.
  """
  new_tagged_keys = []
  for t in tag.tagged:
    try:
      task = GCITask.get(t)
      new_tagged = new_task_for_old(task) if task else None
    except db.KindError:
      new_tagged = t

    if new_tagged:
      new_tagged_keys.append(new_tagged)

  tag.tagged = new_tagged_keys

  yield operation.db.Put(tag)
  yield operation.counters.Increment("tag_updated")


def process_task_children_delete(task):
  """Delete all the task entities and all its descendent entities.
  """
  if not task.key().name():
    return

  task_logic.delete(task)

  yield operation.counters.Increment("task_with_key_deleted")


def process_difficulty(task):
  """Copy task difficulties stored in TaskDifficultyTask to the task entity.
  """

  difficulty = task.difficulty[0].tag

  # difficult tasks should be explicitly renamed to 'Hard'
  if difficulty == 'Difficult':
    difficulty = 'Hard'

  task.difficulty_level = difficulty

  yield operation.db.Put(task)
  yield operation.counters.Increment('difficulty_updated')


def process_task_types(task):
  """Copy task types stored in TaskTypeTag to the task entity.
  """

  type_tags = task.task_type
  types = []

  for type_tag in type_tags:
    types.append(type_tag.tag)

  types = list(set(types))
  task.types = types

  yield operation.db.Put(task)
  yield operation.counters.Increment('task_type_updated')


def process_arbit_tags(task):
  """Copy task types stored in TaskArbitTag to the task entity.
  """
  tags = []

  for arbit_tag in task.arbit_tag:
    tags.append(arbit_tag.tag)

  task.tags = list(set(tags))

  yield operation.db.Put(task)
  yield operation.counters.Increment('task_tags_updated')

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


"""Mapreduce to subscribe all the mentors to the tasks.
"""


from google.appengine.ext import db
from google.appengine.ext.mapreduce import context
from google.appengine.ext.mapreduce import operation

from soc.modules.gci.models.program import GCIProgram
from soc.modules.gci.models.task import GCITask


def process(task):
  ctx = context.get()
  params = ctx.mapreduce_spec.mapper.params
  program_key = params['program_key']

  try:
    program = GCIProgram.get_by_key_name(program_key)
  except db.BadValueError:
    yield operation.counters.Increment('program_key_is_empty_or_invalid')
    return

  def subscribe_to_task_txn(task_key, subscribe):
    task = GCITask.get(task_key)
    task.subscribers = list(set(task.subscribers + subscribe))
    task.put()
    return task

  if task.program.key() != program.key():
    yield operation.counters.Increment("old_program_task_not_updated")
    return

  mentors = db.get(task.mentors)
  entities = mentors + [task.created_by, task.modified_by]

  subscribe = [ent.key() for ent in entities if ent.automatic_task_subscription]

  result = db.run_in_transaction(subscribe_to_task_txn, task.key(), subscribe)

  if result:
    yield operation.counters.Increment("task_updated")
  else:
    yield operation.counters.Increment("task_not_updated")

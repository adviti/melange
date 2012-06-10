#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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

"""Appengine Tasks related to GCI Ranking.
"""


import logging

from google.appengine.api import taskqueue
from google.appengine.ext import db

from django.conf.urls.defaults import url

from soc.tasks import responses
from soc.views.helper import url_patterns

from soc.modules.gci.logic import ranking as ranking_logic
from soc.modules.gci.models.profile import GCIProfile
from soc.modules.gci.models.program import GCIProgram
from soc.modules.gci.models.score import GCIScore
from soc.modules.gci.models.task import GCITask


class RankingUpdater(object):
  """Appengine tasks for updating the rankings for a GCI program.
  """

  def djangoURLPatterns(self):
    """Returns the URL patterns for the tasks in this module.
    """
    patterns = [
        url(r'^tasks/gci/ranking/update$', self.updateRankingWithTask,
            name='task_update_gci_ranking_with_task'),
        url(r'^tasks/gci/ranking/recalculate/%s$' % url_patterns.PROGRAM,
            self.recalculateGCIRanking, name='task_recalculate_gci_ranking'),
        url(r'^tasks/gci/ranking/recalculate_student$',
            self.recalculateForStudent,
            name='task_recalculate_gci_ranking_for_student'),
        url(r'^tasks/gci/ranking/clear/%s$'%url_patterns.PROGRAM,
            self.clearGCIRanking, name='task_clear_gci_ranking')]
    return patterns

  def updateRankingWithTask(self, request, *args, **kwargs):
    """Updates student ranking based on the task passed as post argument.

    Args in POST dict:
      id: The (numeric) id of the task to update the ranking for
    """
    post_dict = request.POST

    id = int(post_dict.get('id'))
    task = GCITask.get_by_id(id)

    if not task:
      logging.warning('Ranking update queued for non-existing task: %s' %id)
      responses.terminateTask()

    ranking_logic.updateScore(task)

    logging.info("ranking_update updateRankingWithTask ends")
    return responses.terminateTask()

  def recalculateGCIRanking(self, request, *args, **kwargs):
    """Recalculates student ranking for the entire program.

    Args in POST dict:
      cursor: Query cursor to figure out where we need to start processing
    """

    key_name = '%s/%s' % (kwargs['sponsor'], kwargs['program'])
    cursor = request.POST.get('cursor')

    program = GCIProgram.get_by_key_name(key_name)
    if not program:
      logging.warning(
          'Enqueued recalculate ranking task for non-existing '
          'program: %s' %key_name)
      return responses.terminateTask()

    # Retrieve the students for the program
    q = GCIProfile.all()
    q.filter('scope', program)
    q.filter('is_student', True)

    if cursor:
      q.with_cursor(cursor)

    students = q.fetch(25)

    for student in students:
      # get all the tasks that the student has completed
      task_q = GCITask.all()
      task_q.filter('student', student)
      task_q.filter('status', 'Closed')

      tasks = task_q.fetch(1000)

      # calculate ranking with all the tasks
     # ranking_logic.calculateRankingForStudent(student, tasks)
      ranking_logic.calculateScore(student, tasks, program)

    if students:
      # schedule task to do the rest of the students
      params = {
          'cursor': q.cursor(),
          }
      taskqueue.add(queue_name='gci-update', url=request.path, params=params)

    return responses.terminateTask()

  def clearGCIRanking(self, request, *args, **kwargs):
    """Clears student ranking for a program with the specified key_name.
    """
    key_name = '%s/%s' %(kwargs['sponsor'], kwargs['program'])

    program = GCIProgram.get_by_key_name(key_name)
    if not program:
      logging.warning(
          'Enqueued recalculate ranking task for non-existing '
          'program: %s' %key_name)
      return responses.terminateTask()

    q = GCIScore.all()
    q.filter('program', program)

    rankings = q.fetch(500)
    while rankings:
      db.delete(rankings)
      rankings = q.fetch(500)

    return responses.terminateTask()

  def recalculateForStudent(self, request, *args, **kwargs):
    """Recalculates GCI Student Ranking for the specified student.

    Args in POST:
      key: The string version of the key for the GCIProfile entity
           representing the student.
    """
    post_dict = request.POST
    key = db.Key(post_dict['key'])
    student = GCIProfile.get(key)

    if not student:
      logging.warning('Enqueued task to recalculate ranking for '
                      'non-existent student %s' %(key))
      return responses.terminateTask()

    # get all the tasks that the student has completed
    q = GCITask.all()
    q.filter('student', student)
    q.filter('status', 'Closed')
    tasks = q.fetch(1000)

    ranking_logic.calculateRankingForStudent(student, tasks)

    return responses.terminateTask()


def startUpdatingTask(task, transactional=False):
  """Starts a new task which updates ranking entity for the specified task.

  Args:
    task: The GCI task to update the ranking for
    transactional: Whether this task is enqueued in a transaction.
  """
  url = '/tasks/gci/ranking/update'
  params = {
      'id': task.key().id_or_name()
      }
  taskqueue.add(queue_name='gci-update', url=url, params=params,
                transactional=transactional)


def startClearingTask(program):
  """Starts a new task which clears all ranking entities for the program.
  """
  url = '/tasks/gci/ranking/clear/%s' % program.key().id_or_name()
  taskqueue.add(queue_name='gci-update', url=url)

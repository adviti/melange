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

"""GCIStudentRanking logic methods.
"""


import logging

from google.appengine.ext import db

from soc.modules.gci.models.profile import GCIStudentInfo
from soc.modules.gci.models.score import GCIScore
from soc.modules.gci.models.student_ranking import GCIStudentRanking
from soc.modules.gci.models.task import POINTS


def getOrCreateForStudent(student):
  """Gets or creates the ranking object for the student.

  Args:
    student: GCIProfile entity representing the student.
  """
  q = GCIStudentRanking.all()
  q.filter('student', student)
  ranking = q.get()

  if not ranking:
    # create a new one
    ranking = GCIStudentRanking(program=student.scope, student=student)
    ranking.put()

  return ranking


def get(profile):
  """Gets the score entity associated with the specified profile.

  Args:
    profile: GCIProfile entity to retrieve a score for
  """
  query = GCIScore.all().ancestor(profile)
  return query.get()


def updateScore(task):
  """Updates score for a student who worked on the specified task.

  Args:
    task: GCITask that has been completed and should be taken into account in
          the score.
  """
  logging.info("updateScore starts for task %s" % task.key().id())
  if task.status != 'Closed':
    logging.warning('Trying to update score for a task that is not closed.')

  student = task.student
  program = task.program
  task_key = task.key()

  def update_ranking_txn():
    logging.info("updateScore txn starts for task %s" % task_key.id())
    query = GCIScore.all().ancestor(student)
    score = query.get()

    # create a new GCIStore entity if one does not exist yet
    if not score:
      logging.info("score entity is being created")
      score = GCIScore(parent=student, program=program)

    # check if the task has been included in the score
    if task_key not in score.tasks:
      score.points += POINTS[task.difficulty_level]
      score.tasks.append(task_key)

    # TODO(dhans): optimize it; sometimes, put may not be needed
    logging.info("score put")
    score.put()
    logging.info("score put returned")

    query = GCIStudentInfo.all().ancestor(student)
    student_info = query.get()

    # set in student info that the student has completed a task
    if not student_info.task_closed:
      student_info.task_closed = True
      student_info.put()

  db.run_in_transaction(update_ranking_txn)


def updateRankingWithTask(task):
  """Updates ranking with the specified task.

  Args:
    task: GCITask that has been completed and should be taken into account in
          the ranking.
  """

  # get current ranking for the student if it is not specified
  ranking = getOrCreateForStudent(task.student)

  # check if the task has not been considered
  if task.key() not in ranking.tasks:
    #: update total number of points with number of points for this task
    ranking.points = ranking.points + POINTS[task.difficulty_level]
    ranking.tasks.append(task.key())
    ranking.put()

  return ranking


def calculateRankingForStudent(student, tasks):
  """Calculates ranking for the specified student with the specified
  list of tasks.

  It is assumed that all the tasks from the list belong to the student. Any
  existing ranking for this student will be overwritten.

  Args:
    student: GCIProfile entity representing the student
    tasks: List of GCITasks that have been completed by the student
  """
  ranking = getOrCreateForStudent(student)

  points = 0
  for task in tasks:
    points += POINTS[task.difficulty_level]

  ranking.points = points
  ranking.tasks = [task.key() for task in tasks]
  ranking.put()

  return ranking


def calculateScore(student, tasks, program):
  """Calculates score for the specified student with the specified
  list of tasks.

  It is assumed that all the tasks from the list belong to the student. Any
  existing score for this student will be overwritten.

  Args:
    student: GCIProfile entity representing the student
    tasks: List of GCITasks that have been completed by the student
    program: GCIProgram entity that all the tasks refer to
  """
  # do not calculate score for students who have not completed any tasks
  if not tasks:
    return None

  points = 0
  for task in tasks:
    points += POINTS[task.difficulty_level]

  def calculate_score_txn():
    query = GCIScore.all().ancestor(student)
    score = query.get()

    # create a new GCIStore entity if one does not exist yet
    if not score:
      score = GCIScore(parent=student, program=program)

    score.points = points
    score.tasks = [task.key() for task in tasks]
    score.put()

    # set that the student closed a task in GCIStudentInfo
    query = GCIStudentInfo.all().ancestor(student)
    student_info = query.get()
    student_info.task_closed = True
    student_info.put()

  return db.run_in_transaction(calculate_score_txn)


def allScoresForProgramQuery(program):
  """Returns the query to fetch all the scores for the specified program.

  Args:
    program: GCIProgram entity for which the query should filter the program 
  """
  return GCIScore.all().filter('program =', program)

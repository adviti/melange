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

"""GradingRecord related functions.
"""


from google.appengine.ext import db

from soc.modules.gsoc.models.grading_project_survey_record import GSoCGradingProjectSurveyRecord
from soc.modules.gsoc.models.grading_record import GSoCGradingRecord
from soc.modules.gsoc.models.project_survey_record import GSoCProjectSurveyRecord


def updateOrCreateRecordsFor(survey_group, projects):
  """Updates or creates GradingRecords in batch.

  Args:
    survey_group: GradingSurveyGroup entity
    projects: list of GSoCProjects which to process

  Returns:
    The list of updated and new records.
  """
  records = []

  for project in projects:
    q = GSoCGradingRecord.all()
    q.filter('grading_survey_group', survey_group)
    q.ancestor(project)

    # try to retrieve an existing record
    record = q.get()

    # retrieve the fields that should be set
    record_fields = getFieldsForGradingRecord(
        project, survey_group, record)

    if not record and project.status in ['failed', 'invalid'] \
        and not record_fields['mentor_record'] \
        and not record_fields['student_record']:
      # Don't create a new GradingRecord for an already failed project which
      # has no records attached. Because it does not matter.
      continue

    if record:
      # update existing GradingRecord
      for key,value in record_fields.iteritems():
        setattr(record, key, value)
    else:
      # create a new GradingRecord
      record = GSoCGradingRecord(parent=project, **record_fields)

    # prepare the new/updated record for storage
    records.append(record)

  db.put(records)

  return records


def getFieldsForGradingRecord(project, survey_group, record_entity=None):
  """Returns the fields for a GradingRecord.

  See GradingRecord model for description of the grade_decision value.

  Args:
    project: Project entity
    survey_group: a GradingSurveyGroup entity
    record_entity: an optional GradingRecord entity

  Returns:
    Dict containing the fields that should be set on a GradingRecord for this
    GradingSurveyGroup and StudentProject
  """

  # retrieve the two Surveys, student_survey might be None
  grading_survey = survey_group.grading_survey
  student_survey = survey_group.student_survey

  # retrieve a GradingSurveyRecord
  q = GSoCGradingProjectSurveyRecord.all()
  q.filter('project', project)
  q.filter('survey', grading_survey)
  grading_survey_record = q.get()

  if student_survey:
    # retrieve ProjectSurveyRecord
    q = GSoCProjectSurveyRecord.all()
    q.filter('project', project)
    q.filter('survey', student_survey)
    project_survey_record = q.get()
  else:
    project_survey_record = None

  # set the required fields
  fields = {'grading_survey_group': survey_group,
            'mentor_record': grading_survey_record,
            'student_record': project_survey_record}

  if not record_entity or not record_entity.locked:
    # find grading decision for new or unlocked records

    if not grading_survey_record:
      # no record found, return undecided
      grade_decision = 'undecided'
    elif not student_survey or project_survey_record:
      # if the grade is True then pass else fail
      grade_decision = 'pass' if grading_survey_record.grade else 'fail'
    else:
      # no ProjectSurveyRecord on file while there is a survey to be taken
      grade_decision = 'fail'

    fields['grade_decision'] = grade_decision

  # return the fields that should be set for a GradingRecord
  return fields


def updateProjectsForGradingRecords(records):
  """Updates StudentProjects using a list of GradingRecord entities.

  Args:
    records: List of GradingRecord entities to process.
  """
  projects_to_update = []

  for record in records:
    project = record.parent()

    if project.status in ['withdrawn', 'invalid']:
      # skip this project
      continue

    # get the key from the GradingRecord entity since that gets stored
    record_key = record.key()

    passed_evals = project.passed_evaluations
    failed_evals = project.failed_evaluations

    # try to remove this GradingRecord from the existing list of evals
    if record_key in passed_evals:
      passed_evals.remove(record_key)

    if record_key in failed_evals:
      failed_evals.remove(record_key)

    # get the grade_decision from the GradingRecord
    grade_decision = record.grade_decision

    # update GradingRecord lists with respect to the grading_decision
    if grade_decision == 'pass':
      passed_evals.append(record_key)
    elif grade_decision == 'fail':
      failed_evals.append(record_key)

    if project.status != 'completed':
      # Only when the project has not been completed should the status be
      # updated to reflect the new setting of the evaluations.

      if len(failed_evals) == 0:
        # no failed evaluations present
        new_status = 'accepted'
      else:
        new_status = 'failed'
    else:
        new_status = project.status

    # update the necessary fields and store it before updating
    project.passed_evaluations = passed_evals
    project.failed_evaluations = failed_evals
    project.status = new_status

    profile = project.parent()
    profile.student_info.passed_evaluations = len(passed_evals)
    profile.student_info.failed_evaluations = len(failed_evals)

    projects_to_update.append(project)
    projects_to_update.append(profile.student_info)

  # batch put the StudentProjects that need to be updated
  db.put(projects_to_update)

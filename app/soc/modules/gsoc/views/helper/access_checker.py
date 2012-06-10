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

"""Module containing the AccessChecker class that contains helper functions
for checking access.
"""


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.logic.exceptions import AccessViolation, BadRequest
from soc.logic.exceptions import NotFound
from soc.logic.exceptions import RedirectRequest
from soc.views.helper import access_checker

from soc.modules.gsoc.logic import slot_transfer as slot_transfer_logic
from soc.modules.gsoc.models.grading_project_survey import GradingProjectSurvey
from soc.modules.gsoc.models.grading_project_survey_record import \
    GSoCGradingProjectSurveyRecord
from soc.modules.gsoc.models.grading_survey_group import GSoCGradingSurveyGroup
from soc.modules.gsoc.models.grading_record import GSoCGradingRecord
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.models.project_survey import ProjectSurvey
from soc.modules.gsoc.models.project_survey_record import \
    GSoCProjectSurveyRecord
from soc.modules.gsoc.models.proposal import GSoCProposal


DEF_FAILED_PREVIOUS_EVAL = ugettext(
    'You cannot access %s for this project because this project was '
    'failed in the previous evaluation.')

DEF_MAX_PROPOSALS_REACHED = ugettext(
    'You have reached the maximum number of proposals allowed '
    'for this program.')

DEF_NO_STUDENT_EVALUATION = ugettext(
    'The project survey with name %s parameters does not exist.')

DEF_NO_MENTOR_EVALUATION = ugettext(
    'The project evaluation with name %s does not exist.')

DEF_NO_PROJECT = ugettext('Requested project does not exist.')

DEF_NO_RECORD_FOUND = ugettext(
    'The Record with the specified key was not found.')

DEF_MENTOR_EVAL_DOES_NOT_BELONG_TO_YOU = ugettext(
    'This evaluation does not correspond to the project you are mentor for, '
    'and hence you cannot access it.')

DEF_STUDENT_EVAL_DOES_NOT_BELONG_TO_YOU = ugettext(
    'This evaluation does not correspond to your project, and hence you '
    'cannot access it.')

DEF_EVAL_NOT_ACCESSIBLE_FOR_PROJECT = ugettext(
    'You cannot access this evaluation because you do not have any '
    'ongoing project.')

DEF_ALREADY_PARTICIPATING_AS_NON_STUDENT = ugettext(
    'You cannot register as a student since you are already a '
    'mentor or organization administrator in %s.')

DEF_NOT_ALLOWED_TO_DOWNLOAD_FORM = ugettext(
    'You are not allowed to download the form.')


class Mutator(access_checker.Mutator):
  """Mutator for the GSoC module.
  """

  def unsetAll(self):
    """Clear the fields of the data object.
    """
    self.data.private_comments_visible = access_checker.unset
    self.data.proposal = access_checker.unset
    self.data.proposer = access_checker.unset
    self.data.public_comments_visible = access_checker.unset
    self.data.public_only = access_checker.unset
    super(Mutator, self).unsetAll()

  def profileFromKwargs(self):
    """Retrieves profile from the kwargs for GSoC.
    """
    super(Mutator, self).profileFromKwargs(GSoCProfile)

  def proposalFromKwargs(self):
    self.profileFromKwargs()
    assert access_checker.isSet(self.data.url_profile)

    # can safely call int, since regexp guarnatees a number
    proposal_id = int(self.data.kwargs['id'])

    if not proposal_id:
      raise NotFound('Proposal id must be a positive number')

    self.data.proposal = GSoCProposal.get_by_id(
        proposal_id, parent=self.data.url_profile)

    if not self.data.proposal:
      raise NotFound('Requested proposal does not exist')

    org_key = GSoCProposal.org.get_value_for_datastore(self.data.proposal)

    self.data.proposal_org = self.data.getOrganization(org_key)

    parent_key = self.data.proposal.parent_key()
    if self.data.profile and parent_key == self.data.profile.key():
      self.data.proposer = self.data.profile
    else:
      self.data.proposer = self.data.proposal.parent()

  def projectFromKwargs(self):
    """Sets the project entity in RequestData object.
    """
    self.profileFromKwargs()
    assert access_checker.isSet(self.data.url_profile)

    # can safely call int, since regexp guarnatees a number
    project_id = int(self.data.kwargs['id'])

    if not project_id:
      raise NotFound(ugettext('Proposal id must be a positive number'))

    self.data.project = GSoCProject.get_by_id(
        project_id, parent=self.data.url_profile)

    if not self.data.project:
      raise NotFound(DEF_NO_PROJECT)

    parent_key = self.data.project.parent_key()
    if self.data.profile and parent_key == self.data.profile.key():
      self.data.project_owner = self.data.profile
    else:
      self.data.project_owner = self.data.project.parent()

  def studentEvaluationFromKwargs(self, raise_not_found=True):
    """Sets the student evaluation in RequestData object.

    Args:
      raise_not_found: iff False do not send 404 response.
    """
    # kwargs which defines a survey
    fields = ['sponsor', 'program', 'survey']

    key_name = '/'.join(['gsoc_program'] +
                        [self.data.kwargs[field] for field in fields])
    self.data.student_evaluation = ProjectSurvey.get_by_key_name(key_name)

    if raise_not_found and not self.data.student_evaluation:
      raise NotFound(DEF_NO_STUDENT_EVALUATION % key_name)


  def studentEvaluationRecordFromKwargs(self):
    """Sets the student evaluation record in RequestData object.
    """
    assert access_checker.isSet(self.data.student_evaluation)
    assert access_checker.isSet(self.data.project)

    self.data.organization = self.data.project.org

    q = GSoCProjectSurveyRecord.all()
    q.filter('project', self.data.project)
    q.filter('survey', self.data.student_evaluation)
    self.data.student_evaluation_record = q.get()

  def mentorEvaluationFromKwargs(self, raise_not_found=True):
    """Sets the mentor evaluation in RequestData object.

    Args:
      raise_not_found: iff False do not send 404 response.
    """
    # kwargs which defines an evaluation
    fields = ['sponsor', 'program', 'survey']

    key_name = '/'.join(['gsoc_program'] +
                        [self.data.kwargs[field] for field in fields])
    self.data.mentor_evaluation = GradingProjectSurvey.get_by_key_name(
        key_name)

    if raise_not_found and not self.data.mentor_evaluation:
      raise NotFound(DEF_NO_MENTOR_EVALUATION % key_name)

  def mentorEvaluationRecordFromKwargs(self):
    """Sets the mentor evaluation record in RequestData object.
    """
    assert access_checker.isSet(self.data.mentor_evaluation)
    assert access_checker.isSet(self.data.project)

    self.data.organization = self.data.project.org

    q = GSoCGradingProjectSurveyRecord.all()
    q.filter('project', self.data.project)
    q.filter('survey', self.data.mentor_evaluation)
    self.data.mentor_evaluation_record = q.get()

  def gradingSurveyRecordFromKwargs(self):
    """Sets a GradingSurveyRecord entry in the RequestData object.
    """
    self.projectFromKwargs()

    if not ('group' in self.data.kwargs and 'id' in self.data.kwargs):
      raise BadRequest(access_checker.DEF_NOT_VALID_REQUEST)

    # url regexp ensures that it is a digit
    record_id = long(self.data.kwargs['record'])
    group_id = long(self.data.kwargs['group'])

    record = GSoCGradingRecord.get_by_id(record_id, parent=self.data.project)

    if not record or record.grading_survey_group.key().id() != group_id:
      raise NotFound(DEF_NO_RECORD_FOUND) 

    self.data.record = record

  def surveyGroupFromKwargs(self):
    """Sets the GradingSurveyGroup from kwargs.
    """
    assert access_checker.isSet(self.data.program)

    survey_group = GSoCGradingSurveyGroup.get_by_id(int(self.data.kwargs['id']))

    if not survey_group:
      raise NotFound('Requested GSoCGradingSurveyGroup does not exist')

    if survey_group.program.key() != self.data.program.key():
      raise NotFound(
          'Requested GSoCGradingSurveyGroup does not exist in this program')

    self.data.survey_group = survey_group

  def slotTransferEntities(self):
    assert access_checker.isSet(self.data.organization)

    self.data.slot_transfer_entities = \
        slot_transfer_logic.getSlotTransferEntitiesForOrg(
            self.data.organization)


class DeveloperMutator(access_checker.DeveloperMutator, Mutator):
  pass


class AccessChecker(access_checker.AccessChecker):
  """Helper classes for access checking in GSoC module.
  """

  def canStudentPropose(self):
    """Checks if the student is eligible to submit a proposal.
    """
    # check if the timeline allows submitting proposals
    self.studentSignupActive()

    # check how many proposals the student has already submitted 
    query = GSoCProposal.all()
    query.filter('scope = ', self.data.profile).ancestor(self.data.user)

    if query.count() >= self.data.program.apps_tasks_limit:
      # too many proposals access denied
      raise AccessViolation(DEF_MAX_PROPOSALS_REACHED)

  def isStudentForSurvey(self):
    """Checks if the student can take survey for the project.
    """
    assert access_checker.isSet(self.data.profile)
    assert access_checker.isSet(self.data.project)

    self.isProjectInURLValid()

    project = self.data.project

    # check if the project belongs to the current user and if so he
    # can access the survey
    expected_profile_key = project.parent_key()
    if expected_profile_key != self.data.profile.key():
      raise AccessViolation(DEF_STUDENT_EVAL_DOES_NOT_BELONG_TO_YOU)

    # check if the project is still ongoing
    if project.status in ['invalid', 'withdrawn']:
      raise AccessViolation(DEF_EVAL_NOT_ACCESSIBLE_FOR_PROJECT)

    # check if the project has failed in a previous evaluation
    # TODO(Madhu): This still has a problem that when the project fails
    # in the final evaluation, the users will not be able to access the
    # midterm evaluation show page. Should be fixed.
    if project.status == 'failed' and project.failed_evaluations:
      failed_evals = db.get(project.failed_evaluations)
      fe_keynames = [f.grading_survey_group.grading_survey.key(
          ).id_or_name() for f in failed_evals]
      if self.data.student_evaluation.key().id_or_name() not in fe_keynames:
        raise AccessViolation(DEF_FAILED_PREVIOUS_EVAL % (
            self.data.student_evaluation.short_name.lower()))

  def isMentorForSurvey(self):
    """Checks if the user is the mentor for the project or org admin.
    """
    assert access_checker.isSet(self.data.project)

    self.isProjectInURLValid()

    project = self.data.project

    # check if the project is still ongoing
    if project.status in ['invalid', 'withdrawn']:
      raise AccessViolation(DEF_EVAL_NOT_ACCESSIBLE_FOR_PROJECT)

    # check if the project has failed in a previous evaluation
    # TODO(Madhu): This still has a problem that when the project fails
    # in the final evaluation, the users will not be able to access the
    # midterm evaluation show page. Should be fixed.
    if project.status == 'failed' and project.failed_evaluations:
      failed_evals = db.get(project.failed_evaluations)
      fe_keynames = [f.grading_survey_group.grading_survey.key(
          ).id_or_name() for f in failed_evals]
      if self.data.mentor_evaluation.key().id_or_name() not in fe_keynames:
        raise AccessViolation(DEF_FAILED_PREVIOUS_EVAL % (
            self.data.mentor_evaluation.short_name.lower()))

    if self.data.orgAdminFor(self.data.organization):
      return

    # check if the currently logged in user is the mentor or co-mentor
    # for the project in request or the org admin for the org
    if self.data.profile.key() not in project.mentors:
      raise AccessViolation(DEF_MENTOR_EVAL_DOES_NOT_BELONG_TO_YOU)

  def canApplyStudent(self, edit_url):
    """Checks if the user can apply as a student.
    """
    self.isLoggedIn()

    if self.data.profile and self.data.profile.student_info:
      raise RedirectRequest(edit_url)

    self.studentSignupActive()

    if not self.data.profile:
      return

    raise AccessViolation(
        DEF_ALREADY_PARTICIPATING_AS_NON_STUDENT % self.data.program.name)
    
  def canStudentDownloadForms(self):
    """Checks if the user can download the forms.
    """
    self.isProfileActive()
    si = self.data.profile.student_info
    if si:
      if si.number_of_projects > 0:
        return
    raise AccessViolation(DEF_NOT_ALLOWED_TO_DOWNLOAD_FORM)
  
class DeveloperAccessChecker(access_checker.DeveloperAccessChecker):
  pass

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

"""Module for the GSoC organization page listing all evaluations.
"""


from django.utils.dateformat import format
from django.utils.translation import ugettext

from soc.logic.exceptions import AccessViolation
from soc.views.helper import lists
from soc.views.helper import url_patterns
from soc.views.helper.surveys import dictForSurveyModel

from soc.modules.gsoc.logic import project as project_logic
from soc.modules.gsoc.logic.evaluations import evaluationRowAdder
from soc.modules.gsoc.logic.survey_record import getEvalRecord
from soc.modules.gsoc.models.grading_project_survey import GradingProjectSurvey
from soc.modules.gsoc.models.grading_project_survey_record import \
    GSoCGradingProjectSurveyRecord
from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.models.project_survey import ProjectSurvey
from soc.modules.gsoc.models.project_survey_record import \
    GSoCProjectSurveyRecord
from soc.modules.gsoc.views import dashboard
from soc.modules.gsoc.views.helper.url_patterns import url


DEF_NOT_ADMIN = ugettext(
    'You must be an organization administrator for at least one '
    'organization in the program to access this page.')


class StudentEvaluationComponent(dashboard.Component):
  """Component for listing student evaluations for organizations.
  """

  def __init__(self, request, data, evals, idx):
    """Initializes this component.

    Args:
      request: The Django HTTP Request object
      data: The RequestData object containing the entities from the request
      evals: Dictionary containing evaluations for which the list must be built
      idx: The id for this list component
    """
    self.request = request
    self.data = data
    self.evals = evals
    self.idx = idx

    self.record = None

    list_config = lists.ListConfiguration(add_key_column=False)
    list_config.addColumn(
        'key', 'Key',
        (lambda ent, eval, *args: "%s/%s/%s" % (
            eval, ent.parent().key().name(),
            ent.key().id())), hidden=True)
    list_config.addColumn(
        'evaluation', 'Evaluation',
        lambda ent, eval, *args: eval.capitalize() if eval else '')
    list_config.addColumn(
        'student', 'Student',
        lambda entity, eval, *args: entity.parent().name())
    list_config.addSimpleColumn('title', 'Project Title')
    list_config.addColumn('org', 'Organization',
                          lambda entity, eval, *args: entity.org.name)
    list_config.addColumn(
        'mentors', 'Mentors',
        lambda ent, eval, mentors, *args: ', '.join(
            [mentors.get(m).name() for m in ent.mentors]))
    list_config.addColumn(
        'status', 'Status', self._getStatus)
    list_config.addColumn(
        'created', 'Submitted on',
        lambda ent, eval, *args: format(
            self.record.created, dashboard.DATETIME_FORMAT) if \
            self.record else 'N/A')
    list_config.addColumn(
        'modified', 'Last modified on',
        lambda ent, eval, *args: format(
            self.record.modified, dashboard.DATETIME_FORMAT) if (
            self.record and self.record.modified) else 'N/A')
    list_config.setDefaultSort('student')

    def getRowAction(entity, eval, *args):
      eval_ent = self.evals.get(eval)

      if not self.data.timeline.afterSurveyEnd(eval_ent):
        return ''

      url = self.data.redirect.survey_record(
          eval, entity.key().id_or_name(),
          entity.parent().link_id).urlOf('gsoc_show_student_evaluation')
      return url
    list_config.setRowAction(getRowAction)

    self._list_config = list_config

  def _getStatus(self, entity, eval, *args):
    eval_ent = self.evals.get(eval)
    self.record = getEvalRecord(GSoCProjectSurveyRecord, eval_ent, entity)
    return dashboard.colorize(bool(self.record), "Submitted", "Not submitted")

  def context(self):
    list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=self.idx, preload_list=False)

    return {
        'name': 'student_evaluations',
        'lists': [list],
        'title': 'Student Evaluations',
        'description': ugettext('Student evaluations'),
        'idx': self.idx,
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == self.idx:
      list_query = project_logic.getProjectsQueryForEvalForOrgs(
          orgs=self.data.org_admin_for)

      starter = lists.keyStarter
      prefetcher = lists.listModelPrefetcher(
          GSoCProject, ['org'],
          ['mentors', 'failed_evaluations'],
          parent=True)
      row_adder = evaluationRowAdder(self.evals)

      response_builder = lists.RawQueryContentResponseBuilder(
          self.request, self._list_config, list_query,
          starter, prefetcher=prefetcher, row_adder=row_adder)
      return response_builder.build()
    else:
      return None

  def templatePath(self):
    return'v2/modules/gsoc/dashboard/list_component.html'


class MentorEvaluationComponent(StudentEvaluationComponent):
  """Component for listing mentor evaluations for organizations.
  """

  def __init__(self, request, data, evals, idx):
    """Initializes this component.

    Args:
      request: The Django HTTP Request object
      data: The RequestData object containing the entities from the request
      evals: Dictionary containing evaluations for which the list must be built
      idx: The id for this list component
    """
    super(MentorEvaluationComponent, self).__init__(request, data, evals, idx)

    self.record = None

    self._list_config.addColumn(
        'grade', 'Grade', self._getGrade)
    self._list_config.setRowAction(lambda entity, eval, *args:
        data.redirect.survey_record(
            eval, entity.key().id_or_name(),
            entity.parent().link_id).urlOf(
                'gsoc_take_mentor_evaluation'))

  def _getStatus(self, entity, eval, *args):
    eval_ent = self.evals.get(eval)
    self.record = getEvalRecord(GSoCGradingProjectSurveyRecord,
                                eval_ent, entity)
    return dashboard.colorize(
        bool(self.record), "Submitted", "Not submitted")

  def _getGrade(self, entity, eval, *args):
    if self.record:
      return dashboard.colorize(
        self.record.grade, "Pass", "Fail")
    else:
      return "N/A"

  def context(self):
    context = super(MentorEvaluationComponent, self).context()
    context['title'] = 'Mentor Evaluations'
    context['description'] = ugettext('Student evaluations')
    context['name'] = 'mentor_evaluations'
    return context


class Dashboard(dashboard.DashboardPage):
  """View for the list of all the organization related components.
  """

  def djangoURLPatterns(self):
    """The URL pattern for the org evaluations.
    """
    return [
        url(r'dashboard/org/%s$' % url_patterns.PROGRAM, self,
            name='gsoc_org_dashboard')]

  def checkAccess(self):
    """Denies access if the user is not an org admin.
    """
    self.check.isProfileActive()

    if self.data.is_org_admin:
      return

    raise AccessViolation(DEF_NOT_ADMIN)

  def components(self):
    """Returns the components that are active on the page.
    """
    program = self.data.program
    mentor_evals =  dictForSurveyModel(GradingProjectSurvey, program,
                                       ['midterm', 'final'])
    student_evals = dictForSurveyModel(ProjectSurvey, program,
                                       ['midterm', 'final'])

    components = [
        MentorEvaluationComponent(self.request, self.data, mentor_evals, 0),
        StudentEvaluationComponent(self.request, self.data, student_evals, 1)]
    return components

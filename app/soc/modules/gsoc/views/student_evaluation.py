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

"""Module for the GSoC project student survey.
"""


from soc.views import forms
from soc.views import survey
from soc.views.helper import lists

from django.utils.translation import ugettext

from soc.logic.exceptions import AccessViolation
from soc.logic.exceptions import RedirectRequest
from soc.views.helper.access_checker import isSet
from soc.views.readonly_template import SurveyRecordReadOnlyTemplate

from soc.modules.gsoc.models.project_survey import ProjectSurvey
from soc.modules.gsoc.models.project_survey_record import \
    GSoCProjectSurveyRecord
from soc.modules.gsoc.views import forms as gsoc_forms
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.base_templates import LoggedInMsg
from soc.modules.gsoc.views.helper import url_patterns


DEF_CANNOT_ACCESS_EVALUATION = ugettext(
    'Organization Administrators can view this evaluation submitted by the '
    'student only after the evaluation deadline. Please visit this page '
    'after the evaluation deadline has passed.')


class GSoCStudentEvaluationEditForm(gsoc_forms.SurveyEditForm):
  """Form to create/edit GSoC project survey for students.
  """

  class Meta:
    model = ProjectSurvey
    css_prefix = 'gsoc-student-eval-edit'
    exclude = ['scope', 'author', 'modified_by', 'survey_content',
               'scope_path', 'link_id', 'prefix', 'read_access',
               'write_access', 'taking_access', 'is_featured']


class GSoCStudentEvaluationTakeForm(gsoc_forms.SurveyTakeForm):
  """Form for students to respond to the survey during evaluations.
  """

  class Meta:
    model = GSoCProjectSurveyRecord
    css_prefix = 'gsoc-student-eval-record'
    exclude = ['project', 'org', 'user', 'survey', 'created', 'modified']


class GSoCStudentEvaluationEditPage(RequestHandler):
  """View for creating/editing student evalution.
  """

  def djangoURLPatterns(self):
    return [
         url_patterns.url(r'eval/student/edit/%s$' % url_patterns.SURVEY,
             self, name='gsoc_edit_student_evaluation'),
    ]

  def checkAccess(self):
    self.check.isHost()
    self.mutator.studentEvaluationFromKwargs(raise_not_found=False)

  def templatePath(self):
    return 'v2/modules/gsoc/_evaluation.html'

  def context(self):
    if self.data.student_evaluation:
      form = GSoCStudentEvaluationEditForm(
          self.data.POST or None, instance=self.data.student_evaluation)
    else:
      form = GSoCStudentEvaluationEditForm(self.data.POST or None)

    page_name = ugettext('Edit - %s' % (self.data.student_evaluation.title)) \
        if self.data.student_evaluation else 'Create new student evaluation'
    context = {
        'page_name': page_name,
        'post_url': self.redirect.survey().urlOf(
            'gsoc_edit_student_evaluation'),
        'forms': [form],
        'error': bool(form.errors),
        }

    return context

  def evaluationFromForm(self):
    """Create/edit the student evaluation entity from form.

    Returns:
      a newly created or updated student evaluation entity or None.
    """
    if self.data.student_evaluation:
      form = GSoCStudentEvaluationEditForm(
          self.data.POST, instance=self.data.student_evaluation)
    else:
      form = GSoCStudentEvaluationEditForm(self.data.POST)

    if not form.is_valid():
      return None

    form.cleaned_data['modified_by'] = self.data.user

    if not self.data.student_evaluation:
      form.cleaned_data['link_id'] = self.data.kwargs.get('survey')
      form.cleaned_data['prefix'] = 'gsoc_program'
      form.cleaned_data['author'] = self.data.user
      form.cleaned_data['scope'] = self.data.program
      # kwargs which defines an evaluation
      fields = ['sponsor', 'program', 'survey']

      key_name = '/'.join(['gsoc_program'] +
                          [self.data.kwargs[field] for field in fields])

      entity = form.create(commit=True, key_name=key_name)
    else:
      entity = form.save(commit=True)

    return entity

  def post(self):
    evaluation = self.evaluationFromForm()
    if evaluation:
      r = self.redirect.survey()
      r.to('gsoc_edit_student_evaluation', validated=True)
    else:
      self.get()

class GSoCStudentEvaluationTakePage(RequestHandler):
  """View for students to submit their evaluation.
  """

  def djangoURLPatterns(self):
    return [
         url_patterns.url(r'eval/student/%s$' % url_patterns.SURVEY_RECORD,
             self, name='gsoc_take_student_evaluation'),
    ]

  def checkAccess(self):
    self.mutator.projectFromKwargs()
    self.mutator.studentEvaluationFromKwargs()
    self.mutator.studentEvaluationRecordFromKwargs()

    assert isSet(self.data.student_evaluation)

    if self.data.is_host:
      return

    show_url = self.data.redirect.survey_record(
          self.data.student_evaluation.link_id).urlOf(
          'gsoc_show_student_evaluation')
    self.check.isSurveyActive(self.data.student_evaluation, show_url)

    self.check.isProfileActive()
    if self.data.orgAdminFor(self.data.project.org):
      raise RedirectRequest(show_url)

    self.check.canUserTakeSurvey(self.data.student_evaluation, 'student')
    self.check.isStudentForSurvey()

  def templatePath(self):
    return 'v2/modules/gsoc/_evaluation_take.html'

  def context(self):
    if self.data.student_evaluation_record:
      form = GSoCStudentEvaluationTakeForm(
          self.data.student_evaluation,
          self.data.POST or None, instance=self.data.student_evaluation_record)
    else:
      form = GSoCStudentEvaluationTakeForm(
          self.data.student_evaluation, self.data.POST or None)

    context = {
        'page_name': '%s' % (self.data.student_evaluation.title),
        'description': self.data.student_evaluation.content,
        'form_top_msg': LoggedInMsg(self.data, apply_link=False,
                                    div_name='user-login'),
        'project': self.data.project.title,
        'forms': [form],
        'error': bool(form.errors),
        }

    return context

  def recordEvaluationFromForm(self):
    """Create/edit a new student evaluation record based on the form input.

    Returns:
      a newly created or updated evaluation record entity or None
    """
    if self.data.student_evaluation_record:
      form = GSoCStudentEvaluationTakeForm(
          self.data.student_evaluation,
          self.data.POST, instance=self.data.student_evaluation_record)
    else:
      form = GSoCStudentEvaluationTakeForm(
          self.data.student_evaluation, self.data.POST)

    if not form.is_valid():
      return None

    if not self.data.student_evaluation_record:
      form.cleaned_data['project'] = self.data.project
      form.cleaned_data['org'] = self.data.project.org
      form.cleaned_data['user'] = self.data.user
      form.cleaned_data['survey'] = self.data.student_evaluation
      entity = form.create(commit=True)
    else:
      entity = form.save(commit=True)

    return entity

  def post(self):
    student_evaluation_record = self.recordEvaluationFromForm()
    if student_evaluation_record:
      r = self.redirect.survey_record(
          self.data.student_evaluation.link_id)
      r.to('gsoc_take_student_evaluation', validated=True)
    else:
      self.get()


class GSoCStudentEvaluationPreviewPage(RequestHandler):
  """View for the host to preview the evaluation.
  """

  def djangoURLPatterns(self):
    return [
         url_patterns.url(
             r'eval/student/preview/%s$' % url_patterns.SURVEY,
             self, name='gsoc_preview_student_evaluation'),
    ]

  def checkAccess(self):
    self.check.isHost()
    self.mutator.studentEvaluationFromKwargs(raise_not_found=False)

  def templatePath(self):
    return 'v2/modules/gsoc/_evaluation_take.html'

  def context(self):
    form = GSoCStudentEvaluationTakeForm(self.data.student_evaluation)

    context = {
        'page_name': '%s' % (self.data.student_evaluation.title),
        'description': self.data.student_evaluation.content,
        'form_top_msg': LoggedInMsg(self.data, apply_link=False,
                                    div_name='user-login'),
        'project': "The Project Title",
        'forms': [form],
        'error': bool(form.errors),
        }

    return context


class GSoCStudentEvaluationRecordsList(RequestHandler):
  """View for listing all records of a GSoCGProjectSurveyRecord.
  """

  def djangoURLPatterns(self):
    return [
         url_patterns.url(
             r'eval/student/records/%s$' % url_patterns.SURVEY,
             self, name='gsoc_list_student_eval_records')
         ]

  def checkAccess(self):
    """Defines access checks for this list, all hosts should be able to see it.
    """
    self.check.isHost()
    self.mutator.studentEvaluationFromKwargs()

  def context(self):
    """Returns the context of the page to render.
    """
    record_list = self._createSurveyRecordList()

    page_name = ugettext('Records - %s' % (self.data.student_evaluation.title))
    context = {
        'page_name': page_name,
        'record_list': record_list,
        }
    return context

  def jsonContext(self):
    """Handler for JSON requests.
    """
    idx = lists.getListIndex(self.request)
    if idx == 0:
      record_list = self._createSurveyRecordList()
      return record_list.listContentResponse(
          self.request, prefetch=['org', 'project']).content()
    else:
      super(GSoCStudentEvaluationRecordsList, self).jsonContext()

  def _createSurveyRecordList(self):
    """Creates a SurveyRecordList for the requested survey.
    """
    record_list = survey.SurveyRecordList(
        self.data, self.data.student_evaluation, GSoCProjectSurveyRecord, idx=0)

    record_list.list_config.addColumn(
        'project', 'Project', lambda ent, *args: ent.project.title)
    record_list.list_config.addColumn(
        'org', 'Organization', lambda ent, *args: ent.org.name)

    return record_list

  def templatePath(self):
    return 'v2/modules/gsoc/student_eval/record_list.html'


class GSoCStudentEvaluationReadOnlyTemplate(SurveyRecordReadOnlyTemplate):
  """Template to construct readonly student evaluation record.
  """

  class Meta:
    model = GSoCProjectSurveyRecord
    css_prefix = 'gsoc-student-eval-show'
    survey_name = 'Student Evaluation'


class GSoCStudentEvaluationShowPage(RequestHandler):
  """View to display the readonly page for student evaluation.
  """

  def djangoURLPatterns(self):
    return [
        url_patterns.url(r'eval/student/show/%s$' % url_patterns.SURVEY_RECORD,
            self, name='gsoc_show_student_evaluation'),
    ]

  def checkAccess(self):
    self.mutator.projectFromKwargs()
    self.mutator.studentEvaluationFromKwargs()
    self.mutator.studentEvaluationRecordFromKwargs()

    assert isSet(self.data.project)
    assert isSet(self.data.student_evaluation)

    self.check.isProfileActive()
    if self.data.orgAdminFor(self.data.project.org):
      self.data.role = 'org_admin'
      if self.data.timeline.afterSurveyEnd(self.data.student_evaluation):
        return
      else:
        raise AccessViolation(DEF_CANNOT_ACCESS_EVALUATION)

    self.check.isStudentForSurvey()
    self.data.role = 'student'

  def templatePath(self):
    return 'v2/modules/gsoc/_survey/show.html'

  def context(self):
    assert isSet(self.data.program)
    assert isSet(self.data.timeline)
    assert isSet(self.data.student_evaluation_record)

    record = self.data.student_evaluation_record
    student = self.data.url_profile

    context = {
        'page_name': 'Student evaluation - %s' % (student.name()),
        'student': student.name(),
        'organization': self.data.project.org.name,
        'project': self.data.project.title,
        'top_msg': LoggedInMsg(self.data, apply_link=False),
        'css_prefix': GSoCStudentEvaluationReadOnlyTemplate.Meta.css_prefix,
        }

    if record:
      context['record'] = GSoCStudentEvaluationReadOnlyTemplate(record)

    if self.data.timeline.surveyPeriod(self.data.student_evaluation):
      if self.data.role == 'student':
        context['update_link'] = self.data.redirect.survey_record(
            self.data.student_evaluation.link_id).urlOf(
            'gsoc_take_student_evaluation')
      else:
        context['submission_msg'] = ugettext(
            'Bug your student to submit the evaluation.')

    return context

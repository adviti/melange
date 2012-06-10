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

"""Module for displaying GradingSurveyGroups and records.
"""


from google.appengine.api import taskqueue

from soc.views import forms
from soc.views.helper import lists
from soc.views.helper import url_patterns
from soc.views.helper.access_checker import isSet
from soc.views.template import Template

from soc.modules.gsoc.logic import grading_record
from soc.modules.gsoc.models.grading_record import GSoCGradingRecord
from soc.modules.gsoc.views import forms as gsoc_forms
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns as gsoc_url_patterns
from soc.modules.gsoc.views.helper.url_patterns import url


class GradingRecordsOverview(RequestHandler):
  """View to display all GradingRecords for a single group.
  """

  def djangoURLPatterns(self):
    return [
        url(r'grading_records/overview/%s$' % url_patterns.ID,
         self, name='gsoc_grading_record_overview'),
    ]

  def checkAccess(self):
    self.mutator.surveyGroupFromKwargs()
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/grading_record/overview.html'

  def context(self):
    return {
        'page_name': 'Evaluation Group Overview',
        'record_list': GradingRecordsList(self.request, self.data)
        }

  def jsonContext(self):
    """Handler for JSON requests.
    """
    idx = lists.getListIndex(self.request)
    if idx == 0:
      return GradingRecordsList(self.request, self.data).listContent().content()
    else:
      super(GradingRecordsOverview, self).jsonContext()

  def post(self):
    """Handles the POST request from the list and starts the appropriate task.
    """
    post_dict = self.data.POST

    if post_dict['button_id'] == 'update_records':
      task_params = {'group_key': self.data.survey_group.key().id_or_name()}
      task_url = '/tasks/gsoc/grading_record/update_records'

      task = taskqueue.Task(params=task_params, url=task_url)
      task.add()
    elif post_dict['button_id'] == 'update_projects':
      task_params = {'group_key': self.data.survey_group.key().id_or_name(),
                     'send_mail': 'true'}
      task_url = '/tasks/gsoc/grading_record/update_projects'

      task = taskqueue.Task(params=task_params, url=task_url)
      task.add()


class GradingRecordsList(Template):
  """Lists all GradingRecords for a single GradingSurveyGroup.
  """

  def __init__(self, request, data):
    """Initializes the template.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    self.request = request
    self.data = data

    list_config = lists.ListConfiguration(add_key_column=False)
    list_config.addColumn(
        'key', 'Key',
        (lambda ent, *args: "%s/%d/%d" % (
            ent.parent_key().parent().name(),
            ent.parent_key().id(),
            ent.key().id())),
        hidden=True)

    title_func = lambda rec, *args: rec.parent().title
    list_config.addColumn('project_title', 'Project Title', title_func)
    org_func = lambda rec, *args: rec.parent().org.name
    list_config.addColumn('org_name', 'Organization', org_func)
    stud_rec_func = lambda rec, *args: \
        'Present' if rec.student_record else 'Missing'
    list_config.addColumn('student_record', 'Survey by Student', stud_rec_func)
    stud_id_func = lambda rec, *args: rec.parent().parent().link_id
    list_config.addColumn('student_id', 'Student Link Id', stud_id_func, hidden=True)

    list_config.addPostButton('update_records', 'Update Records', '', [0,'all'], [])
    list_config.addPostButton('update_projects', 'Update Projects', '', [0,'all'], [])

    def mentorRecordInfo(rec, *args):
      """Displays information about a GradingRecord's mentor_record property.
      """
      if not rec.mentor_record:
        return 'Missing'

      if rec.mentor_record.grade:
        return 'Passing Grade'
      else:
        return 'Fail Grade'

    list_config.addColumn('mentor_record', 'Survey by Mentor', mentorRecordInfo)

    list_config.addSimpleColumn('grade_decision', 'Decision')
    r = data.redirect
    list_config.setRowAction(lambda e, *args:
        r.grading_record(e).urlOf('gsoc_grading_record_detail'))

    self._list_config = list_config

  def context(self):
    """Returns the context for the current template.
    """
    list = lists.ListConfigurationResponse(self.data, self._list_config, idx=0)
    return {'lists': [list]}

  def listContent(self):
    """Returns the ListContentResponse object that is constructed from the data.
    """
    q = GSoCGradingRecord.all()
    q.filter('grading_survey_group', self.data.survey_group)

    starter = lists.keyStarter
    prefetcher = lists.modelPrefetcher(
        GSoCGradingRecord, ['mentor_record', 'student_record'], parent=True)

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self._list_config, q,
        starter, prefetcher=prefetcher)
    return response_builder.build()

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return 'v2/soc/list/lists.html'


class GradingRecordForm(gsoc_forms.GSoCModelForm):
  """Django form to edit a GradingRecord manually.
  """

  class Meta:
    model = GSoCGradingRecord
    css_prefix = 'gsoc_grading_record'
    fields = ['grade_decision', 'locked']
    widgets = forms.choiceWidgets(GSoCGradingRecord, ['grade_decision'])


class GradingRecordDetails(RequestHandler):
  """View to display GradingRecord details.
  """

  def djangoURLPatterns(self):
    return [
        url(r'grading_records/detail/%s$' % gsoc_url_patterns.GRADING_RECORD,
         self, name='gsoc_grading_record_detail'),
    ]

  def checkAccess(self):
    self.mutator.gradingSurveyRecordFromKwargs()
    self.check.isHost()

  def context(self):
    assert isSet(self.data.record)

    record = self.data.record

    if self.data.POST:
      record_form = GradingRecordForm(self.data.POST)
    else:
      # locked is initially set to true because the user is editing it manually
      record_form = GradingRecordForm(instance=record, initial={'locked': True})

    return {
        'page_name': 'Grading Record Details',
        'record': record,
        'record_form': record_form,
        }

  def post(self):
    """Handles the POST request when editing a GradingRecord.
    """
    assert isSet(self.data.record)

    record_form = GradingRecordForm(self.data.POST)

    if not record_form.is_valid():
      return self.get()

    decision = record_form.cleaned_data['grade_decision']
    locked = record_form.cleaned_data['locked']

    record = self.data.record
    record.grade_decision = decision
    record.locked = locked
    record.put()

    grading_record.updateProjectsForGradingRecords([record])

    # pass along these params as POST to the new task
    task_params = {'record_key': str(record.key())}
    task_url = '/tasks/gsoc/grading_record/mail_result'

    mail_task = taskqueue.Task(params=task_params, url=task_url)
    mail_task.add('mail')

    self.redirect.id(record.grading_survey_group.key().id_or_name())
    self.redirect.to('gsoc_grading_record_overview')

  def templatePath(self):
    return 'v2/modules/gsoc/grading_record/details.html'

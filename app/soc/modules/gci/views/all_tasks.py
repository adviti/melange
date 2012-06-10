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

"""Module containing the view for GCI tasks list page.
"""


from soc.logic.exceptions import AccessViolation
from soc.views.helper import url_patterns
from soc.views.helper import lists
from soc.views.template import Template

from soc.modules.gci.logic import task as task_logic
from soc.modules.gci.models.task import CLAIMABLE
from soc.modules.gci.models.task import GCITask
from soc.modules.gci.views.base import RequestHandler
from soc.modules.gci.views.helper.url_patterns import url


class TaskList(Template):
  """Template for list of tasks.
  """

  def __init__(self, request, data, columns):
    self.request = request
    self.data = data
    r = data.redirect

    self._list_config = lists.ListConfiguration()

    if 'title' in columns:
      self._addTitleColumn()

    if 'organization' in columns:
      self._addOrganizationColumn()
    
    if 'mentors' in columns:
      self._addMentorsColumn()
    
    if 'status' in columns:
      self._addStatusColumn()

    #list_config.addColumn(
    #    'task_type', 'Type',
    #    lambda entity, _, all_d, all_t, *args: entity.taskType(all_t))
    #list_config.addColumn('time_to_complete', 'Time to complete',
    #                      lambda entity, *args: entity.taskTimeToComplete())

    self._list_config.setRowAction(
        lambda e, *args: r.id(e.key().id()).urlOf('gci_view_task'))

  def context(self):
    description = 'List of tasks for %s' % (
            self.data.program.name)

    task_list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0, description)

    return {
        'lists': [task_list],
    }

  def getListData(self):
    idx = lists.getListIndex(self.request)
    if idx == 0:
      q = self._getQueryForTasks()

      starter = lists.keyStarter
      prefetcher = lists.listModelPrefetcher(
          GCITask, ['org'], ['mentors'])

      response_builder = lists.RawQueryContentResponseBuilder(
          self.request, self._list_config, q,
          starter=starter, prefetcher=prefetcher)

      return response_builder.build()
    else:
      return None

  def templatePath(self):
    return 'v2/modules/gci/task/_task_list.html'

  def _addMentorsColumn(self):
    self._list_config.addColumn('mentors', 'Mentors',
        lambda entity, mentors, *args: ', '.join(
            mentors[i].name() for i in entity.mentors))

  def _addOrganizationColumn(self):
    self._list_config.addColumn(
        'org', 'Organization', lambda entity, *args: entity.org.name)

  def _addStatusColumn(self):
    self._list_config.addSimpleColumn('status', 'Status')

  def _addTitleColumn(self):
    self._list_config.addSimpleColumn('title', 'Title')

  def _getQueryForTasks(self):
    raise NotImplementedError


class AllTasksList(TaskList):
  """Template for list of all tasks which are claimable for the program.
  """

  _LIST_COLUMNS = ['title', 'organization', 'mentors', 'status']

  def __init__(self, request, data):
    super(AllTasksList, self).__init__(request, data, self._LIST_COLUMNS)

  def _getQueryForTasks(self):
    return task_logic.queryClaimableTasksForProgram(self.data.program)


class TaskListPage(RequestHandler):
  """View for the list task page.
  """

  TASK_LIST_COLUMNS = ['title', 'organization', 'mentors', 'status']

  def templatePath(self):
    return 'v2/modules/gci/task/task_list.html'

  def djangoURLPatterns(self):
    return [
        url(r'tasks/%s$' % url_patterns.PROGRAM, self,
            name='gci_list_tasks'),
    ]

  def checkAccess(self):
    pass

  def jsonContext(self):
    list_content = AllTasksList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation('You do not have access to this data')

    return list_content.content()

  def context(self):
    return {
        'page_name': "Tasks for %s" % self.data.program.name,
        'task_list': AllTasksList(self.request, self.data),
    }

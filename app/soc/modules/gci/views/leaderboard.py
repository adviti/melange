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
"""Module containing the view for GCI leaderboard page.
"""

from soc.logic.exceptions import AccessViolation

from soc.views.base_templates import ProgramSelect
from soc.views.helper import lists
from soc.views.helper import url_patterns
from soc.views.template import Template

from soc.modules.gci.logic import ranking as ranking_logic
from soc.modules.gci.logic import task as task_logic

from soc.modules.gci.models.score import GCIScore

from soc.modules.gci.views.all_tasks import TaskList
from soc.modules.gci.views import common_templates
from soc.modules.gci.views.base import RequestHandler
from soc.modules.gci.views.helper import url_names
from soc.modules.gci.views.helper.url_patterns import url


class ProgramSelect(ProgramSelect):
  """Program select template.
  """

  def templatePath(self):
    return "v2/modules/gci/leaderboard/_program_select.html"


class LeaderboardList(Template):
  """Template for the leaderboard list.
  """

  LEADERBOARD_LIST_IDX = 0

  def __init__(self, request, data):
    self.request = request
    self.data = data
    r = data.redirect

    list_config = lists.ListConfiguration(add_key_column=False)
    list_config.addColumn('key', 'Key', (lambda ent, *args: "%s" % (
        ent.parent().key().id_or_name())), hidden=True)
    list_config.addColumn('student', 'Student',
        lambda e, *args: e.parent().name())
    list_config.addSimpleColumn('points', 'Points')
    list_config.addColumn('tasks', 'Tasks', lambda e, *args: len(e.tasks))
    list_config.setDefaultSort('points', 'desc')

    list_config.setRowAction(
        lambda e, *args: r.profile(e.parent().link_id).urlOf(
            url_names.GCI_STUDENT_TASKS))

    self._list_config = list_config

  def context(self):
    description = 'Leaderboard for %s' % (
            self.data.program.name)

    leaderboard_list = lists.ListConfigurationResponse(
        self.data, self._list_config, self.LEADERBOARD_LIST_IDX, description)

    return {
        'lists': [leaderboard_list],
    }

  def getListData(self):
    idx = lists.getListIndex(self.request)
    if idx == self.LEADERBOARD_LIST_IDX:
      q = GCIScore.all()
      q.filter('program', self.data.program)

      skipper = lambda entity, start: entity.points <= 0
      prefetcher = lists.modelPrefetcher(GCIScore, [], True)

      response_builder = lists.RawQueryContentResponseBuilder(self.request,
          self._list_config, q, lists.keyStarter,
          skipper=skipper, prefetcher=prefetcher)

      return response_builder.build()
    else:
      return None

  def templatePath(self):
    return 'v2/modules/gci/leaderboard/_leaderboard_list.html'


class AllStudentTasksList(TaskList):
  """Template for list of all tasks which have been completed by
  the specified student.
  """

  _LIST_COLUMNS = ['title', 'organization']

  def __init__(self, request, data):
    super(AllStudentTasksList, self).__init__(
        request, data, self._LIST_COLUMNS)

  def context(self):
    description = 'List of tasks closed by %s' % (
            self.data.url_profile.name())

    task_list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0, description)

    return {
        'lists': [task_list],
    }

  def _getQueryForTasks(self):
    return task_logic.queryAllTasksClosedByStudent(self.data.url_profile)


class YourScore(Template):
  """Template that is used to show score of the current user, provided
  he or she is a student.
  """

  def __init__(self, data):
    self.data = data
    self.score = None

    if self.data.profile and self.data.profile.student_info:
      self.score = ranking_logic.get(self.data.profile)

  def context(self):
    return {} if not self.score else {
        'points': self.score.points,
        'tasks': len(self.score.tasks),
        'my_tasks_link': self.data.redirect.profile(
            self.data.profile.link_id).urlOf(url_names.GCI_STUDENT_TASKS)
        }

  def render(self):
    """This template should only render to a non-empty string, if the
    current user is a student.
    """
    if not self.score:
      return ''

    return super(YourScore, self).render()

  def templatePath(self):
    return "v2/modules/gci/leaderboard/_your_score.html"


class LeaderboardPage(RequestHandler):
  """View for the leaderboard page.
  """

  def templatePath(self):
    return 'v2/modules/gci/leaderboard/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'leaderboard/%s$' % url_patterns.PROGRAM, self,
            name=url_names.GCI_LEADERBOARD),
    ]

  def checkAccess(self):
    pass

  def jsonContext(self):
    list_content = LeaderboardList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation('You do not have access to this data')

    return list_content.content()

  def context(self):
    return {
        'page_name': "Leaderboard for %s" % self.data.program.name,
        'leaderboard_list': LeaderboardList(self.request, self.data),
        'timeline': common_templates.Timeline(self.data),
        'complete_percentage': self.data.timeline.completePercentage(),
        'your_score': YourScore(self.data),
        'program_select': ProgramSelect(self.data, url_names.GCI_LEADERBOARD),
    }


class StudentTasksPage(RequestHandler):
  """View for the list of all the tasks closed by the specified student.
  """

  def templatePath(self):
    return 'v2/modules/gci/leaderboard/student_tasks.html'

  def djangoURLPatterns(self):
    return [
        url(r'student_tasks/%s$' % url_patterns.PROFILE, self,
            name=url_names.GCI_STUDENT_TASKS),
    ]

  def checkAccess(self):
    pass

  def jsonContext(self):
    self.mutator.studentFromKwargs()
    list_content = AllStudentTasksList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation('You do not have access to this data')

    return list_content.content()

  def context(self):
    self.mutator.studentFromKwargs()
    return {
        'page_name': "Tasks closed by %s" % self.data.url_profile.name(),
        'tasks_list': AllStudentTasksList(self.request, self.data),
    }

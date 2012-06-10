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

"""Module containing the views for listing all the projects accepted
into a GSoC program.
"""


from soc.logic.exceptions import AccessViolation
from soc.views.base_templates import ProgramSelect
from soc.views.helper import lists
from soc.views.helper import url_patterns
from soc.views.template import Template

from soc.modules.gsoc.logic import project as project_logic
from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper.url_patterns import url


class ProjectList(Template):
  """Template for listing the student projects accepted in the program.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data

    r = data.redirect
    list_config = lists.ListConfiguration(add_key_column=False)
    list_config.addColumn('key', 'Key', (lambda ent, *args: "%s/%s" % (
        ent.parent().key().name(), ent.key().id())), hidden=True)
    list_config.addColumn('student', 'Student',
                          lambda entity, *args: entity.parent().name())
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn('org', 'Organization',
                          lambda entity, *args: entity.org.name)
    list_config.setDefaultPagination(False)
    list_config.setDefaultSort('student')
    list_config.setRowAction(lambda e, *args:
        r.project(id=e.key().id_or_name(), student=e.parent().link_id).
        urlOf('gsoc_project_details'))
    self._list_config = list_config

  def context(self):
    list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=0,
        description='List of projects accepted into %s' % (
            self.data.program.name))

    return {
        'lists': [list],
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == 0:
      list_query = project_logic.getAcceptedProjectsQuery(
          program=self.data.program)

      starter = lists.keyStarter
      prefetcher = lists.modelPrefetcher(GSoCProject, ['org'],
                                         parent=True)

      response_builder = lists.RawQueryContentResponseBuilder(
          self.request, self._list_config, list_query,
          starter, prefetcher=prefetcher)
      return response_builder.build()
    else:
      return None

  def templatePath(self):
    return "v2/modules/gsoc/projects_list/_project_list.html"


class ListProjects(RequestHandler):
  """View methods for listing all the projects accepted into a program.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/projects_list/base.html'

  def djangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    return [
        url(r'projects/list/%s$' % url_patterns.PROGRAM, self,
            name='gsoc_accepted_projects')
    ]

  def checkAccess(self):
    """Access checks for the view.
    """
    self.check.acceptedStudentsAnnounced()

  def jsonContext(self):
    """Handler for JSON requests.
    """
    list_content = ProjectList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def context(self):
    """Handler for GSoC Accepted Projects List page HTTP get request.
    """
    program = self.data.program

    return {
        'page_name': '%s - Accepted Projects' % program.short_name,
        'program_name': program.name,
        'project_list': ProjectList(self.request, self.data),
        'program_select': ProgramSelect(self.data, 'gsoc_accepted_projects'),
    }

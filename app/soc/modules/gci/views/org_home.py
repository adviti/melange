# Copyright 2011 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing the Org Homepage view.
"""
from soc.logic.exceptions import AccessViolation
from soc.views.helper import lists
from soc.views.helper import url_patterns
from soc.views.template import Template

from soc.modules.gci.models.task import CLAIMABLE
from soc.modules.gci.models.task import GCITask
from soc.modules.gci.views.base import RequestHandler
from soc.modules.gci.views.helper.url_patterns import url
from soc.modules.gci.views.helper import url_names


class AboutUs(Template):
  """About us template.
  """
  def __init__(self, data):
    self.data = data
    
  def context(self):
    org = self.data.organization
    return {
        'description': org.description,
        'logo_url': org.logo_url,
        'homepage': org.home_page,
        'short_name': org.short_name,
    }
  
  def templatePath(self):
    return 'v2/modules/gci/org_home/_about_us.html'


class ContactUs(Template):
  """Organization Contact template.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    return {
        'organization': self.data.organization,
    }

  def templatePath(self):
    return "v2/modules/gci/org_home/_contact_us.html"


class OpenTasksList(Template):
  """List to display all the open tasks for the current organization.
  """
  def __init__(self, request, data):
    self.request = request
    self.data = data
    list_config = lists.ListConfiguration()
    
    list_config.addSimpleColumn('title', 'Title')
    #list_config.addColumn(
    #    'task_type', 'Type',
    #    lambda entity, all_d, all_t, *args: entity.taskType(all_t))
    #list_config.addColumn('arbit_tag', 'Tags', lambda entity,
    #                      *args: entity.taskArbitTag())
    list_config.addColumn('time_to_complete', 'Time to complete',
                          lambda entity, *args: entity.taskTimeToComplete())
    
    list_config.setRowAction(
        lambda e, *args: data.redirect.id(e.key().id()).urlOf(url_names.GCI_VIEW_TASK))

    self.list_config = list_config
  
  def context(self):
    description = 'List of all Open tasks.'
    list = lists.ListConfigurationResponse(
        self.data, self.list_config, 0, description)
    return {
        'lists': [list],
    }
  
  def getListData(self):
    if lists.getListIndex(self.request) != 0:
      return None
    q = GCITask.all()
    q.filter('org', self.data.organization)
    q.filter('status IN', CLAIMABLE)
    starter = lists.keyStarter

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self.list_config, q, starter)
    return response_builder.build()
  
  def templatePath(self):
    return 'v2/modules/gci/org_home/_open_tasks.html'

class CompletedTasksList(Template):
  """List to display all the closed/completed tasks for the current organization.
  """
  def __init__(self, request, data):
    self.request = request
    self.data = data
    
    list_config = lists.ListConfiguration()
    
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn('student', 'Student',
                          lambda entity, *args: entity.student.name())
    
    list_config.setRowAction(
        lambda e, *args: data.redirect.id(e.key().id()).urlOf(url_names.GCI_VIEW_TASK))

    self.list_config = list_config
  
  def context(self):
    description = 'List of all Completed tasks.'
    list = lists.ListConfigurationResponse(
        self.data, self.list_config, 1, description)
    return {
        'lists': [list],
    }
  
  def getListData(self):
    if lists.getListIndex(self.request) != 1:
      return None
    q = GCITask.all()
    q.filter('org', self.data.organization)
    q.filter('status', 'Closed')
    starter = lists.keyStarter

    response_builder = lists.RawQueryContentResponseBuilder(
        self.request, self.list_config, q, starter)
    return response_builder.build()
  
  def templatePath(self):
    return 'v2/modules/gci/org_home/_closed_tasks.html'


class OrgHomepage(RequestHandler):
  """Encapsulates all the methods required to render the org homepage.
  """
  def templatePath(self):
    return 'v2/modules/gci/org_home/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'org/%s$' % url_patterns.ORG, self,
            name=url_names.GCI_ORG_HOME),
        url(r'org/home/%s' % url_patterns.ORG, self),
    ]
    
  def checkAccess(self):
    pass
  
  def jsonContext(self):
    idx = lists.getListIndex(self.request)
    list_content = None
    if idx == 0:
      list_content = OpenTasksList(self.request, self.data).getListData()
    elif idx == 1:
      list_content = CompletedTasksList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()
  
  def context(self):
    context = {
        'page_name': '%s - Home page' % (self.data.organization.name),
        'about_us': AboutUs(self.data),
        'contact_us': ContactUs(self.data),
        'open_tasks_list': OpenTasksList(self.request, self.data),
        'completed_tasks_list': CompletedTasksList(self.request, self.data),
        'feed_url': self.data.organization.feed_url,
    }
    
    return context

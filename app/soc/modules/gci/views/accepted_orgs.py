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

"""Module containing the views for GCI accepted orgs.
"""


from django.conf.urls.defaults import url as django_url

from soc.logic.exceptions import AccessViolation
from soc.views.helper import lists
from soc.views.template import Template
from soc.views.helper import url as url_helper
from soc.views.helper import url_patterns

from soc.modules.gci.logic import profile as profile_logic
from soc.modules.gci.models.organization import GCIOrganization
from soc.modules.gci.views.base import RequestHandler
#from soc.modules.gci.views.base_templates import ProgramSelect
from soc.modules.gci.views.helper.url_patterns import url
from soc.modules.gci.views.helper import url_names


class AcceptedOrgsList(Template):
  """Template for list of accepted organizations.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data
    r = data.redirect

    list_config = lists.ListConfiguration()
    list_config.addColumn('name', 'Name',
        lambda e, *args: e.name.strip())
    list_config.addSimpleColumn('link_id', 'Link ID', hidden=True)
    list_config.setRowAction(
        lambda e, *args: r.organization(e).urlOf(url_names.GCI_ORG_HOME))
    list_config.addColumn(
        'ideas', 'Ideas',
        (lambda e, *args: url_helper.urlize(e.ideas, name="[ideas page]")),
        hidden=True)
    list_config.setDefaultPagination(False)
    list_config.setDefaultSort('name')

    self._list_config = list_config

  def context(self):
    description = 'List of organizations accepted into %s' % (
            self.data.program.name)

    list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0, description)

    return {
        'lists': [list],
    }

  def getListData(self):
    idx = lists.getListIndex(self.request)
    if idx == 0:
      q = GCIOrganization.all()
      q.filter('scope', self.data.program)
      q.filter('status IN', ['new', 'active'])

      starter = lists.keyStarter

      response_builder = lists.RawQueryContentResponseBuilder(
          self.request, self._list_config, q, starter)
      return response_builder.build()
    else:
      return None

  def templatePath(self):
    return "v2/modules/gci/accepted_orgs/_project_list.html"


class AcceptedOrgsPage(RequestHandler):
  """View for the accepted organizations page.
  """

  def templatePath(self):
    return 'v2/modules/gci/accepted_orgs/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'accepted_orgs/%s$' % url_patterns.PROGRAM, self,
            name='gci_accepted_orgs'),
    ]

  def checkAccess(self):
    self.check.acceptedOrgsAnnounced()

  def jsonContext(self):
    list_content = AcceptedOrgsList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def context(self):
    return {
        'page_name': "Accepted organizations for %s" % self.data.program.name,
        'accepted_orgs_list': AcceptedOrgsList(self.request, self.data),
        #'program_select': ProgramSelect(self.data, 'gci_accepted_orgs'),
    }


class AcceptedOrgsAdminList(Template):
  """Template for list of accepted organizations for admins.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data
    r = data.redirect

    list_config = lists.ListConfiguration()
    list_config.addColumn('name', 'Name',
        lambda e, *args: e.name.strip())
    list_config.addSimpleColumn('link_id', 'Link ID', hidden=True)
    list_config.setRowAction(
        lambda e, *args: r.organization(e).urlOf(url_names.GCI_ORG_HOME))
    list_config.setDefaultPagination(False)
    list_config.setDefaultSort('name')
    list_config.addColumn(
      'org_admins', 'Org Admins',
      lambda e, org_admins, *args: ", ".join(
          ["%s <%s>" % (o.name(), o.email) for o in org_admins[e.key()]]),
      hidden=True)

    self._list_config = list_config

  def context(self):
    description = 'List of organizations accepted into %s' % (
            self.data.program.name)

    list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0, description)

    return {
        'lists': [list],
    }

  def getListData(self):
    idx = lists.getListIndex(self.request)
    if idx == 0:
      q = GCIOrganization.all()
      q.filter('scope', self.data.program)
      q.filter('status IN', ['new', 'active'])

      starter = lists.keyStarter

      def prefetcher(entities):
        prefetched_dict = {}
        for ent in entities:
          prefetched_dict[ent.key()] = profile_logic.orgAdminsForOrg(ent)

        return [prefetched_dict], {}

      response_builder = lists.RawQueryContentResponseBuilder(
          self.request, self._list_config, q, starter, prefetcher=prefetcher)
      return response_builder.build()
    else:
      return None

  def templatePath(self):
    return "v2/modules/gci/accepted_orgs/_project_list.html"


class AcceptedOrgsAdminPage(RequestHandler):
  """View for the accepted organizations page for admin with additional info.
  """

  def templatePath(self):
    return 'v2/modules/gci/accepted_orgs/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'admin/accepted_orgs/%s$' % url_patterns.PROGRAM, self,
            name='gci_admin_accepted_orgs'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def jsonContext(self):
    list_content = AcceptedOrgsAdminList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def context(self):
    return {
        'page_name': "Accepted organizations for %s" % self.data.program.name,
        'accepted_orgs_list': AcceptedOrgsAdminList(self.request, self.data),
    }

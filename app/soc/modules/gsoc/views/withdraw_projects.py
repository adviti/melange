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


import logging

from google.appengine.ext import db

from django.utils import simplejson

from soc.logic.exceptions import AccessViolation
from soc.logic.exceptions import BadRequest
from soc.views.base_templates import ProgramSelect
from soc.views.helper import lists
from soc.views.helper import url_patterns
from soc.views.template import Template

from soc.modules.gsoc.logic import project as project_logic
from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper.url_patterns import url


class ProjectList(Template):
  """Template for listing the student projects accepted in the program.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data

    list_config = lists.ListConfiguration(add_key_column=False)
    list_config.addColumn('key', 'Key', (lambda ent, *args: "%s/%s" % (
        ent.parent().key().name(), ent.key().id())), hidden=True)
    list_config.addColumn('student', 'Student',
                          lambda entity, *args: entity.parent().name())
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn('org', 'Organization',
                          lambda entity, *args: entity.org.name)

    def status(project):
      """Status to show on the list with color.
      """
      if project.status == 'accepted':
        return """<strong><font color="green">Accepted</font><strong>"""
      elif project.status == 'withdrawn':
        return """<strong><font color="red">Withdrawn</font></strong>"""

      return project.status

    list_config.addColumn('status', 'Status',
                          lambda entity, *args: status(entity))

    list_config.setDefaultPagination(False)
    list_config.setDefaultSort('student')

    # hidden keys
    list_config.addColumn(
        'full_project_key', 'Full project key',
        (lambda ent, *args: str(ent.key())), hidden=True)

    # action button
    bounds = [1,'all']
    keys = ['full_project_key']
    list_config.addPostButton('withdraw', "Withdraw", "", bounds, keys)
    list_config.addPostButton('accept', "Accept", "", bounds, keys)

    self._list_config = list_config

  def context(self):
    list = lists.ListConfigurationResponse(
        self.data, self._list_config, idx=0,
        description='List of %s projects whether accepted or withdrawn' % (
            self.data.program.name))

    return {
        'lists': [list],
        }

  def post(self):
    idx = lists.getListIndex(self.request)
    if idx != 0:
      return None

    data = self.data.POST.get('data')

    if not data:
      raise BadRequest("Missing data")

    parsed = simplejson.loads(data)

    button_id = self.data.POST.get('button_id')

    if not button_id:
      raise BadRequest("Missing button_id")
    elif button_id == 'withdraw':
      return self.postHandler(parsed)
    elif button_id == 'accept':
      return self.postHandler(parsed, withdraw=False)

    raise BadRequest("Unknown button_id")

  def postHandler(self, data, withdraw=True):
    program = self.data.program

    for properties in data:
      if 'full_project_key' not in properties:
        logging.warning("Missing key in '%s'" % properties)
        continue

      project_key = properties['full_project_key']
      project = db.get(db.Key(project_key))

      if not project:
        logging.warning("Project '%s' doesn't exist" % project_key)
        continue

      if withdraw and project.status == 'withdrawn':
        logging.warning("Project '%s' already withdrawn" % project_key)
        continue

      if not withdraw and project.status == 'accepted':
        logging.warning("Project '%s' already accepted" % project_key)
        continue

      profile = project.parent()
      profile_key = profile.key()
      qp = GSoCProposal.all()
      qp.ancestor(profile_key)
      qp.filter('org', project.org)
      # FIXME: ??? Mentors can change overtime so how does this work???
      qp.filter('mentor IN', project.mentors)

      if withdraw:
        qp.filter('status', 'accepted')
      else:
        qp.filter('status', 'withdrawn')

      proposal = qp.get()

      def withdraw_or_accept_project_txn():
        if withdraw:
          new_status = 'withdrawn'
          new_number = 0
        else:
          new_status = 'accepted'
          new_number = 1

        project.status = new_status
        proposal.status = new_status
        profile.number_of_projects = new_number

        db.put([proposal, project, profile])

      db.run_in_transaction(withdraw_or_accept_project_txn)

    return True

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == 0:
      list_query = project_logic.getProjectsQuery(program=self.data.program)

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
    return "v2/modules/gsoc/withdraw_projects/_project_list.html"


class WithdrawProjects(RequestHandler):
  """View methods for withdraw projects
  """

  def templatePath(self):
    return 'v2/modules/gsoc/withdraw_projects/base.html'

  def djangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    return [
        url(r'withdraw_projects/%s$' % url_patterns.PROGRAM, self,
            name='gsoc_withdraw_projects')
    ]

  def checkAccess(self):
    """Access checks for the view.
    """
    self.check.isHost()

  def jsonContext(self):
    """Handler for JSON requests.
    """
    list_content = ProjectList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def post(self):
    list_content = ProjectList(self.request, self.data)

    if not list_content.post():
      raise AccessViolation(
          'You cannot change this data')

  def context(self):
    """Handler for GSoC Accepted Projects List page HTTP get request.
    """
    program = self.data.program

    return {
        'page_name': '%s - Projects' % program.short_name,
        'program_name': program.name,
        'project_list': ProjectList(self.request, self.data),
        'program_select': ProgramSelect(self.data, 'gsoc_withdraw_projects'),
    }

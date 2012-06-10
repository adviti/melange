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

"""Module containing the views for GSoC proposal duplicates.
"""


from google.appengine.api import taskqueue
from google.appengine.ext import db

from django import http

from soc.views.helper import url_patterns
from soc.views.template import Template

from soc.modules.gsoc.logic import duplicates as duplicates_logic
from soc.modules.gsoc.models.proposal_duplicates import GSoCProposalDuplicate
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper.url_patterns import url


class DuplicatesPage(RequestHandler):
  """View for the host to see duplicates.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/duplicates/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'duplicates/%s$' % url_patterns.PROGRAM, self,
            name='gsoc_view_duplicates'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def context(self):
    """Returns the context for this page.
    """
    program = self.data.program

    q = GSoCProposalDuplicate.all()
    q.filter('program', program)
    q.filter('is_duplicate', True)

    duplicates = [Duplicate(self.data, duplicate)
                  for duplicate in q.fetch(1000)]
    duplicates_status = duplicates_logic.getOrCreateStatusForProgram(program)

    context = {
      'page_name': 'Duplicates for %s' %program.name,
      'duplicates_status': duplicates_status,
      'duplicates': duplicates,
    }

    return context

  def post(self):
    """Handles the POST request to (re)start calcuation.
    """
    post_data = self.request.POST

    # pass along these params as POST to the new task
    task_params = {'program_key': self.data.program.key().id_or_name()}
    task_url = '/tasks/gsoc/proposal_duplicates/start'

    # checks if the task newly added is the first task
    # and must be performed repeatedly every hour or
    # just be performed once right away
    if 'calculate' in post_data:
      task_params['repeat'] = 'yes'
    elif 'recalculate' in post_data:
      task_params['repeat'] = 'no'

    # adds a new task
    new_task = taskqueue.Task(params=task_params, url=task_url)
    new_task.add()

    # redirect to self
    self.response = http.HttpResponseRedirect('')


class Duplicate(Template):
  """Template for showing a duplicate to the host.
  """

  def __init__(self, data, duplicate):
    """Constructs the template for showing a duplicate.

    Args:
      data: RequestData object.
      duplicate: GSoCProposalDuplicat entity to render.
    """
    self.duplicate = duplicate
    super(Duplicate, self).__init__(data)

  def context(self):
    """Returns the context for the current template.
    """
    r = self.data.redirect

    context = {'duplicate': self.duplicate}
    orgs = db.get(self.duplicate.orgs)
    proposals = db.get(self.duplicate.duplicates)

    orgs_details = {}
    for org in orgs:
      orgs_details[org.key().id_or_name()] = {
          'name': org.name,
          'link': r.organization(org).urlOf('gsoc_org_home')
          }
      q = GSoCProfile.all()
      q.filter('org_admin_for', org)
      q.filter('status', 'active')
      org_admins = q.fetch(1000)

      orgs_details[org.key().id_or_name()]['admins'] = []
      for org_admin in org_admins:
        orgs_details[org.key().id_or_name()]['admins'].append({
            'name': org_admin.name(),
            'email': org_admin.email
            })

      orgs_details[org.key().id_or_name()]['proposals'] = []
      for proposal in proposals:
        if proposal.org.key() == org.key():
          orgs_details[org.key().id_or_name()]['proposals'].append({
              'key': proposal.key().id_or_name(),
              'title': proposal.title,
              'link': r.review(proposal.key().id_or_name(),
                               proposal.parent().link_id).urlOf(
                                   'review_gsoc_proposal')
              })

    context['orgs'] = orgs_details

    return context

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return 'v2/modules/gsoc/duplicates/proposal_duplicate.html'

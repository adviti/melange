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

"""Module containing the views for GSoC accept proposals.
"""


from google.appengine.api import taskqueue

from django import http

from soc.views.helper import url_patterns

from soc.modules.gsoc.logic import accept_proposals as conversion_logic
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper.url_patterns import url


class AcceptProposalsPage(RequestHandler):
  """View for the host to trigger proposals to projets conversion.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/accept_proposals/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'accept_proposals/%s$' % url_patterns.PROGRAM, self,
            name='gsoc_accept_proposals'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def context(self):
    """Returns the context for this page.
    """
    program = self.data.program

    conversion_status = conversion_logic.getOrCreateStatusForProgram(program)

    context = {
      'page_name': 'Accept proposals for %s' %program.name,
      'conversion_status': conversion_status,
    }

    return context

  def post(self):
    """Handles the POST request to (re)start conversion.
    """

    # pass along these params as POST to the new task
    task_params = {'program_key': self.data.program.key().id_or_name()}
    task_url = '/tasks/gsoc/accept_proposals/main'

    # adds a new task
    new_task = taskqueue.Task(params=task_params, url=task_url)
    new_task.add()

    # redirect to self
    self.response = http.HttpResponseRedirect('')

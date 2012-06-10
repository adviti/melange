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

"""Module containing the boiler plate required to construct GSoC views.
"""


from soc.views.base import RequestHandler

from soc.modules.gsoc.views import base_templates
from soc.modules.gsoc.views.helper import access_checker
from soc.modules.gsoc.views.helper.request_data import RequestData
from soc.modules.gsoc.views.helper.request_data import RedirectHelper


class RequestHandler(RequestHandler):
  """Customization required by GSoC to handle HTTP requests.
  """

  def render(self, template_path, context):
    """Renders the page using the specified context.

    See soc.views.base.RequestHandler.

    The context object is extended with the following values:
      base_layout: path to the base template. cbox is for a page that need
                   to be rendered inside colorbox iframe. See admin dahsboard.
      cbox: flag to indicate wether the page requested should be rendered
            inside colorbox iframe.
      header: a rendered header.Header template for the current self.data
      mainmenu: a rendered site_menu.MainMenu template for the current self.data
      footer: a rendered site_menu.Footer template for the current self.data
    """
    if self.data.GET.get('cbox'):
      base_layout = 'v2/modules/gsoc/base_colorbox.html'
      cbox = True
    else:
      base_layout = 'v2/modules/gsoc/base.html'
      cbox = False

    context['base_layout'] = base_layout
    context['cbox'] = cbox
    context['header'] = base_templates.Header(self.data)
    context['mainmenu'] = base_templates.MainMenu(self.data)
    context['footer'] = base_templates.Footer(self.data)
    super(RequestHandler, self).render(template_path, context)

  def init(self, request, args, kwargs):
    self.data = RequestData()
    self.redirect = RedirectHelper(self.data, self.response)
    self.data.populate(self.redirect, request, args, kwargs)
    if self.data.is_developer:
      self.mutator = access_checker.DeveloperMutator(self.data)
      self.check = access_checker.DeveloperAccessChecker(self.data)
    else:
      self.mutator = access_checker.Mutator(self.data)
      self.check = access_checker.AccessChecker(self.data)

  def error(self, status, message=None):
    if not self.data.program:
      return super(RequestHandler, self).error(status, message)

    self.response.set_status(status, message=message)

    template_path = "v2/modules/gsoc/error.html"
    context = {
        'page_name': self.response.content,
        'message': self.response.content,
        'logged_in_msg': base_templates.LoggedInMsg(self.data, apply_link=False),
    }

    self.response.content = ''
    self.render(template_path, context)

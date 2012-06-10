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

"""Module containing the views for GSoC Organization Application.
"""


from soc.views import forms

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns
from soc.modules.gsoc.views.helper.url_patterns import url


class OrgApp(RequestHandler):
  """View methods for Organization Application Applications.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/org_app/apply.html'

  def djangoURLPatterns(self):
    return [
        url(r'org_app/apply/%s$' % url_patterns.SURVEY, self,
            name='gsoc_org_app_apply')
    ]

  def checkAccess(self):
    # TODO
    pass

  def context(self):
    return {
        'page_name': 'Organization Application',
    }

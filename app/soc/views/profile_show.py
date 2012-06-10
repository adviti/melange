#!/usr/bin/env python2.5
#
# Copyright 2012 the Melange authors.
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

"""Module for displaying the Profile read-only page.
"""


from soc.models.user import User
from soc.views import readonly_template
from soc.views.helper.access_checker import isSet

from soc.modules.gsoc.views.base import RequestHandler


class UserReadOnlyTemplate(readonly_template.ModelReadOnlyTemplate):
  """Template to construct readonly Profile data.
  """

  class Meta:
    model = User
    css_prefix = 'gsoc_profile_show'
    fields = ['link_id']

  def __init__(self, *args, **kwargs):
    super(UserReadOnlyTemplate, self).__init__(*args, **kwargs)
    self.fields['link_id'].group = "1. User info"


class ProfileShowPage(object):
  """View to display the read-only profile page.
  """

  def checkAccess(self):
    self.check.isLoggedIn()
    self.check.hasProfile()

  def context(self):
    assert isSet(self.data.program)
    assert isSet(self.data.profile)
    assert isSet(self.data.user)

    profile = self.data.profile
    program = self.data.program

    user_template = self._getUserReadOnlyTemplate(self.data.user)
    profile_template = self._getProfileReadOnlyTemplate(profile)
    css_prefix = profile_template.Meta.css_prefix

    return {
        'page_name': '%s Profile - %s' % (program.short_name, profile.name()),
        'program_name': program.name,
        'user': user_template,
        'profile': profile_template,
        'css_prefix': css_prefix,
        }

  def _getUserReadOnlyTemplate(self, user):
    return UserReadOnlyTemplate(user)

  def _getProfileReadOnlyTemplate(self, profile):
    raise NotImplementedError

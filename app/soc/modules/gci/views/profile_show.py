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

"""Module for displaying the GCI profile read-only page.
"""


from soc.models.user import User
from soc.views import readonly_template
from soc.views import profile_show
from soc.views.helper import url_patterns
from soc.views.helper.access_checker import isSet

from soc.modules.gci.models.profile import GCIProfile
from soc.modules.gci.views.base import RequestHandler
from soc.modules.gci.views.helper.url_patterns import url


class GCIProfileReadOnlyTemplate(readonly_template.ModelReadOnlyTemplate):
  """Template to construct read-only GSoCProfile data.
  """

  class Meta:
    model = GCIProfile
    css_prefix = 'gci_profile_show'
    fields = ['public_name', 'given_name', 'surname', 'im_network',
              'im_handle', 'home_page', 'blog', 'photo_url',
              'publish_location', 'email', 'res_street',
              'res_street_extra', 'res_city', 'res_state', 'res_country',
              'res_postalcode', 'phone', 'ship_name', 'ship_street',
              'ship_street_extra', 'ship_city', 'ship_state',
              'ship_country', 'ship_postalcode', 'birth_date',
              'tshirt_style', 'tshirt_size', 'gender', 'program_knowledge']
    hidden_fields = ['latitude', 'longitude']


class GCIProfileShowPage(profile_show.ProfileShowPage, RequestHandler):
  """View to display the read-only profile page.
  """

  def djangoURLPatterns(self):
    return [
        url(r'profile/show/%s$' % url_patterns.PROGRAM,
         self, name='show_gci_profile'),
    ]

  def templatePath(self):
    return 'v2/modules/gci/profile_show/base.html'

  def _getProfileReadOnlyTemplate(self, profile):
    return GCIProfileReadOnlyTemplate(profile)

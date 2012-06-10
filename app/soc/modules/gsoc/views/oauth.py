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

"""Module containing views for Open Auth.
"""


from soc.views import oauth


class OAuthRedirectPage(oauth.OAuthRedirectPage):
  """Redirect page to Google Documents.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/oauth/redirect_page.html'


class OAuthVerifyToken(oauth.OAuthVerifyToken):
  """Verify request token and redirect user.
  """
  pass

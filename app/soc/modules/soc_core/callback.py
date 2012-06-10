# Copyright 2009 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing the core callback.
"""


from soc.tasks.updates import project_conversion
from soc.tasks.updates import proposal_conversion
from soc.tasks.updates import role_conversion


class Callback(object):
  """Callback object that handles interaction between the core.
  """

  API_VERSION = 1

  def __init__(self, core):
    """Initializes a new Callback object for the specified core.
    """

    self.core = core
    self.views = []

  def registerViews(self):
    """Instantiates all view objects.
    """
    from soc.views import host
    from soc.views import legacy
    from soc.tasks import mailer
    from soc.views import oauth
    from soc.views import site
    from soc.views import user

    self.views.append(host.HostProfilePage())
    self.views.append(legacy.Legacy())
    self.views.append(mailer.MailerTask())
    self.views.append(oauth.PopupOAuthRedirectPage())
    self.views.append(oauth.PopupOAuthVerified())
    self.views.append(oauth.MakeRequest())
    self.views.append(site.EditSitePage())
    self.views.append(site.SiteHomepage())
    self.views.append(user.CreateUserPage())
    self.views.append(user.EditUserPage())

  def registerWithSitemap(self):
    """Called by the server when sitemap entries should be registered.
    """

    self.core.requireUniqueService('registerWithSitemap')

    # Redesigned view registration
    for view in self.views:
      self.core.registerSitemapEntry(view.djangoURLPatterns())

    self.core.registerSitemapEntry(role_conversion.getDjangoURLPatterns())
    self.core.registerSitemapEntry(proposal_conversion.getDjangoURLPatterns())
    self.core.registerSitemapEntry(project_conversion.getDjangoURLPatterns())

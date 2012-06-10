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

"""Module for the site global pages.
"""


import os

from google.appengine.api import users

from django.conf.urls.defaults import url as django_url
from django.forms import widgets as django_widgets
from django.utils.functional import lazy
from django.utils.translation import ugettext

from soc.models.document import Document
from soc.logic import cleaning
from soc.logic import site
from soc.logic.exceptions import AccessViolation
from soc.models.site import Site
from soc.views.base import Response
from soc.views.base import SiteRequestHandler
from soc.views.forms import ModelForm


from soc.modules import callback


DEF_NO_DEVELOPER = ugettext(
    'This page is only accessible to developers.')


def getProgramMap():
  choices = [('', 'Active program')]
  choices += callback.getCore().getProgramMap()
  return choices


class SiteForm(ModelForm):
  """Django form for the site settings.
  """

  class Meta:
    model = Site
    exclude = ['link_id', 'scope', 'scope_path', 'home', 'xsrf_secret_key']
    widgets = {
        'active_program': django_widgets.Select(
            choices=lazy(getProgramMap, list)()),
    }

  def clean_tos(self):
    if self.cleaned_data['tos'] is None:
      return ''
    return self.cleaned_data['tos']

  def templatePath(self):
    return 'v2/modules/gsoc/_form.html'

  clean_noreply_email = cleaning.clean_empty_field('noreply_email')


class EditSitePage(SiteRequestHandler):
  """View for the participant profile.
  """

  def djangoURLPatterns(self):
    return [
        django_url(r'^site/edit$', self, name='edit_site_settings'),
    ]

  def jsonContext(self):
    entities = Document.all().filter('prefix', 'site')

    data = [{'key': str(i.key()),
            'link_id': i.link_id,
            'label': i.title}
            for i in entities]

    return {'data': data}

  def checkAccess(self):
    if not self.data.is_developer:
      raise AccessViolation(DEF_NO_DEVELOPER)

  def templatePath(self):
    # TODO: make this specific to the current active program
    return 'v2/soc/site/base.html'

  def context(self):
    # TODO: suboptimal
    from soc.modules.gsoc.views.forms import GSoCBoundField
    site_form = SiteForm(GSoCBoundField, self.data.POST or None,
                         instance=self.data.site)
    return {
        'app_version': os.environ.get('CURRENT_VERSION_ID', '').split('.')[0],
        'page_name': 'Edit site settings',
        'site_form': site_form,
    }

  def validate(self):
    from soc.modules.gsoc.views.forms import GSoCBoundField
    site_form = SiteForm(GSoCBoundField, self.data.POST,
                         instance=self.data.site)

    if not site_form.is_valid():
      return False

    site_form.save()

  def post(self):
    """Handler for HTTP POST request.
    """
    if self.validate():
      self.redirect.to('edit_site_settings')
    else:
      self.get()


class SiteHomepage(SiteRequestHandler):
  """View for the site home page.
  """

  def djangoURLPatterns(self):
    return [
        django_url(r'^$', self, name='site_home'),
        django_url(r'^(login)$', self, name='login'),
        django_url(r'^(logout)$', self, name='logout'),
    ]

  def __call__(self, request, *args, **kwargs):
    """Custom call implementation.

    This avoids looking up unneeded data.
    """
    self.response = Response()

    self.init(request, args, kwargs)

    action = args[0] if args else ''

    if action == 'login':
      self.redirect.toUrl(users.create_login_url('/'))
    elif action == 'logout':
      self.redirect.toUrl(users.create_logout_url('/'))
    else:
      settings = site.singleton()
      program = settings.active_program
      if program:
        self.redirect.program(program).to(program.homepage_url_name)
      else:
        self.redirect.to('edit_site_settings')

    return self.response

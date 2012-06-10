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

"""Module for the program host views.
"""


from google.appengine.ext import db

from django import http
from django.conf.urls.defaults import url as django_url
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext

from soc.logic.exceptions import AccessViolation
from soc.models.host import Host
from soc.views.base import SiteRequestHandler
from soc.views.helper import url_patterns
from soc.views.forms import ModelForm


DEF_DEVELOPER_ONLY = ugettext(
    "You must be a developer to access other hosts' profile settings.")

DEF_NO_HOST = ugettext(
    'You must be a host to access this page.')


class HostProfileForm(ModelForm):
  """Django form for the site settings.
  """

  class Meta:
    model = Host
    fields = ['notify_slot_transfer']


class HostProfilePage(SiteRequestHandler):
  """View for the host profile.
  """

  def djangoURLPatterns(self):
    return [
        django_url(r'^host/profile$', self, name='edit_host_profile'),
        django_url(r'^host/profile/%s$' % url_patterns.USER, self,
                   name='edit_host_profile_linkid'),
    ]

  def checkAccess(self):
    if self.data.is_developer:
      self.mutator.hostFromKwargs()
      return

    link_id = self.data.kwargs.get('link_id')
    if link_id and self.data.user.link_id != link_id:
      raise AccessViolation(DEF_DEVELOPER_ONLY)

    self.mutator.host()
    if self.data.is_host:
      return

    raise AccessViolation(DEF_NO_HOST)

  def templatePath(self):
    return 'v2/soc/host/base.html'

  def context(self):
    host_profile_form = HostProfileForm(self.data.POST or None,
                                        instance=self.data.host)
    return {
        'page_name': 'Host profile settings',
        'forms': [host_profile_form],
    }

  def createOrUpdateHost(self):
    """Creates or Updates the host entity
    """
    host_profile_form = HostProfileForm(self.data.POST,
                                        instance=self.data.host)

    if not host_profile_form.is_valid():
      return None

    if self.data.is_developer:
      if self.data.host_user_key:
        user_key = self.data.host_user_key
      else:
        user_key = self.data.user.key()
    elif self.data.is_host:
      user_key = self.data.user.key()

    def create_or_update_host_txn():
      if self.data.host:
        # get the latest host entity
        host = db.get(self.data.host.key())
        host_profile_form.instance = host
        host = host_profile_form.save(commit=True)
      else:
        user_entity = db.get(user_key)
        host = host_profile_form.create(
            commit=True, parent=user_entity)

      return host

    return db.run_in_transaction(create_or_update_host_txn)

  def post(self):
    """Handler for HTTP POST request.
    """
    host = self.createOrUpdateHost()
    if host:
      link_id = self.data.kwargs.get('link_id')
      if link_id:
        kwargs = {'link_id': link_id}
        self.redirect.to('edit_host_profile_linkid', kwargs=kwargs)
      else:
        self.redirect.to('edit_host_profile')
    else:
      self.get()

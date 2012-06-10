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

"""Module for the User related pages.
"""


import os


from django.conf.urls.defaults import url as django_url

from soc.logic import accounts
from soc.logic import cleaning
from soc.models.user import User
from soc.views.base import SiteRequestHandler
from soc.views.forms import ModelForm


class UserCreateForm(ModelForm):
  """Django form for the User profile.
  """

  class Meta:
    model = User
    fields = ['link_id', 'name']

  clean_link_id = cleaning.clean_user_not_exist('link_id')

  def templatePath(self):
    # TODO: This needs a more generic form.
    return 'v2/modules/gsoc/_form.html'


class UserEditForm(ModelForm):
  """Django form to edit a User profile.
  """

  class Meta:
    model = User
    fields = ['name']

  def templatePath(self):
    # TODO: This needs a more generic form.
    return 'v2/modules/gsoc/_form.html'


class CreateUserPage(SiteRequestHandler):
  """View for creating the user profile.
  """

  def djangoURLPatterns(self):
    return [
        django_url(r'^user/create$', self, name='create_user'),
    ]

  def checkAccess(self):
    """Ensures that the user is logged in and does not have a User profile.
    """
    self.check.isNotUser()

  def templatePath(self):
    # TODO: make this specific to the current active program
    return 'v2/soc/user/base.html'

  def context(self):
    # TODO: program specific in core module, needs to be avoided
    from soc.modules.gsoc.views.forms import GSoCBoundField
    form = UserCreateForm(GSoCBoundField, self.data.POST or None)

    return {
        'base_layout': 'v2/modules/gsoc/base.html',
        'app_version': os.environ.get('CURRENT_VERSION_ID', '').split('.')[0],
        'page_name': 'Create User profile',
        'forms': [form],
    }

  def post(self):
    """Handler for HTTP POST request.
    """
    from soc.modules.gsoc.views.forms import GSoCBoundField
    form = UserCreateForm(GSoCBoundField, self.data.POST)

    if not form.is_valid():
      return self.get()

    cleaned_data = form.cleaned_data
    norm_account = accounts.normalizeAccount(self.data.gae_user)
    cleaned_data['account'] = norm_account
    cleaned_data['account_id'] = self.data.gae_user.user_id()

    form.create(key_name=cleaned_data['link_id'])

    self.redirect.to('edit_user', validated=True)


class EditUserPage(SiteRequestHandler):
  """View to edit the user profile.
  """

  def djangoURLPatterns(self):
    return [
        django_url(r'^user/edit', self, name='edit_user'),
    ]

  def checkAccess(self):
    self.check.isUser()

  def templatePath(self):
    # TODO: make this specific to the current active program
    return 'v2/soc/user/base.html'

  def context(self):
    # TODO: program specific in core module
    from soc.modules.gsoc.views.forms import GSoCBoundField
    form = UserEditForm(
        GSoCBoundField, self.data.POST or None, instance=self.data.user)

    return {
        'base_layout': 'v2/modules/gsoc/base.html',
        'app_version': os.environ.get('CURRENT_VERSION_ID', '').split('.')[0],
        'page_name': 'Edit User profile',
        'forms': [form],
    }

  def post(self):
    """Handler for HTTP POST request.
    """
    from soc.modules.gsoc.views.forms import GSoCBoundField
    form = UserEditForm(GSoCBoundField, self.data.POST,
                         instance=self.data.user)

    if not form.is_valid():
      return self.get()

    form.save()

    self.redirect.to('edit_user', validated=True)

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

"""This module contains the view for the site menus."""


from google.appengine.api import users

from soc.views.template import Template

from soc.views.base_templates import LoggedInMsg


def siteMenuContext(data):
  """Generates URL links for the hard-coded GSoC site menu items.
  """
  redirect = data.redirect
  program = data.program

  from soc.modules.gsoc.models.program import GSoCProgram
  about_page = GSoCProgram.about_page.get_value_for_datastore(program)
  connect = GSoCProgram.connect_with_us_page.get_value_for_datastore(program)
  help_page = GSoCProgram.help_page.get_value_for_datastore(program)

  context = {
      'about_link': redirect.document(about_page).url(),
      'events_link': redirect.events().url(),
      'connect_link': redirect.document(connect).url(),
      'help_link': redirect.document(help_page).url(),
  }

  if users.get_current_user():
    context['logout_link'] = redirect.logout().url()
  else:
    context['login_link'] = redirect.login().url()

  if data.profile:
    context['dashboard_link'] = redirect.dashboard().url()

  if data.timeline.studentsAnnounced():
    context['projects_link'] = redirect.allProjects().url()

  return context


class Header(Template):
  """MainMenu template.
  """

  def __init__(self, data):
    self.data = data

  def templatePath(self):
    return "v2/modules/gsoc/header.html"

  def context(self):
    return {
        'home_link': self.data.redirect.homepage().url(),
        'program_link_id': self.data.program.link_id,
    }


class MainMenu(Template):
  """MainMenu template.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    context = siteMenuContext(self.data)
    context.update({
        'home_link': self.data.redirect.homepage().url(),
        'search_link': self.data.redirect.searchpage().url(),
    })

    if self.data.profile:
      self.data.redirect.program()
      if self.data.profile.status == 'active':
        if self.data.timeline.programActive():
          context['profile_link'] = self.data.redirect.urlOf(
              'edit_gsoc_profile')
        else:
          context['profile_link'] = self.data.redirect.urlOf(
              'show_gsoc_profile')

        # Add org admin dashboard link if the user has active
        # org admin profile and is an org admin of some organization
        if self.data.is_org_admin:
          context['org_dashboard_link'] = self.data.redirect.urlOf(
              'gsoc_org_dashboard')

    if self.data.is_host:
      self.data.redirect.program()
      context['admin_link'] = self.data.redirect.urlOf('gsoc_admin_dashboard')

    return context

  def templatePath(self):
    return "v2/modules/gsoc/mainmenu.html"


class Footer(Template):
  """Footer template.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    context = siteMenuContext(self.data)
    redirect = self.data.redirect
    program = self.data.program

    context.update({
        'privacy_policy_url': program.privacy_policy_url,
        'blogger_url': program.blogger,
        'email_id': program.email,
        'irc_url': program.irc,
        })

    return context

  def templatePath(self):
    return "v2/modules/gsoc/footer.html"


class LoggedInMsg(LoggedInMsg):
  """Template to render user login message at the top of the profile form.
  """

  def templatePath(self):
    return "v2/modules/gsoc/_loggedin_msg.html"

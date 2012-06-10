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

"""Module for rendering dual buttons for enabling/disabling feature.
"""


from django.utils.translation import ugettext

from soc.views.template import Template


class ButtonTemplate(Template):
  """Template to render buttons on proposal review page.
  """

  DEF_ENABLE_BTN_DISABLED = ugettext(
      'This functionality is already enabled. To disable this functionality, '
      'press the button adjacent to this.')

  DEF_DISABLE_BTN_DISABLED = ugettext(
      'This functionality is already disabled. To enable this functionality, '
      'press the button adjacent to this.')

  def __init__(self, data, title, id, url_name, enable=True,
               disabled_msgs=None, labels=None):
    """Instantiates the template for rendering review page buttons.

    Args:
      data: RequestData object
      title: The text that must be displayed before the button
      id: value to be given to HTML id attribute for button
      url_name: The name with which the RequestHandler has registered
      enable: if True Enable button is activated otherwise Disable button
      disabled_msgs : dictionary containing the message to be shown for
          each button when clicked in the disabled state
      labels: dictionary containing the label for each of the two buttons
    """
    super(ButtonTemplate, self).__init__(data)
    self.title = title
    self.labels = labels
    self._id = id
    self._url_name = url_name
    self._enable = enable
    self._disabled_msgs = disabled_msgs

  def context(self):
    """The context for this template used in render().
    """
    context = {
        'title': self.title,
        'id': self.id,
        'state': self.state,
        }

    if self.labels:
      context['enable_label'] = self.labels.get('enable')
      context['disable_label'] = self.labels.get('disable')

    return context

  @property
  def state(self):
    """Returns the state as needed by the Javascript and HTML.
    """
    return "enable" if self._enable else "disable"

  @property
  def link(self):
    """Returns the post url for the button.
    """
    return self.data.redirect.review().urlOf(self._url_name)

  @property
  def id(self):
    """Returns the id to be used for the button.
    """
    return self._id

  @property
  def enable_btn_disabled_msg(self):
    """Returns the message to be displayed when the enable button is
    pressed when it is disabled.
    """
    msg = self._disabled_msgs.get('enable')
    return msg if msg else self.DEF_ENABLE_BTN_DISABLED

  @property
  def disable_btn_disabled_msg(self):
    """Returns the message to be displayed when the disable button is
    pressed when it is disabled.
    """
    msg = self._disabled_msgs.get('disable')
    return msg if msg else self.DEF_DISABLE_BTN_DISABLED

  def templatePath(self):
    return 'v2/soc/_button.html'

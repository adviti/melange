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

"""Module for rendering toggle buttons for enabling/disabling feature.
"""


from soc.views.template import Template


class ToggleButtonTemplate(Template):
  """Template to render toggle buttons.
  """

  def __init__(self, data, type, title, id, post_url, checked=False,
               help_text=None, note=None, labels=None):
    """Instantiates the template for rendering review page buttons.

    Args:
      data: RequestData object
      type: Type of the button, can be one of on_off, disabled or long
      title: The text that must be displayed before the button
      id: value to be given to HTML id attribute for button
      post_url: The url to which post should be performed on click
      enable: if True Enable button is activated otherwise Disable button
      help_text: Tooltip to be displayed for the button.
      note: additional message to be displayed along with the buttons
      labels: dictionary containing the label for each of the two buttons
    """
    super(ToggleButtonTemplate, self).__init__(data)
    self.checked = checked
    self.help_text = help_text
    self.labels = labels
    self.note = note
    self.title = title
    self.type = type
    self.id = id
    self.post_url = post_url

  def context(self):
    """The context for this template used in render().
    """
    context = {
        'button': self,
        }

    return context

  @property
  def state(self):
    """Returns the state as needed by the Javascript and HTML.
    """
    return "checked" if self.checked else "unchecked"

  def templatePath(self):
    return 'v2/soc/_toggle_button.html'

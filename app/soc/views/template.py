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

"""Module containing the boiler plate required to construct templates
"""


import logging

from django.template import loader

from soc.views.helper import context as context_helper


class Template(object):
  """Template class that facilitates the rendering of templates.
  """

  def __init__(self, data):
    self.data = data

  def render(self):
    """Renders the template to a string.

    Uses the context method to retrieve the appropriate context, uses the
    self.templatePath() method to retrieve the template that should be used.
    """
    try:
      context = context_helper.default(self.data)
      context.update(self.context())
      rendered = loader.render_to_string(self.templatePath(), dictionary=context)
    except Exception, e:
      logging.exception(e)
      raise e

    return rendered

  def context(self):
    """Returns the context for the current template.
    """
    return {}

  def templatePath(self):
    """Returns the path to the template that should be used in render().

    Subclasses should override this method.
    """
    raise NotImplementedError()

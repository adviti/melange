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

"""Module for the program settings pages.
"""


from soc.views.helper import url_patterns

from soc.models.document import Document
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.timeline import GSoCTimeline
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.forms import GSoCModelForm
from soc.modules.gsoc.views.helper.url_patterns import url


class TimelineForm(GSoCModelForm):
  """Django form to edit timeline settings.
  """

  class Meta:
    css_prefix = 'timeline_form'
    model = GSoCTimeline
    exclude = ['link_id', 'scope', 'scope_path']


class ProgramForm(GSoCModelForm):
  """Django form for the program settings.
  """

  def __init__(self, request_data, *args, **kwargs):
    self.request_data = request_data
    super(ProgramForm, self).__init__(*args, **kwargs)

  class Meta:
    css_prefix = 'program_form'
    model = GSoCProgram
    exclude = ['link_id', 'scope', 'scope_path', 'timeline',
               'home', 'slots_allocation']


class ProgramPage(RequestHandler):
  """View for the program profile.
  """

  def djangoURLPatterns(self):
    return [
        url(r'program/%s$' % url_patterns.PROGRAM, self,
            name='edit_gsoc_program'),
        url(r'program/edit/%s$' % url_patterns.PROGRAM, self),
    ]

  def jsonContext(self):
    q = Document.all()
    q.filter('prefix', 'gsoc_program')
    q.filter('scope', self.data.program.key())

    data = [{'key': str(i.key()),
            'key_name': i.key().name(),
            'label': i.title}
            for i in q]

    return {'data': data}

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/program/base.html'

  def context(self):
    scope_path = self.data.program.key().id_or_name()
    program_form = ProgramForm(self.data, self.data.POST or None,
                               instance=self.data.program)
    return {
        'page_name': 'Edit program settings',
        'forms': [program_form],
        'error': program_form.errors,
    }

  def validate(self):
    scope_path = self.data.program.key().id_or_name()
    program_form = ProgramForm(self.data, self.data.POST,
                               instance=self.data.program)

    if not program_form.is_valid():
      return False

    program_form.save()
    return True

  def post(self):
    """Handler for HTTP POST request.
    """
    if self.data.GET.get('cbox'):
      cbox = True
    else:
      cbox = False

    if self.validate():
      self.redirect.program()
      self.redirect.to('edit_gsoc_program', validated=True, cbox=cbox)
    else:
      self.get()


class TimelinePage(RequestHandler):
  """View for the participant profile.
  """

  def djangoURLPatterns(self):
    return [
        url(r'timeline/%s$' % url_patterns.PROGRAM, self,
            name='edit_gsoc_timeline'),
        url(r'timeline/edit/%s$' % url_patterns.PROGRAM, self),
    ]

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/timeline/base.html'

  def context(self):
    timeline_form = TimelineForm(self.data.POST or None,
                                 instance=self.data.program_timeline)
    return {
        'page_name': 'Edit program timeline',
        'forms': [timeline_form],
        'error': timeline_form.errors,
    }

  def validate(self):
    timeline_form = TimelineForm(self.data.POST,
                                 instance=self.data.program_timeline)

    if not timeline_form.is_valid():
      return False

    timeline_form.save()
    return True

  def post(self):
    """Handler for HTTP POST request.
    """
    if self.data.GET.get('cbox'):
      cbox = True
    else:
      cbox = False

    if self.validate():
      self.redirect.program()
      self.redirect.to('edit_gsoc_timeline', validated=True, cbox=cbox)
    else:
      self.get()

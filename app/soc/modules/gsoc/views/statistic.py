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

"""Module for the GSoC statistics page."""


from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext

from soc.logic.exceptions import AccessViolation

from soc.views.template import Template
from soc.views.toggle_button import ToggleButtonTemplate

from soc.modules.gsoc.models.statistic_info import GSoCStatisticInfo
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper.url_patterns import url

from soc.modules.gsoc.statistics import mapping
from soc.modules.gsoc.statistics.presentation import GvizPresenter
from soc.modules.gsoc.statistics.presentation import JsonPresenter


class ManageActions(Template):
  """Template to render the left side admin actions.
  """

  IS_VISIBLE_HELP_MSG = ugettext(
      'Whether this statistic is publicly visible to all users or not.')

  def context(self):
    self.toggle_buttons = [
        ToggleButtonTemplate(
            self.data, 'on_off', 'Is visible', 'is-visible-statistic',
            None,
            checked=True,
            help_text=self.IS_VISIBLE_HELP_MSG,
            labels = {
                'checked': 'Yes',
                'unchecked': 'No'})]
    
    return {
        'toggle_buttons': self.toggle_buttons
    }

  def templatePath(self):
    return "v2/modules/gsoc/proposal/_user_action.html"

class UnsupportedFormatException(Exception):
  pass


class StatisticDashboard(RequestHandler):
  """View for the statistic page.
  """

  def djangoURLPatterns(self):
    return [
         url(r'statistic/dashboard$', self, name='gsoc_statistic_dashboard'),
    ]

  def templatePath(self):
    return 'v2/modules/gsoc/statistic/base.html'

  def checkAccess(self):
    self.isHost = False
    try:
      self.check.isHost()
      self.isHost = True
    except AccessViolation:
      pass

  def context(self):
    if self.isHost:
      infos = GSoCStatisticInfo.getInstance().getStatistics()
    else:
      infos = GSoCStatisticInfo.getInstance().getVisibleStatistics()
    names = [i.name for i in infos]

    statistics = [s for s in mapping.STATISTICS if s['name'] in names]
    visualizations = dict(
        filter(lambda (k, v): k in names, mapping.VISUALIZATIONS.items()))

    return {
        'fetch_urls': self._constructFetchUrls(),
        'manage_urls': self._constructManageUrls(),
        'statistics': statistics,
        'visualizations': visualizations,
        'manage_actions': self._constructManageActions(),
        'visibilities': self._constructVisibilities(infos),
        }

  def _constructManageActions(self):
    return ManageActions(self.data) if self.isHost else None

  def _constructFetchUrls(self):
    fetch_urls = {}
    for name in mapping.STATISTIC_NAMES:
      fetch_urls[name] = reverse(
          'gsoc_statistic_fetch', kwargs={'key_name': name})

    return fetch_urls

  def _constructManageUrls(self):
    manage_urls = {}
    for name in mapping.STATISTIC_NAMES:
      manage_urls[name] = reverse(
          'gsoc_statistic_manage', kwargs={'key_name': name})
    return manage_urls
  
  def _constructVisibilities(self, infos):
    visibilities = {}
    if self.isHost:
      for info in infos:
        visibilities[str(info.name)] = True if info.is_visible else False
    return simplejson.dumps(visibilities)

class StatisticFetcher(RequestHandler):
  """Loads data for a particular statistic.
  """

  def __init__(self):
    self._presenter = None

  def checkAccess(self):
    key_name = self.data.kwargs['key_name']
    
    # TODO(dhans): check if the statistic is visible
    pass

  def djangoURLPatterns(self):
    return [
         url(r'statistic/fetch/(?P<key_name>(\w+))$', self,
             name='gsoc_statistic_fetch'),
    ]

  def _getPresentation(self, key_name):
    type = self.data.GET.get('type', 'json')

    if type == 'json':
      self.response['Content-Type'] = 'application/json'
      self._presenter = JsonPresenter()
    elif type == 'gviz':
      self.response['Content-Type'] = 'application/json'
      self._presenter = GvizPresenter()
    else:
      raise UnsupportedFormatException('Requested format is not supported.')

    return self._presenter.get(key_name)
    
  def jsonContext(self):
    key_name = self.data.kwargs['key_name']
    presentation = self._getPresentation(key_name)
    return presentation


class StatisticManager(RequestHandler):
  """Manages the statistic entities.
  """

  def checkAccess(self):
    self.check.isHost()

  def djangoURLPatterns(self):
    return [
         url(r'statistic/manage/(?P<key_name>(\w+))$', self,
             name='gsoc_statistic_manage'),
    ]

  def post(self):
    key_name = self.data.kwargs['key_name']
    statistic = GSoCStatisticInfo.getInstance().getStatisticByName(key_name)

    value = simplejson.loads(self.data.POST.get('value'))
    if not isinstance(value, bool):
      raise AccessViolation('Unsupported value sent to the server')

    if statistic.getVisible() != value:
      statistic.setVisible(value)
      GSoCStatisticInfo.getInstance().updateStatistic(statistic)
      
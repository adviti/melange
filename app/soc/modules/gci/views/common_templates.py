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

"""This module contains the templates which are used across the views."""


from soc.views.template import Template


class Timeline(Template):
  """Timeline template.
  """

  def context(self):
    rem_days, rem_hours, rem_mins = self.data.timeline.remainingTime()
    complete_percentage = self.data.timeline.completePercentage()
    stopwatch_percentage = self.data.timeline.stopwatchPercentage()
    return {
        'remaining_days': rem_days,
        'remaining_hours': rem_hours,
        'remaining_minutes': rem_mins,
        'complete_percentage': complete_percentage,
        'stopwatch_percentage': stopwatch_percentage
    }

  def templatePath(self):
    return "v2/modules/gci/common_templates/_timeline.html"

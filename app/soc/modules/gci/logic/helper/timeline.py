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

"""Logic for time related calculations like durations, remaining time etc.
"""


from datetime import datetime
from datetime import timedelta


def remainingTime(*args):
  """Returns the remaining time as the timedelta object.

  Args:
    *args: contains either 2 arguments which represent the start and
        the end time datetime objects. If only one argument is supplied
        it represents the end time as datetime object.
  """
  if len(args) == 1:
    start = datetime.now()
    end = args[0]
  elif len(args) == 2:
    start, end = args

  return end - start if end > start else timedelta(0)


def remainingTimeSplit(*args):
  """Returns the remaining time as days, hours and minutes.

  If the number of days is greater than 2, days, hours and minutes are
  returned as computed. If the number of days is less than 2, days is set
  to 0 and hours and minutes are returned.

  Resembles the Django's timesince/timeuntil helper functions customized to
  the way we want to display remaining time.

  Args:
    *args: contains either 2 arguments which represent the start and
        the end time datetime objects. If only one argument is supplied
        it represents the end time as datetime object.
  """
  delta = remainingTime(*args)
  days = delta.days
  seconds = delta.seconds
  hours = seconds / 3600
  minutes = (seconds % 3600) / 60

  if days < 2:
    hours += days * 24
    days = 0

  return days, hours, minutes


def remainingTimeInSeconds(*args):
  """Returns the remaining time purely in seconds.

  Args:
    *args: contains either 2 arguments which represent the start and
        the end time datetime objects. If only one argument is supplied
        it represents the end time as datetime object.
  """
  delta = remainingTime(*args)
  return delta.seconds + (delta.days * 24 * 3600)


def completePercentage(start=None, end=None, duration=None):
  """Computes the percentage of the time remaining of the total time.

  Args:
    start: a datetime object representing the start of the total duration
    end: a datetime object representing the end of the total duration
    duration: total duration of the event in seconds
  """
  if not duration:
    duration = remainingTimeInSeconds(start, end)

  remaining = remainingTimeInSeconds(end)

  if remaining == 0:
    percentage = 100
  elif remaining >= duration:
    percentage = 0
  else:
    percentage = 100 - (remaining * 100 / duration)

  return int(percentage)


def stopwatchPercentage(complete_percentage):
  """Computes the closest matching percentage for the static clock images.

  Args:
    complete_percentage: percentage of the time that is completed in the
        program.
  """
  stopwatch_percentages = [25, 33, 50, 75, 100]

  stopwatch_percentage = 0

  for p in stopwatch_percentages:
    # The 15 percent allowance is added so as to NOT make the clock
    # look to be at 75% when the time is just 51%
    if complete_percentage <= p + 15:
      stopwatch_percentage = p
      break

  return stopwatch_percentage

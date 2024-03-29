#!/usr/bin/env python2.5
#
# Copyright 2008 the Melange authors.
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

"""Common validation helper functions.
"""


import feedparser

from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_errors

from soc.models import linkable


def isFeedURLValid(feed_url=None):
  """Returns True if provided url is valid ATOM or RSS.

  Args:
    feed_url: ATOM or RSS feed url
  """

  # a missing or empty feed url is never valid
  if not feed_url:
    return False

  try:
    result = urlfetch.fetch(feed_url)
  except urlfetch_errors.Error:
    return False

  # 200 is the status code for 'all ok'
  if result.status_code != 200:
    return False

  try:
    parsed_feed = feedparser.parse(result.content)
  except:
    return False

  # version is always present if the feed is valid
  if not parsed_feed.version:
    return False

  return True


def isLinkIdFormatValid(link_id):
  """Returns True if link_id is in a valid format.

  Args:
    link_id: link ID used in URLs for identification
  """
  if linkable.LINK_ID_REGEX.match(link_id):
    return True
  return False


def isScopePathFormatValid(scope_path):
  """Returns True if scope_path is in a valid format.
  
  Args:
    scope_path: scope path prepended to link ID
      used for identification.
  """
   
  if linkable.SCOPE_PATH_REGEX.match(scope_path):
    return True
  
  return False


def isAgeSufficientForProgram(birth_date, program):
  """Returns True if the specified birth_date is between student_min_age
  and student_max_age for the specified program. 
  """
  
  # do not check if the data is not present
  validation_result = True
  if program.student_min_age_as_of: 
    if program.student_min_age:
      min_year = program.student_min_age_as_of.year - program.student_min_age
      min_date = program.student_min_age_as_of.replace(year=min_year)
      validation_result = birth_date <= min_date

    if validation_result and program.student_max_age:
      max_year = program.student_min_age_as_of.year - program.student_max_age
      max_date = program.student_min_age_as_of.replace(year=max_year)
      validation_result = birth_date > max_date

  return validation_result

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

"""Helpers used to construct urls.
"""


def trim_url_to(url, limit):
  """Returns a version of url at most limit long.
  """
  if not url:
    return url
  if len(url) > limit:
    return '%s...' % url[:max(0, limit - 3)]
  return url


URL_PATTERN = '<a href="%(url)s"%(target)s%(nofollow)s>%(name)s</a>'


def urlize(url, name=None, target="_blank", nofollow=True):
  """Make an url clickable.

  Args:
    url: the actual url, such as '/user/list'
    name: the display name, such as 'List Users', defaults to url
    target: the 'target' attribute of the <a> element
    nofollow: whether to add the 'rel="nofollow"' attribute
  """

  if not url:
    return ''

  from django.utils.safestring import mark_safe
  from django.utils.html import escape

  safe_url = escape(url)
  safe_name = escape(name)

  link = URL_PATTERN % {
      'url': safe_url,
      'name': safe_name if name else safe_url,
      'target': ' target="%s"' % target if target else '',
      'nofollow': ' rel="nofollow"' if nofollow else "",
  }

  return mark_safe(link)

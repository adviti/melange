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

"""Module for constructing GSoC related URL patterns
"""


from django.conf.urls.defaults import url as django_url

from soc.views.helper.url_patterns import namedIdBasedPattern
from soc.views.helper.url_patterns import namedLinkIdPattern
from soc.views.helper import url_patterns


def url(regex, view, kwargs=None, name=None):
  """Constructs an url pattern prefixed with ^gsoc/.

  Args: see django.conf.urls.defaults.url
  """
  return django_url('^gsoc/%s' % regex, view, kwargs=kwargs, name=name)


SURVEY    = namedLinkIdPattern(['sponsor', 'program', 'survey'])
PROPOSAL  = namedIdBasedPattern(['sponsor', 'program'])
REVIEW    = namedIdBasedPattern(['sponsor', 'program', 'user'])
PROJECT   = namedIdBasedPattern(['sponsor', 'program', 'user'])
SURVEY_RECORD = namedIdBasedPattern(['sponsor', 'program', 'survey', 'user'])
GRADING_RECORD = '/'.join([PROJECT, r'(?P<group>(\d+))', r'(?P<record>(\d+))'])
PREFIXES = "(gsoc_program|gsoc_org)"
DOCUMENT = url_patterns.DOCUMENT_FMT % PREFIXES
ORG_DOCUMENT = url_patterns.ORG_DOCUMENT_FMT % PREFIXES

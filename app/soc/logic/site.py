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

"""Site (Model) query functions.
"""


from google.appengine.api import memcache

from soc.models.site import Site
from soc.logic.helper import xsrfutil


def singleton():
  """Return singleton Site settings entity, since there is always only one.
  """
  return Site.get_or_insert('site', link_id='site')


def xsrfSecretKey(settings):
  """Return the secret key for use by the XSRF middleware.

  If the Site entity does not have a secret key, this method will also create
  one and persist it.

  Args:
    settings: the singleton Site entity

  Returns:
    a secret key.
  """
  if not settings.xsrf_secret_key:
    key = xsrfutil.newXsrfSecretKey()
    if not memcache.add("new_xsrf_secret_key", key):
      key = memcache.get("new_xsrf_secret_key")
    settings.xsrf_secret_key = key
    settings.put()
  return settings.xsrf_secret_key

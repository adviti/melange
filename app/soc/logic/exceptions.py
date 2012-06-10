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

"""Module containing the exceptions from the AccessChecker class.
"""


class Error(Exception):
  """Error class for the access_exception module.
  """
  status = 500


class LoginRequest(Error):
  """Use needs to be logged in to view this page.
  """
  pass


class RedirectRequest(Error):
  """User should be redirected to specific url.
  """

  status = 302

  def __init__(self, url):
    self.url = url


class AccessViolation(Error):
  """An access requirement was not met.
  """
  status = 403

class GDocsLoginRequest(Error):
  """GDocs login required.
  """

  url_name = 'gdata_oauth_redirect'

  def __init__(self, next):
    self.next = next

class NotFound(Error):
  """Item Not Found.
  """
  status = 404


class BadRequest(Error):
  """Bad Request
  """
  status = 400

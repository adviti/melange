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

"""Module containing views for Open Auth.
"""


from django.conf.urls.defaults import url as django_url

from soc.views.helper.gdata_apis import oauth as oauth_helper

from soc.modules.gsoc.views.base import RequestHandler

from django.conf import settings
from django.utils import simplejson


class OAuthRedirectPage(RequestHandler):
  """Redirect page to Google Documents.
  """

  def djangoURLPatterns(self):
    patterns = [
        django_url(r'^gdata/oauth/redirect$', self, name='gdata_oauth_redirect'),
    ]
    return patterns

  def checkAccess(self):
    self.check.isUser()

  def context(self):
    service = oauth_helper.createDocsService(self.data)
    next = '%s?next=%s' % (self.redirect.urlOf('gdata_oauth_verify'),
                           self.request.GET.get('next','/'))
    url = oauth_helper.generateOAuthRedirectURL(
        service, self.data.user,
        next)
    context = {
        'approval_page_url': url,
        'page_name': 'Authorization Required',
    }
    return context

  def templatePath(self):
    """Override this method to define a rendering template
    """
    pass


class OAuthVerifyToken(RequestHandler):
  """Verify request token and redirect user.
  """

  def djangoURLPatterns(self):
    patterns = [
        django_url(r'^gdata/oauth/verify$', self, name='gdata_oauth_verify'),
    ]
    return patterns

  def get(self):
    service = oauth_helper.createDocsService(self.data)
    oauth_helper.checkOAuthVerifier(service, self.data)
    next = self.request.GET.get('next','/')
    self.redirect.toUrl(next)
    return self.response


class PopupOAuthRedirectPage(RequestHandler):
  """Redirects popup page to Google Documents.
  """

  def djangoURLPatterns(self):
    patterns = [
        django_url(r'^gdata/popup/oauth/redirect$', self,
                   name='gdata_popup_oauth_redirect'),
    ]
    return patterns

  def checkAccess(self):
    self.check.isUser()

  def get(self):
    access_token = oauth_helper.getAccessToken(self.data.user)
    if access_token:
      url = self.redirect.urlOf('gdata_popup_oauth_verified')
    else:
      service = oauth_helper.createDocsService(self.data)
      next = '%s?next=%s' % (self.redirect.urlOf('gdata_oauth_verify'),
                             self.redirect.urlOf('gdata_popup_oauth_verified'))
      url = oauth_helper.generateOAuthRedirectURL(
          service, self.data.user,
          next)
    self.redirect.toUrl(url)
    return self.response


class PopupOAuthVerified(RequestHandler):
  """ Calls parent window's methods to indicate successful login.
  """

  def djangoURLPatterns(self):
    patterns = [
        django_url(r'^gdata/popup/oauth/verified$', self,
                   name='gdata_popup_oauth_verified')
    ]
    return patterns

  def checkAccess(self):
    self.check.canAccessGoogleDocs()

  def get(self):
    html = (
        "<html><body><script type='text/javascript'>"
        "    window.opener.melange.gdata.loginSuccessful();"
        "    window.close();"
        "</script></body></html>"
    )
    self.response.write(html)
    

class MakeRequest(RequestHandler):
    """Work as a proxy view and deliver JS request to GData server.
    """

    def djangoURLPatterns(self):
      patterns = [
        django_url(r'^gdata/make_request$', self, name='gdata_make_request')
      ]
      return patterns

    def checkAccess(self):
      self.check.canAccessGoogleDocs()

    def post(self):
      params = self.request.POST

      gdata_service = oauth_helper.createGDataService(self.data)
      service_name = params['service_name']
      method = params.get('method', 'GET')
      data = simplejson.loads(params.get('data', '{}'))

      url = params['url']
      if not url.startswith('https'):
        host = settings.GDATA_HOSTS[service_name]
        url = 'https://%s%s' % (host, url)

      alt = params.get('alt')
      if alt == 'json':
        url = url + '?alt=json'

      headers = simplejson.loads(params.get('headers','{}'))
      if not 'GData-Version' in headers:
        headers['GData-Version'] = '1.0'

      response = gdata_service.request(method, url, data, headers=headers)
      response_data = response.read().decode('utf-8')
      self.response.write(response_data)

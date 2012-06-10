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

"""Generic views and tools for OAuth.
"""


from gdata import auth
from gdata import service as gdata_service
from gdata.alt import appengine
from gdata.docs import service as docs_service

from google.appengine.api import memcache

from django.conf import settings

from soc.logic import system

def setOAuthInputParamaters(service, data):
  """Sets OAuth input parameters for given service.
   """

  request = data.request
  site = data.site
  if system.isSecondaryHostname(request):
    consumer_key = site.secondary_gdata_consumer_key
    consumer_secret = site.secondary_gdata_consumer_secret
  else:
    consumer_key = site.gdata_consumer_key
    consumer_secret = site.gdata_consumer_secret

  if not consumer_key or not consumer_secret:
    return

  service.SetOAuthInputParameters(
      auth.OAuthSignatureMethod.HMAC_SHA1, consumer_key.encode('utf-8'),
      consumer_secret.encode('utf-8'), settings.GDATA_SCOPES)
  appengine.run_on_appengine(service)
  
  
def createDocsService(data):
  """Create and return a Docs Service.
  """

  service = docs_service.DocsService(source=settings.GDATA_SOURCE)
  setOAuthInputParamaters(service, data)
  return service


def createGDataService(data):
  """Create and return a low level GData Service.

  This service is used to make low level API calls. E.g. GData
  proxy view (soc.views.oauth.MakeRequest) uses this service
  to deliver JS requests to GData server by using 'request'
  method of this service.
  """

  service = gdata_service.GDataService(source=settings.GDATA_SOURCE)
  setOAuthInputParamaters(service, data)
  return service


def getAccessToken(user):
  """Returns access token for an user.
  """

  access_token = memcache.get("%s;%s" %
                              (user.key().name(), system.getRawHostname()),
                              namespace='access_token')
  if isinstance(access_token, auth.OAuthToken):
    return access_token


def createDocsServiceWithAccessToken(data):
  """Returns Docs Service which uses user's access token.
  """

  user = data.user
  service = createDocsService(data)
  access_token = getAccessToken(user)
  service.access_token = access_token
  return service
  
  
def createGDataServiceWithAccessToken(data):
  """Returns GData service which uses user's access token.
  """

  user = data.user
  service = createGDataService(data)
  access_token = getAccessToken(user)
  service.access_token = access_token
  return service


def deleteAccessToken(user):
  """Deletes access token of user.
  """

  memcache.set("%s;%s" % (user.key().name(), system.getRawHostname()),
               None, namespace='access_token')


def generateOAuthRedirectURL(service, user, next):
  """Returns OAuth redirect URL for authenticating user.
  """

  req_token = service.FetchOAuthRequestToken(
      scopes=settings.GDATA_SCOPES,
      oauth_callback='http://%s%s' % (system.getRawHostname(), next))
  memcache.add(user.key().name(), req_token.secret, 300,
               namespace='request_token_secret')
  approval_page_url = service.GenerateOAuthAuthorizationURL(
      extra_params={'hd': 'default'})
  return approval_page_url


def checkOAuthVerifier(service, data):
  """Checks for OAuth verifier and exchanges token with access token.
  """

  request = data.request
  user = data.user
  oauth_token = auth.OAuthTokenFromUrl(
      request.get_full_path())
  if oauth_token:
    oauth_token.secret = memcache.get(user.key().name(),
                                      namespace='request_token_secret')
    oauth_token.oauth_input_params = service.GetOAuthInputParameters()
    service.SetOAuthToken(oauth_token)

    oauth_verifier = request.GET.get('oauth_verifier', '')
    access_token = service.UpgradeToOAuthAccessToken(
        oauth_verifier=oauth_verifier)

    if access_token:
      memcache.set('%s;%s' %
                   (user.key().name(), system.getRawHostname()),
                   access_token, namespace='access_token')

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

"""This module contains the Site Model."""


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.presence_with_tos
import soc.models.program


class Site(soc.models.presence_with_tos.PresenceWithToS):
  """Model of a Site, which stores per site configuration.

  The Site Model stores configuration information unique to the Melange
  web site as a whole (in addition to any configuration that is common to
  any "presence" on the site, such as a Group or Program).
  """

  #: The official name of the site
  site_name = db.StringProperty(default="Melange",
      verbose_name=ugettext('Site Name'))
  site_name.help_text = ugettext('The official name of the Site')

  #: A notice that should be displayed site-wide
  site_notice = db.StringProperty(verbose_name=ugettext('Site Notice'))
  site_notice.help_text = ugettext('A notice that will be displayed site-wide')

  maintenance_start = db.DateTimeProperty(
      verbose_name=ugettext('Maintenance start date'))

  maintenance_end = db.DateTimeProperty(
      verbose_name=ugettext('Maintenance end date'))

  #: Valid Google Custom Search Engine key. Used to load the appropriate
  #: search box in the search page.
  cse_key = db.StringProperty(verbose_name=ugettext('Custom Search Engine key'))
  cse_key.help_text = ugettext(
      'Google Custom Search Engine key for embedding a '
      'CSE search box into the website.')

  #: Valid Google Analytics tracking number, if entered every page
  #: is going to have Google Analytics JS initialization code in
  #: the footer with the given tracking number.
  ga_tracking_num = db.StringProperty(
      verbose_name=ugettext('Google Analytics'))
  ga_tracking_num.help_text = ugettext(
      'Valid Google Analytics tracking number. If the number is '
      'entered every page is going to have Google Analytics '
      'initialization code in footer.')

  #: Valid Google API Key. Used to embed Google services.
  google_api_key = db.StringProperty(verbose_name=ugettext('Google API'))
  google_api_key.help_text = ugettext(
      'Valid Google API Key. This key is used for '
      'embedding Google services into the website.')

  #: Valid Google API Key. Used to embed Google services.
  secondary_google_api_key = db.StringProperty(verbose_name=ugettext('Secondary Google API'))
  secondary_google_api_key.help_text = ugettext(
      'Valid Google API Key. This secondary key is used for '
      'embedding Google services into the website when '
      'accessed through the "hostname" url.')

  #: Optional field storing the consumer key for GData APIs
  gdata_consumer_key = db.StringProperty(
      verbose_name=ugettext('GData Consumer Key'),
      multiline=False)
  gdata_consumer_key.help_text = ugettext(
      'OAuth Consumer Key that is provided by Google after '
      'registering your domain. This is used in authentication '
      'that is required to use particular GData APIs.')

  #: Optional field storing the consumer secret for GData APIs
  gdata_consumer_secret = db.StringProperty(
      verbose_name=ugettext('GData Consumer Secret'),
      multiline=False)
  gdata_consumer_secret.help_text = ugettext(
      'OAuth Consumer Secret that is also provided by Google after '
      'registering your domain.')

  #: Secondary consumer key to be used with multiple domains
  secondary_gdata_consumer_key = db.StringProperty(
      verbose_name=ugettext('Secondary GData Consumer Key'),
      multiline=False)
  secondary_gdata_consumer_key.help_text = ugettext(
      'Same with "GData Consumer Key" except this is used when '
      'not accessed through the "hostname" url. To be used with '
      'multiple domains.')

  #: Secondary consumer secret to be used with multiple domains
  secondary_gdata_consumer_secret = db.StringProperty(
      verbose_name=ugettext('Secondary GData Consumer Secret'),
      multiline=False)
  secondary_gdata_consumer_secret.help_text = ugettext(
      'Same with "GData Consumer Secret" except this is used when '
      'not accessed through the "hostname" url. To be used with '
      'multiple domains.')

  #: No Reply Email address used for sending notification emails to site users
  noreply_email = db.EmailProperty(verbose_name=ugettext('No reply email'))
  noreply_email.help_text = ugettext(
      'No reply email address is used for sending emails to site users. '
      'Email address provided in this field needs to be added as Developer '
      'in GAE admin console.')

  #: Optional field storing the url of the site logo.
  logo_url = db.LinkProperty(
      verbose_name=ugettext('Site logo'))
  logo_url.help_text = ugettext(
      'URL of the site logo.')

  #: XSRF tokens are generated using a secret key.  This field is not visible in
  #: /site/edit because it is hidden in soc.views.models.site, and is populated
  #: automatically by soc.logic.models.site.
  xsrf_secret_key = db.StringProperty(multiline=False)
  xsrf_secret_key.help_text = ugettext('An automatically generated random '
      'value used to prevent cross-site request forgery attacks.')

  #: Optional field storing the hostname
  hostname = db.StringProperty(
      verbose_name=ugettext('Hostname'))
  hostname.help_text = ugettext(
      'URL of the hostname.')

  #: Reference to Program which is currently active
  active_program = db.ReferenceProperty(
    reference_class=soc.models.program.Program)
  active_program.help_text = ugettext(
      'The Program which is currently active.')

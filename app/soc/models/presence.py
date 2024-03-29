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

"""This module contains the Presence Model."""


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.document
import soc.models.linkable


class Presence(soc.models.linkable.Linkable):
  """Model for anything that has a "presence" on a Melange site.

  A "presence" is (currently) defined as:
  * having a "home" page with contents set by selecting a Document
  * displaying an (optional) ATOM or RSS feed

  Models that have a "presence" on a Melange web site are (currently):
  * any Group (Organization, Club, etc.)
  * any Program
  * the site itself, which is a singleton Presence
  """

  #: Reference to Document containing the contents of the "/home" page
  home = db.ReferenceProperty(
    reference_class=soc.models.document.Document,
    collection_name='home')
  home.help_text = ugettext(
      'Document to be used as the "/home" page static contents.')
  home.group = ugettext("1. Public Info")

  #: Valid ATOM or RSS feed url or None if unused. Feed entries are shown 
  #: on the site page using Google's JavaScript blog widget  
  feed_url = db.LinkProperty(verbose_name=ugettext('Feed URL'))
  feed_url.help_text = ugettext(
      'The URL should be a valid ATOM or RSS feed. '
      'Feed entries are shown on the home page.')
  feed_url.group = ugettext("1. Public Info")

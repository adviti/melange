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

"""This module contains the Work Model."""


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.linkable
import soc.models.user


class Work(soc.models.linkable.Linkable):
  """Model of a Work created by one or more Persons in Roles.

  Work is a "base entity" of other more specific "works" created by Persons
  serving in "roles".

    reviews)  a 1:many relationship between a Work and the zero or more
      Reviews of that Work.  This relation is implemented as the 'reviews'
      back-reference Query of the Review model 'reviewed' reference.
  """

  #: Required 1:1 relationship indicating the User who initially authored the
  #: Work (this relationship is needed to keep track of lifetime document
  #: creation limits, used to prevent spamming, etc.).
  author = db.ReferenceProperty(reference_class=soc.models.user.User,
                                required=True,
                                collection_name="created_documents",
                                verbose_name=ugettext('Created by'))

  #: Required field indicating the "title" of the work, which may have
  #: different uses depending on the specific type of the work. Works
  #: can be indexed, filtered, and sorted by 'title'.
  title = db.StringProperty(required=True,
      verbose_name=ugettext('Title'))
  title.help_text = ugettext(
      'title of the document; often used in the window title')

  #: short name used in places such as the sidebar menu and breadcrumb trail
  #: (optional: title will be used if short_name is not present)
  short_name = db.StringProperty(verbose_name=ugettext('Short name'))
  short_name.help_text = ugettext(
      'short name used, for example, in the sidebar menu')

  #: Required db.TextProperty containing the contents of the Work.
  #: The content is only to be displayed to Persons in Roles eligible to
  #: view them (which may be anyone, for example, with the site front page).
  content = db.TextProperty(verbose_name=ugettext('Content'))

  #: date when the work was created
  created = db.DateTimeProperty(auto_now_add=True)

  #: date when the work was last modified
  modified = db.DateTimeProperty(auto_now=True)

  # indicating wich user last modified the work. Used in displaying Work
  modified_by = db.ReferenceProperty(reference_class=soc.models.user.User,
                                     required=True,
                                     collection_name="modified_documents",
                                     verbose_name=ugettext('Modified by'))

  def name(self):
    """Alias 'title' Property as 'name' for use in common templates.
    """
    return self.title

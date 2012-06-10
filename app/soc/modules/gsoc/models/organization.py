#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""This module contains the GSoC specific Organization Model.
"""


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models import countries

from taggable.taggable import Tag
from taggable.taggable import Taggable
from taggable.taggable import tag_property

import soc.models.organization


class OrgTag(Tag):
  """Model for storing all Organization tags.
  """

  predefined = db.BooleanProperty(required=True, default=False)

  def __init__(self, *args, **kwds):
    """Initialization function.
    """

    Tag.__init__(self, *args, **kwds)
    if not self.predefined:
      self.auto_delete = True

  @classmethod
  def get_or_create(cls, scope, tag_name, predefined=False):
    """Get the Tag object that has the tag value given by tag_value.
    """

    tag_key_name = cls._key_name(scope.key().name(), tag_name)
    existing_tag = cls.get_by_key_name(tag_key_name)
    if existing_tag is None:
      # the tag does not yet exist, so create it.
      def create_tag_txn():
        new_tag = cls(key_name=tag_key_name, tag=tag_name, scope=scope,
            predefined=predefined)
        new_tag.put()
        return new_tag
      existing_tag = db.run_in_transaction(create_tag_txn)
    else:
      # the tag exists, but if predefined argument is True, let us make sure
      # that its value in the store is updated
      if predefined and not existing_tag.predefined:
        existing_tag.predefined = True
        existing_tag.put()
    return existing_tag

  @classmethod
  def get_predefined_for_scope(cls, scope):
    """Get a list of predefined tag objects that has a given scope.
    """

    return db.Query(cls).filter('scope = ', scope).filter(
        'predefined = ', True).fetch(1000)


class GSoCOrganization(Taggable, soc.models.organization.Organization):
  """GSoC Organization model extends the basic Organization model.
  """

  #====================================================================
  # (private) contact information
  #====================================================================

  #: Required field containing a group street address.
  #: Group street address can only be ASCII, not UTF-8 text,
  #: because, if supplied, it might be used as a shipping address.
  contact_street = db.StringProperty(required=True,
      verbose_name=ugettext('Street Address 1'))
  contact_street.help_text = ugettext(
      'street number and name, '
      'only A-z, 0-9 and whitespace characters')
  contact_street.group = ugettext("2. Contact Info (Private)")

  #: Optional field containing the 2nd group street address.
  #: Group street address can only be ASCII, not UTF-8 text,
  #: because, if supplied, it might be used as a shipping address.
  contact_street_extra = db.StringProperty(required=False,
      verbose_name=ugettext('Street Address 2'))
  contact_street_extra.help_text = ugettext(
      '2nd address line usually used for apartment numbers, '
      'only A-z, 0-9 and whitespace characters')
  contact_street_extra.group = ugettext("2. Contact Info (Private)")

  #: Required field containing group address city.
  #: City can only be ASCII, not UTF-8 text, because, if
  #: supplied, it might be used as a shipping address.
  contact_city = db.StringProperty(required=True,
      verbose_name=ugettext('City'))
  contact_city.help_text = ugettext(
      'only A-z, 0-9 and whitespace characters')
  contact_city.group = ugettext("2. Contact Info (Private)")

  #: Required field containing group address state or province.
  #: Group state/province can only be ASCII, not UTF-8
  #: text, because, if supplied, it might be used as a shipping address.
  contact_state = db.StringProperty(
      verbose_name=ugettext('State/Province'))
  contact_state.help_text = ugettext(
      'optional if country/territory does not have states or provinces, '
      'only A-z, 0-9 and whitespace characters')
  contact_state.group = ugettext("2. Contact Info (Private)")

  #: Required field containing address country or territory of the group.
  contact_country = db.StringProperty(required=True,
      verbose_name=ugettext('Country'),
      choices=countries.COUNTRIES_AND_TERRITORIES)
  contact_country.group = ugettext("2. Contact Info (Private)")

  #: Required field containing address postal code of the group (ZIP code in
  #: the United States).Postal code can only be ASCII, not UTF-8
  #: text, because, if supplied, it might be used as a shipping address.
  contact_postalcode = db.StringProperty(required=True,
      verbose_name=ugettext('ZIP/Postal Code'))
  contact_postalcode.help_text = ugettext(
      'Only A-z, 0-9 and whitespace characters')
  contact_postalcode.group = ugettext("2. Contact Info (Private)")

  #: Required contact phone number that will be, amongst other uses,
  #: supplied to shippers along with the shipping address; kept private.
  phone = db.PhoneNumberProperty(required=True,
      verbose_name=ugettext('Phone Number'))
  phone.help_text = ugettext(
      'include complete international calling number with country code, '
      'use numbers only.')
  phone.example_text = ugettext(
      "e.g. 1650253000 for Google's Corp HQ number in the United States")
  phone.group = ugettext("2. Contact Info (Private)")

  #====================================================================
  # (private) shipping information
  #====================================================================

  #: Optional field containing a group street address.
  #: Group street address can only be ASCII, not UTF-8 text,
  #: because, if supplied, it is used as a shipping address.
  shipping_street = db.StringProperty(required=False,
      verbose_name=ugettext('Shipping Street Address 1'))
  shipping_street.help_text = ugettext(
      'street number and name, '
      'only A-z, 0-9 and whitespace characters.'
      'Fill in only if you want the shipping address to differ from the '
      'contact address.')
  shipping_street.group = ugettext("3. Shipping Info (Private and Optional)")

  #: Optional field containing a 2nd line for the shipping street address; kept
  #: private. If shipping address is not present in its entirety, the
  #: group contact address will be used instead. Shipping street address can
  #: only be ASCII, not UTF-8 text, because, if supplied, it is used as a
  #: shipping address.
  shipping_street_extra = db.StringProperty(
      verbose_name=ugettext('Shipping Street Address 2'))
  shipping_street_extra.help_text = ugettext(
      '2nd address line usually used for apartment numbers, '
      'only A-z, 0-9 and whitespace characters. '
      'Fill in only if you want the shipping address to differ from the '
      'contact address.')
  shipping_street_extra.group = ugettext("3. Shipping Info (Private and Optional)")

  #: Optional field containing group address city.
  #: City can only be ASCII, not UTF-8 text, because, if
  #: supplied, it is used as a shipping address.
  shipping_city = db.StringProperty(required=False,
      verbose_name=ugettext('Shipping City'))
  shipping_city.help_text = ugettext(
      'Only A-z, 0-9 and whitespace characters '
      'Fill in only if you want the shipping address to differ from the '
      'contact address.')
  shipping_city.group = ugettext("3. Shipping Info (Private and Optional)")

  #: Optional field containing group address state or province.
  #: Group state/province can only be ASCII, not UTF-8
  #: text, because, if supplied, it is used as a shipping address.
  shipping_state = db.StringProperty(
      verbose_name=ugettext('Shipping State/Province'))
  shipping_state.help_text = ugettext(
      'optional if country/territory does not have states or provinces, '
      'only A-z, 0-9 and whitespace characters '
      'Fill in only if you want the shipping address to differ from the '
      'contact address.')
  shipping_state.group = ugettext("3. Shipping Info (Private and Optional)")

  #: Optional field containing address postal code of the group (ZIP code in
  #: the United States). Postal code can only be ASCII, not UTF-8
  #: text, because, if supplied, it is used as a shipping address.
  shipping_postalcode = db.StringProperty(required=False,
      verbose_name=ugettext('Shipping ZIP/Postal Code'))
  shipping_postalcode.help_text = ugettext(
      'Only A-z, 0-9 and whitespace characters. '
      'Fill in only if you want the shipping address to differ from the '
      'contact address.')
  shipping_postalcode.group = ugettext("3. Shipping Info (Private and Optional)")

  #: Optional field containing address country or territory of the group.
  shipping_country = db.StringProperty(required=False,
      verbose_name=ugettext('Shipping Country'),
      choices=countries.COUNTRIES_AND_TERRITORIES)
  shipping_country.help_text = ugettext(
      'Choose one only if you want the shipping address to differ from the '
      'contact address.')
  shipping_country.group = ugettext("3. Shipping Info (Private and Optional)")

  contrib_template = db.TextProperty(required=False, verbose_name=ugettext(
      'Application template'))
  contrib_template.help_text = ugettext(
      'This template can be used by contributors, such as students'
      ' and other non-member participants, when they apply to contribute'
      ' to the organization.')
  contrib_template.group = ugettext("1. Public Info")

  # whether this org is new to the program
  new_org = db.BooleanProperty(default=False)

  slots = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Slots allocated'))
  slots.help_text = ugettext(
      'The amount of slots allocated to this organization.')

  note = db.TextProperty(required=False, verbose_name=ugettext(
      'Note'))

  slots_desired = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('#amazing proposals'))
  slots_desired.help_text = ugettext(
      'The amount of amazing proposals submitted to this organization that '
      'have a mentor assigned and the organization would _really_ like to '
      'have a slot for.')
  slots_desired.group = ugettext("4. Organization Preferences")

  max_slots_desired = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('#desired slots'))
  max_slots_desired.help_text = ugettext(
      'The amount of slots that this organization would like to receive if '
      'there was an unlimited amount of slots available.')
  max_slots_desired.group = ugettext("4. Organization Preferences")

  slots_calculated = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Slots calculated'))
  slots_calculated.help_text = ugettext(
      'The amount of slots calculated for this organization.')

  nr_applications = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Amount of applications received'))
  nr_applications.help_text = ugettext(
      'The amount of applications received by this organization.')

  nr_mentors = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Amount of mentors assigned'))
  nr_mentors.help_text = ugettext(
      'The amount of mentors assigned to a proposal by this organization.')

  max_score = db.IntegerProperty(required=False, default=5,
      verbose_name=ugettext('Maximum score'))
  max_score.help_text = ugettext(
      'The maximum amount of stars that can be given to a proposal.')
  max_score.group = ugettext("4. Organization Preferences")

  scoring_disabled = db.BooleanProperty(required=False, default=False,
      verbose_name=ugettext('Scoring disabled'))
  scoring_disabled.help_text = ugettext(
      'Check this field if you want to disable private reviews for '
      'student proposals which have been sent to your organization.')
  scoring_disabled.group = ugettext("4. Organization Preferences")

  list_all_mentors = db.BooleanProperty(required=False, default=False,
      verbose_name=ugettext('List all mentors while assigning mentors '
      'to proposal'))
  list_all_mentors.help_text = ugettext(
      'Check this field if you want to list all the mentors (in addition '
      'to the mentors who have shown interest towards the proposal) in '
      'the select box to assign a mentor on the proposal review page.')
  list_all_mentors.group = ugettext('4. Organization Preferences')

  facebook = db.LinkProperty(
      required=False, verbose_name=ugettext("Facebook URL"))
  facebook.help_text = ugettext("URL of the Facebook page of your Organization")
  facebook.group = ugettext("1. Public Info")

  twitter = db.LinkProperty(
      required=False, verbose_name=ugettext("Twitter URL"))
  twitter.help_text = ugettext("URL of the Twitter profile of your Organization")
  twitter.group = ugettext("1. Public Info")

  blog = db.LinkProperty(
      required=False, verbose_name=ugettext("Blog URL"))
  blog.help_text = ugettext("URL of the Blog of your Organization")
  blog.group = ugettext("1. Public Info")

  org_tag = tag_property('org_tag')

  tags = db.StringListProperty(verbose_name=ugettext('Tags'))

  proposal_extra = db.StringListProperty(
      required=True, verbose_name=ugettext("Additional proposal columns"))
  proposal_extra.help_text = ugettext(
      "Additional columns that will be added to all proposals, one per line.")
  proposal_extra.group = ugettext('4. Organization Preferences')

  accepted_student_msg = db.TextProperty(
      required=False, verbose_name=ugettext('Message to accepted students'))
  accepted_student_msg.help_text = ugettext(
      'Message from the organization to be added to the email sent to '
      'accepted students. The format consists of a standard message to '
      'all the accepted students, followed by this message, which is in '
      'turn followed by the signature.')
  accepted_student_msg.group = ugettext('4. Organization Preferences')

  rejected_student_msg = db.TextProperty(
      required=False, verbose_name=ugettext('Message to rejected students'))
  rejected_student_msg.help_text = ugettext(
      'Message from the organization to be added to the email sent to '
      'rejected students. The format consists of a standard message to '
      'all the rejected students, followed by this message, which is in '
      'turn followed by the signature.')
  rejected_student_msg.group = ugettext('4. Organization Preferences')

  def __init__(self, parent=None, key_name=None, app=None, **entity_values):
    """Constructor for GSoCOrganization Model.

    Args:
        See Google App Engine APIs.
    """

    db.Model.__init__(self, parent, key_name, app, **entity_values)

    Taggable.__init__(self, org_tag=OrgTag)

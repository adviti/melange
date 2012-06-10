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

"""Logic related to handling deletion of user accounts.
"""


from google.appengine.api import mail

from soc.logic import accounts
from soc.logic import system


ADMIN_REQUEST_EMAIL_SUBJEST = """
User %(link_id)s has requested account deletion.
"""

ADMIN_REQUEST_EMAIL_BODY = """
Dear application admin,

User %(name)s (%(email)s), whose username is %(link_id)s, has 
requested their account to be deleted. 
"""


def request_account_deletion(user):
  """Requests deletion of user's account from application administrators
  by sending them an email.
  
  This is a temporary method, until we have an automated solution.
  """
  account = accounts.getCurrentAccount(normalize=False)
  sender = system.getApplicationNoReplyEmail()

  subject = ADMIN_REQUEST_EMAIL_SUBJEST % {
      'link_id': user.link_id
      }
  body = ADMIN_REQUEST_EMAIL_BODY % {
      'name': user.name,
      'email': account.email(),
      'link_id': user.link_id
      }

  mail.send_mail_to_admins(sender, subject, body)

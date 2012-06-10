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

"""OrgAppSurvey related functions.
"""


from google.appengine.ext import db

from soc.logic.helper import notifications
from soc.models.org_app_survey import OrgAppSurvey
from soc.models.org_app_record import OrgAppRecord
from soc.tasks import mailer


def getForProgram(program):
  """Return the org_app survey for a given program.

  Args:
    program: program entity for which the survey should be searched
  """
  # retrieve a OrgAppSurvey
  q = OrgAppSurvey.all()
  q.filter('program', program)
  survey = q.get()

  return survey


def setStatus(data, record, new_status, accept_url):
  """Updates the status of an org_app record.

  Args:
    record: an OrgAppRecord
    new_status: the new status that should be assigned to the record
  """
  if record.status == new_status:
    return

  if new_status not in OrgAppRecord.status.choices:
    return

  record_key = record.key()

  context = None

  if new_status in ['accepted', 'rejected']:
    context = notifications.orgAppContext(
        data, record, new_status, accept_url)

  def txn():
    record = db.get(record_key)
    record.status = new_status
    record.put()

    if context:
      sub_txn = mailer.getSpawnMailTaskTxn(context, parent=record)
      sub_txn()

  db.run_in_transaction(txn)

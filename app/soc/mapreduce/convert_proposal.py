#!/usr/bin/python2.5
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

"""GSoCProposal updating mapreduce.
"""


import logging

from google.appengine.ext import db
from google.appengine.ext.mapreduce import operation

from soc.modules.gsoc.models.score import GSoCScore
from soc.modules.gsoc.models.proposal import GSoCProposal


def process(proposal_key):
  def update_proposal_txn():
    proposal = db.get(proposal_key)
    if not proposal:
      logging.error("Missing profile for key '%s'." % proposal_key)
      return False

    number = db.Query(GSoCScore).ancestor(proposal).count()
    proposal.nr_scores = number
    mentor_key = GSoCProposal.mentor.get_value_for_datastore(proposal)
    proposal.has_mentor = bool(mentor_key)
    proposal.put()
    return True

  if db.run_in_transaction(update_proposal_txn):
    yield operation.counters.Increment("proposals_updated")
  else:
    yield operation.counters.Increment("missing_proposal")

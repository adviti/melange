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

"""GCI org proposal processing mapreduce.
"""


import logging

from google.appengine.ext import db
from google.appengine.ext.mapreduce import context
from google.appengine.ext.mapreduce import operation

from soc.models.site import Site
from soc.models.org_app_record import OrgAppRecord

from soc.modules.gci.logic import org_app as org_app_logic
from soc.modules.gci.models.program import GCIProgram
from soc.modules.gci.views.helper.request_data import RequestData
from soc.modules.gci.views.helper.request_data import RedirectHelper


def process(org_app):
  ctx = context.get()
  params = ctx.mapreduce_spec.mapper.params
  program_key = params['program_key']
  # TODO(SRabbelier): should have been a full url
  url = 'gci/profile/organization/%s' % program_key

  # TODO(SRabbelier): create a MapReduce/Task RequestData
  data = RequestData()
  data.program = GCIProgram.get_by_key_name(program_key)
  data.site = Site.get_by_key_name('site')

  if org_app.status == 'pre-accepted':
    org_app_logic.setStatus(data, org_app, 'accepted', url)
    yield operation.counters.Increment("proposals_accepted")
  elif org_app.status == 'pre-rejected':
    org_app_logic.setStatus(data, org_app, 'rejected', url)
    yield operation.counters.Increment("proposals_rejected")
  else:
    yield operation.counters.Increment("proposals_ignored")

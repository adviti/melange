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

"""This module contains the ProposalDuplicatesStatus Model.
"""


from google.appengine.ext import db

import soc.modules.gsoc.models.program


class GSoCAcceptProposalsStatus(db.Model):
  """Model used to store the status of the proposals conversion to projects.
  """

  #: Program in which this proposals conversion running on
  program = db.ReferenceProperty(
      reference_class=soc.modules.gsoc.models.program.GSoCProgram,
      required=True, collection_name='accept_proposals_status')

  #: Status of the accept proposals conversion. When the conversion is
  #: happening the status will be 'proceeded', 'idle' otherwise
  status = db.StringProperty(required=True,
      choices=['idle', 'proceeded'],
      default='idle')

  #: Number of converted proposals to projects so far
  nr_converted_projects = db.IntegerProperty(required=True, default=0)

  #: Time where the conversion started on
  started_on = db.DateTimeProperty(auto_now_add=True)

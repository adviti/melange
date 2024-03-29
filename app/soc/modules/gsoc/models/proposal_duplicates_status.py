#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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


class GSoCProposalDuplicatesStatus(db.Model):
  """Model used to store the status of the duplicate proposals stored
  in the corresponding ProposalDuplicate model.
  """

  #: Program in which this duplicates exist
  program = db.ReferenceProperty(
      reference_class=soc.modules.gsoc.models.program.GSoCProgram,
      required=True, collection_name='duplicates_status')

  #: Status of the duplicate proposals. When the calculation is
  #: happening the status will be 'processing', 'idle' otherwise
  status = db.StringProperty(required=True, choices=['processing', 'idle'],
                             default='idle')

  #: date when this calculation was last updated
  calculated_on = db.DateTimeProperty()

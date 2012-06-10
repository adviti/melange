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

"""This module contains the GCI specific Score Model.
"""


from google.appengine.ext import db

from soc.modules.gci.models.program import GCIProgram


class GCIScore(db.Model):
  """GCIScore model.

  It is applicable to students in order to keep track on the points
  they earn by completing on the tasks. The corresponding GCIProfile
  model is a parent of an entity belonging to this model.
  """

  #: Required reference to the program so we can query for all rankings
  #: in a single program at once.
  program = db.ReferenceProperty(reference_class=GCIProgram, required=True)

  #: total number of points that the student collected by working on tasks
  points = db.IntegerProperty(required=True, default=0)

  #: tasks that have been taken into account when calculating the score
  tasks = db.ListProperty(item_type=db.Key, default=[])

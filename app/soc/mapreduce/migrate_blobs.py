#!/usr/bin/python2.5
#
# Copyright 2012 the Melange authors.
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

"""Blobstore migrating MapReduce.
"""


import logging

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.mapreduce import operation

from soc.modules.gsoc.models.profile import GSoCStudentInfo


class BlobMigration(db.Model):
  """Model representing the mapping from old blob keys to new blob keys.

  The key name for an entity will be the old blob key that the entity maps
  from.
  """
  new_blob_key = db.StringProperty()
  old_blob_key = db.StringProperty()

  @classmethod
  def kind(cls):
    return blobstore.BLOB_MIGRATION_KIND

def migrate(form):
  if not form:
    return None

  old_blob_key = form.key()
  mapping_entity = BlobMigration.get_by_key_name(str(old_blob_key))

  if not mapping_entity:
    return None

  new_blob_key = blobstore.BlobKey(mapping_entity.new_blob_key)
  return new_blob_key


def process(student_entity):
  # Update the tax form blob
  new_blob_key = migrate(student_entity.tax_form)

  if new_blob_key:
    student_entity.tax_form = new_blob_key

  # Update the enrollment form blob
  new_blob_key = migrate(student_entity.enrollment_form)

  if new_blob_key:
    student_entity.enrollment_form = new_blob_key

  # Save the entity
  yield operation.db.Put(student_entity)

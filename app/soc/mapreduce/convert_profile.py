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

"""GSoCProfile updating MapReduce.
"""


import logging

from google.appengine.ext import db
from google.appengine.ext.mapreduce import operation

from soc.models.user import User
from soc.modules.gsoc.models.profile import GSoCProfile


def process(profile_key):
  def convert_profile_txn():
    profile = db.get(profile_key)
    if not profile:
      logging.error("Missing profile for key '%s'." % profile_key)
      return False
    profile._fix_name(commit=False)
    profile.is_student = bool(profile.student_info)
    profile.org_admin_for = list(set(profile.org_admin_for))
    profile.mentor_for = list(set(profile.org_admin_for + profile.mentor_for))
    profile.is_org_admin = bool(profile.org_admin_for)
    profile.is_mentor = bool(profile.mentor_for)
    profile.put()
    return (profile.is_student, profile.is_org_admin, profile.is_mentor)

  result = db.run_in_transaction(convert_profile_txn)

  if not result:
    yield operation.counters.Increment("missing_profile")
    return

  is_student, is_admin, is_mentor = result

  if is_student:
    yield operation.counters.Increment("student_profiles_converted")

  if is_admin:
    yield operation.counters.Increment("admin_profiles_converted")
  elif is_mentor:
    yield operation.counters.Increment("mentor_profiles_converted")

  if is_mentor:
    yield operation.counters.Increment("only_mentor_profiles_converted")

  yield operation.counters.Increment("profiles_converted")

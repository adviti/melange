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

"""Logic related to handling dictionaries.
"""


from google.appengine.ext import db

import datetime


DICT_TYPES = (db.StringProperty, db.IntegerProperty)
STR_TYPES = (datetime.datetime)


def filter(target, keys):
  """Filters a dictonary to only allow items with the given keys.
  
  Args:
    target: The dictionary that is to be filtered
    keys: The list with keys to filter the dictionary on
  
  Returns:
    A dictionary that only contains the (key,value) from target that 
    have their key in keys.
  """
  result = {}
  
  for key, value in target.iteritems():
    if key in keys:
      result[key] = value
  
  return result


def merge(target, updates, sub_merge=False, recursive=False):
  """Like the builtin 'update' method but does not overwrite existing values.

  Args:
    target: The dictionary that is to be updated, may be None
    updates: A dictionary containing new values for the original dict
    sub_merge: Merge a dict or list present in both target and update
    recursive: Determines whether merge_subdicts is recursive

  Returns:
    a new dict, with any missing values from updates merged into target
  """

  target = target.copy() if target else {}

  for key, value in updates.iteritems():
    if key not in target:
      target[key] = value
    elif sub_merge:
      target_value = target[key]

      # try to merge dicts
      if isinstance(value, dict) and isinstance(target_value, dict):
        # the merge becomes recursive by specifying it not only as value
        # to sub_merge but also to recursive
        target[key] = merge(target_value, value,
                            sub_merge=recursive, recursive=recursive)

      # try to merge lists
      if isinstance(value, list) and isinstance(target_value, list):
        target[key] = target_value + value

  return target


def zip(keys, values):
  """Returns a dict containing keys with values.

  If there are more items in keys than in values, None will be used.
  If there are more items in values than in keys, they will be ignored.

  Args:
    keys: the keys for the dictionary
    values: the values for the dictionary
  """

  result = {}

  size = len(keys)

  for i in range(size):
    if i < len(values):
      value = values[i]
    else:
      value = None
    key = keys[i]
    result[key] = value

  return result


def unzip(target, order):
  """Constructs a list from target in the order specified by order.

  Args:
    target: the dictionary to pull the values from
    order: the order of the keys
  """

  return (target[key] for key in order)


def rename(target, keys):
  """Returns a dict containing only the key/value pairs from keys.

  The keys from target will be looked up in keys, and the corresponding
  value from keys will be used instead. If a key is not found, it is skipped.

  Args:
    target: the dictionary to filter
    keys: the fields to filter
  """

  result = {}

  for key, value in target.iteritems():
    if key in keys:
      new_key = keys[key]
      result[new_key] = value

  return result


def split(target):
  """Takes a dictionary and splits it into single-valued dicts.

  If there are any values in target that are a list it is split up
  into a new dictionary instead.

  >>> split({})
  [{}]
  >>> split({'foo':'bar'})
  [{'foo': 'bar'}]
  >>> split({'foo':'bar', 'bar':'baz'})
  [{'foo': 'bar', 'bar': 'baz'}]
  >>> split({'foo':'bar', 'bar':['one', 'two']})
  [{'foo': 'bar', 'bar': 'one'}, {'foo': 'bar', 'bar': 'two'}]
  >>> split({'foo':'bar', 'bar':['one', 'two'], 'baz': ['three', 'four']})
  [{'bar': 'one', 'foo': 'bar', 'baz': 'three'},
  {'bar': 'two', 'foo': 'bar', 'baz': 'three'},
  {'bar': 'one', 'foo': 'bar', 'baz': 'four'},
  {'bar': 'two', 'foo': 'bar', 'baz': 'four'}]
  """

  result = [{}]

  for key, values in target.iteritems():
    # Make the value a list if it's not
    if not isinstance(values, list):
      values = [values]

    tmpresult = []

    # Iterate over all we gathered so far
    for current_filter in result:
      for value in values:
        # Create a new dict from the current filter
        newdict = dict(current_filter)

        # And create a new dict that also has the current key/value pair
        newdict[key] = value
        tmpresult.append(newdict)

    # Update the result for the next iteration
    result = tmpresult

  return result


def groupby(target, group_key):
  """Groups a list of dictionaries by group_key.
  """

  result = {}

  for value in target:
    key_value = value[group_key]

    if not key_value in result:
      result[key_value] = []

    result[key_value].append(value)

  return result


def groupDictBy(target, key, new_key=None):
  """Groups a dictionary by a key.
  """

  if not new_key:
    new_key = key

  result = ((k, v[new_key]) for k, v in target.iteritems() if v[key])
  return dict(result)


def identity(target):
  """Returns a dictionary with the values equal to the keys.
  """

  result = ((i, i) for i in target)
  return dict(result)


def format(target, input):
  """Returns a dictionary with the values formatted with input.
  """

  result = ((k, v % input) for k, v in target.iteritems())
  return dict(result)


def containsAll(target, keys):
  """Returns true iff target contains all keys.
  """

  result = ((i in target) for i in keys)
  return all(result)

def toDict(entity, field_names=None):
  """Returns a dict with all specified values of this entity.

  Args:
    entity: entity to be put in a dictionary
    field_names: the fields that should be included, defaults to
      all fields that are of a type that is in DICT_TYPES.
  """

  result = {}

  if not field_names:
    props = entity.properties().iteritems()
    field_names = [k for k, v in props if isinstance(v, DICT_TYPES)]

  for key in field_names:
    # Skip everything that is not valid
    if not hasattr(entity, key):
      continue

    value = getattr(entity, key)

    if callable(value):
      value = value()

    if isinstance(value, STR_TYPES):
      value = str(value)

    result[key] = value

  return result

def cleanDict(target, filter_fields, escape_safe=False):
  """Returns a version of target with all specified fields html escaped

  Args:
    target: the dictionary that should be escaped
    filter_fields: the fields that should be escaped
    escape_false: also escape fields marked as safe
  """

  from django.utils.html import escape
  from django.utils.safestring import SafeData

  result = target.copy()

  for field in filter_fields:
    data = result[field]

    if not data or (not escape_safe and isinstance(data, SafeData)):
      continue

    result[field] = escape(data)

  return result

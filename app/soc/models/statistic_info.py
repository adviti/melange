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

"""This module contains the StatisticInfo Model.

The entity contain metadata for all the actual statistics which are
available. 

Only one singleton entity should exist across the page. 
"""


from google.appengine.ext import db
from django.utils import simplejson


class StatisticInfo(db.Model):
  """Model class for StatisticInfo.
  """

  #: Should be defined by subclasses
  INSTANCE_KEY_NAME = None

  #: list of JSON encoded data of the statistics
  data = db.StringListProperty(required=True, default=[])

  class Statistic(object):
    """Convenience class which represents a statistic.
    """

    @classmethod
    def fromString(cls, s):
      data = simplejson.loads(s)
      return cls(data['name'], data['is_visible'])

    def __init__(self, name, is_visible):
      """Initialization function for the class.
      
      Args:
       name: name of the statistic
       is_visible: whether the statistic is visible publicly 
      """
      
      self.name = name
      self.is_visible = is_visible

    def __str__(self):
      return simplejson.dumps({
          'name': self.name,
          'is_visible': self.is_visible})

    def __eq__(self, other):
      return self.name == other.name

    def setVisible(self, is_visible):
      self.is_visible = is_visible

    def getVisible(self):
      return self.is_visible

  @classmethod
  def getInstance(cls):
    return cls.get_or_insert(cls.INSTANCE_KEY_NAME)

  def getStatistics(self):
    """Returns a list which contains Statistic instances, one for each
    available statistic.
    """    
    return [self.Statistic.fromString(s) for s in self.data]

  def appendStatistic(self, statistic):
    """Appends a Statistic instance to the entity if it does not exist.
    """
    if not self.hasStatistic(statistic):
      self.data.append(str(statistic))

  def getVisibleStatistics(self):
    """Returns a list which contains a Statistic instance for each visible
    statistic.
    """

    return [s for s in self.getStatistics() if s.is_visible]

  def hasStatistic(self, statistic):
    """Returns True if the specified statistic exists in the instance
    """
    return statistic in self.getStatistics()

  def getStatisticByName(self, name):
    """Returns statistic for the specified name.
    """
    for statistic in self.getStatistics():
      if statistic.name == name:
        return statistic

    raise Exception('Statistic does not exist')

  def removeStatistic(self, statistic):
    """Removes statistic from the entity.
    """
    self.getStatistics().remove(statistic)

  def updateStatistic(self, statistic):
    """Updates an existing statistic in the entity.
    """
    
    updated = False
    for i, item in enumerate(self.data):
      if self.Statistic.fromString(item).name == statistic.name:
        updated = True
        self.data[i] = str(statistic)
        break

    if not updated:
      self.appendStatistic(statistic)

    self.put()

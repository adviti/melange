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


"""General Views/Templates for surveys are in this module.
"""


from django.utils.dateformat import format

from soc.views.helper import lists
from soc.views.helper import surveys
from soc.views.template import Template


DATETIME_FORMAT = 'Y-m-d H:i:s'


def field_or_empty(field_id):
  """In a list return the contents of the field with the id or an empty
  string if the field does not exist.
  """
  def func(ent, *args):
    return getattr(ent, field_id, '')
  return func


class SurveyRecordList(Template):
  """Template for listing all records of a survey.
  """

  def __init__(self, data, survey, record_model, idx=0, description=''):
    """Creates a new SurveyRecordList template.

    Args:
      data: The RequestData object to use.
      survey: The Survey to show the records for
      record_model: The Model class of the Record entities.
      idx: The index of the list to use.
      description: The (optional) description of the list.
    """
    super(SurveyRecordList, self).__init__(data)

    self.survey = survey
    self.record_model = record_model
    self.idx = idx
    self.description = description

    # Create the configuration based on the schema of the survey
    list_config = lists.ListConfiguration()
    schema = surveys.SurveySchema(survey)

    for field in schema:
      label = field.getLabel()
      field_id = field.getFieldName()
      list_config.addColumn(
          field_id, label, field_or_empty(field_id), hidden=True)

    list_config.addColumn(
        'created', 'Created On',
        lambda ent, *args: format(ent.created, DATETIME_FORMAT))
    list_config.addColumn(
        'modified', 'Last Modified On',
        lambda ent, *args: format(ent.modified, DATETIME_FORMAT))
    self.list_config = list_config

  def context(self):
    """Returns the context for the current template.
    """
    list = lists.ListConfigurationResponse(
        self.data, self.list_config, idx=self.idx, description=self.description)
    return {'lists': [list]}

  def listContentResponse(self, request, prefetch=[]):
    """Returns the ListContentResponse object that is constructed from the data.

    Args:
      request: The Django request object.
      prefetch: List of fields to prefetch for increased performance.
    """
    q = self.record_model.all()
    q.filter('survey', self.survey)

    starter = lists.keyStarter

    if prefetch:
      prefetcher = lists.modelPrefetcher(self.record_model, prefetch)
    else:
      prefetcher = None

    response_builder = lists.RawQueryContentResponseBuilder(
        request, self.list_config, q, starter, prefetcher=prefetcher)
    return response_builder.build()

  def templatePath(self):
    """Returns the path to the template.
    """
    return 'v2/soc/list/lists.html'

#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""Helper classes that abstract survey form structure and fields meta data.
"""


import urllib

from django.utils.datastructures import SortedDict
from django.utils.simplejson import loads

from soc.modules.gsoc.logic.survey import getSurveysForProgram


class SurveyField(object):
  """Meta data for single field in the survey form.
  """

  def __init__(self, fields, field_id):
    """Initialize the meta data dictionary for the field
    """
    self.fields = fields
    self.field_id = field_id

    # Assign the meta dictionary corresponding to an individial field
    # to an object attribute
    self.meta_dict = self.fields.get(self.field_id, {})

    # If the field contains multiple choices, it contains additional
    # meta data for each choice and which of them must be checked
    self.choices = []
    self.checked = []

  def getFieldName(self):
    """Returns the name to be used as the property name in the survey record.
    """
    return self.field_id

  def getType(self):
    """Returns the type of the field to which it should be rendered.

    Possible types:
      1. input_text
      2. textarea
      3. radio
      4. checkbox
    """
    return self.meta_dict.get('field_type', '')

  def getLabel(self):
    """Returns the label which should be shown along with the field.
    """
    return urllib.unquote(self.meta_dict.get('label', ''))

  def isRequired(self):
    """Returns True if the field is a mandatory field on the form else False
    """
    return self.meta_dict.get('required', True)

  def requireOtherField(self):
    """Returns True if field needs "Other" option to be rendered automatically.
    """
    return self.meta_dict.get('other', False)

  def getHelpText(self):
    """Returns the help text which should be shown along with the field.
    """
    return self.meta_dict.get('tip', '')

  def getValues(self):
    """Returns the list of options which should be rendered for the field.
    """
    return self.meta_dict.get('values', '')

  def getChoices(self):
    """Returns the list of choices for the field as 2-tuple.

    This format of returning the list of 2-tuples where each 2-tuple
    corresponds to a single option for the multiple choice fields is
    the format that Django uses in its form. So we can directly use this
    list in the Django forms.
    """
    for choice in self.getValues():
      value = urllib.unquote(choice.get('value'))
      self.choices.append((value, value))
      if choice['checked']:
        self.checked.append(value)

    return self.choices

  def getCheckedChoices(self):
    """Returns the list of choices that must be checked as initial values.
    """
    return self.checked


class SurveySchema(object):
  """Meta data containing the form elements needed to build surveys.
  """

  def __init__(self, survey):
    """Intialize the Survey Schema from the provided survey entity.
    """
    self.order, self.fields = loads(survey.schema)

  def __iter__(self):
    """Iterator for providing the fields in order to be used to build surveys.
    """
    for field_id in self.order:
      yield SurveyField(self.fields, field_id)


def dictForSurveyModel(model, program, surveys):
  """Returns a dictionary of link id and entity pairs for given model.

  Args:
    model: The survey model class for which the dictionary must be built
    program: The program to query
    surveys: The list containing the link ids of the surveys
  """
  survey_dict = dict([(e.link_id, e) for e in getSurveysForProgram(
    model, program, surveys)])

  # Create a sorted dictionary to ensure that the surveys are stored
  # in the same order they were asked for in addition to giving key
  # based access to surveys fetched
  survey_sorted_dict = SortedDict()
  for s in surveys:
    survey = survey_dict.get(s)
    if survey:
      survey_sorted_dict[s] = survey

  return survey_sorted_dict

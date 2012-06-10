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

"""Module containing the classes which lets us construct readonly
pages for models.
"""


import collections
import re

from django.template import loader
from django.utils.datastructures import SortedDict

from soc.views.helper.surveys import SurveySchema


class ModelReadOnlyTemplateOptions(object):
  """Class holding options specified in the Meta class of the model template.

  Holds the following options:
    model: an Appengine db.Model class, or None
    css_prefix: the prefix that needs to be added to CSS attributes
        while rendering
    fields: list of appengine model property names to be rendered in the
        template, or None
    hidden_fields: list of appengine model property names to be rendered in the
        template with 'display: none' style, or None
    exclude: list of appengine model property names to be skipped from the
        template, or None
  """

  def __init__(self, options=None):
    """
    """
    self.model = getattr(options, 'model', None)
    self.css_prefix = getattr(options, 'css_prefix',
                              getattr(self.model, '__name__', None))
    self.fields = getattr(options, 'fields', None)
    self.hidden_fields = getattr(options, 'hidden_fields', None)
    self.exclude = getattr(options, 'exclude', None)


class ModelReadOnlyTemplateMetaclass(type):
  """Meta class that alters the creation of model readonly template classes.

  During the creation of the model readonly template class we filter out
  the needed and unnecessary properties from the model using the attributes
  specified in the Meta class of the model readonly template class.
  """

  def __new__(cls, class_name, bases, dict):
    """Method that alters the class attributes in the model readonly template.

    This method alters the creation of the object before initialization by
    adding in the model's attributes that needs to be rendered. It also
    adds other necessary options extracted from the Meta class inside the
    model's readonly template class.
    """
    opts = ModelReadOnlyTemplateOptions(dict.get('Meta', None))

    if opts.model is not None:
      model_fields = SortedDict()
      model_hidden_fields = {}
      for name, prop in sorted(opts.model.properties().iteritems(),
                               key=lambda prop: prop[1].creation_counter):
        if opts.fields and name not in opts.fields:
          if opts.hidden_fields and name in opts.hidden_fields:
            model_hidden_fields[name] = prop
          continue
        if opts.exclude and name in opts.exclude:
          continue

        model_fields[name] = prop

      dict['fields'] = model_fields
      dict['hidden_fields'] = model_hidden_fields

    if opts.css_prefix:
      dict['css_prefix'] = opts.css_prefix

    return super(ModelReadOnlyTemplateMetaclass, cls).__new__(
        cls, class_name, bases, dict)


class ModelReadOnlyTemplate(object):
  """A base class that constructs the readonly template for a given model.

  This uses the same notion that Django's forms APIs use to generate forms
  for given models. The idea is completely inspired from Django's ModelForm
  APIs and tries to mimic the same names that is used there in order to
  provide consistency.

  In addition, to provide more consistency with the Melange's framework
  itself we also add a render method that render this class into an html
  template.
  """

  __metaclass__ = ModelReadOnlyTemplateMetaclass

  template_path = 'v2/modules/gsoc/_readonly_template.html'

  def __init__(self, instance=None):
    """Constructor to initialize the model instance.

    The readonly template will be rendered for the data in this model instance.
    """
    self.instance = instance
    
    for name, field in self.hidden_fields.items():
      self.hidden_fields[name] = getattr(self.instance, name)

  def __iter__(self):
    """Iterator yielding groups of model instance's properties to be rendered.
    """
    grouping = collections.defaultdict(list)

    for name, field in self.fields.items():
      group = getattr(field, 'group', '0. ')
      grouping[group].append((field.verbose_name, getattr(
          self.instance, name)))

    rexp = re.compile(r"\d+. ")

    for group, fields in sorted(grouping.items()):
      yield rexp.sub('', group), fields

  def render(self):
    """Renders the html collecting the attributes available in this class.
    """

    context = {
      'model': self,
      'hidden_fields': self.hidden_fields,
      'css_prefix': self.css_prefix,
    }
    rendered = loader.render_to_string(self.template_path,
                                       dictionary=context)
    return rendered


class SurveyRecordReadOnlyTemplate(ModelReadOnlyTemplate):
  """A base class that constructs the readonly template for given survey record.

  This uses the same notion that is used to build the model based readonly
  templates but the schema read from the survey schema rather than the model.
  """

  template_path = 'v2/modules/gsoc/_survey/readonly_template.html'

  def __init__(self, instance=None):
    """Constructor to initialize the model instance.

    The readonly template will be rendered for the data in this model instance.
    """
    self.instance = instance
    self.schema = None
    if self.instance:
      self.schema = SurveySchema(self.instance.survey)

  def __iter__(self):
    """Iterator yielding groups of record instance's properties to be rendered.
    """
    for name, field in self.fields.items():
      yield field.verbose_name, getattr(self.instance, name)

    if self.schema:
      for field in self.schema:
        field_id = field.getFieldName()
        label = field.getLabel()
        value = getattr(self.instance, field_id, 'N/A')
        if isinstance(value, list):
          value = ', '.join(value)

        yield label, value

  def render(self):
    """Renders the html collecting the attributes available in this class.
    """

    context = {
      'record': self,
      'hidden_fields': self.hidden_fields,
      'css_prefix': self.css_prefix,
    }

    meta = getattr(self, 'Meta', None)
    context['survey_name'] = getattr(meta, 'survey_name', '')

    rendered = loader.render_to_string(self.template_path,
                                       dictionary=context)
    return rendered

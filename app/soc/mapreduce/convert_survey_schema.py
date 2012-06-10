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

"""Map reduce to convert old style survey_content model data into schema
propery in Survey models.
"""


from google.appengine.ext.mapreduce import operation

from django.utils import simplejson as json


def process(survey):
  survey_content = survey.survey_content
  schema = survey.schema

  if survey_content and not schema:
    old_schema_str = survey_content.schema
    if old_schema_str:
      old_schema = eval(old_schema_str)
      order = []
      fields_dict = {}

      def build_options(field):
        values = getattr(survey_content, field, [])
        return [{'checked': False, 'value': v} for v in values]

      for fk in sorted(old_schema, key=lambda key: old_schema[key]['index']):
        f = old_schema[fk]
        question = f.get('question')
        required = f.get('required', False)

        new_f = {
            'label': question,
            'required': required,
            'other': False,
            }

        tip = f.get('tip')
        if tip:
          new_f['tip'] = tip

        f_type = f.get('type')
        if f_type == 'pick_quant':
          new_f['field_type'] = 'radio'
          new_f['values'] = build_options(fk)
        elif f_type == 'pick_multi':
          new_f['field_type'] = 'checkbox'
          new_f['values'] = build_options(fk)
        elif f_type == 'long_answer':
          new_f['field_type'] = 'textarea'
        elif f_type == 'short_answer':
          new_f['field_type'] = 'input_text'

        fields_dict[fk] = new_f
        order.append(fk)

        if f.get('has_comment') == True:
          comment_field = '%s_comment' % fk
          order.append(comment_field)
          fields_dict[comment_field] = {
              'field_type': 'textarea',
              'label': '%s - (Additional Comment)' % question,
              'required': required,
              'other': False,
              }
          if tip:
            new_f['tip'] = tip

      survey.schema = json.dumps([order, fields_dict])

      yield operation.db.Put(survey)
      yield operation.counters.Increment("survey_updated")
    else:
      yield operation.counters.Increment("survey_not_updated")
  else:
    yield operation.counters.Increment("survey_not_updated")

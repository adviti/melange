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

"""Module containing the template for documents.
"""


from soc.views.template import Template
from soc.logic.helper import prefixes
from soc.views.helper import lists

import soc.models.document


class Document(Template):
  def __init__(self, data, entity):
    assert(entity != None)
    self.data = data
    self.entity = entity

  def context(self):
    return {
        'content': self.entity.content,
        'title': self.entity.title,
    }

  def templatePath(self):
    return "v2/soc/_document.html"


def validateForm(data, document_form):
  if not document_form.is_valid():
    return

  cleaned_data = document_form.cleaned_data
  cleaned_data['modified_by'] = data.user

  if data.document:
    document = document_form.save()
  else:
    prefix = data.kwargs['prefix']
    cleaned_data['link_id'] = data.kwargs['document']
    cleaned_data['author'] = data.user
    cleaned_data['prefix'] = prefix
    cleaned_data['scope'] = prefixes.getScopeForPrefix(prefix, data.scope_path)
    cleaned_data['scope_path'] = data.scope_path
    document = document_form.create(key_name=data.key_name)

  return document


class DocumentList(Template):
  """Template for list of documents.
  """

  def __init__(self, request, data, edit_name):
    self.request = request
    self.data = data
    r = data.redirect

    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('title', 'Title')
    list_config.addSimpleColumn('link_id', 'Link ID', hidden=True)
    list_config.addSimpleColumn('short_name', 'Short Name')
    list_config.setRowAction(
        lambda e, *args: r.document(e).urlOf(edit_name))

    list_config.setDefaultPagination(False)
    list_config.setDefaultSort('title')

    self._list_config = list_config

  def context(self):
    description = 'List of documents for %s' % (
            self.data.program.name)

    list = lists.ListConfigurationResponse(
        self.data, self._list_config, 0, description)

    return {
        'lists': [list],
    }

  def getListData(self):
    idx = lists.getListIndex(self.request)
    if idx == 0:
      q = soc.models.document.Document.all()
      q.filter('scope', self.data.program)

      response_builder = lists.RawQueryContentResponseBuilder(
          self.request, self._list_config, q, lists.keyStarter)

      return response_builder.build()
    else:
      return None

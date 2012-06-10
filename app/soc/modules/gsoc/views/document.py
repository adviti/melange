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

"""Module containing the views for GSoC documents page.
"""


from django.conf.urls.defaults import url as django_url

from soc.logic.exceptions import AccessViolation
from soc.logic.exceptions import NotFound
from soc.models.document import Document
from soc.views import document
from soc.views.base_templates import ProgramSelect
from soc.views.helper import url_patterns
from soc.views.helper.access_checker import isSet

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.forms import GSoCModelForm
from soc.modules.gsoc.views.helper.url_patterns import url
from soc.modules.gsoc.views.helper import url_patterns as gsoc_url_patterns


class GSoCDocumentForm(GSoCModelForm):
  """Django form for creating documents.
  """

  class Meta:
    model = Document
    exclude = [
        'scope', 'scope_path', 'author', 'modified_by', 'prefix', 'home_for',
        'link_id', 'read_access', 'write_access', 'is_featured'
    ]


class EditDocumentPage(RequestHandler):
  """Encapsulate all the methods required to edit documents.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/document/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'document/edit/%s$' % gsoc_url_patterns.DOCUMENT, self,
            name='edit_gsoc_document'),
        url(r'document/edit/%s$' % gsoc_url_patterns.ORG_DOCUMENT, self,
            name='edit_gsoc_document'),
    ]

  def checkAccess(self):
    self.mutator.documentKeyNameFromKwargs()

    assert isSet(self.data.key_name)

    self.check.canEditDocument()

  def context(self):
    form = GSoCDocumentForm(self.data.POST or None, instance=self.data.document)

    if self.data.document:
      page_name = 'Edit %s' % self.data.document.title
    else:
      page_name = 'Create new Document'

    return {
        'page_name': page_name,
        'document_form': form,
    }

  def post(self):
    """Handler for HTTP POST request.
    """
    form = GSoCDocumentForm(self.data.POST or None, instance=self.data.document)
    validated_document = document.validateForm(self.data, form)
    if validated_document:
      self.redirect.document(validated_document)
      self.redirect.to('edit_gsoc_document')
    else:
      self.get()


class DocumentPage(RequestHandler):
  """Encapsulate all the methods required to show documents.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'document/show/%s$' % gsoc_url_patterns.DOCUMENT, self,
            name='show_gsoc_document'),
        url(r'document/show/%s$' % gsoc_url_patterns.ORG_DOCUMENT, self,
            name='show_gsoc_document'),
        django_url(r'^document/show/%s$' % gsoc_url_patterns.DOCUMENT,
                   self),
        django_url(r'^document/show/%s$' % gsoc_url_patterns.ORG_DOCUMENT,
                   self),
    ]

  def checkAccess(self):
    self.mutator.documentKeyNameFromKwargs()

    if not self.data.document:
      raise NotFound("No such document: '%s'" % self.data.key_name)

    self.check.canViewDocument()

  def context(self):
    return {
        'tmpl': document.Document(self.data, self.data.document),
        'page_name': self.data.document.title,
    }


class EventsPage(RequestHandler):
  """Encapsulates all the methods required to show the events page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/document/events.html'

  def djangoURLPatterns(self):
    return [
        url(r'events/%s$' % url_patterns.PROGRAM, self,
            name='gsoc_events')
    ]

  def checkAccess(self):
    self.data.document = self.data.program.events_page
    self.check.canViewDocument()

  def context(self):
    return {
        'document': self.data.program.events_page,
        'frame_url': self.data.program.events_frame_url,
        'page_name': 'Events and Timeline',
    }


class DocumentList(document.DocumentList):
  """Template for list of documents.
  """

  def __init__(self, request, data):
    super(DocumentList, self).__init__(request, data, 'edit_gsoc_document')

  def templatePath(self):
    return 'v2/modules/gsoc/document/_document_list.html'


class DocumentListPage(RequestHandler):
  """View for the list documents page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/document/document_list.html'

  def djangoURLPatterns(self):
    return [
        url(r'documents/%s$' % url_patterns.PROGRAM, self,
            name='list_gsoc_documents'),
    ]

  def checkAccess(self):
    self.check.isHost()

  def jsonContext(self):
    list_content = DocumentList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def context(self):
    return {
        'page_name': "Documents for %s" % self.data.program.name,
        'document_list': DocumentList(self.request, self.data),
        'program_select': ProgramSelect(self.data, 'list_gsoc_documents'),
    }

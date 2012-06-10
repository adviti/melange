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

"""Blobstore Django helpers.

These helpers are used to handle uploading and downloading appengine blobs.

With due credits, this is not Melange code. This was shamelessly
flicked from http://appengine-cookbook.appspot.com/recipe/blobstore-get_uploads-helper-function-for-django-request/
Credits and big thanks to to: sebastian.serrano and emi420
"""


import cgi
import logging
import urllib

from google.appengine.ext import blobstore

from soc.logic.exceptions import BadRequest
from soc.views.helper.response import Response


def _parseField(request, key, field):
  """Parses one field.

  Handles BlobInfo objects and adds the 'name' field for Django.
  """
  if isinstance(field, cgi.FieldStorage) and 'blob-key' in field.type_options:
    blob_info = blobstore.parse_blob_info(field)
    uploads = request.__uploads.setdefault(key, [])
    uploads.append(blob_info)

    # Put the BlobInfo in the POST data and format it for Django by
    # adding the name property.
    blob_info.name = blob_info.filename
    request.file_uploads[key] = blob_info
  elif isinstance(field, list):
    request.POST[key] = [f.value for f in field]
  else:
    request.POST[key] = field.value


def cacheUploads(request):
  """Caches uploads in the request.__uploads field.

  Also recreates the POST dictionary.

  The __uploads attribute in the request object is used only to cache
  the file uploads so that we do not have to go through the process of
  reading HTTP request original file if it has already been read in
  the same request.

  Args:
    request: a django Request object
  """
  if hasattr(request, '__uploads'):
    return

  wsgi_input = request.META['wsgi.input']
  wsgi_input.seek(0)

  fields = cgi.FieldStorage(wsgi_input, environ=request.META)

  request.POST = {}
  request.file_uploads = {}
  request.__uploads = {}

  for key in fields.keys():
    field = fields[key]
    _parseField(request, key, field)


def getUploads(request, field_name=None):
  """Get uploads sent to this handler.

  Args:
    field_name: Only select uploads that were sent as a specific field
  Returns:
    A list of BlobInfo records corresponding to each upload
    Empty list if there are no blob-info records for field_name
  """

  results = []
  cacheUploads(request)

  if field_name:
    return request.file_uploads.get(field_name, [])

  for uploads in request.__uploads.itervalues():
    results += uploads

  return results


def sendBlob(blob_info):
  """Send a blob-response based on a blob_key.

  Sets the correct response header for serving a blob.  If BlobInfo
  is provided and no content_type specified, will set request content type
  to BlobInfo's content type.

  Args:
    blob_info: BlobInfo record to serve

  Raises:
    BadRequest: on missing filename in blob_info
  """
  logging.debug(blob_info)
  assert isinstance(blob_info, blobstore.BlobInfo)

  CONTENT_DISPOSITION = 'attachment; filename="%s"'

  content_type = blob_info.content_type
  filename = blob_info.filename

  if isinstance(content_type, unicode):
    content_type = content_type.encode('utf-8')

  if not filename:
    raise BadRequest('No filename in blob_info.')

  if isinstance(filename, unicode):
    filename = filename.encode('utf-8')

  response = Response()
  response['Content-Type'] = content_type
  response['Content-Disposition'] = (CONTENT_DISPOSITION % filename)
  response[blobstore.BLOB_KEY_HEADER] = str(blob_info.key())

  return response

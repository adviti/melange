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

"""Module that generates the lists.
"""


import logging

from google.appengine.ext import db

from django.utils import simplejson

from soc.views.template import Template


def getListIndex(request):
  """Returns the index of the requested list.
  """
  if 'idx' in request.GET:
    idx = request.GET['idx']
  elif 'idx' in request.POST:
    idx = request.POST['idx']
  else:
    return -1

  idx = int(idx) if idx.isdigit() else -1

  return idx


class ListConfiguration(object):
  """Resembles the configuration of a list. This object is sent to the client
  on page load.

  See the wiki page on ListProtocols for more information
  (http://code.google.com/p/soc/wiki/ListsProtocol).

  Public fields are:
    description: The description as shown to the end user.
    autowidth: Whether the width of the columns should be automatically set.
    height: Whether the height of the list should be automatically set.
    multiselect: If true then the list will have a column with checkboxes which
                 allows the user to select a number of rows.
    toolbar: [boolean, string] showing if and where the toolbar with buttons
             should be present.
  """

  VALID_EDIT_TYPES = [
      'text', 'textarea', 'select', 'checkbox', 'password',
      'button', 'image', 'file'
  ]

  def __init__(self, add_key_column=True):
    """Initializes the configuration.

    If add_key_column is set will add a 'key' column with the key id/name.
    """
    self._col_names = []
    self._col_model = []
    self._col_map = {}
    self._col_functions = {}
    self._row_num = 50
    self._row_list = [5, 10, 20, 50, 100, 500, 1000]
    self.autowidth = True
    self._sortname = ''
    self._sortorder = 'asc'
    self._footer_row = False
    self.height = 'auto'
    self.multiselect = False
    self.toolbar = [True, 'top']

    self._buttons = {}
    self._button_functions = {}
    self._row_operation = {}
    self._row_operation_func = None
    self._row_buttons = {}
    self._row_button_functions = {}

    self._templates = {}
    
    self._features = None

    if add_key_column:
      self._addKeyColumn()

  def _addKeyColumn(self):
    """Adds a column for the key.
    """
    func = lambda e, *args: str(e.key().id_or_name())
    self.addColumn('key', 'Key', func, hidden=True)

  def setDefaultPagination(self, row_num, row_list=None):
    """Sets the default pagination.

    If row_num is False then pagination is disabled, and the row_list
    argument is ignored.

    Args:
        row_num: The number of rows that should be shown on a page on default.
        row_list: List of integers which is the allowed pagination size a user
                  can can choose from.
    """
    if not row_num:
      self._row_num = -1
      self._row_list = []
      return

    self._row_num = row_num

    if row_list:
      self.row_list = row_list

  def addColumn(self, col_id, name, func,
                width=None, resizable=True,
                hidden=False, searchhidden=True, options=None):
    """Adds a column to the end of the list.

    Args:
      col_id: A unique identifier of this column.
      name: The header of the column that is shown to the user.
      func: The function to be called when rendering this column for
            a single entity. This function should take an entity as first
            argument and args and kwargs if needed. The string rendering of
            the return value will be sent to the end user.
      width: The width of the column.
      resizable: Whether the width of the column should be resizable by the
                 end user.
      hidden: Whether the column should be hidden by default.
      searchhidden: Whether this column should be searchable when hidden.
      options: An array of (regexp, display_value) tuples.
    """
    if self._col_functions.get(col_id):
      logging.warning('Column with id %s is already defined' % col_id)

    if not callable(func):
      raise TypeError('Given function is not callable')

    model = {
        'name': col_id,
        'index': col_id,
        'resizable': resizable,
        'hidden': hidden,
    }

    if width:
      model['width'] = width

    if options:
      values = ";".join("%s:%s" % i for i in options)

      model["stype"] = "select"
      model["editoptions"] = dict(value=values)

    if searchhidden:
      model["searchoptions"] = {
        "searchhidden": True
      }

    self._col_model.append(model)
    self._col_map[col_id] = model
    self._col_names.append(name)
    self._col_functions[col_id] = func

  def __addRowButton(self, col_id, button_id, caption, type, classes,
                     parameters):
    """Internal method for adding row buttons so that the uniqueness of
    the column id can be checked.

    Args:
      col_id: a unique identifier of the column that the button should be
          displayed on
      button_id: a unique identifier of the button which should be 
          unique per column
      type: type of the button
      classes: css classes that should be appended to the button
      parameters: a dictionary of parameters and their values which should be
          associated with the button
    """

    column_row_buttons = self._row_buttons.get(col_id, {})
    if column_row_buttons and column_row_buttons.get(button_id):
      logging.warning('Button with name %s is already defined for column %s'
          % (button_id, col_id))

    button_config = {
        'caption': caption,
        'type': type,
        'classes': classes if classes is not None else [],
        'parameters': parameters
        }

    column_row_buttons[button_id] = button_config
    self._row_buttons[col_id] = column_row_buttons

  def addCustomRedirectRowButton(self, col_id, button_id, caption, func,
                                 classes=None, new_window=False):
    """Adds a custom redirect row button to the specified column.
    """
    parameters = {
        'new_window': new_window
        }
    self.__addRowButton(col_id, button_id, caption, 'redirect_simple',
        classes, parameters)
    column_row_button_functions = self._row_button_functions.get(col_id, {})
    column_row_button_functions[button_id] = func
    self._row_button_functions[col_id] = column_row_button_functions

  def addSimpleRedirectRowButton(self, col_id, button_id, caption, url,
                                 classes=None, new_window=False):
    """Adds a simple redirect row button the the specified column with
    the same link for each entity.
    """

    # always return the static url
    func = lambda e, *args: url

    self.addCustomRedirectRowButton(col_id, button_id, caption, func,
        classes, new_window)

  def addSimpleColumn(self, col_id, name, **kwargs):
    """Adds a column to the end of the list which uses the id of the column as
    attribute name of the entity to get the data from.

    This method is basically a shorthand for addColumn with the function as
    lambda ent, *args: getattr(ent, id).

    Args:
      col_id: A unique identifier of this column and name of the field to get
          the data from.
      name: The header of the column that is shown to the user.
      **kwargs: passed on to addColumn
    """
    func = lambda ent, *args: getattr(ent, col_id)
    self.addColumn(col_id, name, func, **kwargs)

  def addDictColumn(self, col_id, name, **kwargs):
    """Adds a column to the end of the list which uses the id of the column as
    key of the dictionary to get the data from.

    This method is basically a shorthand for addColumn with the function as
    lambda d, *args: d[id].

    Args:
      col_id: A unique identifier of this column and name of the field to get
          the data from.
      name: The header of the column that is shown to the user.
      **kwargs: passed on to addColumn
    """
    func = lambda d, *args: d[col_id]
    self.addColumn(col_id, name, func, **kwargs)

  def __addButton(self, col_id, caption, bounds, col_type, parameters):
    """Internal method for adding buttons so that the uniqueness of the id can
    be checked.
    """
    if self._buttons.get(col_id):
      logging.warning('Button with id %s is already defined' % col_id)

    button_config = {
        'id': col_id,
        'caption': caption,
        'type': col_type,
        'parameters': parameters
    }

    if bounds:
      button_config['bounds'] = bounds

    self._buttons[col_id] = button_config

  def setColumnEditable(self, col_id, editable, edittype=None, editoptions=None):
    """Sets the editability for the specified column.

    Args:
      editable: A boolean indicating whether the column should be editable.
      edittype: A string indicating the type of values that should be entered,
          see VALID_EDIT_TYPES for a list of valid values.
      editoptions: A dictionary with options for the edit field.
    """
    model = self._col_map.get(col_id)

    if not model:
      raise ValueError('Id %s is not a defined column (Known columns %s)'
                       % (col_id, self._col_map.keys()))

    if edittype and edittype not in self.VALID_EDIT_TYPES:
      raise ValueError("Invalid edit type '%s', known edit types: %s" % (
          edittype, self.VALID_EDIT_TYPES))

    model['editable'] = editable

    if edittype:
      model['edittype'] = edittype

    if editoptions:
      model['editoptions'] = editoptions

  def setColumnSummary(self, col_id, summary_type, summary_tpl):
    """Sets the column summary for the specified column.

    Args:
      summary_type: the summary type
      summary_tpl: the summary template
    """
    model = self._col_map.get(col_id)

    if not model:
      raise ValueError('Id %s is not a defined column (Known columns %s)'
                       % (col_id, self._col_map.keys()))

    model['summaryType'] = summary_type
    model['summaryTpl'] = summary_tpl

    self._footer_row = True

  def setColumnExtra(self, col_id, **kwargs):
    """Sets the column 'extra' field.

    Args:
      col_id: The unique identifier of the column.
      **kwargs: the contents of the 'extra' field.
    """
    model = self._col_map.get(col_id)

    if not model:
      raise ValueError('Id %s is not a defined column (Known columns %s)'
                       % (col_id, self._col_map.keys()))

    if model.get('extra'):
      logging.warning('Column with id %s already has extra defined' % col_id)

    model['extra'] = kwargs

  def addTemplateColumn(self, col_id, name, template, **kwargs):
    """Adds a new template column.
    """
      
    self.addColumn(col_id, name, lambda *args, **kwargs: '' , **kwargs)

    if self._templates.get(col_id):
      logging.warning(
          'Template column with id %s already has template defined.' % col_id)

    self._templates[col_id] = template

  def addSimpleRedirectButton(self, button_id, caption, url, new_window=True):
    """Adds a button to the list that simply opens a URL.

    Args:
      button_id: The unique id the button.
      caption: The display string shown to the end user.
      url: The url to redirect the user to.
      new_window: Boolean indicating whether the url should open in a new
                  window.
    """
    parameters = {
        'link': url,
        'new_window': new_window
    }
    bounds = [0, 'all']
    # add a simple redirect button that is always active.
    self.__addButton(button_id, caption, bounds, 'redirect_simple', parameters)

  def addCustomRedirectButton(self, button_id, caption, func, new_window=True):
    """Adds a button to the list that simply opens a URL.

    Args:
      button_id: The unique id of the button.
      caption: The display string shown to the end user.
      func: The function to generate a url to redirect the user to.
            This function should take an entity as first argument and args and
            kwargs if needed. The return value of this function should be a
            dictionary with the value for 'link' set to the url to redirect the
            user to. A value for the key 'caption' can also be returned to
            dynamically change the caption off the button.
      new_window: Boolean indicating whether the url should open in a new
                  window.
    """
    if not callable(func):
      raise TypeError('Given function is not callable')

    parameters = {'new_window': new_window}
    # add a custom redirect button that is active on a single row
    self.__addButton(id, caption, [1, 1], 'redirect_custom', parameters)
    self._button_functions[id] = func

  def addPostButton(self, button_id, caption, url, bounds, keys,
                    refresh='current', redirect=False):
    """This button is used when there is something to send to the backend in a
    POST request.

    Sets multiselect to True.

    Args:
      button_id: The unique id of the button.
      caption: The display string shown to the end user.
      url: The URL to make the POST request to.
      bounds: An array of size two with integers or of an integer and the
              keyword "all". This indicates how many rows need to be selected
              for the button to be pressable.
      keys: A list of column identifiers of which the content of the selected
            rows will be send to the server when the button is pressed.
      refresh: Indicates which list to refresh, is the current list by default.
               The keyword 'all' can be used to refresh all lists on the page or
               a integer index referring to the idx of the list to refresh can
               be given.
      redirect: Set to True to have the user be redirected to a URL returned by
                the URL where the POST request hits.
    """
    self.multiselect = True

    parameters = {
        'url': url,
        'keys': keys,
        'refresh': refresh,
        'redirect': redirect,
    }
    self.__addButton(button_id, caption, bounds, 'post', parameters)

  def addPostEditButton(self, button_id, caption, url='', keys=[], refresh='current'):
    """This button is used when all changed values should be posted.

    Args:
      See addPostButton
    """
    parameters = {
        'url': url,
        'refresh': refresh,
    }

    if keys:
      parameters['keys'] = keys

    self.__addButton(button_id, caption, None, 'post_edit', parameters)

  def setRowAction(self, func, new_window=True):
    """The redirects the user to a URL when clicking on a row in the list.

    This sets multiselect to False as indicated in the protocol spec.

    Args:
      func: The function that returns the url to redirect the user to.
            This function should take an entity as first argument and args and
            kwargs if needed.
      new_window: Boolean indicating whether the url should open in a new
                  window.
    """
    if not callable(func):
      raise TypeError('Given function is not callable')

    self.multiselect = False

    parameters = {'new_window': new_window}
    self._row_operation = {
        'type': 'redirect_custom',
        'parameters': parameters
        }
    self._row_operation_func = func

  def setDefaultSort(self, col_id, order='asc'):
    """Sets the default sort order for the list.

    Args:
      id: The id of the column to sort on by default. If this evaluates to
      False then the default sort order will be removed.
      order: The order in which to sort, either 'asc' or 'desc'.
             The default value is 'asc'.
    """
    if col_id and col_id not in self._col_map:
      raise ValueError('Id %s is not a defined column (Known columns %s)'
                       % (col_id, self._col_map.keys()))

    if order not in ['asc', 'desc']:
      raise ValueError('%s is not a valid order' % order)

    self._sortname = col_id if col_id else ''
    self._sortorder = order

  def setFeatures(self, features):
    """Sets features for the list.
    """
    self._features = features


class ListFeatures(object):
  """Represents features of the list which define, for instance, which
  elements should be displayed.
  """

  @classmethod
  def defaultFeatures(cls):
    """Constructs a default ListFeatures object which may be used, when a list
    does not define one on its own.
    """

    features = cls()
    features.setCookieService(True)
    features.setColumnSearch(True, True)
    features.setColumnShowHide(True)
    features.setSearchDialog(True)
    features.setCsvExport(True)
    features.setGlobalSearch(False, '')
    features.setGloablSort(False, '')
    return features

  def __init__(self):
    """Initializes values of the newly created object.
    """

    self._cookie_service = {
        'enabled': False,
        }

    self._column_search = {
        'enabled': False,
        'regexp': False
        }

    self._columns_show_hide = {
        'enabled': False
        }

    self._search_dialog = {
        'enabled': False
        }

    self._csv_export = {
        'enabled': False
        }

    self._global_search = {
        'enabled': False,
        'element_path': ''
        }

    self._global_sort = {
        'enabled': False,
        'element_paths': ''
        }

  def setCookieService(self, enabled):
    self._cookie_service['enabled'] = enabled

  def setColumnSearch(self, enabled, regexp):
    self._column_search['enabled'] = enabled
    self._column_search['regexp'] = regexp

  def setColumnShowHide(self, enabled):
    self._columns_show_hide['enabled'] = enabled

  def setSearchDialog(self, enabled):
    self._search_dialog['enabled'] = enabled

  def setCsvExport(self, enabled):
    self._csv_export['enabled'] = enabled

  def setGlobalSearch(self, enabled, element_path):
    if enabled:
      if not element_path:
        logging.warning('Trying to enable global search with no element_path')
    else:
      if element_path:
        logging.warning('Non empty element_path in disabled global search')

    self._global_search['enabled'] = enabled
    self._global_search['element_path'] = element_path

  def setGloablSort(self, enabled, element_paths):
    if enabled:
      if not element_paths:
        logging.warning('Trying to enable global sort with no element_paths')
    else:
      if element_paths:
        logging.warning('Non empty element_paths in disabled global sort')

    self._global_sort['enabled'] = enabled
    self._global_sort['element_paths'] = element_paths

  def get(self):
    """Returns a dictionary which contains all the features.
    """

    return {
        'cookie_service': self._cookie_service,
        'column_search': self._column_search,
        'columns_show_hide': self._columns_show_hide,
        'search_dialog': self._search_dialog,
        'csv_export': self._csv_export,
        'global_search': self._global_search,
        'global_sort': self._global_sort,
        }

class ListConfigurationResponse(Template):
  """Class that builds the template for configuring a list.
  """

  def __init__(self, data, config, idx, description='', preload_list=True):
    """Initializes the configuration.

    Args:
      data: a RequestData object
      config: A ListConfiguration object.
      idx: A number uniquely identifying this list. ValueError will be raised if
           not an int.
      description: The description of this list, as should be shown to the
                   user.
      preload_list: Boolean to indicate whether the list should be loaded
          when this configuration is rendered. If you want the list to be
          loaded later (such as in the iconic dashboard) set preload_list
          to False.
    """
    self._data = data
    self._config = config
    self._idx = int(idx)
    self._description = description
    self._preload_list = preload_list

    super(ListConfigurationResponse, self).__init__(data)

  def context(self):
    """Returns the context for the current template.
    """
    configuration = self._constructConfigDict()

    context = {
        'idx': self._idx,
        'configuration': simplejson.dumps(configuration),
        'description': self._description,
        'preload_list': self._preload_list
        }
    return context

  def _constructConfigDict(self):
    """Builds the core of the list configuration that is sent to the client.

    Among other things this configuration defines the columns and buttons
    present on the list.
    """
    configuration = {
        'autowidth': self._config.autowidth,
        'colNames': self._config._col_names,
        'colModel': self._config._col_model,
        'height': self._config.height,
        'rowList': self._config._row_list,
        'rowNum': self._config._row_num,
        'sortname': self._config._sortname,
        'sortorder': self._config._sortorder,
        'multiselect': self._config.multiselect,
        'multiboxonly': self._config.multiselect,
        'toolbar': self._config.toolbar,
    }

    if self._config._footer_row:
      configuration['footerrow'] = self._config._footer_row

    if self._config._features:
      features = self._config._features
    else:
      features = ListFeatures.defaultFeatures()

    operations = {
        'buttons': self._config._buttons,
        'row': self._config._row_operation,
    }

    listConfiguration = {
      'configuration': configuration,
      'features': features.get(),
      'operations': operations,
      'templates': self._config._templates,
    }
    return listConfiguration

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return 'v2/soc/list/list.html'


class ListContentResponse(object):
  """Class that builds the response for a list content request.
  """

  def __init__(self, request, config):
    """Initializes the list response.

    The request given can define the start parameter in the GET request
    otherwise an empty string will be used indicating a request for the first
    batch.

    Public fields:
      start: The start argument as parsed from the request.
      next: The value that should be used to query for the next set of
            rows. In other words what start will be on the next roundtrip.
      limit: The maximum number of rows to return as indicated by the request,
             defaults to 50. This is not enforced by this object.

    Args:
      request: The HTTPRequest containing the request for data.
      config: A ListConfiguration object
    """
    self._request = request
    self._config = config

    self.__rows = []

    get_args = request.GET
    self.next = ''
    self.start =  get_args.get('start', '')
    self.limit = int(get_args.get('limit', 50))

  def addRow(self, entity, *args, **kwargs):
    """Renders a row for a single entity.

    Args:
      entity: The entity to render.
      args: The args passed to the render functions defined in the config.
      kwargs: The kwargs passed to the render functions defined in the config.
    """
    columns = {}
    for col_id, func in self._config._col_functions.iteritems():
      val = func(entity, *args, **kwargs)
      columns[col_id] = val if val != None else ''

    row = {}
    buttons= {}
    row_buttons = {}

    if self._config._row_operation_func:
      # perform the row operation function to retrieve the link
      link = self._config._row_operation_func(entity, *args, **kwargs)
      if link:
        row['link'] = link

    for button_id, func in self._config._button_functions.iteritems():
      # The function called here should return a dictionary with 'link' and
      # an optional 'caption' as keys.
      buttons[button_id] = func(entity, *args, **kwargs)

    for col_id, buttons in self._config._row_buttons.iteritems():
      row_buttons[col_id] = {
          'buttons_def': {},
          }
      for button_id, button_config in buttons.iteritems():
        func = self._config._row_button_functions[col_id][button_id]
        link = func(entity)
        if link:
          button_config['parameters']['link'] = link
          row_buttons[col_id]['buttons_def'][button_id] = button_config

    operations = {
        'row': row,
        'buttons': buttons,
        'row_buttons': row_buttons
    }

    data = {
      'columns': columns,
      'operations': operations,
    }
    self.__rows.append(data)

  def content(self):
    """Returns the object that should be parsed to JSON.
    """
    data = {self.start: self.__rows}
    return {'data': data,
            'next': self.next}


def collectKeys(prop, data):
  """Collects all keys for the specified property.
  """
  keys = [prop.get_value_for_datastore(i) for i in data]
  return [i for i in keys if i]


def collectParentKeys(data):
  """Collects all parent keys for the specified data.
  """
  keys = [i.parent_key() for i in data]
  return [i for i in keys if i]


def distributeKeys(prop, data, prefetched_dict):
  """Distributes the keys for the specified property.
  """
  for i in data:
    key = prop.get_value_for_datastore(i)
    #key = str(key)

    if key not in prefetched_dict:
      continue

    value = prefetched_dict[key]
    setattr(i, prop.name, value)


def distributeParentKeys(data, prefetched_dict):
  """Distributes the keys for the parent property.

  Uses an AppEngine internal api (the _parent property). See also:
  https://groups.google.com/forum/#!topic/google-appengine-python/eBAzvJRAvH8
  """
  for i in data:
    key = i.parent_key()

    if key not in prefetched_dict:
      continue

    value = prefetched_dict[key]
    try:
      # BAD BAD BAD
      i._parent = value
    except Exception, e:
      logging.exception(e)


def prefetchFields(model, fields, data, parent):
  """Prefetches the specified fields in data.
  """
  keys = []

  for field in fields:
    prop = getattr(model, field, None)

    if not prop:
      logging.exception("Model %s does not have attribute %s" %
                        (model.kind(), field))
      return

    if not isinstance(prop, db.ReferenceProperty):
      logging.exception("Property %s of %s is not a ReferenceProperty but a %s" %
                        (field, model.kind(), prop.__class__.__name__))
      return

  for field in fields:
    prop = getattr(model, field)
    keys += collectKeys(prop, data)

  if parent:
    keys += collectParentKeys(data)

  prefetched_entities = db.get(keys)
  prefetched_dict = dict((i.key(), i) for i in prefetched_entities if i)

  for field in fields:
    prop = getattr(model, field)
    distributeKeys(prop, data, prefetched_dict)

  if parent:
    distributeParentKeys(data, prefetched_dict)


def modelPrefetcher(model, fields, parent=False):
  """Returns a prefetcher for the specified model and fields.
  """
  def prefetcher(entities):
    prefetchFields(model, fields, entities, parent)
    return [], {}
  return prefetcher


def prefetchListFields(model, fields, data):
  """Prefetches the specified list fields in data.
  """
  for field in fields:
    prop = getattr(model, field, None)

    if not prop:
      logging.exception("Model %s does not have attribute %s" %
                        (model.kind(), field))
      return

    if not isinstance(prop, db.ListProperty):
      logging.exception("Property %s of %s is not a ReferenceProperty but a %s" %
                        (field, model.kind(), prop.__class__.__name__))
      return

  keys = []

  for field in fields:
    for i in data:
      keys += getattr(i, field)

  prefetched_entities = db.get(keys)
  prefetched_dict = dict((i.key(), i) for i in prefetched_entities if i)

  return prefetched_dict


def listPrefetcher(model, fields):
  """Returns a prefetcher for the specified models and list fields.
  """
  def prefetcher(entities):
    prefetched_entities = prefetchListFields(model, fields, entities)
    return [prefetched_entities], {}
  return prefetcher


def listModelPrefetcher(model, fields, list_fields, parent=False):
  """Returns a prefetcher for the specified model and (list) fields.
  """
  def prefetcher(entities):
    prefetchFields(model, fields, entities, parent)
    prefetched_entities = prefetchListFields(model, list_fields, entities)
    return [prefetched_entities], {}
  return prefetcher


def keyStarter(start, q):
  """Returns a starter for the specified key-based model.
  """
  if not start:
    return True
  if '/' in start:
    return False
  try:
    start_entity = db.get(start)
  except db.BadKeyError, e:
    return False
  if not start_entity:
    return False
  q.filter('__key__ >=', start_entity.key())
  return True


class RawQueryContentResponseBuilder(object):
  """Builds a ListContentResponse for lists that are based on a single query.
  """

  def __init__(self, request, config, query, starter,
               ender=None, skipper=None, prefetcher=None,
               row_adder=None):
    """Initializes the fields needed to built a response.

    Args:
      request: The HTTPRequest containing the request for data.
      config: The ListConfiguration object.
      fields: The fields to query on.
      query: The query object to use.
      starter: The function used to retrieve the start entity.
      ender: The function used to retrieve the value for the next start.
      skipper: The function used to determine whether to skip a value.
      prefetch: The fields that need to be prefetched for increased
                performance.
    """
    if not ender:
      ender = lambda entity, is_last, start: (
          "done" if is_last else str(entity.key()))
    if not skipper:
      skipper = lambda entity, start: False
    if not prefetcher:
      prefetcher = lambda entitites: ([], {})
    if not row_adder:
      row_adder = lambda content_response, entity, *args: \
          content_response.addRow(entity, *args)

    self._request = request
    self._config = config
    self._query = query
    self._starter = starter
    self._ender = ender
    self._skipper = skipper
    self._prefetcher = prefetcher
    self._row_adder = row_adder

  def build(self, *args, **kwargs):
    """Returns a ListContentResponse containing the data as indicated by the
    query.

    The start variable will be used as the starting key for our query, the data
    returned does not contain the entity that is referred to by the start key.
    The next variable will be defined as the key of the last entity returned,
    empty if there are no entities to return.

    Args and Kwargs passed into this method will be passed along to
    _addEntity() method.
    """
    content_response = ListContentResponse(self._request, self._config)

    start = content_response.start

    if start == 'done':
      logging.warning('Received query with "done" start key')
      # return empty response
      return content_response

    if not self._starter(start, self._query):
      logging.warning('Received data query for non-existing start entity %s' % start)
      # return empty response
      return content_response

    count = content_response.limit + 1
    entities = self._query.fetch(count)

    is_last = len(entities) != count

    extra_args, extra_kwargs = self._prefetcher(entities)
    args = list(args) + list(extra_args)
    kwargs.update(extra_kwargs)

    for entity in entities[0:content_response.limit]:
      if self._skipper(entity, start):
        continue
      self._row_adder(content_response, entity, *args, **kwargs)

    if entities:
      content_response.next = self._ender(entities[-1], is_last, start)
    else:
      content_response.next = self._ender(None, True, start)

    return content_response

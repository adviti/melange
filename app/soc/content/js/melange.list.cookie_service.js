/* Copyright 2011 the Melange authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
/**
 * @author <a href="mailto:fadinlight@gmail.com">Mario Ferraro</a>
 */
(function () {
  /** @lends melange.list.cookie_service */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  if (window.melange.list === undefined) {
    throw new Error("melange.list not loaded");
  }

  if (window.jLinq === undefined) {
    throw new Error("jLinq not loaded");
  }

  var jLinq = window.jLinq;

  /** Package that handles all the save/load list state from cookies.
    * @name melange.list.cookie_service
    * @namespace melange.list.cookie_service
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.list.cookie_service = window.melange.list.cookie_service = function () {
    return new melange.list.cookie_service();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.list.cookie_service);

  var setTableColumns = function (colModel) {
    var columns_configuration = {
      hidden_columns: {}
    };

    jQuery.each(colModel, function(index, column) {
      columns_configuration.hidden_columns[column.name] = column.hidden;
    });

    return columns_configuration;
  };

  var setTableOrder = function (sortname, sortorder) {
    return {
      sort_settings : {
        "sortname": sortname,
        "sortorder": sortorder
      }
    }
  };

  var setTableFilters = function (colModel, postData) {
    var filters_configuration = {
      filters: {}
    };

    if (postData._search === true) {
      jQuery.each(colModel, function(index, column) {
        if (postData[column.name] !== undefined) {
          filters_configuration.filters[column.name] = postData[column.name];
        }
      });
    }

    return filters_configuration;
  };

  $m.saveCurrentTableConfiguration = function (idx, jqgrid_object) {
    //TODO(Mario): insulate all the functions better.
    var previous_configuration = melange.cookie.getCookie(melange.cookie.MELANGE_USER_PREFERENCES);
    var colModel = jqgrid_object.jqGrid('getGridParam', 'colModel');

    // Retrieve sort options
    var sortCol = jqgrid_object.jqGrid('getGridParam', 'sortname');
    var sortOrder = jqgrid_object.jqGrid('getGridParam', 'sortorder');

    // Retrieve search filters
    var postData = jqgrid_object.jqGrid('getGridParam', 'postData');

    var configuration_to_save = setTableColumns(colModel);
    configuration_to_save = jQuery.extend(setTableOrder(sortCol, sortOrder), configuration_to_save);
    configuration_to_save = jQuery.extend(setTableFilters(colModel, postData), configuration_to_save);
    var new_configuration = {
      lists_configuration: {}
    };
    new_configuration.lists_configuration[idx] = configuration_to_save;
    new_configuration.lists_configuration = jQuery.extend(previous_configuration.lists_configuration, new_configuration.lists_configuration);
    melange.cookie.saveCookie(melange.cookie.MELANGE_USER_PREFERENCES, new_configuration, 14, window.location.pathname);
  };

  $m.getPreviousTableConfiguration = function (idx, configuration) {
    var previous_configuration = melange.cookie.getCookie(melange.cookie.MELANGE_USER_PREFERENCES);
    var colModel = configuration.colModel;
    if (previous_configuration["lists_configuration"][idx] !== undefined) {
      var this_list_preferences = previous_configuration["lists_configuration"][idx];
      jQuery.each(this_list_preferences.hidden_columns, function (column_name, is_hidden) {
        var column_from_colmodel = jLinq.from(colModel).equals("name",column_name).select()[0] || null;
        if (column_from_colmodel !== null) {
          column_from_colmodel.hidden = is_hidden;
        }
      });
      if (previous_configuration["lists_configuration"][idx].sort_settings !== undefined) {
        var previous_sortname = previous_configuration.lists_configuration[idx].sort_settings.sortname;
        var previous_sortorder = previous_configuration.lists_configuration[idx].sort_settings.sortorder;
        var column_present = jLinq.from(colModel).equals("name",previous_sortname).select()[0] !== undefined ? true : false;
        if (column_present) {
          configuration.sortname = previous_sortname;
          configuration.sortorder = previous_sortorder;
        }
      }
      if (previous_configuration["lists_configuration"][idx].filters !== undefined) {
        var previous_filters = previous_configuration["lists_configuration"][idx].filters;
        jQuery.each(previous_filters, function (column_name, column_filter) {
          var column = jLinq.from(colModel).equals("name",column_name).select()[0];
          if (column !== undefined) {
            column.searchoptions = {
              defaultValue: column_filter
            }
          }
        });
      }
    }
    return configuration;
  };

}());

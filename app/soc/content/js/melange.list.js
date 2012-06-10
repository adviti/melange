/* Copyright 2009 the Melange authors.
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
  /** @lends melange.list */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  if (window.jLinq === undefined) {
    throw new Error("jLinq not loaded");
  }

  var jLinq = window.jLinq;

  /** Package that handles all lists related functions
    * @name melange.list
    * @namespace melange.list
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.list = window.melange.list = function () {
    return new melange.list();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.list);

  melange.error.createErrors([
    "listIndexNotValid",
    "divNotExistent",
    "indexAlreadyExistent"
  ]);

  $m.list_objects = (function () {
    var self = this;
    var lists = [];

    return {
      add: function (list_object) {
        lists[list_object.getIdx()] = list_object;
      },
      get: function (idx) {
        if (lists[idx] !== undefined) {
          return lists[idx];
        }
        else return null;
      },
      getAll: function () {
        return jQuery.extend({}, lists);
      },
      isExistent: function (idx) {
        if (lists[idx] !== undefined) {
          return true;
        }
        else return false;
      }
    };
  }());

  var list_objects = $m.list_objects;

  function List (div, idx, jqgrid_configuration, melange_list_configuration, preload_list) {
    var _self = this;

    // Init data
    var div = div;
    var idx = idx;
    var preload_list = preload_list;

    var features_default = {
      cookie_service: {
        enabled: true
      },
      column_search: {
        enabled: true,
        regexp: true
      },
      columns_show_hide: {
        enabled: true
      },
      search_dialog: {
        enabled: true
      },
      csv_export: {
        enabled: true
      },
      global_search: {
        enabled: false
      },
      global_sort: {
        enabled: false
      }
    };

    // Configuration (sent by protocol either by server or at init)
    this.configuration = jqgrid_configuration;
    this.operations = melange_list_configuration.operations !== undefined ? melange_list_configuration.operations : {};
    this.templates = melange_list_configuration.templates !== undefined ? melange_list_configuration.templates : {};
    this.features = melange_list_configuration.features !== undefined ? jQuery.extend(features_default, melange_list_configuration.features) : features_default;

    var default_jqgrid_options = {
      datatype: function(postdata) {
                  melange.list.process_data.retrieveData(postdata, list_objects.get(postdata.my_index));
                },
      viewrecords: true
    };

    // Default options
    var default_pager_options = {
      edit: false,
      add: false,
      del: false,
      refreshtext: "Refresh",
      searchtext: "Filter",
      afterRefresh:
        function() {
          _self.refreshData();
          _self.jqgrid.object.trigger("reloadGrid");
        }
    };

    if (!_self.features.search_dialog.enabled) {
      default_pager_options.search = false;
    }

    // JQGrid related data
    this.jqgrid = {
      id: null,
      object: null,
      options: null,
      last_selected_row: null,
      editable_columns: [],
      dirty_fields: {},
      pager: {
        id: null,
        options: null
      }
    };

    // Data fetched from server
    this.data = {
      data: [],
      all_data: [],
      filtered_data: null
    };

    // Functions for jqGrid
    var jqgrid_functions = {
      //TODO (Mario): change the name of the functions to reflect the new editing feature
      enableDisableButtons: (function (list_object) {
        return function (row_id) {
          var option_name = list_object.jqgrid.object.jqGrid('getGridParam','multiselect') ? 'selarrrow' : 'selrow'
          var selected_ids = list_object.jqgrid.object.jqGrid('getGridParam',option_name);
          if (!(selected_ids instanceof Array)) {
            selected_ids = [selected_ids];
          }

          function updateDirtyField (row_id) {
            var row = jQuery("#" + list_object.jqgrid.id).jqGrid('getRowData', row_id);
            //Extract the key from the key stored in the cell value, which could be enclosed in a link
            //TODO(Mario)
            //Need to refactor the internal data of the lists to prevent this from happening, temporary workaround.
            var key_value = row.key.toString();
            // extract link href (if any) from the text
            var extracted_text = /^<a\b[^>]*href="(.*?)" \b[^>]*>(.*?)<\/a>$/.exec(key_value);
            if (extracted_text !== null) {
              key_value = extracted_text[2];
            }

            var original_data = jLinq.from(list_object.data.all_data).equals("columns.key",key_value).select()[0];
            if (list_object.jqgrid.dirty_fields[key_value] === undefined) {
              list_object.jqgrid.dirty_fields[key_value] = [];
            }
            var changed_columns = [];
            var not_changed_columns = [];
            jQuery.each(row, function (column_name, column_content) {
              //Extract the value stored in the cell value, which could be enclosed in a link
              //TODO(Mario)
              //Need to refactor the internal data of the lists to prevent this from happening, temporary workaround.
              var column_content = column_content.toString();
              // extract link href (if any) from the text
              var extracted_text = /^<a\b[^>]*href="(.*?)" \b[^>]*>(.*?)<\/a>$/.exec(column_content);
              if (extracted_text !== null) {
                column_content = extracted_text[2];
              }

              /* Need to have a loose comparison here, as e.g. previously integer values
                 could be changed into strings by jqGrid. Also, need to cast an original
                 boolean to string to check for changes
              */
              var column_content_to_compare = original_data.columns[column_name];
              if (typeof column_content_to_compare == 'boolean') {
                column_content_to_compare = "" + column_content_to_compare;
              }
              if (column_content != column_content_to_compare) {
                changed_columns.push(column_name);
              } else {
                not_changed_columns.push(column_name);
              }
            });

            // Update dirty row with dirty columns
            jQuery.each(changed_columns, function (column_index, column_name) {
              if (jQuery.inArray(column_name, list_object.jqgrid.dirty_fields[key_value]) === -1) {
                list_object.jqgrid.dirty_fields[key_value].push(column_name);
              }
            });

            // Check if a previously dirty column has now the original value again
            jQuery.each(not_changed_columns, function (column_index, column_name) {
              var index_in_row_array = jQuery.inArray(column_name, list_object.jqgrid.dirty_fields[key_value]);
              if (index_in_row_array !== -1) {
                list_object.jqgrid.dirty_fields[key_value].splice(index_in_row_array, 1);
              }
            });

            // if deleting the not-anymore-dirty column has left the row array empty, then delete it
            if (list_object.jqgrid.dirty_fields[key_value].length === 0) {
              delete list_object.jqgrid.dirty_fields[key_value];
            }

            jQuery.each(list_object.operations.buttons, function (setting_index, operation) {
              if (operation.type === "post_edit") {
                var button_object = jQuery("#" + list_object.jqgrid.id + "_buttonOp_" + operation.id);
                // if this button is a post_edit button then disable or enable the button if dirty_fields apply
                if (jQuery.isEmptyObject(list_object.jqgrid.dirty_fields)) {
                  button_object.attr("disabled","disabled");
                }
                else {
                  // Artificially click the save button to implement a quick and dirty autosaving
                  button_object.click();
                  button_object.removeAttr("disabled");
                }
              }
            });

            footerAggregates();

          }

          // Enable editing if set by backend
          // editable params for *_field_props available at http://www.trirand.com/jqgridwiki/doku.php?id=wiki:inline_editing
          if (selected_ids.length === 1) {
            if(row_id && row_id !== list_object.jqgrid.last_selected_row) {
              jQuery("#" + list_object.jqgrid.id).restoreRow(list_object.jqgrid.last_selected_row);
              jQuery("#" + list_object.jqgrid.id).jqGrid("editRow", row_id, true, null, null, 'clientArray', null, updateDirtyField);
              list_object.jqgrid.last_selected_row = row_id;
            }
          }

          jQuery.each(list_object.operations.buttons, function (setting_index, operation) {
            var button_object = jQuery("#" + list_object.jqgrid.id + "_buttonOp_" + operation.id);
            // if this button is not a post_edit button (which is already autoupdated during updates of dirty fields)
            if (operation.type !== "post_edit") {
              if (selected_ids.length >= operation.real_bounds[0] && selected_ids.length <= operation.real_bounds[1]) {
                button_object.removeAttr("disabled");
                // If this is a per-entity operation, substitute click event for button (if present)
                if (operation.real_bounds[0] === 1 && operation.real_bounds[1] === 1 && button_object.data('melange') !== undefined) {
                  // get current selection
                  var row = list_object.jqgrid.object.jqGrid('getRowData',selected_ids[0]);
                  var object = jLinq.from(list_object.data.all_data).equals("columns.key",row.key).select()[0];
                  var partial_click_method = button_object.data('melange').click;
                  button_object.click(partial_click_method(object.operations.buttons[operation.id].link));
                  button_object.attr("value",object.operations.buttons[operation.id].caption);
                }
              }
              else {
                button_object.attr("disabled","disabled");
              }
            }
          });
        }
      }(_self)),
      // function defines for global buttons
      global_button_functions : {
        redirect_simple : function (parameters) {
          if (parameters.new_window) {
            return function () {
              window.open(parameters.link);
            }
          }
          else {
            return function () {
              window.location.href = parameters.link;
            }
          }
        },
        redirect_custom: function (parameters) {
          return function (link) {
            if (parameters.new_window) {
              return function () {
                window.open(link);
              }
            }
            else {
              return function () {
                window.location.href = link;
              }
            }
          };
        },
        post: function (parameters) {
          return function () {
            var option_name = list_objects.get(parameters.idx).jqgrid.object.jqGrid('getGridParam','multiselect') ? 'selarrrow' : 'selrow'
            var selected_ids = list_objects.get(parameters.idx).jqgrid.object.jqGrid('getGridParam',option_name);
            if (!(selected_ids instanceof Array)) {
              if (selected_ids === null) {
                selected_ids = [];
              }
              else {
                selected_ids = [selected_ids];
              }
            }
            var objects_to_send = [];
            if (selected_ids.length < parameters.real_bounds[0] || selected_ids.length > parameters.real_bounds[1]) {
              return;
            }
            jQuery.each(selected_ids, function (id_index, id) {
              var row = jQuery("#" + list_objects.get(parameters.idx).jqgrid.id).jqGrid('getRowData',id);
              var object = jLinq.from(list_objects.get(parameters.idx).all_data).equals("columns.key",row.key).select()[0];
              var single_object = {};
              jQuery.each(parameters.keys, function (key_index, column_name) {
                // If there was a surrounding link (with class listsnoul, so just link for rows)
                var field_text = row[column_name];
                if (jQuery(field_text).hasClass("listsnoul")) {
                  // strip the surrounding link from the text
                  var extracted_text = /^<a\b[^>]*>(.*?)<\/a>$/.exec(field_text);
                  field_text = extracted_text[1];
                }
                single_object[column_name] = field_text;
              });
              objects_to_send.push(single_object);
            });
            if (parameters.url === "") {
              parameters.url = window.location.href;
            }
            jQuery.post(
              parameters.url,
              {
                xsrf_token: window.xsrf_token,
                idx: parameters.idx,
                button_id: parameters.button_id,
                data: JSON.stringify(objects_to_send)
              },
              function (data) {
                if (parameters.redirect == "true") {
                  try {
                    var data_from_server = JSON.parse(data);
                    if (data_from_server.data.url !== undefined) {
                      window.location.href = data_from_server.data.url;
                    }
                  }
                  catch (e) {
                    //TODO (Mario): display an error message
                  }
                }
                var refresh_int = parseInt(parameters.refresh, 10);
                if (!isNaN(refresh_int)) {
                  list_objects.get(refresh_int).refreshData();
                  jQuery("#" + list_objects.get(refresh_int).jqgrid.id).trigger("reloadGrid");
                }
                if (parameters.refresh == "current") {
                  list_objects.get(parameters.idx).refreshData();
                  jQuery("#" + list_objects.get(parameters.idx).jqgrid.id).trigger("reloadGrid");
                }
                else if (parameters.refresh == "all") {
                  var lists = list_objects.getAll();
                  jQuery.each(lists, function (list_index, list_object) {
                    list_object.refreshData();
                    jQuery("#" + list_objects.get(list_index).jqgrid.id).trigger("reloadGrid");
                  });
                }
              }
            )
          }
        },
        post_edit: function (parameters) {
          return function () {
            var current_grid = list_objects.get(parameters.idx).jqgrid;
            var rows_to_send = {};
            if (current_grid.editable_columns.length === 0 && jQuery.isEmptyObject(current_grid.dirty_fields)) {
              return;
            }
            // This is done to make sure we detect rows by key column and not by row id
            var number_of_records = current_grid.object.jqGrid('getGridParam','records');
            //TODO(Mario) Temporary fix: getRowData will fail if it reaches a non displayed column due to pagination
            var displayed_records = current_grid.object.jqGrid('getGridParam','reccount');
            for (var record_number = 1; record_number <= displayed_records; record_number++) {
              var row = jQuery("#" + current_grid.id).jqGrid('getRowData',record_number);
              //Extract the key from the key stored in the cell value, which could be enclosed in a link
              //TODO(Mario)
              //Need to refactor the internal data of the lists to prevent this from happening, temporary workaround.
              var key_value = row.key.toString();
              // extract link href (if any) from the text
              var extracted_text = /^<a\b[^>]*href="(.*?)" \b[^>]*>(.*?)<\/a>$/.exec(key_value);
              if (extracted_text !== null) {
                key_value = extracted_text[2];
              }
              if (current_grid.dirty_fields[key_value] !== undefined) {
                // This row should be updated, create object
                rows_to_send[key_value] = {};
                jQuery.each(current_grid.dirty_fields[key_value], function (column_index, column_name) {
                  //Extract the value stored in the cell value, which could be enclosed in a link
                  //TODO(Mario)
                  //Need to refactor the internal data of the lists to prevent this from happening, temporary workaround.
                  var column_value = row[column_name].toString();
                  // extract link href (if any) from the text
                  var extracted_text = /^<a\b[^>]*href="(.*?)" \b[^>]*>(.*?)<\/a>$/.exec(column_value);
                  if (extracted_text !== null) {
                    column_value = extracted_text[2];
                  }
                  rows_to_send[key_value][column_name] = column_value;
                });
                // Send other columns, which are requested by the operation.
                if (parameters.keys !== undefined) {
                  jQuery.each(parameters.keys, function (index, column_to_send) {
                    if (rows_to_send[key_value][column_to_send] === undefined) {
                      //Extract the value stored in the cell value, which could be enclosed in a link
                      //TODO(Mario)
                      //Need to refactor the internal data of the lists to prevent this from happening, temporary workaround.
                      var column_value = row[column_to_send].toString();
                      // extract link href (if any) from the text
                      var extracted_text = /^<a\b[^>]*href="(.*?)" \b[^>]*>(.*?)<\/a>$/.exec(column_value);
                      if (extracted_text !== null) {
                        column_value = extracted_text[2];
                      }
                      rows_to_send[key_value][column_to_send] = column_value;
                    }
                  });
                }
              }
            }
            if (parameters.url === "") {
              parameters.url = window.location.href;
            }
            jQuery.post(
              parameters.url,
              {
                xsrf_token: window.xsrf_token,
                idx: parameters.idx,
                button_id: parameters.button_id,
                data: JSON.stringify(rows_to_send)
              },
              function (data) {
                if (parameters.redirect == "true") {
                  try {
                    var data_from_server = JSON.parse(data);
                    if (data_from_server.data.url !== undefined) {
                      window.location.href = data_from_server.data.url;
                    }
                  }
                  catch (e) {
                    //TODO (Mario): display an error message
                  }
                }
                var refresh_int = parseInt(parameters.refresh, 10);
                if (!isNaN(refresh_int)) {
                  list_objects.get(refresh_int).refreshData();
                  jQuery("#" + list_objects.get(refresh_int).jqgrid.id).trigger("reloadGrid");
                }
                if (parameters.refresh == "current") {
                  list_objects.get(parameters.idx).refreshData();
                  jQuery("#" + list_objects.get(parameters.idx).jqgrid.id).trigger("reloadGrid");
                }
                else if (parameters.refresh == "all") {
                  var lists = list_objects.getAll();
                  jQuery.each(lists, function (list_index, list_object) {
                    list_object.refreshData();
                    jQuery("#" + list_objects.get(list_index).jqgrid.id).trigger("reloadGrid");
                  });
                }
              }
            )
          }
        }
      },
      row_functions : {
        redirect_custom: function (parameters) {
          return function (link, event) {
            /* Even if default is not to open in a new window/tab, will open
               if middle button click or if ctrl+left button click.
            */
            if ((parameters.new_window) || (event.which === 2) || ((event.which === 1) && (event.ctrlKey))) {
              return function () {
                window.open(link);
              }
            }
            else {
              return function () {
                window.location.href = link;
              }
            }
          };
         }
       }
    };

    var createListHTML = function () {
        jQuery("#" + div).replaceWith([
          '<p id="temporary_list_placeholder_',idx,'">',
          '</p>',
          '<table id="' + _self.jqgrid.id + '"',
          ' cellpadding="0" cellspacing="0"',
          '></table>',
          '<div id="' + _self.jqgrid.pager.id + '"',
          ' style="text-align:center"',
          '></div>'
        ].join(""));
    };

    var preRenderData = function (row_num, data) {
      data.columns = preRenderTemplates(data.columns);
      data = preRenderButtons(row_num, data);
    };

    var preRenderButtons = function(row_num, data) {
      if (data.operations === undefined || data.operations.row_buttons === undefined) {
        return data;
      }
      jQuery.each(data.operations.row_buttons, function (column_to_append, definitions) {
        var buttons_htmls = {};
        jQuery.each(definitions.buttons_def, function (id, button) {
          if (button.type === 'redirect_simple') {
            var button_id = 'row_button_' + _self.getIdx() + '_' + row_num + '_' + id;
            var button_classes = '';
            if (button.classes !== undefined && button.classes.length !== 0) {
              button_classes = ' class = "' + button.classes.join(' ') + '"';
            }
            var button_html = [
              '<input type="button" value="', button.caption,'" id="', button_id ,'"', button_classes, '></input>'
            ].join("");
            buttons_htmls[id] = button_html;
          }
        });
        var template = '';
        if (definitions.template === undefined || jQuery.trim(definitions.template) === '') {
          jQuery.each(buttons_htmls, function (button_id, button_html) {
            template += '{{ ' + button_id + '}}';
          });
        }
        else {
          template = definitions.template;
        }
        // Use template to render buttons.
        // TODO(Mario): do not repeat preRenderTemplates' code.
        var match;
        var re =  /\{\{([^\}]+)\}\}/g
        var final_string = template;
        while (match = re.exec(template)) {
          var button_to_replace = jQuery.trim(match[1]);
          if (buttons_htmls[button_to_replace] !== undefined) {
            final_string = final_string.replace(match[0], buttons_htmls[button_to_replace]);
          }
        }
        data.columns[column_to_append] += final_string;
      });
      return data;
    }

    var getListDataAsCSV = function () {
      var csv_export = [];
      csv_export[0] = [];
      //get Columns names
      if (_self.data.data[0] !== undefined || _self.data.filtered_data[0] !== undefined) {
        var iterate_through = _self.data.filtered_data || _self.data.data;
        jQuery.each(_self.configuration.colNames, function (column_index, column_name) {
          // check index for column name
          var field_text = column_name;
          // Check for &quot;, which is translated to " when output to textarea
          field_text = field_text.replace(/\"|&quot;|&#34;/g,"\"\"");

          if (field_text.indexOf(",") !== -1 || field_text.indexOf("\"") !== -1 || field_text.indexOf("\r\n") !== -1) {
            field_text = "\"" + field_text + "\"";
          }
          csv_export[0].push(field_text);
        });
        csv_export[0] = csv_export[0].join(",");

        //Check the actual order of the column, so the data dictionary can be in any order
        var column_ids = [];
        jQuery.each(_self.configuration.colModel, function (column, details) {
          column_ids.push(details.name);
        });
        //now run through the columns
        jQuery.each(iterate_through, function (row_index, row) {
          csv_export[csv_export.length] = [];
          jQuery.each(column_ids, function (column_index, column_id) {
            var cell_value = row[column_id];
            if (cell_value === null) {
              cell_value = "";
            }
            if (cell_value === undefined) {
              cell_value = "";
            }
            var field_text = cell_value.toString();

            // extract link href (if any) from the text
            var extracted_text = /^<a\b[^>]*href="(.*?)" \b[^>]*>(.*?)<\/a>$/.exec(field_text);
            if (extracted_text !== null) {
              field_text = extracted_text[1];
            }

            // Check for &quot;, which is translated to " when output to textarea
            field_text = field_text.replace(/\"|&quot;|&#34;/g,"\"\"");

            if (field_text.indexOf(",") !== -1 || field_text.indexOf("\"") !== -1 || field_text.indexOf("\r\n") !== -1) {
              field_text = "\"" + field_text + "\"";
            }
            csv_export[csv_export.length - 1].push(field_text);
          });
          csv_export[csv_export.length - 1] = csv_export[csv_export.length - 1].join(",");
        });
        csv_export = csv_export.join("\r\n");
      }
      else {
        csv_export = '';
      }

      return csv_export;
    };

    var preRenderTemplates = function (columns) {
      if (_self.templates === undefined) {
        return columns;
      }
      var columns = columns;
      jQuery.each(_self.templates, function (dest_column, template) {
        var match;
        var re =  /\{\{([^\}]+)\}\}/g
        var final_string = template;
        while (match = re.exec(template)) {
          var column_to_replace = jQuery.trim(match[1]);
          if (columns[column_to_replace] !== undefined && columns[dest_column] !== undefined) {
            final_string = final_string.replace(match[0], columns[column_to_replace]);
          }
        }
        columns[dest_column] = final_string
      });
      return columns;
    };

    var fetchDataFromServer = function() {
      var start = "";
      var current_loop = 0;

      // Show Loading message
      jQuery("#load_" + _self.jqgrid.id).show();

      var server_loop = function () {
        // Preserve current query string
        var ampersand_question = "?";
        if (window.location.href.indexOf("?") !== -1) {
          ampersand_question = "&";
        }
        jQuery.ajax({
          async: true,
          cache: false,
          url: [
            window.location.href.split('#')[0],
            ampersand_question,
            "fmt=json&limit=100",
            (start === "" ? "" : "&start=" + start),
            "&idx=", idx
          ].join(""),
          timeout: 60000,
          tryCount: 1,
          retryLimit: 5,
          error: function (xhr, textStatus, errorThrown) {
            // retry on 500 errors from server
            if (xhr.status == 500) {
              this.tryCount++;
              if (this.tryCount <= this.retryLimit) {
                jQuery.ajax(this);
                return;
              }
              // retryLimit is reached, show a message
              jQuery("#temporary_list_placeholder_" + idx).html([
                '<span style="color:red">',
                'Error retrieving data: please refresh the list or the whole page to try again',
                '</span>'].join("")
              );
              jQuery("#load_" + _self.jqgrid.id).hide();
            } else {
              // another error from server, show a message
              jQuery("#temporary_list_placeholder_" + idx).html([
                '<span style="color:red">',
                'Error retrieving data: please refresh the list or the whole page to try again',
                '</span>'].join("")
              );
              jQuery("#load_" + _self.jqgrid.id).hide();
            }
          },
          success: function (data_from_server) {
            var source = data_from_server;
            var first_batch_received = (current_loop > 0);
            var data_received = source.data[start] !== undefined;
            var last_batch = source.next === "done";

            if (data_received) {
              // temporary fix until Issue 766
              if (_self.configuration === null) {
                _self.configuration = source.configuration;
              }
              if (_self.operations === null) {
                _self.operations = source.operations;
              }
              var my_data = source.data[start];

              jQuery.each(my_data, function (index, current_row) {
                preRenderData(index, current_row);
                _self.data.data.push(current_row.columns);
                _self.data.all_data.push(current_row);
              });

              //if jQGrid object is not already instantiated, create it
              if (_self.jqgrid.object === null) {
                initJQGrid();
              }
              else {
                //else trigger new data in jqgrid object
                _self.jqgrid.object.trigger("reloadGrid");
              }

              // Bind row buttons click events, if present. Can be bound only after the actual object is appended to the DOM.
              jQuery.each(_self.data.all_data, function (row_index, row) {
                if (row.operations !== undefined && row.operations.row_buttons !== undefined) {
                  jQuery.each(row.operations.row_buttons, function (column, definitions) {
                    jQuery.each(definitions.buttons_def, function (id, button) {
                      var button_id = 'row_button_' + _self.getIdx() + '_' + row_index + '_' + id;
                      // Only redirect_simple operation is supported at the moment.
                      if (button.type === 'redirect_simple') {
                        jQuery('#' + button_id).click(jqgrid_functions.global_button_functions[button.type](button.parameters));
                      }
                    });
                  });
                }
              });

              //call next iteration
              if (!last_batch) {
                start = source.next;
                setTimeout(server_loop, 100);
                current_loop++;
              }
              else {
                jQuery("#temporary_list_placeholder_" + idx).remove();
                jQuery("#load_" + _self.jqgrid.id).hide();
              }
            }
            if (last_batch) {
              //loading data finished, hiding loading message
              jQuery("#temporary_list_placeholder_" + idx).remove();
              jQuery("#load_" + _self.jqgrid.id).hide();

              //Trigger toolbar set default filters if a default one is requested (searchoptions)
              if (_self.jqgrid.object.triggerToolbar !== undefined) {
                _self.jqgrid.object.triggerToolbar();
              }

              //check if there are editable columns
              jQuery.each(_self.configuration.colModel, function (column_index, column) {
                if (column.editable !== undefined && column.editable === true) {
                  _self.jqgrid.editable_columns.push(column.name);
                }
              });

              // Delete previous buttons, if any
              jQuery("#t_" + _self.jqgrid.id).children().remove();

              // Add global action buttons on the toolbar
              if (_self.operations !== undefined && _self.operations.buttons !== undefined) {
                jQuery.each(_self.operations.buttons, function (setting_index, operation) {
                  var bounds = operation.bounds;
                  // create button for global operation
                  var new_button_id = _self.jqgrid.id + "_buttonOp_" + operation.id;
                  var new_button_object = jQuery("<input type='button' value='" + operation.caption + "' style='float:left' id='" + new_button_id + "'/>").button();
                  jQuery("#t_" + _self.jqgrid.id).append(new_button_object);

                  operation.parameters.idx = idx;

                  /* If this button is a post_edit button then button bounds should
                     behave differently: the button should be disabled if no dirty
                     fields are detected, then enabled the first time a cell content
                     is changed
                  */
                  if (operation.type !== "post_edit") {
                    // Substitute "all" string (if any) to actual number of records
                    operation.real_bounds = operation.bounds;
                    var handle_all = operation.real_bounds.indexOf("all");
                    if (handle_all !== -1) {
                      operation.real_bounds[handle_all] = _self.jqgrid.object.jqGrid('getGridParam','records');
                    }
                    /* Add button bounds on parameters to let POST
                       requests working also with [0,"all"] bounds */
                    operation.parameters.real_bounds = operation.real_bounds;
                  }
                  // the button should be disabled by default if lower bound is >0 or operation is a post_edit one
                  if (operation.type === "post_edit" || operation.real_bounds[0] > 0) {
                    jQuery("#" + new_button_id).attr("disabled","disabled");
                  }
                  /* Add id of the button operation to parameters so the appropriate backend action
                     can be identified if multiple buttons redirect to the same page. */
                  operation.parameters.button_id = operation.id;
                  // associate action
                  jQuery("#" + new_button_id).click(jqgrid_functions.global_button_functions[operation.type](operation.parameters));
                  // If this is a partial function, than store it in a safe place
                  if (operation.type == "redirect_custom") {
                    jQuery("#" + new_button_id).data(
                      'melange',
                      {
                        click: jqgrid_functions.global_button_functions[operation.type](operation.parameters)
                      }
                    );
                  }
                });
              }

              //Add row action if present
              /*var multiselect = _self.jqgrid.object.jqGrid('getGridParam','multiselect');
              if (_self.operations !== undefined && _self.operations.row !== undefined && !jQuery.isEmptyObject(_self.operations.row)) {

                // if row action is present, than change cursor
                // FIXME: this is done by polling continuosly the body element
                // this is not so elegant nor efficient, need to find another solution
                jQuery("body").live("mouseover", function() {
                  if (multiselect) {
                    jQuery("#" + _self.jqgrid.id + " tbody tr td:gt(0)").css("cursor","pointer")
                  }
                  else {
                    jQuery("#" + _self.jqgrid.id + " tbody tr td").css("cursor","pointer")
                  }
                });

                var operation = _self.operations.row;
                operation.parameters.idx = idx;

                // If this is a partial function, than store it in a safe place
                if (operation.type == "redirect_custom") {
                  _self.jqgrid.object.data(
                    'melange',
                    {
                      rowsel: jqgrid_functions.row_functions[operation.type](operation.parameters)
                    }
                  );
                }
                // associate action to row
                _self.jqgrid.object.jqGrid('setGridParam',{
                  onCellSelect: function (row_number, cell_index, cell_content, event) {*/
                    /* If this is a multiselect table, do not trigger row action
                       if user clicks on a checkbox in the first column
                    */
                    /*if (multiselect && cell_index == 0) {
                      return;
                    }
                    // get current selection
                    var row = jQuery("#" + _self.jqgrid.id).jqGrid('getRowData',row_number);
                    var object = jLinq.from(_self.data.all_data).equals("columns.key",row.key).select()[0];
                    var partial_row_method = _self.jqgrid.object.data('melange').rowsel;
                    partial_row_method(object.operations.row.link, event)();
                  }
                });
              }*/

              //Add CSV Export button and RegEx switch only once all data is loaded

              //Add some padding at the bottom of the toolbar to display buttons correctly
              jQuery("#t_" + _self.jqgrid.id).css("padding-bottom","3px");

              //Add CSV export button
              if (_self.features.csv_export.enabled) {
                jQuery("#t_" + _self.jqgrid.id).append("<input type='button' value='CSV Export' style='float:right;' id='csvexport_" + _self.jqgrid.id + "'/>");
                jQuery("#csvexport_" + _self.jqgrid.id).button();
                //Add Click event to CSV export button
                jQuery("#csvexport_" + _self.jqgrid.id).click(function () {
                  csv_export = getListDataAsCSV();
                  if (!csv_export) {
                    return;
                  }
                  //CSV string is there, now put it in a modal dialog for the user to copy/paste
                  jQuery("#csv_dialog").remove();
                  jQuery("body").append(
                    [
                      "<div id='csv_dialog' style='display:none'>",
                      "  <h3>Now you can copy and paste CSV data from the text area to a new file:</h3>",
                      "  <textarea style='width:450px;height:250px'>",csv_export,"</textarea>",
                      "</div>"
                    ].join("")
                  );
                  jQuery("#csv_dialog").dialog({
                    height: 420,
                    width: 500,
                    modal: true,
                    buttons: {
                      "Close": function () {
                        jQuery(this).dialog("close");
                        }
                    }
                  });
                });
              }

              //Add RegExp switch
              if (_self.features.column_search.enabled && _self.features.column_search.regexp) {
                jQuery("#t_" + _self.jqgrid.id).append("<div style='float:right;margin-right:4px;'><input type='checkbox' id='regexp_" + _self.jqgrid.id + "'/>RegExp Search</div>");

                //Make the switch trigger a new search when clicked
                jQuery("#regexp_" + _self.jqgrid.id).click(function () {
                  jQuery("#" + _self.jqgrid.id).jqGrid().trigger("reloadGrid");
                });
              }


              //Trigger event when loading of the list is finished
              var loaded_event = jQuery.Event("melange_list_loaded");
              loaded_event.list_object = _self;
              _self.jqgrid.object.trigger(loaded_event);

              /* Tweak the width of the element, because of horizontal bar
               * appearing in Chrome. This should be temporary, since it's
               * probably related to a small jqgrid bug when calculating
               * the dimensions of the lists. This is also a quick hack,
               * since to do it properly it should iterate through all the
               * jqgrid's dom and make every width equal. Serve its purpose,
               * though.
               */
              var jqgrid_dom = jQuery("#gview_" + _self.jqgrid.id + " .ui-jqgrid-bdiv");
              jqgrid_dom.width(jqgrid_dom.width() + 1);
            }
          }
        });
      };
      setTimeout(server_loop, 100);
    };

    this.refreshData = function () {
      _self.data = {
        data: [],
        all_data: [],
        filtered_data: null
      };
      fetchDataFromServer();
    }

    var footerAggregates = function () {
      /* Calculate aggregates if requested, using summaryType as a reference, since
         it won't work without grouping and so there's no harm on using it
      */
      if (!_self.configuration.footerrow) {
        return;
      }

      var footer_updates = {};

      var grid = _self.jqgrid.object;

      jQuery.each(_self.configuration.colModel, function (col_index, col_object) {
        if (col_object.summaryType !== undefined) {
          var footer_aggregate = grid.jqGrid('getCol', col_object.name, false, col_object.summaryType);
          footer_updates[col_object.name] = col_object.summaryTpl.replace(/\{0\}/ig, footer_aggregate);
        }
      });
      grid.jqGrid('footerData', 'set', footer_updates);
    };

    var gridCompletionTasks = function () {
      if (!_self.jqgrid.object) {
        //TODO(Mario): check this in a better fashion.
        // The list is not created yet, this is likely to be fired by gridComplete
        // but it's not yet necessary to catch that.
        return;
      }

      footerAggregates();
      if (_self.features.cookie_service.enabled) {
        // Temporarily disable cookie service for new lists.
        melange.list.cookie_service.saveCurrentTableConfiguration(idx, _self.jqgrid.object);
      }
    };

    var initJQGrid = function () {
      if (_self.features.cookie_service.enabled) {
        // Temporarily disable cookie service for new lists.
        _self.configuration = melange.list.cookie_service.getPreviousTableConfiguration(idx, _self.configuration);
      }

      var final_jqgrid_configuration = jQuery.extend(
        _self.configuration,
        {
          //giving index of the table in post data
          postData: {my_index: idx},
          // Disable or enable button depending on how many rows are selected
          onSelectAll: jqgrid_functions.enableDisableButtons,
          onSelectRow: jqgrid_functions.enableDisableButtons,
          // When something changes in the list, update the cookie
          gridComplete: gridCompletionTasks,
          // Zebra striping
          altRows: true,
          altclass: 'alternate_row'
        }
      );

      var button_showhide_options = {
        caption: "Columns",
        buttonicon: "ui-icon-calculator",
        onClickButton: function () {
          var original_width = jQuery("#" + _self.jqgrid.id).jqGrid("getGridParam","width");
          jQuery("#" + _self.jqgrid.id).jqGrid('columnChooser', {
            done: function(perm) {
                if (perm) {
                  this.jqGrid("remapColumns", perm, true);
                  this.jqGrid("setGridWidth", original_width);
                  melange.list.cookie_service.saveCurrentTableConfiguration(idx, _self.jqgrid.object);
                }
            }
          });
        },
        position: "last",
        title: "Show/Hide Columns",
        cursor: "pointer"
      };

      var search_parameters = {};

      if (_self.features.column_search.enabled) {
        search_parameters = {
          closeAfterSearch: true,
          multipleSearch: true
        };
      }

      jQuery("#" + _self.jqgrid.id)
       .jqGrid(
         jQuery.extend(_self.jqgrid.options, final_jqgrid_configuration)
       )
       .jqGrid(
         // show pager
         "navGrid",
         "#" + _self.jqgrid.pager.id,
         _self.jqgrid.pager.options,
         {}, // settings for edit
         {}, // settings for add
         {}, // settings for delete
         search_parameters,
         {} // view parameters
        );
      // Do not show columns and filter Toolbar for new lists.
      if (_self.features.columns_show_hide.enabled) {
        jQuery("#" + _self.jqgrid.id).jqGrid(
          // show button to hide/show columns
          "navButtonAdd",
          "#" + _self.jqgrid.pager.id,
          button_showhide_options
        );
      }
      if (_self.features.column_search.enabled) {
        jQuery("#" + _self.jqgrid.id).jqGrid(
          'filterToolbar',
          {
            beforeSearch: function() {
                            melange.list.cookie_service.saveCurrentTableConfiguration(idx, _self.jqgrid.object)
                          },
            searchOnEnter: false,
            autosearch: true
          }
        );
      }

      // Prepare the Loading message, substituting it with an animated image
      jQuery("#load_" + _self.jqgrid.id).closest("div").css("line-height","100%");
      jQuery("#load_" + _self.jqgrid.id).html("<img src='/soc/content/" + melange.config.app_version + "/images/jqgrid_loading.gif'></img>");

      _self.jqgrid.object = jQuery("#" + _self.jqgrid.id);

      // Global Search

      if (_self.features.global_search.enabled) {
        jQuery(_self.features.global_search.element_path).bind("keyup", function(event) {
          var search_query = jQuery(_self.features.global_search.element_path).val();
          var postData = _self.jqgrid.object.jqGrid('getGridParam', 'postData');
          postData._search = true;
          postData.filters = {
            "groupOp": "OR",
            "rules": []
          };
          jQuery.each(_self.configuration.colModel, function(index, column) {
            postData.filters.rules.push({
              "field": column.name,
              "op": "cn",
              "data": search_query
            });
          });
          postData.filters = JSON.stringify(postData.filters);
          _self.jqgrid.object.jqGrid('setGridParam', {search: true, postData: postData});
          _self.jqgrid.object.trigger("reloadGrid");
        });
      }

      // Global Sort

      var gs = _self.features.global_sort;
      if (gs.enabled) {
        if (gs.element_paths.column !== undefined) {
          var select = jQuery(gs.element_paths.column);
          jQuery(' option', select).remove();
          var cm = _self.configuration.colModel;
          jQuery.each(_self.configuration.colModel, function(index, column) {
            select.append(jQuery('<option></option>').val(column.name).html(_self.configuration.colNames[index]));
          });
          var selected_item = (_self.jqgrid.object.jqGrid('getGridParam', 'postData')).sidx;
          select.val(selected_item);

          select.bind("change", function() {
            var column_to_sort = jQuery(this).val();
            _self.jqgrid.object.jqGrid('setGridParam', {sortname: column_to_sort});
            _self.jqgrid.object.trigger("reloadGrid");
          });
        }
        if (gs.element_paths.asc_desc !== undefined) {
          var select = jQuery(gs.element_paths.asc_desc);
          jQuery(' option', select).remove();
          select.append(jQuery('<option></option>').val('asc').html('Ascending'));
          select.append(jQuery('<option></option>').val('desc').html('Descending'));
          var selected_item = (_self.jqgrid.object.jqGrid('getGridParam', 'postData')).sord;
          select.val(selected_item);

          select.bind("change", function() {
            var asc_desc = jQuery(this).val();
            _self.jqgrid.object.jqGrid('setGridParam', {sortorder: asc_desc});
            _self.jqgrid.object.trigger("reloadGrid");
          });
        }

      }
    };

    this.getDiv = function () {return div;};
    this.getIdx = function () {return idx;};

    this.init = function () {
      jQuery(
        function () {
          if (jQuery("#" + div).length === 0) {
            throw new melange.error.divNotExistent("Div " + div + " is not existent");
          }

          _self.jqgrid.id = "jqgrid_" + div;
          _self.jqgrid.pager.id = "jqgrid_pager_" + div;
          _self.jqgrid.options = jQuery.extend(default_jqgrid_options, {pager: "#" + _self.jqgrid.pager.id});
          _self.jqgrid.pager.options = default_pager_options;

          list_objects.add(_self);

          createListHTML();
          initJQGrid();
          fetchDataFromServer();
        }
      );

    };

    if (preload_list !== undefined && preload_list === true) {
      this.init();
    } else {
      // we need to add this list for later retrieval
      list_objects.add(this);
    }
  };

  $m.loadList = function (div, init, idx, preload_list) {
    var idx = parseInt(idx, 10);
    var init = JSON.parse(init);
    if (isNaN(idx) || idx < 0) {
      throw new melange.error.listIndexNotValid("List index " + idx + " is not valid");
    }
    if (list_objects.isExistent(idx)) {
      throw new melange.error.indexAlreadyExistent("Index " + idx + " is already existent");
    }

    var list = new List(div, idx, init.configuration, init, preload_list);
  };
}());

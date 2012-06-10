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
  /** @lends melange.list.process_data */

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

  /** Package that handles all lists data processing.
    * @name melange.list.process_data
    * @namespace melange.list.process_data
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.list.process_data = window.melange.list.process_data = function () {
    return new melange.list.process_data();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.list.process_data);

  $m.retrieveData = function(postdata, list) {
    var my_index = postdata.my_index;
    var original_data = list.data.data;
    var temp_data = original_data;
    var group_operation = "";
    var searches = {
      "eq": { // equals
        method: "equals",
        not: false
      },
      "ne": { // not equals
        method: "equals",
        not: true
      },
      "lt": { // less
        method: "less",
        not: false
      },
      "le": { // less or equal
        method: "lessEquals",
        not: false
      },
      "gt": { // greater
        method: "greater",
        not: false
      },
      "ge": { // greater or equal
        method: "greaterEquals",
        not: false
      },
      "bw": { // begins with
        method: "startsWith",
        not: false
      },
      "bn": { // does not begins with
        method: "startsWith",
        not: true
      },
      "ew": { // ends with
        method: "endsWith",
        not: false
      },
      "en": { // does not end with
        method: "endsWith",
        not: true
      },
      "cn": { // contains
        method: "contains",
        not: false
      },
      "nc": { // does not contain
        method: "contains",
        not: true
      },
      "in": {
        method: "match",
        not: false
      },
      "ni": {
        method: "match",
        not: true
      }
    };

    // Process search filter
    if (postdata._search && postdata.filters) {
      var filters = JSON.parse(postdata.filters);
      if (filters.rules[0].data !== "") {
        group_operation = filters.groupOp;
        if (group_operation === "OR") {
          temp_data = {};
        }
        jQuery.each(filters.rules, function (arr_index, filter) {
          if (filter.op === "in" || filter.op === "ni") {
            filter.data = filter.data.split(",").join("|");
          }
          if (searches[filter.op].not) {
            if (group_operation === "OR") {
              temp_data = jLinq.from(temp_data).union(jLinq.from(original_data).not()[searches[filter.op].method](filter.field, filter.data).select()).select();
            }
            else {
              temp_data = jLinq.from(temp_data).not()[searches[filter.op].method](filter.field, filter.data).select();
            }
          }
          else {
            if (group_operation === "OR") {
              temp_data = jLinq.from(temp_data).union(jLinq.from(original_data)[searches[filter.op].method](filter.field, filter.data).select()).select();
            }
            else {
              temp_data = jLinq.from(temp_data)[searches[filter.op].method](filter.field, filter.data).select();
            }
          }
        });
      }
    }
    // otherwise process simple filter
    else if (original_data[0] !== undefined) {
      jQuery.each(original_data[0], function (element_key, element_value) {
        if (postdata[element_key] !== undefined) {
          var search_by_reg_exp = false;
          if (jQuery("#regexp_" + list.jqgrid.id) !== undefined && jQuery("#regexp_" + list.jqgrid.id).is(":checked")) {
            search_by_reg_exp = true;
          }
          var select_filter = false;
          jQuery.each(list.configuration.colModel, function (item_index, column) {
            if (column.editoptions !== undefined && element_key === column.name) {
              select_filter = true;
            }
          });
          // Search by regular expression if switch is on or if there is a select box to filter
          if (search_by_reg_exp || select_filter) {
            temp_data = jLinq.from(temp_data).match(element_key, postdata[element_key]).select();
          }
          // else search by simple text
          else {
            temp_data = jLinq.from(temp_data).contains(element_key, postdata[element_key]).select();
          }
        }
      });
    }
    // Get only unique values
    temp_data = temp_data.filter(function (item, index, array) {
      return index == array.indexOf(item) && !jQuery.isEmptyObject(item);
    });

    // Process index/sorting filters
    var sort_column = postdata.sidx;
    var order_type = postdata.sord;

    // Do internal conversion if sort type is number
    jQuery.each(list.configuration.colModel, function (column_index, column) {
      if (column.name === sort_column && (column.sorttype === "integer" || column.sorttype === "int")) {
        jQuery.each(temp_data, function (datum_index, datum) {
          var parsed_int = parseInt(datum[sort_column], 10);
          if (!isNaN(parsed_int)) {
            datum[sort_column] = parsed_int;
          }
        });
      }
    });

    if (order_type === "asc") {
      order_type = "";
    }
    else {
      order_type = "-";
    }

    if (temp_data.length > 0) {
      temp_data = jLinq.from(temp_data).ignoreCase().orderBy(order_type + sort_column).select();
    }
    list.data.filtered_data = temp_data;

    // If pagination is disabled, change number or rows to length of filtered data
    if (postdata.rows === -1) {
      postdata.rows = list.data.filtered_data.length;
    }

    var offset_start = (postdata.page - 1) * postdata.rows;
    var offset_end = (postdata.page * postdata.rows) - 1;

    var json_to_return = {
      "page": postdata.page,
      "total": temp_data.length === 0 ? 0 : Math.ceil(temp_data.length / postdata.rows),
      "records": temp_data.length,
      "rows": []
    };
    for (var i = offset_start; i <= offset_end; i++) {
      if (temp_data[i] === undefined) {
        continue;
      }
      var my_cell = [];
      if (original_data[0] !== undefined) {
          jQuery.each(list.configuration.colModel, function (element_key, element_value) {
              var current_row;
              var search_into = list.data.all_data;
              for (var row_index = 0; row_index < search_into.length; row_index++) {
                if (search_into[row_index].columns.key === temp_data[i]["key"]) {
                  current_row = search_into[row_index];
                  break;
                }
              }
            var column_content = temp_data[i][element_value.name];
            if (current_row && current_row.operations !== undefined && current_row.operations.row !== undefined && current_row.operations.row.link !== undefined) {
              // If there are no links in the text and the column is not editable then insert a listsnoul link
              var column_editable = element_value.editable || false;
              if (column_content !== null && column_content !== undefined && !column_editable && column_content.toString().match(/<a\b[^>]*>.*<\/a>/) === null) {
                column_content = '<a style="display:block;" href="' + current_row.operations.row.link + '" class="listsnoul">' + column_content + '</a>';
              }
            }
            if (column_content !== null) {
              my_cell.push(column_content);
            }
          });
      }

      json_to_return.rows.push({
        "key": temp_data[i].key,
        "cell": my_cell
      });
    }

    var thegrid = jQuery("#" + list.jqgrid.id);
    var thegrid_dom = thegrid[0];
    thegrid_dom.addJSONData(json_to_return);

    // Hide/Show columns if an extra field is defined and this filter filtered that extra field
    var colModel = list.configuration.colModel;

    jQuery.each(colModel, function (col_index, col_object) {
      if (col_object.extra !== undefined) {
        var filters_to_check = col_object.extra;
        var show_column = false;
        var filters_matches = 0;
        var filters_total = 0;
        jQuery.each(filters_to_check, function (filter_name, filter_value) {
          if (postdata[filter_name] === filter_value) {
            filters_matches++;
          }
          filters_total++;
        });
        if (filters_matches !== filters_total) {
          colModel[col_index].hidden = true;
          colModel[col_index].hidedlg = true;
          // This is needed otherwise hidedlg won't be added to the actual grid
          thegrid.jqGrid("getColProp", col_object.name).hidedlg = true;
          thegrid.jqGrid("hideCol", col_object.name);
        } else {
          colModel[col_index].hidden = false;
          colModel[col_index].hidedlg = false;
          // This is needed otherwise hidedlg won't be added to the actual grid
          thegrid.jqGrid("getColProp", col_object.name).hidedlg = false;
          thegrid.jqGrid("showCol", col_object.name);
        }
      }
    });
  };
}());

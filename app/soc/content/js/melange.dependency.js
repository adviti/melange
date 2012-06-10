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
  /** @lends melange.dependency */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  /** Package that handles melange JS dependencies
    * Doesn't list jQuery, JSON, melange and melange.dependency
    * in any chain as they're dependencies of this own script,
    * and they will be then loaded anyway.
    * @name melange.dependency
    * @namespace melange.depencency
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.dependency = window.melange.dependency = function () {
    return new melange.dependency();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.dependency);

  melange.error.createErrors([
  ]);


  $m.templateWithContext = function (script_template, context) {
    this.script_template = script_template;
    this.context = context;
  };

  $m.cssFile = function (css) {
    this.css = css;
  };

  var script_dependencies_chains = {};

  var s = script_dependencies_chains;

  // Third party JS URL prefix
  var tpjs = "/js/" + melange.config.app_version + "/";

  // Melange packages URL prefix
  var mpjs = "/soc/content/" + melange.config.app_version + "/js/";

  // Melange CSS URL prefix
  var mcss = "/" + melange.config.css_path + "/";

  if (melange.config.google_api_key !== undefined) {
    s.google = [
      "https://www.google.com/jsapi?key=" + melange.config.google_api_key
    ];
  }
  else {
    s.google = [
      "https://www.google.com/jsapi"
    ];
  }

  if (melange.config.is_local !== undefined && melange.config.is_local === true) {
    s.jquery = [
      tpjs + "jquery/jquery-1.6.4.js"
    ];
  }
  else {
    s.jquery = [
      "https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"
    ];
  }

  s.json = [
    tpjs + "json/json2.js"
  ];

  s.tinymce = [
    "/tiny_mce/tiny_mce.js"
  ];

  s.purr = [
    tpjs + "jquery/jquery-purr.js"
  ];

  s.counter = [
    tpjs + "jquery/jquery-counter.js"
  ];

  s.spin = [
    tpjs + "jquery/jquery-spin-1.1.1.js"
  ];

  s.bgiframe = [
    tpjs + "jquery/jquery-bgiframe.js"
  ];

  s.ajaxQueue = [
    tpjs + "jquery/jquery-ajaxQueue.js"
  ];

  s.progressbar = [
    tpjs + "jquery/jquery-progressbar.js"
  ];

  s.uniform = [
    tpjs + "jquery/jquery-uniform.js"
  ];

  s.raty = [
    tpjs + "jquery/jquery.raty.js"
  ];

  s.cluetip = [
    tpjs + "jquery/jquery.cluetip.js"
   ];

  s.dimensions = [
    tpjs + "jquery/jquery.dimensions.js"
  ];

  s.scrollTo = [
    tpjs + "jquery/jquery.scrollTo.js"
  ];

  s.formbuilder = [
    s.scrollTo,
    null,
    tpjs + "jquery/jquery.formbuilder.js"
  ];

  s.colorbox = [
    tpjs + "jquery/jquery.colorbox.js"
  ];

  s.hashchange = [
    tpjs + "jquery/jquery.ba-hashchange.js"
  ];

  s.dd = [
    tpjs + "jquery/jquery.dd.js"
  ];

  s.modernizr = [
    tpjs + "modernizr/modernizr-svg.js"
  ];

  s.jqueryui = {}

  if (melange.config.is_local !== undefined && melange.config.is_local === true) {
    s.jqueryui.core = [
      new $m.cssFile(mcss + "jquery-ui/jquery.ui.all.css"),
      tpjs + "jquery/jquery-ui.core.js"
    ];
  }
  else {
    s.jqueryui.core = [
      new $m.cssFile(mcss + "jquery-ui/jquery.ui.merged.css"),
      tpjs + "jquery/jquery-ui.core.js"
    ];
  }

  s.jqueryui.datepicker = [
    s.jqueryui.core,
    null,
    tpjs + "jquery/jquery-ui.datepicker.js"
  ];

  s.jqueryui.position = [
    s.jqueryui.core,
    null,
    tpjs + "jquery/jquery-ui.position.js"
  ];

  s.jqueryui.widget = [
    s.jqueryui.core,
    null,
    tpjs + "jquery/jquery-ui.widget.js"
  ];

  s.jqueryui.mouse = [
    s.jqueryui.core,
    null,
    tpjs + "jquery/jquery-ui.mouse.js"
  ];

  s.jqueryui.button = [
    s.jqueryui.widget,
    null,
    tpjs + "jquery/jquery-ui.button.js"
  ];

  s.jqueryui.autocomplete = [
    s.jqueryui.position,
    s.jqueryui.widget,
    null,
    new $m.cssFile(mcss + "jquery-ui/jquery.ui.autocomplete.css"),
    tpjs + "jquery/jquery-ui.autocomplete.js",
    tpjs + "jquery/jquery-ui.autocomplete.html.js" //allows html with results
  ];

  s.jqueryui.dialog = [
    s.jqueryui.position,
    s.jqueryui.widget,
    null,
    tpjs + "jquery/jquery-ui.dialog.js"
  ];

  s.jqueryui.checkboxes = [
    s.jqueryui.core,
    tpjs + "jquery/jquery.ui-checkboxes.js"
  ];

  s.jqueryui.draggable = [
    s.jqueryui.widget,
    s.jqueryui.mouse,
    null,
    tpjs + "jquery/jquery-ui.draggable.js"
  ];

  s.jqueryui.sortable = [
    s.jqueryui.widget,
    s.jqueryui.mouse,
    null,
    tpjs + "jquery/jquery-ui.sortable.js"
  ];

  s.jqueryui.effects = [
    tpjs + "jquery/jquery-ui.effects.core.js"
  ];

  s.jqueryui.effects.blind = [
    s.jqueryui.effects,
    null,
    tpjs + "jquery/jquery-ui.effects.blind.js"
  ];

  s.jqgrid = [
    s.jqueryui.core,
    s.jqueryui.dialog,
    s.jqueryui.draggable,
    s.jqueryui.sortable,
    null,
    new $m.cssFile(mcss + "ui.multiselect.css"),
    tpjs + "jquery/jquery-jqgrid.ui.multiselect.js",
    null,
    new $m.cssFile(mcss + "ui.jqgrid.css"),
    tpjs + "jquery/jquery-jqgrid.locale-en.js",
    null,
    tpjs + "jquery/jquery-jqgrid.base.js",
    null,
    tpjs + "jquery/jquery-jqgrid.custom.js",
    tpjs + "jquery/jquery-jqgrid.filter.js",
    tpjs + "jquery/jquery-jqgrid.jqueryui.js"
  ];

  s.jqgridediting = [
    s.jqgrid,
    null,
    tpjs + "jquery/jquery-jqgrid.common.js",
    tpjs + "jquery/jquery-jqgrid.fmatter.js",
    tpjs + "jquery/jquery-jqgrid.formedit.js",
    null,
    tpjs + "jquery/jquery-jqgrid.searchFilter.js",
    tpjs + "jquery/jquery-jqgrid.inlinedit.js",
    null,
    tpjs + "jquery/jquery-jqgrid.jqDnR.js",
    null,
    tpjs + "jquery/jquery-jqgrid.jqModal.js"
  ];

  s.cookie = [
    tpjs + "jquery/jquery-cookie.js"
  ];

  s.jquery.svg = [
    tpjs + "jquery/jquery.svg.pack.js"
  ];

  s.jlinq = [
    tpjs + "jlinq/jLinq-2.2.1.js"
  ];

  /** Melange packages **/

  s.melange = {};

  s.melange.main = [
    s.google,
    s.cookie,
    null,
    mpjs + "melange.js"
  ];

  s.melange.gdata = {};

  s.melange.gdata.core = [
    mpjs + "melange.gdata.core.js"
  ];

  s.melange.gdata.documents = [
    s.melange.gdata.core,
    s.jqueryui.dialog,
    null,
    mpjs + "melange.gdata.documents.js"
  ];

  s.melange.datetimepicker = [
    s.jqueryui.datepicker,
    null,
    mpjs + "melange.datetimepicker.js"
  ];

  s.melange.duplicates = [
    s.progressbar,
    null,
    mpjs + "duplicate-slots.js"
  ];

  s.melange.form = [
  ];

  s.melange.list = [
    s.jqgrid,
    s.jlinq,
    new $m.cssFile(mcss + "others.css"),
    null,
    s.jqueryui.dialog,
    s.jqueryui.button,
    s.jqgridediting,
    null,
    mpjs + "melange.list.js",
    null,
    mpjs + "melange.list.cookie_service.js",
    mpjs + "melange.list.process_data.js",
    null,
    function () {
      if (window.melange_list_queue !== undefined && window.melange_list_queue instanceof Array) {
        jQuery.each(window.melange_list_queue, function (index, function_to_call) {
          function_to_call();
        });
      }
    }
  ];

  s.melange.tooltip = [
    s.purr,
    null
  ];

  s.melange.autocomplete = [
    s.jqueryui.autocomplete,
    null,
    mpjs + "melange.autocomplete.js"
  ];

  s.melange.graph = [
    s.google,
    null,
    mpjs + "melange.graph.js"
  ];

  s.melange.uploadform = [
    mpjs + "upload-form.js"
  ];

  s.melange.blog = [
    s.google,
    null,
    mpjs + "melange.blog.js"
  ];

  s.melange.action = [
    s.dimensions,
    s.cluetip,
    s.jqueryui.checkboxes,
    null,
    mpjs + "melange.action.js"
  ];

  s.melange.map = [
    mpjs + "melange.map.js"
  ];

  s.melange.program_select = [
    mpjs + "melange.program_select.js"
  ];

  s.melange.dynamicoptions = [
    s.json,
    null,
    mpjs + "melange.dynamicoptions.js"
  ];

  s.melange.clock = [
    s.modernizr,
    s.jquery.svg,
    null,
    mpjs + "melange.clock.js"
  ];

  $m.s = s;

  var unpack = function (orig_array) {
    var array_to_return = [];
    for (var i = 0, len = orig_array.length; i < len; i++) {
      var current_element = orig_array[i];
      if (typeof current_element === 'object' && current_element instanceof
          Array) {
        var unpacks = unpack(current_element);
        array_to_return = array_to_return.concat(unpacks);
      }
      else {
        array_to_return.push(current_element);
      }
    }
    return array_to_return;
  };

  $m.loadScripts = function(requested_packages) {
    var _tempqueue = unpack(requested_packages);

    /* Remove duplicates from the queue, as allowDuplicates with LAB
     * fails randomly at least in Safari and Chrome
     */
    var _queue = [];
    // Temporary queue with CSS paths strings.
    var _cssqueue = [];

    for (var i = 0, len = _tempqueue.length; i < len; i++) {
      var temp_val = _tempqueue[i];
      if (typeof temp_val == "string") {
        if (jQuery.inArray(temp_val, _queue) === -1) {
          _queue.push(temp_val);
        }
      }
      else if (temp_val instanceof $m.cssFile) {
        if (jQuery.inArray(temp_val.css, _cssqueue) === -1) {
          _queue.push(temp_val);
          _cssqueue.push(temp_val.css);
        }
      }
      else {
        _queue.push(temp_val);
      }
    }

    for (var i=0, len=_queue.length; i<len; i++) {
      if (typeof _queue[i] == "string") { // script string source found
          $LAB = $LAB.script(_queue[i]);
      }
      else if (!_queue[i]) { // null/false found
          $LAB = $LAB.wait();
      }
      else if (typeof _queue[i] == "object" && _queue[i] instanceof $m.templateWithContext) {
          $LAB = $LAB.wait(
            function (context_to_send) {
              return function () {
                melange.templates.setContextToLast(context_to_send);
              }
            }(_queue[i].context)
          ).script(_queue[i].script_template).wait();
      }
      else if (typeof _queue[i] == "object" && _queue[i] instanceof $m.cssFile) {
        jQuery("<link>", {
          href: _queue[i].css,
          media: "screen",
          rel: "stylesheet",
          type: "text/css"
        }).appendTo("head");
      }
      else if (typeof _queue[i] == "function") { // inline function found
          $LAB = $LAB.wait(_queue[i]);
      }
    }
  };

}());

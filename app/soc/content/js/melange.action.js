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
 * @author <a href="mailto:madhusudancs@gmail.com">Madhusudan.C.S</a>
 */
(function () {
  /** @lends melange.action */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  /** Package that handles all action buttons related functions
    * @name melange.action
    * @namespace melange.action
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.action = window.melange.action = function () {
    return new melange.action();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.action);

  melange.error.createErrors([
  ]);

  $m.createFloatMenu = function () {
    var name = "#floatMenu";
    var menuYloc = null;
    jQuery(document).ready(function(){
      menuYloc = parseInt(jQuery(name).css("top").substring(
          0, jQuery(name).css("top").indexOf("px")))
      jQuery(window).scroll(function () {
        offset = menuYloc + jQuery(document).scrollTop()+"px";
        jQuery(name).animate({top: offset},{duration: 500, queue: false});
      });
    });
  }

  $m.toggleButton = function (id, type, post_url, init_state, labels, callback) {
    var button_id = id;
    var button_type = type;
    var button_post_url = post_url;
    var button_state = init_state;
    var button_labels = labels;

    jQuery(document).ready(function() {
      jQuery('.' + button_type + ' :checkbox#' + button_id)
        .iphoneStyle({
          checkedLabel: button_labels.checked,
          uncheckedLabel: button_labels.unchecked
        }).change(function (){
          jQuery.post(button_post_url,
              {value: button_state, xsrf_token: window.xsrf_token},
              function(data) {
            if (button_state == "checked") {
              button_state = "unchecked";
            } else if (button_state == "unchecked") {
              button_state = "checked";
            }
            if (callback !== undefined && typeof(callback) === 'function') {
              callback();
            }
          });
      });
    });
  }

  /* This function exists as a show case function to show that this
   * functionality of chaining the onchange of some other button to
   * this button is possible. It is currently not used anywhere. */
  $m.createOnChangeButton = function () {
    var onchange_checkbox = jQuery('.onchange :checkbox').iphoneStyle();
    setInterval(function toggleCheckbox() {
      onchange_checkbox.attr(
        'checked', !onchange_checkbox.is(':checked')).change();
      jQuery('span#status').html(onchange_checkbox.is(':checked').toString());
    }, 2500);
  }

  $m.createCluetip = function () {
    jQuery(document).ready(function() {
      jQuery('a.load-tooltip').cluetip({
        local:true,
        cursor: 'pointer',
        showTitle:false,
        tracking:true,
        dropShadow:false
      });
    });
  }

}());

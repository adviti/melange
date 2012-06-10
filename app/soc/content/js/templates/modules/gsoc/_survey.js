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

melange.templates.inherit(
  function (_self, context) {
    var current_content = {};

    // Dom Objects selectors
    var selectors = {
      submit_button: function() {return "#form-register-fieldset-button-row"},
      container: function() {return "#survey_container"},
      menu: {
        menu: function() {return [selectors.container(), ".survey_menu"].join(" ")},
        buttons: {
          radio: function() {return [selectors.menu.menu(), ".radio"].join(" ");},
          checkbox: function() {return [selectors.menu.menu(), ".checkbox"].join(" ");},
          short_answer: function() {return [selectors.menu.menu(), ".short_answer"].join(" ")},
          long_answer: function() {return [selectors.menu.menu(), ".long_answer"].join(" ")}
        }
      },

      menu_template: function() {return "#survey_menu_template"},
      widget_template: function() {return "#survey_widget_template"}
    }

    var dos = {
      submit_button: function() {return jQuery(selectors.submit_button());},

      container: function() {return jQuery(selectors.container());},

      menu: {
        menu: function() {return jQuery(selectors.menu.menu())[0];},
        buttons: {
          radio: function() {return jQuery(selectors.menu.buttons.radio())},
          checkbox: function() {return jQuery(selectors.menu.buttons.checkbox())},
          short_answer: function() {return jQuery(selectors.menu.buttons.short_answer())},
          long_answer: function () {return jQuery(selectors.menu.buttons.long_answer())}
        }
      },

      menu_template: function() {return (jQuery(selectors.menu_template())[0]).innerHTML;},
      widget_template: function() {return (jQuery(selectors.widget_template())[0]).innerHTML;}
    };

    function SurveyWidget() {
      this.widget = jQuery(dos.widget_template()).appendTo(dos.container());

      this.deleteMe = function (event) {
        var widget = event.data.widget;
        widget.remove();
      };

      this.button_edit = this.widget.find(".button_edit");
      this.button_delete = this.widget.find(".button_delete");

      this.button_delete.bind("click", {widget: this.widget}, this.deleteMe);

      (this.widget.find(".message")[0]).innerHTML = new Date().getTime();
    };

    var createRadioWidget = function() {
      var widget_container = new SurveyWidget();
    };

    var createCheckboxWidget = function() {
      var widget_container = new SurveyWidget();
    };

    var createShortAnswerWidget = function() {
      var widget_container = new SurveyWidget();
    };

    var createLongAnswerWidget = function() {
      var widget_container = new SurveyWidget();
    }

    var callbacks = {
      menu: {
        buttons: {
          radio: createRadioWidget,
          checkbox: createCheckboxWidget,
          short_answer: createShortAnswerWidget,
          long_answer: createLongAnswerWidget
        }
      }
    };

    var initMenu = function () {
      // Append menu to the container
      jQuery(dos.container()).append(dos.menu_template());

      // Bind events to buttons
      jQuery.each(dos.menu.buttons, function (button_key, button_do) {
        button_do().bind("click", callbacks.menu.buttons[button_key]);
      });
    }

    dos.container().insertBefore(dos.submit_button()).removeClass("hidden");

    if (context.previous_content !== undefined) {
      current_content = context.previous_content;
    }
    initMenu();
  }
);

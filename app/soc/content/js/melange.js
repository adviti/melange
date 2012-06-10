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
  /** @lends melange */

  /** General melange package.
    * @name melange
    * @namespace melange
    */
  var melange = window.melange = function () {
    return new melange();
  };

  if (window.jQuery === undefined) {
    throw new Error("jQuery package must be loaded exposing jQuery namespace");
  }

  /** Shortcut to current package.
    * @private
    */
  var $m = melange;

  /** Contains general configuration for melange package.
    * @variable
    * @public
    * @name melange.config
    */
  $m.config = {};

  $m.init = function (configuration) {
    if (configuration) {
      $m.config = jQuery.extend($m.config, configuration);
    }
  };

  /** Shortcut to clone objects using jQuery.
    * @function
    * @public
    * @name melange.clone
    * @param {Object} object the object to clone
    * @returns {Object} a new, cloned object
    */
  $m.clone = function (object) {
    // clone object, see
    // http://stackoverflow.com/questions/122102/
    // what-is-the-most-efficent-way-to-clone-a-javascript-object
    return jQuery.extend(true, {}, object);
  };

  /** Set melange general options.
    * @function
    * @public
    * @name melange.setOptions
    * @param {Object} options Options to set/unset
    */
  $m.setOptions = function (options) {
    switch (options.debug) {
    case true:
      $m.logging.setDebug();
      break;
    case false:
      $m.logging.unsetDebug();
      break;
    default:
      $m.logging.setDebug();
    }
    if (options.debugLevel) {
      $m.logging.setDebugLevel(options.debugLevel);
    }
  };

  /** Facility to prepare tinyMCE settings.
    * @function
    * @public
    * @name melange.tinyMceConfig
    * @param {String[]} textareas Array of textareas IDs
    */
  $m.tinyMceConfig = function (textareas, config_switch) {
    var tinymce_settings = {
      "basic": {
        "height": 400,
        "width": 500,
        "mode": "exact",
        "relative_urls": 0,
        "remove_script_host": 0,
        "theme": "advanced",
        "theme_advanced_path": false,
        "theme_advanced_resizing": false,
        "theme_advanced_resizing_max_height": 600,
        "theme_advanced_resizing_max_width": 600,
        "theme_advanced_statusbar_location": "bottom",
        "theme_advanced_toolbar_align": "left",
        "theme_advanced_toolbar_location": "top",
        "theme_advanced_buttons1": ["bold,italic,underline,fontsizeselect,|,bullist,numlist,outdent,",
          "indent,|,undo,redo,|,justifyleft,justifycenter,justifyright,|,link,unlink,anchor"].join(),
        "theme_advanced_buttons2": "",
        "theme_advanced_buttons3": "",
        "theme_advanced_source_editor_width": 700
      },
    
      "advanced": {
        "gecko_spellcheck": "true",
        "theme_advanced_blockformats": "p,div,h1,h2,h3,h4,h5,h6,blockquote,dt,dd,code,samp",
        "theme_advanced_buttons1": ["bold,italic,underline,strikethrough,hr,",
          "|,fontselect,formatselect,fontsizeselect,forecolor"].join(),
        "theme_advanced_buttons3": "",
        "theme_advanced_buttons2": ["undo,redo,|,justifyleft,justifycenter,justifyright,|,",
          "link,unlink,anchor,code,image,|,bullist,numlist,outdent,indent"].join(),
        "theme_advanced_fonts": ["Andale Mono=andale mono,times;",
          "Arial=arial,helvetica,sans-serif;",
          "Arial Black=arial black,avant garde;",
          "Book Antiqua=book antiqua,palatino;",
          "Comic Sans MS=comic sans ms,sans-serif;",
          "Courier New=courier new,courier;",
          "Georgia=georgia,palatino;",
          "Helvetica=helvetica;",
          "Impact=impact,chicago;",
          "Symbol=symbol;",
          "Tahoma=tahoma,arial,helvetica,sans-serif;",
          "Terminal=terminal,monaco;",
          "Times New Roman=times new roman,times;",
          "Trebuchet MS=trebuchet ms,geneva;",
          "Verdana=verdana,geneva;",
          "Webdings=webdings;",
          "Wingdings=wingdings,zapf dingbats"].join()
      }
      
    };
    
    var returned_tinymce_settings = tinymce_settings.basic;
    
    if (config_switch !== undefined && config_switch !== null && 
      tinymce_settings[config_switch] !== undefined) {
      jQuery.extend(returned_tinymce_settings, tinymce_settings[config_switch]);
    };
        
    var textareaids = textareas.join(",");
    return jQuery.extend (
      returned_tinymce_settings,
      {
        elements: textareaids
      }
    );
  };


  /** Facility to load google API.
    * @function
    * @public
    * @name melange.loadGoogleApi
    * @param {String} modulename Google Ajax module to load
    * @param {String|Number} moduleversion Google Ajax module version to load
    * @param {Object} settings Google Ajax settings for the module
    * @param {Function} callback to be called as soon as module is loaded
    */
  $m.loadGoogleApi = function (modulename, moduleversion, settings, callback) {

    if (!modulename || !moduleversion) {
      throw new TypeError("modulename must be defined");
    }

    /** Options to be sent to google.load constructor
      * @private
      * @name melange.loadGoogleApi.options
      */
    var options = {
      name : modulename,
      version : moduleversion,
      settings : settings
    };
    jQuery.extend(options.settings, {callback: callback});
    google.load(options.name, options.version, options.settings);
  };

  (function () {
    /** @lends melange.cookie */

    /** Package that handles melange cookies
      * @namespace melange.cookie
      */
    melange.cookie = window.melange.cookie = function () {
      return new melange.cookie();
    };

    /** Shortcut to current package.
      * @property
      * @private
      */
    var $m = melange.cookie;

    $m.MELANGE_COOKIE_VERSION = "20110421";

    $m.MELANGE_USER_PREFERENCES = "melange_user_preferences";

    var cookie_to_save = {
      version: $m.MELANGE_COOKIE_VERSION,
      lists_configuration: {}
    };

    $m.getCookie = function (cookie_name) {
      var cookie = jQuery.cookie(cookie_name);

      try {
        cookie = JSON.parse(cookie);
        if (cookie === null) {
          throw "null_cookie";
        }
      }
      catch(e) {
        cookie = cookie_to_save;
      }

      return cookie;
    };

    $m.saveCookie = function (cookie_name, cookie_content, cookie_expires, cookie_path) {
      jQuery.extend(cookie_to_save, cookie_content);
      jQuery.cookie(cookie_name,JSON.stringify(cookie_to_save),{expires: cookie_expires, path: cookie_path});
    };

  }());


  (function () {
    /** @lends melange.error */

    /** Package that handles melange errors
      * @namespace melange.error
      */
    melange.error = window.melange.error = function () {
      return new melange.error();
    };

    /** Shortcut to current package.
      * @property
      * @private
      */
    var $m = melange.error;

    /** List of default custom error types to be created.
      * @property
      * @private
      */
    var error_types = [
      "DependencyNotSatisfied",
      "notImplementedByChildClass"
    ];

    /** Create errors
      * @function
      * @public
      * @name melange.error.createErrors
      * @param {String[]} error_types Array of strings with errors names
      */
    $m.createErrors = function (error_types) {
      jQuery.each(error_types, function () {
        melange.error[this] = Error;
      });
    };

    $m.createErrors(error_types);
  }());

  (function () {
    /** @lends melange.logging */

    /** Package that contains all log related functions.
      * @name melange.logging
      * @namespace melange.logging
      */
    melange.logging = window.melange.logging = function () {
      return new melange.logging();
    };

    /** Shortcut to current package.
      * @property
      * @private
      */
    var $m = melange.logging;
    /** @private */
    var debug = false;
    /** @private */
    var current_debug_level = 5;

    /** Set debug logging on.
      * @function
      * @public
      * @name melange.logging.setDebug
      */
    $m.setDebug = function () {
      debug = true;
    };

    /** Set debug logging off.
      * @function
      * @public
      * @name melange.logging.unsetDebug
      */
    $m.unsetDebug = function () {
      debug = false;
    };

    /** Check if debug is active.
      * @function
      * @public
      * @name melange.logging.isDebug
      * @returns {boolean} true if debug is on, false otherwise
      */
    $m.isDebug = function () {
      return debug ? true : false;
    };

    /** Set the current debug level.
      * @function
      * @public
      * @name melange.logging.setDebugLevel
      * @param level The log level to set
      * @throws {TypeError} if the parameter given is not a number
      */
    $m.setDebugLevel = function (level) {
      if (isNaN(level)) {
        throw new melange.error.TypeError(
          "melange.logging.setDebugLevel: parameter must be a number"
        );
      }
      if (level <= 0) {
        level = 1;
      }
      if (level >= 6) {
        level = 5;
      }
      current_debug_level = level;
    };

    /** Get the current debug level.
      * @function
      * @public
      * @name melange.logging.getDebugLevel
      * @returns {Number} The current debug level
      */
    $m.getDebugLevel = function () {
      return current_debug_level;
    };

    /** A decorator for logging.
      * @function
      * @public
      * @name melange.logging.debugDecorator
      * @param {Object} object_to_decorate The Function/Object to decorate
      * @returns {Object} Same object,decorated with log(level,message) func
    */
    $m.debugDecorator = function (object_to_decorate) {
      /** Function to handle output of logs.
        * @function
        * @name melange.logging.debugDecorator.log
        * @param level The log level
        * @param message The string
        */
      object_to_decorate.log = function (level, message) {
          if (melange.logging.isDebug() && current_debug_level >= level) {
            console.debug(message);
          }
        };
      return object_to_decorate;
    };
  }());

  (function () {
    /** @lends melange.templates */

    /** Package that provides basic templates functions
      * @name melange.templates
      * @namespace melange.templates
      */
    melange.templates = window.melange.templates = function () {
      return new melange.templates();
    };

    /** Shortcut to current package
      * @private
      */
    var $m = melange.logging.debugDecorator(melange.templates);

    melange.error.createErrors([
    ]);

    /** Contains a queue of all loaded templates
      *
      * This is needed to keep track of all loaded templates
      * and to give them appropriate contexts using the
      * following setContextToLast function.
      * @private
      */
    var contextQueue = [];

    /** Assign a context to the template
      *
      * @function
      * @public
      * @name melange.templates.setContextToLast
      */
    $m.setContextToLast = function (context) {
      contextQueue.push(context);
    };

    /** Parent prototype for all templates
      * @class
      * @constructor
      * @name melange.templates._baseTemplate
      * @public
      */
    $m._baseTemplate = function () {
      // Create internal context variable and push this template to the queue
      this.context = contextQueue.pop();
    };

    $m.inherit = function (template_object) {
      template_object.prototype = new melange.templates._baseTemplate();
      template_object.prototype.constructor = template_object;
      template_object.apply(
        template_object,
        [template_object, template_object.prototype.context]
      );
    }
  }());
}());
window.melange = window.melange.logging.debugDecorator(window.melange);

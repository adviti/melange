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
 *
 * Melange jQuery plugin to add options to select type HTML widgets on the fly
 *
 * Inspired by (and some portions of code taken from) Mike Botsko's jQuery
 * form builder plugin available at
 * http://www.botsko.net/blog/2009/04/jquery-form-builder-plugin/
 */

(function(jQuery){
  jQuery.fn.dynamicoptions = function(options) {
    // Extend the configuration options with user-provided
    var defaults = {};
    var opts = jQuery.extend(defaults, options);

    return this.each(function () {
      var addFieldHtml = function (values) {
        var field = '';
        field += '<div class="options">';
        field += '<a href="#" class="remove" title="X">X</a>';
        var j = 0;
        jQuery.each(opts.fields, function(field_name, item) {
          var value;
          if (values !== undefined && values.length > j) {
            value = values[j];
          }
          else {
            value = '';
          }
          field += '<input type="text" name=' + field_name + ' class="tagfield" value="' + unescape(value) + '" />';
          j += 1;
        });
        field += '</div>';
        return field;
      };

      var field = '<label class="form-label">' + opts.label + '</label>';

      var initial = JSON.parse(opts.initial);

      jQuery.each(initial, function(index, item) {
        field += addFieldHtml(item);
      });

      field += '<div class="add-area clearfix"><a id=add-' + opts.id + ' href="#" class="add">Add</a></div>';

      jQuery(this).append(field);

      jQuery(this).sortable({ opacity: 0.6, cursor: 'move'});

      jQuery('.options').live('hover', function () {
        jQuery(this).css('cursor','move');
      }, function() {
        jQuery(this).css('cursor','auto');
      });

      jQuery('#add-' + opts.id).live('click', function () {
        jQuery(this).parent().before(addFieldHtml());
        return false;
      });

      jQuery('.remove').live('click', function () {
        jQuery(this).parent('div').animate({
          opacity: 'hide',
          height: 'hide',
          marginBottom: '0px'
        }, 'fast', function () {
          jQuery(this).remove();
        });
        return false;
      });

    });
  };
})(jQuery);

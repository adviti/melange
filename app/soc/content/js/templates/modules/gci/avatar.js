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
 * @author <a href="mailto:admin@gedex.web.id">Akeda Bagus</a>
 */

melange.templates.inherit(
  function (_self, context) {

    /**
     * Get color from a given avatar value/filename.
     * @param {String} value The value in '1-blue.jpg' format.
     * @returns {String} If '1-blue.jpg' given as value it returns 'blue'.
     */
    function getColorFromValue(value) {
      var extracted_value = /^(\d\d?)-(\w+)\.jpg$/.exec(value);
      var color = 'blue';

      if (extracted_value !== null) {
        color = extracted_value[2];
      }

      return color;
    }

    /**
     * Get leading path and avatar's filename from a given img's src attribute.
     * @param {String} src Img's src attribute.
     * @returns {Object} [path, file] representing object path and filename.
     */
    function getPartsFromSrc(src) {
      var parts = src.split('/');
      var file = parts.pop();
      var path = parts.join('/');

      return {'path': path, 'file': file};
    }

    /**
     * Capitalize first letter. This is used by color picker to update the
     * color name given color's name in lowercase.
     * @param {String} str String to be capitalized.
     * @returns {String} String with first letter capitalized.
     */
    function capitalizeFirstLetter(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }

    /**
     * Function to add title attr and remove content for each select options.
     * Only called once, that's, when first load before jquery.dd construction.
     * @param {String} elemed_id Id of picker element, which is select element.
     */
    function updateOptions(element_id) {
      var path = context.prefix_path;
      var prefix = '';
      var suffix = '';
      var text = '';
      var select = jQuery('#' + element_id);

      // Since title attribute of option should contain the path
      // of the image, we need to differentiate the images location
      // of avatar-icon picker and color picker.
      if (element_id === 'avatar-color') {
        prefix = 'colors/avatar-color-';
        suffix = '.png';
      } else {
        prefix = getColorFromValue(select.val()) + '/';
      }

      // Updates title and text for each option.
      select.children('option').each(function() {
        var option = jQuery(this);
        var value = option.attr('value');

        if (element_id === 'avatar-color') {
          text = capitalizeFirstLetter(value);
        }
        option.attr('title', path + prefix + value + suffix).text(text);
      });
    }

    /**
     * Update avatar preview path. It updates the src attribute given the new
     * value in '1-blue.jpg' format.
     * @param {String} value Value in '1-blue.jpg' format.
     */
    function updatePreview(value) {
      var color = getColorFromValue(value);

      jQuery('#avatar-preview').attr('src', context.prefix_path + color + '/' + value);
    }

    // Bind an event to dynamic link created by jquery.dd so when 
    // gets clicked it updates options in #avatar-icon, hidden #avatar value,
    // and img preview.
    jQuery('#avatar-color_child a').live('click', function() {
      var color = jQuery(this).children('.ddTitleText:first').text().toLowerCase();
      var path = context.prefix_path + color + '/';

      var selected_avatar = 1 + '-' + color + '.jpg';

      // Updates each icon child that's dynamically created by jquery.dd.
      jQuery('#avatar-icon_child a').each(function(index) {
        var _index = index + 1;
        var _a = jQuery(this);
        var _img = _a.children('img:first');
        var _avatar = _index + '-' + color + '.jpg'

        // Updates src attribute.
        _img.attr('src', path + _avatar);
        if ( _a.hasClass('selected') ) {
          selected_avatar = _avatar;
        }
      });
      jQuery('#avatar-icon_titletext img').attr('src', path + selected_avatar);

      jQuery('#avatar').val(selected_avatar);
      updatePreview(selected_avatar);
    });

    // Bind an event to dynamic link created by jquery.dd so when
    // gets clicked it updates options in #avatar-icon, value in hidden #avatar,
    // and img preview.
    jQuery('#avatar-icon_child a').live('click', function() {
      var parts = getPartsFromSrc(jQuery(this).children('img:first').attr('src'));
      var value = parts['file'];

      jQuery('#avatar').val(value);
      updatePreview(value);
    });

    jQuery(
      function() {
        // Update options for #avatar and #avatar-color on page load.
        updateOptions('avatar-icon');
        updateOptions('avatar-color');

        // Update preview on page load.
        updatePreview(jQuery('#avatar').val());

        // run dynamic drop down on page load.
        jQuery('#avatar-icon').msDropDown();
        jQuery('#avatar-color').msDropDown();
      }
    );
  }
);

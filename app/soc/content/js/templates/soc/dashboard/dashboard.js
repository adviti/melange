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
    // Bind an event to window.onhashchange that, when the hash changes, gets
    // the hash and shows the related dashboard
    jQuery(window).hashchange(function() {
      var hash = location.hash;

      // targets the link to dashboard of current hash
      var dashboard_link = jQuery('.' + context.dashboard_link_class + '[href="' + hash + '"]');
      if ( !dashboard_link.length ) {
        // if nothing is targeted, targets the link to main dashboard
        hash = '#main';
        dashboard_link = jQuery('.' + context.dashboard_link_class + '[href="' + hash + '"]');
      }

      var current_dasboard = jQuery(hash + context.dashboard_id_suffix);

      // hide other dashboards
      jQuery('.' + context.dashboard_class).addClass('disabled');
      // show current dashboard
      current_dasboard.removeClass('disabled').show();

      // check if this dashboard contains components
      if (dashboard_link.hasClass(context.component_link_class)) {
        // if it does then trigger the list to be loaded
        jQuery('.' + context.list_container_class, current_dasboard).each(function() {
          var extracted_id = /^(\w+[^\d+])(\d+)$/.exec(jQuery(this).attr('id'));
          if (extracted_id !== null) {
            melange.list.list_objects.get(extracted_id[2]).init();
          }
        });
      }
    });

    // Since the event is only triggered when the hash changes, we need to
    // trigger the event now, to handle the hash the page may have loaded with.
    jQuery(window).hashchange();
  }
);

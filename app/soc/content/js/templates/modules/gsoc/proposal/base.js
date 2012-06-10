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
 * @author <a href="mailto:orc.avs@gmail.com">Orcun Avsar</a>
 */

melange.templates.inherit(
  function (_self, context) {

    if (window.melange.gdata === undefined) {
      throw new Error("Melange GData not loaded");
    }

    var melange = window.melange;
    var app_version = melange.config.app_version;

    var proposal_sync_url = context.proposal_sync_url;

    var is_sync_available = false;
    var is_syncing = false;

    var text_sync = "Sync Now";
    var text_syncing = "Syncing...";

    // IDs of HTML elements
    var id_gdoc_field = "google_document";
    var id_sync_row = "form_row_google_document";
    var id_pretty_gdoc_field = "pretty_google_document";
    var id_sync_button = "sync_now";

    // Create jquery elements.
    var jq_gdoc_field = jQuery("#" + id_gdoc_field);
    var jq_sync_row = jQuery("#" + id_sync_row);
    var jq_pretty_gdoc_field = null;
    var jq_sync_button = null;

    // Cached value to decide if pretty field is changed.
    var cached_pretty_value = "";

    function createPrettyField () {
      /* Field to show user pretty value instead of full value 
       * that also contains document id.
       */
      jq_pretty_gdoc_field = jq_gdoc_field.clone().attr(
        "id", id_pretty_gdoc_field).attr(
        "name", "pretty_google_document").attr(
        "type", "text").hide();
      jq_gdoc_field.after(jq_pretty_gdoc_field);
    }

    function disableSync () {
      jq_sync_button.addClass("disabled");
      is_sync_available = false;
    }

    function enableSync () {
      jq_sync_button.removeClass("disabled");
      is_sync_available = true;
    }

    function createSyncButton () {
      /* Creates sync button and hides it.
       */
      html = [
        "<a id='", id_sync_button, "' ",
        "href='javascript:void(0)' ",
        "class='small-orange-button' ",
        "style='display:none'>",
        text_sync, "</a>"
      ].join("");
      jq_pretty_gdoc_field.after(html);
      jq_sync_button = jQuery("#" + id_sync_button);

      // If there is no document selected when loading page, disable button.
      if (!jq_gdoc_field.val()) {
        disableSync();
      }
      // If document field value changes, disable button until next select.
      jq_pretty_gdoc_field.change(function () {
        disableSync();
      });
      // If a key pressed on document field, disable button until next select.
      jq_pretty_gdoc_field.keydown(function () {
        if (jq_pretty_gdoc_field.val() !== cached_pretty_value) {
          disableSync();
        }
      });
    }

    function sync () {
      /* Sync proposal tinymce content with the html content
       * of selected document.
       */
      if (is_sync_available || is_syncing) {
        return;
      }

      jq_sync_button.html(text_syncing);
      is_syncing = true;

      data = jQuery.parseJSON(jq_gdoc_field.val());
      jQuery.ajax({
        type: "GET",
        dataType: "json",
        url: proposal_sync_url,
        data: {fmt: 'json', document_id: data.id},
        success: function (msg) {
          tinyMCE.editors[0].setContent(msg.content);
        },
        error: function (msg) {
          alert("Unable to sync! Make sure you're logged in to Google Docs.");
        },
        complete: function (jqxhr, textstatus) {
          jq_sync_button.html(text_sync);
          is_syncing = false;
        }
      });
    }

    function selectDocument () {
      /* Enables autocomplete selection.
       */
      jq_pretty_gdoc_field.autocomplete("enable");
    }

    function makeAutoComplete () {
      /* Sets up autocomplete field.
       */

      /* Actual field holds a json data in {'title': .. , 'id': ...} form.
       * 'title' is the pretty value that is shown to user.
       */
      var pretty_value = "";
      if (jq_gdoc_field.val()) {
        data = jQuery.parseJSON(jq_gdoc_field.val());
        pretty_value = data.title;
      }
      cached_pretty_value = pretty_value;
      jq_pretty_gdoc_field.val(pretty_value);

      jq_pretty_gdoc_field.autocomplete({
        source: "?fmt=json&field=google_document",
        minLength: 2,
        select: function (event, ui) {
          if (ui.item) {
            // Set actual field value that will be used for syncing
            jq_gdoc_field.val(ui.item.json);

            cached_pretty_value = ui.item.value;
            jq_sync_button.removeClass("disabled");
          }
        }
      });
      // Disable autocomplete until it's enabled by selectDocument function.
      jq_pretty_gdoc_field.autocomplete("disable");
    }

    function clickSyncLabel() {
      /* Runs when label clicked in order to slide down/up sync elements.
       */
      if (jq_sync_button.is(":visible")) {
        jq_pretty_gdoc_field.hide();
        jq_sync_button.hide();
      }
      else {
        jq_sync_button.show();
        jq_pretty_gdoc_field.show();
      }
    }

    function createSlideDownLabel () {
      /* Sets up slide down label for sync elements
       */

      // Preload add icon
      src = "/soc/content/" + app_version + "/images/v2/gsoc/add.png"
      add_icon = new Image();
      add_icon.src = src;

      jq_sync_row.children().filter("label").html([
        "<img src='", src, "' />",
        "<a href='javascript:void(0)'>",
        "  Sync with Google Documents",
        "</a>"
      ].join(""));

    }

    jQuery(
      function () {
        /* Initial set up
         */
        createPrettyField();
        createSyncButton();
        createSlideDownLabel();
        makeAutoComplete();

        // Register event callbacks as gdocs login required
        fn = melange.gdata.loginFunctionFactory(sync, []);
        jq_sync_button.click(fn);

        fn = melange.gdata.loginFunctionFactory(selectDocument, []);
        jq_pretty_gdoc_field.focus(fn);

        // Make slide down event gdocs login required.
        fn = melange.gdata.loginFunctionFactory(clickSyncLabel, []);
        jq_sync_row.children().filter("label").click(fn);
      }
    );
  }
);

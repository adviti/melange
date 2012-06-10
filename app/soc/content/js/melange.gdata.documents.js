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
(function () {
  /** @lends melange.gdata.documents */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  if (window.melange.gdata === undefined) {
    throw new Error("GData not loaded.");
  }

  var melange = window.melange;
  var gdata = melange.gdata;

  /** Package that handles gdata related functions
    * @name melange.gdata.documents
    * @namespace melange.gdata.documents
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.gdata.documents = window.melange.gdata.documents = function () {
    return new melange.gdata.documents();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.gdata.documents);

  melange.error.createErrors([
  ]);

  $m.uploadDocument = function (metadata, content, format) {

    var data = {
      metadata: metadata,
      content: content,
      format: format,
    };

    //Preload loading image
    var img_src = [
      "/soc/content/",
      melange.config.app_version,
      "/images/v2/gsoc/autocomplete-loading.gif"
    ].join("");
    var preload_img = new Image();
    preload_img.src = img_src;


    var createUploadDialog = function () {
      jQuery("#uploading_dialog").remove();
      jQuery("body").append(
        [
          "<div id='uploading_dialog' style='display:none'>",
          "  <img src='", img_src, "'/>",
          "  <h3> Your document is being uploaded... </h3>",
          "</div>"
        ].join("")
      );
      jQuery("#uploading_dialog").dialog({
        height: 150,
        width: 500,
        model: true,
        buttons: {"Close": function () {jQuery(this).dialog("close")}}
      });
    };

    var finishUploadDialog = function (link_to_document) {
      jQuery("#uploading_dialog img").remove();
      jQuery("#uploading_dialog h3").html(
        [
          "Uploaded successfully: ",
          "<a target='_blank' href='", link_to_document, "'>",
          "  Open document",
          "</a> in a new tab."
        ].join("")
      );
    };

    var createDocument = function () {
      createUploadDialog();
      var headers = {
        "Content-Type": "application/atom+xml"
      };
      var as_json = true;
      gdata.makeRequest(
        'documents',
        'POST',
        '/feeds/documents/private/full',
        headers,
        data.metadata,
        as_json,
        updateContent
      );
    };

    var updateContent = function (response) {
      var feed_media_url = '';
      jQuery.each(response.entry.link, function (index, link) {
        if (link.rel.indexOf('edit-media') !== -1) {
          feed_media_url = link.href;
        }
      });
      var feed_media_url = response.entry.link[5].href;
      var headers = {
        'Slug': 'file.ext',
        'Content-Type': data.format
      };
      var as_json = true;
      gdata.makeRequest(
        'documents',
        'PUT',
        feed_media_url,
        headers,
        data.content,
        as_json,
        finishUpload
      );
    };

    var finishUpload = function (response) {
      var document_link = '';
      jQuery.each(response.entry.link, function (index, link) {
        if (link.rel.indexOf('alternate') != -1) {
          document_link = link.href;
        }
      });
      finishUploadDialog(document_link);
    };

    gdata.createAuthorizedFunction(createDocument, [])();
  };

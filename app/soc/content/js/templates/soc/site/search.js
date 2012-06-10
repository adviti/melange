/*
 * Copyright 2010 the Melange authors.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
/**
 * @author <a href="mailto:lpalm@google.com">Leon Palm</a>
 */

melange.templates.inherit(
  function (_self, context) {
    var createSearchBox = function () {
      var customSearchControl =
          new google.search.CustomSearchControl(context.cse_key);
      customSearchControl
          .setResultSetSize(google.search.Search.FILTERED_CSE_RESULTSET);
      customSearchControl.draw('cse');
    };
  
    jQuery(
      function () {
        melange.loadGoogleApi("search", "1", {language: "en"}, createSearchBox);
      }
    );

  }
);

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
 * @author <a href="mailto:dhans@google.com">Daniel Hans</a>
 */

melange.templates.inherit(function (_self, context) {

  // TODO: replace eval with a safe json library
  eval('var urls = ' + context.urls);
  eval('var manage_urls = ' + context.manage_urls)
  eval('var visualizations = ' + context.visualizations);
  eval('var visibilities = ' + context.visibilities);
  
  var toggleButton = null;

  // Whether change() function should send a request to the server
  var sendRequest = true;

  var bindToggleButton = function () {
     toggleButton = jQuery('.on_off :checkbox#is-visible-statistic')
	    .iphoneStyle({
	      checkedLabel: 'Yes',
	      uncheckedLabel: 'No'
	    })
	    .change(toggleButtonChanged);
  }

  var toggleButtonChanged = function () {
	if (!sendRequest) {
	  sendRequest = true;
    } else {
	  var oldState = !toggleButton.is(':checked');
	  var _key_name = key_name;
	  jQuery.post(
	      manage_urls[_key_name],
	      {value: !oldState,
	       xsrf_token: window.xsrf_token
	      },
	      function (data) {
	        visibilities[_key_name] = !oldState;
	      }
	   );
    }
  }

  /* Maps Google Visualization Data packages with human friendly names. */
  var visualization_names = {
    'piechart': 'Pie Chart',
    'table': 'Table'
  }

  /* Maps Google Visualization API objects with vizualization names */
  var visualization_objects = {};

  /* These two variables represent current state of the page:
   * - statistic which is shown
   * - visualization which is displayed
   */
  var key_name = null;
  var visualization_name = null;

  /* Saved data for the statistics which have been fetched. */
  var statistic_data = {};

  var drawStatisticVisualization = function (is_different) {
	var chart = new visualization_objects[visualization_name](
		document.getElementById('statistic-presentation-div'));
	/* check if the data for a given statistic has already been downloaded. */
	if (statistic_data[key_name] !== undefined) {
	  chart.draw(statistic_data[key_name], {width: 400, height: 240});
	  /* reset the options only if this is a different statistic */
	  if (is_different) {
	    setVisualizationOptions();
	  }
	} else {
	/* The statistic is requested for the first time. Data has to fetched from the server. */
	  var url = urls[key_name];
	  jQuery.get(
		url,
		{'fmt': 'json', 'type': 'gviz'},
		function (data) {
		  eval('var _data = ' + data);
		  statistic_data[key_name] = new google.visualization.DataTable(_data);
	      chart.draw(statistic_data[key_name], {width: 400, height: 240});
	      setVisualizationOptions();
		},
		'text'
	  );
	}
  };

  var setVisualizationOptions = function () {
	jQuery('#statistic-visualization-select').find('option').remove();

	jQuery(visualizations[key_name]).each(function (index, value) {
		jQuery('#statistic-visualization-select').append(
		    jQuery('<option></option>')
		        .attr('value', value)
		        .text(visualization_names[value]));
	});
  };
  
  var selectionChanged = function () {
	jQuery('#statistic-select :selected').each(function () {
	  key_name = jQuery(this).attr('id');
	  visualization_name = visualizations[key_name][0];
	  drawStatisticVisualization(true);
	  if (toggleButton.is(':checked') !== visibilities[key_name]) {
		sendRequest = false;
		toggleButton.attr('checked', !toggleButton.is(':checked')).change();
	  }
	});
  };

  var visualizationChanged = function () {
	jQuery('#statistic-visualization-select :selected').each(function () {
	  visualization_name = jQuery(this).attr('value');
	  drawStatisticVisualization(false);
	});
  };

  var initialize = function () {
	visualization_objects = {
	  'piechart': google.visualization.PieChart,
	  'table': google.visualization.Table
	};
	selectionChanged();
  };
  
  jQuery(function () {
	jQuery('#statistic-select').change(selectionChanged);
	jQuery('#statistic-visualization-select').change(visualizationChanged);
	melange.loadGoogleApi('visualization', '1', {'packages':['table', 'corechart']}, initialize);
	bindToggleButton();
  });
});

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
 * @author <a href="mailto:madhusudancs@gmail.com">Madhusudan.C.S</a>
 */

(function () {
  /** @lends melange.map */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  /** Package that handles all map buttons related functions
    * @name melange.map
    * @namespace melange.map
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.map = window.melange.map = function () {
    return new melange.map();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.map);

  melange.error.createErrors([
  ]);

  // Map load function
  $m.loadMap = function (map_div, map_data) {

    var center_latlng = new google.maps.LatLng(0, 0);
    var init_options = {
      zoom: 2,
      center: center_latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById(map_div),
        init_options);

    var mentors = {};
    var students = {};
    var projects = {};
    var polylines = [];

    // Iterate over projects to draw polylines
    jQuery.each(map_data.projects, function (key, project) {
      var current_student = map_data.students[project.student_key];
      var current_mentor = map_data.mentors[project.mentor_key];
      if (current_student !== undefined && 
          current_mentor !== undefined &&
          current_student.lat !== null &&
          current_student.lng !== null &&
          current_mentor.lat !== null &&
          current_mentor.lng !== null) {
            polylines.push([
              new google.maps.LatLng(current_student.lat, current_student.lng),
              new google.maps.LatLng(current_mentor.lat, current_mentor.lng)
            ]);
      }
    });

    // Iterate over students
    jQuery.each(map_data.students, function (key, person) {
      var html = "";
      var marker = null;

      if (person.lat !== null && person.lng !== null) {
        var point = new google.maps.LatLng(person.lat, person.lng);

        var marker = new google.maps.Marker({
            position: point,
            title: person.name,
            map: map
        });
        html = [
          "<strong>", person.name, "</strong><br />",
          "<span style='font-style:italic;'>Student</span><br />",
          "<div style='height:100px;width:300px;",
          "overflow:auto;'>"
        ].join("");
        // iterate through projects
        jQuery.each(person.projects, function () {
          var current_project = map_data.projects[this];
          html += [
            "<a href='", current_project.link, "'>",
            current_project.title, "</a><br />",
            "Mentor: ", current_project.mentor_name, "<br />"
          ].join("");
        });
        html += "</div>";

        var infowindow = new google.maps.InfoWindow({
          content: html
        });
        google.maps.event.addListener(marker, "click", function () {
          infowindow.open(map, marker);
        });
      }
    });

    // Iterate over mentors
    jQuery.each(map_data.mentors, function (key, person) {
      var html = "";
      var marker = null;

      if (person.lat !== null && person.lng !== null) {
        var point = new google.maps.LatLng(person.lat, person.lng);

        marker = new google.maps.Marker({
            position: point,
            title: person.name,
            icon: "/soc/content/" + melange.config.app_version + "/images/mentor-marker.png",
            map: map
        });
        html = [
          "<strong>", person.name, "</strong><br />",
          "<span style='font-style:italic;'>Mentor</span><br />",
          "<div style='height:100px;width:300px;",
          "overflow:auto;font-size:70%'>"
        ].join("");
        // iterate through projects
        jQuery.each(person.projects, function () {
          var current_project = map_data.projects[this];
          html += [
            "<a href='", current_project.link, "'>",
            current_project.title, "</a><br />",
            "Student: ", current_project.student_name, "<br />"
          ].join("");
        });
        html += "</div>";

        var infowindow = new google.maps.InfoWindow({
          content: html
        });
        google.maps.event.addListener(marker, "click", function () {
          infowindow.open(map, marker);
        });
      }
    });

    // Draw all polylines
    jQuery.each(polylines, function () {
      new google.maps.Polyline({
        path: this,
        strokeColor: "#FF0000",
        strokeOpacity: 1.0,
        strokeWeight: 3,
        map: map
      });
    });
  }
}());

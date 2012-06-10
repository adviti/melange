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
 */

(function () {
  /** @lends melange.list */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  /** Package that handles all clock buttons related functions
    * @name melange.clock
    * @namespace melange.clock
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.clock = window.melange.clock = function () {
    return new melange.clock();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.clock);

  melange.error.createErrors([
  ]);

  // Clock load function
  $m.loadClock = function (complete_percentage) {
    jQuery('document').ready(function(){
      if (Modernizr.svg && Modernizr.svgclippaths) {
        var back_image = $('.stopwatch-svgcanvas').css('background-image');
        back_image = back_image.replace(/"/g,"").replace(/url\(|\)$/ig, "");

        var front_image = $('.stopwatch-front').css('background-image');
        front_image = front_image.replace(/"/g,"").replace(/url\(|\)$/ig, "");

        var dial_image = $('.stopwatch-dial').css('background-image');
        dial_image = dial_image.replace(/"/g,"").replace(/url\(|\)$/ig, "");

        $('.stopwatch-watch').hide();
        $('.stopwatch-svgcanvas').css('background-image', 'none');
        $('.stopwatch-svgcanvas').show();
        $('.stopwatch-svgcanvas').svg();

        var percent = complete_percentage / 100;
        var angle = percent * 360;
        var svg = jQuery('.stopwatch-svgcanvas').svg('get');
        var defs = svg.defs();
        var mask = svg.mask(defs, 'mask', 0, 0, 96, 96, {maskUnits: 'userSpaceOnUse'});

        svg.image(defs, 0, 0, 91, 91, back_image, {id: 'back_image'});
        svg.image(defs, 0, 0, 91, 91, front_image, {id: 'front_image'});
        svg.image(defs, 0, 0, 91, 91, dial_image, {id: 'dial_image', transform: 'rotate(' + angle + ', 46, 46)'});

        var path = svg.createPath();
        var ratio = 2 * Math.PI * (percent-.25);
        svg.path(mask, path
          .move(46, 0)
          .line(46, 46)
          .line(46 + 46 * Math.cos(ratio), 46 + 46 * Math.sin(ratio))
          .arc(46, 46, 60, true, false, 46, 0)
          .line(46, 0)
          .close(),
          {fill: '#ffffff', stroke: 'none', strokeWidth: 1}
        );

        svg.use('#back_image');
        if (percent == 1.0) {
          svg.use('#front_image');
        } else {
          svg.use('#front_image', {mask:'url(#mask)'});
        }
        svg.use('#dial_image');
      }
    });
  }
}());

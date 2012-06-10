$(document).ready(function(){
  $('.low-vision-style-toggle').click(toggleLowVisionStyle);
  
  var cookie_lowvision_disabled = readCookie("lowvision_disabled");
  if (cookie_lowvision_disabled == "false") lowvision_disabled = false;
  else lowvision_disabled = true;
  
  $('link[rel*=style][title="low vision"]').each(function(){
    this.disabled = true;
    this.disabled = lowvision_disabled;
  });
});

function toggleLowVisionStyle() {
  lowvision_disabled = ! lowvision_disabled;
  createCookie("lowvision_disabled", lowvision_disabled, 365);
  $('link[rel*=style][title="low vision"]').each(function(){
    this.disabled = lowvision_disabled;
  });
}

function createCookie(name,value,days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime()+(days*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
  }
  else expires = "";
  document.cookie = name+"="+value+expires+"; path=/";
}
function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}

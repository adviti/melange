melange.templates.inherit(function(){function k(){jQuery.each(d,function(c,a){a.old_value=jQuery(a.id).val()})}function q(){var c=false;jQuery.each(d,function(a,b){if(jQuery(b.id).val()!==b.old_value){c=true;return false}});return c}function l(){jQuery(i).val(g);jQuery(j).val(h)}function r(){g=jQuery(i).val();h=jQuery(j).val()}function s(){if(q()){var c="";jQuery.each(d,function(a,b){c+=jQuery(b.id).val()+","});m.getLatLng(c,function(a){if(a){k();var b=n;if(jQuery(d.street.id).val()!=="")b=o;else if(jQuery(d.city.id).val()!==
"")b=t;else if(jQuery(d.state.id).val()!=="")b=u;else if(jQuery(d.country.id).val()!=="")b=v;e.setCenter(a,b);f.setPoint(a);e.clearOverlays();e.addOverlay(f);g=a.lat();h=a.lng();l()}})}}function w(){if(google.maps.BrowserIsCompatible()){k();var c,a=n,b=true;e=new google.maps.Map2(document.getElementById(p));e.addControl(new google.maps.SmallMapControl);e.addControl(new google.maps.MapTypeControl);m=new google.maps.ClientGeocoder;if(jQuery(i).val()!==""&&jQuery(j).val()!==""){r();a=o;b=true}c=new google.maps.LatLng(g,
h);e.setCenter(c,a);f=new google.maps.Marker(c,{draggable:true});b&&e.addOverlay(f);jQuery.each(d,function(y,x){jQuery(x.id).blur(s)});google.maps.Event.addListener(f,"dragend",function(){g=f.getPoint().lat();h=f.getPoint().lng();l()})}}var e,f,m,g=0,h=0,n=1,v=4,u=6,t=10,o=13,p="profile_map",i="#latitude",j="#longitude",d={street:{id:"#res_street",old_value:""},city:{id:"#res_city",old_value:""},state:{id:"#res_state",old_value:""},country:{id:"#res_country",old_value:""},postalcode:{id:"#res_postalcode",
old_value:""}};jQuery(function(){jQuery("#form_row_publish_location").append("<div id='"+p+"'></div>");melange.loadGoogleApi("maps","2",{},w)})});
(function(){if(window.melange===undefined)throw new Error("Melange not loaded");var b=window.melange;b.autocomplete=window.melange.autocomplete=function(){return new b.autocomplete};var f=b.logging.debugDecorator(b.autocomplete);b.error.createErrors([]);f.makeAutoComplete=function(c){var d=c+"-pretty";jQuery.ajax({url:"?fmt=json&field="+c,success:function(g){jQuery("#"+d).autocomplete({source:g.data,focus:function(e,a){jQuery("#"+d).val(a.item.label);return false},select:function(e,a){jQuery("#"+
d).val(a.item.key_name);jQuery("#"+c).val(a.item.key);return false}}).data("autocomplete")._renderItem=function(e,a){return jQuery("<li></li>").data("item.autocomplete",a).append("<a>"+a.key_name+" ("+a.label+")</a>").appendTo(e)}}})}})();
(function(e){var b=[];e.preserveDefaultText={ShowAll:function(){for(var a=0;a<b.length;a+=1)if(b[a].obj.val()===""){b[a].obj.val(b[a].text);b[a].obj.css("color",b[a].WatermarkColor)}else b[a].obj.css("color",b[a].DefaultColor)},HideAll:function(){for(var a=0;a<b.length;a+=1)b[a].obj.val()===b[a].text&&b[a].obj.val("")}};e.fn.preserveDefaultText=function(a,d){d||(d="#aaa");return this.each(function(){function h(){c.val()===a&&c.val("");c.css("color",f)}function g(){if(c.val().length===0||c.val()===
a){c.val(a);c.css("color",d)}else c.css("color",f)}var c=e(this),f=c.css("color");b[b.length]={text:a,obj:c,DefaultColor:f,WatermarkColor:d};c.focus(h);c.blur(g);c.change(g);g()})}})(jQuery);
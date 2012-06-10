/*
			http://opensource.org/licenses/mit-license.php
*/
(function(d){function p(c,a){var b=c.attr("id"),e=d("input#"+b+"-score");d("img."+b);d("#"+b).mouseleave(function(){k(c,e.val(),a)});d("img."+b).mousemove(function(f){l(b,this.alt,a);if(a.half){f=parseFloat(((f.pageX-d(this).offset().left)/a.size).toFixed(1));f=f>=0&&f<0.5?0.5:1;c.data("score",parseFloat(this.alt)+f-1);m(c,c.data("score"),a)}else l(b,this.alt,a)}).click(function(){e.val(a.half?c.data("score"):this.alt);a.click&&a.click.apply(c,[e.val()])})}function n(c,a,b){var e=$global;if(a){if(a.indexOf(".")>=
0){var f;return d(a).each(function(){f="#"+d(this).attr("id");if(b=="start")d.fn.raty.start(c,f);else if(b=="click")d.fn.raty.click(c,f);else b=="readOnly"&&d.fn.raty.readOnly(c,f)})}e=d(a);if(!e.length){o('"'+a+'" is a invalid identifier for the public funtion $.fn.raty.'+b+"().");return}}return e}function o(c){console&&console.log&&console.log(c)}function l(c,a,b){for(var e=d("img."+c).length,f=0,i=0,h,j,g=1;g<=e;g++){h=d("img#"+c+"-"+g);if(g<=a)if(b.iconRange&&b.iconRange.length>f){j=b.iconRange[f][0];
i=b.iconRange[f][1];g<=i&&h.attr("src",b.path+j);g==i&&f++}else h.attr("src",b.path+b.starOn);else h.attr("src",b.path+b.starOff)}}function q(c,a,b){if(a!=0){a=parseInt(a);hint=a>0&&b.number<=b.hintList.length&&b.hintList[a-1]!==null?b.hintList[a-1]:a}else hint=b.noRatedMsg;d("#"+c.attr("id")).attr("title",hint).children("img").attr("title",hint)}function k(c,a,b){var e=c.attr("id");if(a<0||isNaN(a))a=0;else if(a>b.number)a=b.number;d("input#"+e+"-score").val(a);l(e,a,b);b.half&&m(c,a,b);if(b.readOnly||
c.css("cursor")=="default")q(c,a,b)}function m(c,a,b){c=c.attr("id");var e=Math.ceil(a);a=(e-a).toFixed(1);if(a>=0.3&&a<=0.7){e-=0.5;d("img#"+c+"-"+Math.ceil(e)).attr("src",b.path+b.starHalf)}else a>=0.8||d("img#"+c+"-"+e).attr("src",b.path+b.starOn)}d.fn.raty=function(c){options=d.extend({},d.fn.raty.defaults,c);if(this.length==0)o("Selector invalid or missing!");else{if(this.length>1)return this.each(function(){d.fn.raty.apply(d(this),[c])});if(options.number>20)options.number=20;else if(options.number<
0)options.number=0;if(options.path.substring(options.path.length-1,options.path.length)!="/")options.path+="/";$global=d(this);$global.data("options",options);var a=this.attr("id"),b=0,e=options.starOn,f="",i=options.width?options.width:options.number*options.size+options.number*4;if(a==""){a="raty-"+$global.index();$global.attr("id",a)}if(!isNaN(options.start)&&options.start>0)b=options.start>options.number?options.number:options.start;for(var h=1;h<=options.number;h++){e=b>=h?options.starOn:options.starOff;
f=h<=options.hintList.length&&options.hintList[h-1]!==null?options.hintList[h-1]:h;$global.append('<img id="'+a+"-"+h+'" src="'+options.path+e+'" alt="'+h+'" title="'+f+'" class="'+a+'"/>').append(h<options.number?"&nbsp;":"")}d("<input/>",{id:a+"-score",type:"hidden",name:options.scoreName}).appendTo($global).val(b);options.half&&m($global,d("input#"+a+"-score").val(),options);if(options.readOnly){$global.css("cursor","default");q($global,b,options)}else{if(options.cancel){var j=d("img."+a);b='<img src="'+
options.path+options.cancelOff+'" alt="x" title="'+options.cancelHint+'" class="button-cancel"/>';var g=options,r=$global;g.cancelPlace=="left"?$global.prepend(b+"&nbsp;"):$global.append("&nbsp;").append(b);d("#"+a+" img.button-cancel").mouseenter(function(){d(this).attr("src",g.path+g.cancelOn);j.attr("src",g.path+g.starOff)}).mouseleave(function(){d(this).attr("src",g.path+g.cancelOff);j.mouseout()}).click(function(){d("input#"+a+"-score").val(0);g.click&&g.click.apply(r,[0])});$global.css("width",
i+options.size+4)}else $global.css("width",i);$global.css("cursor","pointer");p($global,options)}return $global}};d.fn.raty.click=function(c,a){var b=n(c,a,"click");a=d(a).data("options");k(b,c,a);a.click?a.click.apply(b,[c]):o('You must add the "click: function(score) { }" callback.');return d.fn.raty};d.fn.raty.readOnly=function(c,a){var b=n(c,a,"readOnly"),e=b.children("img.button-cancel");a=d(a).data("options");if(e[0])c?e.hide():e.show();if(c){d("img."+b.attr("id")).unbind();b.css("cursor","default").unbind()}else{p(b,
a);b.css("cursor","pointer")}return d.fn.raty};d.fn.raty.start=function(c,a){var b=n(c,a,"start");a=d(a).data("options");k(b,c,a);return d.fn.raty};d.fn.raty.defaults={cancel:false,cancelHint:"cancel this rating!",cancelOff:"cancel-off.png",cancelOn:"cancel-on.png",cancelPlace:"left",click:null,half:false,hintList:["bad","poor","regular","good","gorgeous"],noRatedMsg:"not rated yet",number:5,path:"img/",iconRange:[],readOnly:false,scoreName:"score",size:16,starHalf:"star-half.png",starOff:"star-off.png",
starOn:"star-on.png",start:0,width:null}})(jQuery);

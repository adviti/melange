(function(b){b.fn.bgIframe=b.fn.bgiframe=function(a){if(b.browser.msie&&/6.0/.test(navigator.userAgent)){a=b.extend({top:"auto",left:"auto",width:"auto",height:"auto",opacity:true,src:"javascript:false;"},a||{});var d=function(c){return c&&c.constructor==Number?c+"px":c},e='<iframe class="bgiframe"frameborder="0"tabindex="-1"src="'+a.src+'"style="display:block;position:absolute;z-index:-1;'+(a.opacity!==false?"filter:Alpha(Opacity='0');":"")+"top:"+(a.top=="auto"?"expression(((parseInt(this.parentNode.currentStyle.borderTopWidth)||0)*-1)+'px')":
d(a.top))+";left:"+(a.left=="auto"?"expression(((parseInt(this.parentNode.currentStyle.borderLeftWidth)||0)*-1)+'px')":d(a.left))+";width:"+(a.width=="auto"?"expression(this.parentNode.offsetWidth+'px')":d(a.width))+";height:"+(a.height=="auto"?"expression(this.parentNode.offsetHeight+'px')":d(a.height))+';"/>';return this.each(function(){b("> iframe.bgiframe",this).length==0&&this.insertBefore(document.createElement(e),this.firstChild)})}return this}})(jQuery);

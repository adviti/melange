(function(b){var v="",ja=function(p,l){var k=this;l=b.extend({height:120,visibleRows:7,rowHeight:23,showIcon:true,zIndex:9999,mainCSS:"dd",useSprite:false,animStyle:"slideDown",onInit:"",style:""},l);this.ddProp={};var A="",q={};q.insideWindow=true;q.keyboardAction=false;q.currentKey=null;var r=false,R={postElementHolder:"_msddHolder",postID:"_msdd",postTitleID:"_title",postTitleTextID:"_titletext",postChildID:"_child",postAID:"_msa",postOPTAID:"_msopta",postInputID:"_msinput",postArrowID:"_arrow",
postInputhidden:"_inp"},g={dd:l.mainCSS,ddTitle:"ddTitle",arrow:"arrow",ddChild:"ddChild",ddTitleText:"ddTitleText",disabled:0.3,ddOutOfVision:"ddOutOfVision",borderTop:"borderTop",noBorderTop:"noBorderTop",selected:"selected"},S={actions:"focus,blur,change,click,dblclick,mousedown,mouseup,mouseover,mousemove,mouseout,keypress,keydown,keyup",prop:"size,multiple,disabled,tabindex"};this.onActions={};var e=b(p).prop("id");if(typeof e=="undefined"||e.length<=0){e="msdrpdd"+b.msDropDown.counter++;b(p).attr("id",
e)}var I=b(p).prop("style");l.style+=I==undefined?"":I;var B=b(p).children();if(r=b(p).prop("size")>1||b(p).prop("multiple")==true?true:false)l.visibleRows=b(p).prop("size");var m={},T=false,C,F={},j=function(a){if(typeof F[a]=="undefined")F[a]=document.getElementById(a);return F[a]},h=function(a){return e+R[a]},U=function(a){return b(a).prop("style")},V=function(a){var c=b("#"+e+" option:selected");if(c.length>1)for(var d=0;d<c.length;d++){if(a==c[d].index)return true}else if(c.length==1)if(c[0].index==
a)return true;return false},D=function(a,c,d,f){var i="",n=f=="opt"?h("postOPTAID"):h("postAID");c=f=="opt"?n+"_"+c+"_"+d:n+"_"+c;f=d="";if(l.useSprite!=false)f=" "+l.useSprite+" "+a.className;else{d=b(a).prop("title");d=d.length==0?"":'<img src="'+d+'" align="absmiddle" /> '}n=b(a).text();var o=b(a).val(),s=b(a).prop("disabled")==true?"disabled":"enabled";m[c]={html:d+n,value:o,text:n,index:a.index,id:c};o=U(a);i+=V(a.index)==true?'<a href="javascript:void(0);" class="'+g.selected+" "+s+f+'"':'<a  href="javascript:void(0);" class="'+
s+f+'"';if(o!==false&&o!==undefined)i+=" style='"+o+"'";i+=' id="'+c+'">';i+=d+'<span class="'+g.ddTitleText+'">'+n+"</span></a>";return i},W=function(a){a=a.toLowerCase();if(a.length==0)return-1;var c="";for(var d in m)if(m[d].text.toLowerCase().substr(0,a.length)==a)c+="#"+m[d].id+", ";return c==""?-1:c},X=function(){if(B.length==0)return"";var a="";h("postAID");h("postOPTAID");B.each(function(c){var d=B[c];if(d.nodeName=="OPTGROUP"){a+="<div class='opta'>";a+="<span style='font-weight:bold;font-style:italic; clear:both;'>"+
b(d).prop("label")+"</span>";var f=b(d).children();f.each(function(i){a+=D(f[i],c,i,"opt")});a+="</div>"}else a+=D(d,c,"","")});return a},Y=function(){h("postID");var a=h("postChildID"),c=l.style;sDiv="";sDiv+='<div id="'+a+'" class="'+g.ddChild+'"';sDiv+=r?c!=""?' style="border-top:1px solid #c3c3c3;display:block;position:relative;'+c+'"':"":c!=""?' style="'+c+'"':"";sDiv+=">";return sDiv},Z=function(){var a=h("postTitleID"),c=h("postArrowID"),d=h("postTitleTextID");h("postInputhidden");var f="",
i="";if(j(e).options.length>0){f=b("#"+e+" option:selected").text();i=b("#"+e+" option:selected").prop("title")}i=i.length==0||i==undefined||l.showIcon==false||l.useSprite!=false?"":'<img src="'+i+'" align="absmiddle" /> ';a='<div id="'+a+'" class="'+g.ddTitle+'"';a+=">";a+='<span id="'+c+'" class="'+g.arrow+'"></span><span class="'+g.ddTitleText+'" id="'+d+'">'+i+'<span class="'+g.ddTitleText+'">'+f+"</span></span></div>";return a},G=function(){var a=h("postChildID");b("#"+a+" a.enabled").unbind("click");
b("#"+a+" a.enabled").bind("click",function(c){c.preventDefault();J(this);x();if(!r){b("#"+a).unbind("mouseover");y(false);c=l.showIcon==false?b(this).text():b(this).html();w(c);k.close()}})},ca=function(){var a=false,c=h("postID"),d=h("postTitleID");h("postTitleTextID");var f=h("postChildID");h("postArrowID");var i=b("#"+e).width();i+=2;var n=l.style;if(b("#"+c).length>0){b("#"+c).remove();a=true}var o='<div id="'+c+'" class="'+g.dd+'"';o+=n!=""?' style="'+n+'"':"";o+=">";o+=Z();o+=Y();o+=X();o+=
"</div>";o+="</div>";if(a==true){n=h("postElementHolder");b("#"+n).after(o)}else b("#"+e).after(o);if(r){d=h("postTitleID");b("#"+d).hide()}b("#"+c).css("width",i+"px");b("#"+f).css("width",i-2+"px");if(B.length>l.visibleRows){i=parseInt(b("#"+f+" a:first").css("padding-bottom"))+parseInt(b("#"+f+" a:first").css("padding-top"));i=l.rowHeight*l.visibleRows-i;b("#"+f).css("height",i+"px")}else if(r){i=b("#"+e).height();b("#"+f).css("height",i+"px")}if(a==false){$();aa(e)}b("#"+e).prop("disabled")==
true&&b("#"+c).css("opacity",g.disabled);ba();b("#"+d).bind("mouseover",function(){K(1)});b("#"+d).bind("mouseout",function(){K(0)});G();b("#"+f+" a.disabled").css("opacity",g.disabled);r&&b("#"+f).bind("mouseover",function(){if(!q.keyboardAction){q.keyboardAction=true;b(document).bind("keydown",function(s){var u=s.keyCode;q.currentKey=u;if(u==39||u==40){s.preventDefault();s.stopPropagation();L();x()}if(u==37||u==38){s.preventDefault();s.stopPropagation();M();x()}})}});b("#"+f).bind("mouseout",function(){y(false);
b(document).unbind("keydown");q.keyboardAction=false;q.currentKey=null});b("#"+d).bind("click",function(){y(false);if(b("#"+f+":visible").length==1)b("#"+f).unbind("mouseover");else{b("#"+f).bind("mouseover",function(){y(true)});k.open()}});b("#"+d).bind("mouseout",function(){y(false)});l.showIcon&&l.useSprite!=false&&E()},t=function(a){for(var c in m)if(m[c].index==a)return m[c];return-1},J=function(a){var c=h("postChildID");if(b("#"+c+" a."+g.selected).length==1)A=b("#"+c+" a."+g.selected).text();
r||b("#"+c+" a."+g.selected).removeClass(g.selected);var d=b("#"+c+" a."+g.selected).prop("id");if(d!=undefined)var f=q.oldIndex==undefined||q.oldIndex==null?m[d].index:q.oldIndex;a&&!r&&b(a).addClass(g.selected);if(r){d=q.currentKey;if(b("#"+e).prop("multiple")==true)if(d==17){q.oldIndex=m[b(a).prop("id")].index;b(a).toggleClass(g.selected)}else if(d==16){b("#"+c+" a."+g.selected).removeClass(g.selected);b(a).addClass(g.selected);a=b(a).prop("id");a=m[a].index;for(c=Math.min(f,a);c<=Math.max(f,a);c++)b("#"+
t(c).id).addClass(g.selected)}else{b("#"+c+" a."+g.selected).removeClass(g.selected);b(a).addClass(g.selected);q.oldIndex=m[b(a).prop("id")].index}else{b("#"+c+" a."+g.selected).removeClass(g.selected);b(a).addClass(g.selected);q.oldIndex=m[b(a).prop("id")].index}}},aa=function(a){j(a).refresh=function(){b("#"+a).msDropDown(l)}},y=function(a){q.insideWindow=a},da=function(){return q.insideWindow},ba=function(){for(var a=h("postID"),c=S.actions.split(","),d=0;d<c.length;d++){var f=c[d];if(z(f)==true)switch(f){case "focus":b("#"+
a).bind("mouseenter",function(){j(e).focus()});break;case "click":b("#"+a).bind("click",function(){b("#"+e).trigger("click")});break;case "dblclick":b("#"+a).bind("dblclick",function(){b("#"+e).trigger("dblclick")});break;case "mousedown":b("#"+a).bind("mousedown",function(){b("#"+e).trigger("mousedown")});break;case "mouseup":b("#"+a).bind("mouseup",function(){b("#"+e).trigger("mouseup")});break;case "mouseover":b("#"+a).bind("mouseover",function(){b("#"+e).trigger("mouseover")});break;case "mousemove":b("#"+
a).bind("mousemove",function(){b("#"+e).trigger("mousemove")});break;case "mouseout":b("#"+a).bind("mouseout",function(){b("#"+e).trigger("mouseout")});break}}},$=function(){var a=h("postElementHolder");b("#"+e).after("<div class='"+g.ddOutOfVision+"' style='height:0px;overflow:hidden;position:absolute;' id='"+a+"'></div>");b("#"+e).appendTo(b("#"+a))},w=function(a){var c=h("postTitleTextID");b("#"+c).html(a)},N=function(a){var c=h("postChildID"),d=b("#"+c+" a:visible"),f=d.length,i=b("#"+c+" a:visible").index(b("#"+
c+" a.selected:visible")),n;switch(a){case "next":if(i<f-1){i++;n=d[i]}break;case "previous":if(i<f&&i>0){i--;n=d[i]}break}if(typeof n=="undefined")return false;b("#"+c+" a."+g.selected).removeClass(g.selected);b(n).addClass(g.selected);d=n.id;if(!r){f=l.showIcon==false?m[d].text:b("#"+d).html();w(f);E(m[d].index)}if(a=="next")parseInt(b("#"+d).position().top+b("#"+d).height())>=parseInt(b("#"+c).height())&&b("#"+c).scrollTop(b("#"+c).scrollTop()+b("#"+d).height()+b("#"+d).height());else parseInt(b("#"+
d).position().top+b("#"+d).height())<=0&&b("#"+c).scrollTop(b("#"+c).scrollTop()-b("#"+c).height()-b("#"+d).height())},L=function(){N("next")},M=function(){N("previous")},E=function(a){if(l.useSprite!=false){var c=h("postTitleTextID");a=typeof a=="undefined"?j(e).selectedIndex:a;a=j(e).options[a].className;if(a.length>0){var d=h("postChildID"),f=b("#"+d+" a."+a).prop("id");a=b("#"+f).css("background-image");d=b("#"+f).css("background-position");f=b("#"+f).css("padding-left");a!=undefined&&b("#"+c).find("."+
g.ddTitleText).attr("style","background:"+a);d!=undefined&&b("#"+c).find("."+g.ddTitleText).css("background-position",d);f!=undefined&&b("#"+c).find("."+g.ddTitleText).css("padding-left",f);b("#"+c).find("."+g.ddTitleText).css("background-repeat","no-repeat");b("#"+c).find("."+g.ddTitleText).css("padding-bottom","2px")}}},x=function(){var a=h("postChildID"),c=b("#"+a+" a."+g.selected);if(c.length==1){b("#"+a+" a."+g.selected).text();var d=b("#"+a+" a."+g.selected).prop("id");if(d!=undefined)j(e).selectedIndex=
m[d].index;l.showIcon&&l.useSprite!=false&&E()}else if(c.length>1)for(a=0;a<c.length;a++){d=b(c[a]).prop("id");d=m[d].index;j(e).options[d].selected="selected"}c=j(e).selectedIndex;k.ddProp.selectedIndex=c},z=function(a){if(b("#"+e).prop("on"+a)!=undefined)return true;var c=b("#"+e).data("events");if(c&&c[a])return true;return false},ea=function(){var a=h("postChildID");if(z("change")==true){a=m[b("#"+a+" a.selected").prop("id")].text;b.trim(A)!==b.trim(a)&&A!==""&&b("#"+e).trigger("change")}z("mouseup")==
true&&b("#"+e).trigger("mouseup");z("blur")==true&&b(document).bind("mouseup",function(){b("#"+e).focus();b("#"+e)[0].blur();x();b(document).unbind("mouseup")})},K=function(a){var c=h("postArrowID");a==1?b("#"+c).css({backgroundPosition:"0 100%"}):b("#"+c).css({backgroundPosition:"0 0"})},fa=function(){for(var a in j(e))typeof j(e)[a]!="function"&&j(e)[a]!==undefined&&j(e)[a]!==null&&k.set(a,j(e)[a],true)},ga=function(a,c){if(t(c)!=-1){j(e)[a]=c;a=h("postChildID");b("#"+a+" a."+g.selected).removeClass(g.selected);
b("#"+t(c).id).addClass(g.selected);c=t(j(e).selectedIndex).html;w(c)}},ha=function(a,c){if(c=="d")for(var d in m)if(m[d].index==a){delete m[d];break}a=0;for(d in m){m[d].index=a;a++}},H=function(){var a=h("postChildID"),c=h("postID"),d=b("#"+c).position(),f=b("#"+c).height(),i=b(window).height(),n=b(window).scrollTop();c=b("#"+a).height();var o={zIndex:l.zIndex,top:d.top+f+"px",display:"none"},s=l.animStyle,u=false,O=g.noBorderTop;b("#"+a).removeClass(g.noBorderTop);b("#"+a).removeClass(g.borderTop);
if(i+n<Math.floor(c+f+d.top)){a=d.top-c;if(d.top-c<0)a=10;o={zIndex:l.zIndex,top:a+"px",display:"none"};s="show";u=true;O=g.borderTop}return{opp:u,ani:s,css:o,border:O}},P=function(){k.onActions.onOpen!=null&&eval(k.onActions.onOpen)(k)},Q=function(){ea();k.onActions.onClose!=null&&eval(k.onActions.onClose)(k)};this.open=function(){if(!(k.get("disabled",true)==true||k.get("options",true).length==0)){var a=h("postChildID");if(v!=""&&a!=v){b("#"+v).slideUp("fast");b("#"+v).css({zIndex:"0"})}if(b("#"+
a).css("display")=="none"){A=m[b("#"+a+" a.selected").prop("id")].text;var c="";C=b("#"+a).height();b("#"+a+" a").show();b(document).bind("keydown",function(f){var i=f.keyCode;if(i==8){f.preventDefault();f.stopPropagation();c=c.length==0?"":c.substr(0,c.length-1)}switch(i){case 39:case 40:f.preventDefault();f.stopPropagation();L();break;case 37:case 38:f.preventDefault();f.stopPropagation();M();break;case 27:case 13:k.close();x();break;default:if(i>46)c+=String.fromCharCode(i);f=W(c);if(f!=-1){b("#"+
a).css({height:"auto"});b("#"+a+" a").hide();b(f).show();f=H();b("#"+a).css(f.css);b("#"+a).css({display:"block"})}else{b("#"+a+" a").show();b("#"+a).css({height:C+"px"})}break}z("keydown")==true&&j(e).onkeydown()});b(document).bind("keyup",function(){b("#"+e).prop("onkeyup")!=undefined&&j(e).onkeyup()});b(document).bind("mouseup",function(){da()==false&&k.close()});var d=H();b("#"+a).css(d.css);if(d.opp==true){b("#"+a).css({display:"block"});b("#"+a).addClass(d.border);P()}else b("#"+a)[d.ani]("fast",
function(){b("#"+a).addClass(d.border);P()});if(a!=v)v=a}}};this.close=function(){var a=h("postChildID"),c=b("#"+h("postTitleID")).position().top,d=H();T=false;d.opp==true?b("#"+a).animate({height:0,top:c},function(){b("#"+a).css({height:C+"px",display:"none"});Q()}):b("#"+a).slideUp("fast",function(){Q();b("#"+a).css({zIndex:"0"});b("#"+a).css({height:C+"px"})});E();b(document).unbind("keydown");b(document).unbind("keyup");b(document).unbind("mouseup")};this.selectedIndex=function(a){if(typeof a==
"undefined")return k.get("selectedIndex");else k.set("selectedIndex",a)};this.debug=function(a){typeof a=="undefined"||a==true?b("."+g.ddOutOfVision).removeAttr("style"):b("."+g.ddOutOfVision).attr("style","height:0px;overflow:hidden;position:absolute")};this.set=function(a,c,d){if(a==undefined||c==undefined)throw{message:"set to what?"};k.ddProp[a]=c;if(d!=true)switch(a){case "selectedIndex":ga(a,c);break;case "disabled":k.disabled(c,true);break;case "multiple":j(e)[a]=c;if(r=b(p).prop("size")>0||
b(p).prop("multiple")==true?true:false){a=b("#"+e).height();c=h("postChildID");b("#"+c).css("height",a+"px");a=h("postTitleID");b("#"+a).hide();c=h("postChildID");b("#"+c).css({display:"block",position:"relative"});G()}break;case "size":j(e)[a]=c;if(c==0)j(e).multiple=false;r=b(p).prop("size")>0||b(p).prop("multiple")==true?true:false;if(c==0){a=h("postTitleID");b("#"+a).show();c=h("postChildID");b("#"+c).css({display:"none",position:"absolute"});a="";if(j(e).selectedIndex>=0){c=t(j(e).selectedIndex);
a=c.html;J(b("#"+c.id))}w(a)}else{a=h("postTitleID");b("#"+a).hide();c=h("postChildID");b("#"+c).css({display:"block",position:"relative"})}break;default:try{j(e)[a]=c}catch(f){}break}};this.get=function(a,c){if(a==undefined&&c==undefined)return k.ddProp;if(a!=undefined&&c==undefined)return k.ddProp[a]!=undefined?k.ddProp[a]:null;if(a!=undefined&&c!=undefined)return j(e)[a]};this.visible=function(a){var c=h("postID");if(a==true)b("#"+c).show();else if(a==false)b("#"+c).hide();else return b("#"+c).css("display")};
this.add=function(a,c){var d=a.text,f=a.value==undefined||a.value==null?d:a.value;a=a.title==undefined||a.title==null?"":a.title;c=c==undefined||c==null?j(e).options.length:c;j(e).options[c]=new Option(d,f);if(a!="")j(e).options[c].title=a;d=t(c);if(d!=-1){f=D(j(e).options[c],c,"","");b("#"+d.id).html(f)}else{f=D(j(e).options[c],c,"","");d=h("postChildID");b("#"+d).append(f);G()}};this.remove=function(a){j(e).remove(a);if(t(a)!=-1){b("#"+t(a).id).remove();ha(a,"d")}if(j(e).length==0)w("");else{a=
t(j(e).selectedIndex).html;w(a)}k.set("selectedIndex",j(e).selectedIndex)};this.disabled=function(a,c){j(e).disabled=a;var d=h("postID");if(a==true){b("#"+d).css("opacity",g.disabled);k.close()}else a==false&&b("#"+d).css("opacity",1);c!=true&&k.set("disabled",a)};this.form=function(){return j(e).form==undefined?null:j(e).form};this.item=function(){if(arguments.length==1)return j(e).item(arguments[0]);else if(arguments.length==2)return j(e).item(arguments[0],arguments[1]);else throw{message:"An index is required!"};
};this.namedItem=function(a){return j(e).namedItem(a)};this.multiple=function(a){if(typeof a=="undefined")return k.get("multiple");else k.set("multiple",a)};this.size=function(a){if(typeof a=="undefined")return k.get("size");else k.set("size",a)};this.addMyEvent=function(a,c){k.onActions[a]=c};this.fireEvent=function(a){eval(k.onActions[a])(k)};var ia=function(){k.set("version",b.msDropDown.version);k.set("author",b.msDropDown.author)};(function(){ca();fa();ia();l.onInit!=""&&eval(l.onInit)(k)})()};
b.msDropDown={version:2.37,author:"Marghoob Suleman",counter:20,create:function(p,l){return b(p).msDropDown(l).data("dd")}};b.fn.extend({msDropDown:function(p){return this.each(function(){var l=new ja(this,p);b(this).data("dd",l)})}});if(typeof b.fn.prop=="undefined")b.fn.prop=function(p){return b(this).attr(p)}})(jQuery);
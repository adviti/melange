(function(a){a.jgrid.extend({getColProp:function(e){var b={},c=this[0];if(!c.grid)return false;c=c.p.colModel;for(var g=0;g<c.length;g++)if(c[g].name==e){b=c[g];break}return b},setColProp:function(e,b){return this.each(function(){if(this.grid)if(b)for(var c=this.p.colModel,g=0;g<c.length;g++)if(c[g].name==e){a.extend(this.p.colModel[g],b);break}})},sortGrid:function(e,b,c){return this.each(function(){var g=this,p=-1;if(g.grid){if(!e)e=g.p.sortname;for(var k=0;k<g.p.colModel.length;k++)if(g.p.colModel[k].index==
e||g.p.colModel[k].name==e){p=k;break}if(p!=-1){k=g.p.colModel[p].sortable;if(typeof k!=="boolean")k=true;if(typeof b!=="boolean")b=false;k&&g.sortData("jqgh_"+g.p.id+"_"+e,p,b,c)}}})},GridDestroy:function(){return this.each(function(){if(this.grid){this.p.pager&&a(this.p.pager).remove();var e=this.id;try{a("#gbox_"+e).remove()}catch(b){}}})},GridUnload:function(){return this.each(function(){if(this.grid){var e={id:a(this).attr("id"),cl:a(this).attr("class")};this.p.pager&&a(this.p.pager).empty().removeClass("ui-state-default ui-jqgrid-pager corner-bottom");
var b=document.createElement("table");a(b).attr({id:e.id});b.className=e.cl;e=this.id;a(b).removeClass("ui-jqgrid-btable");if(a(this.p.pager).parents("#gbox_"+e).length===1){a(b).insertBefore("#gbox_"+e).show();a(this.p.pager).insertBefore("#gbox_"+e)}else a(b).insertBefore("#gbox_"+e).show();a("#gbox_"+e).remove()}})},setGridState:function(e){return this.each(function(){if(this.grid){var b=this;if(e=="hidden"){a(".ui-jqgrid-bdiv, .ui-jqgrid-hdiv","#gview_"+b.p.id).slideUp("fast");b.p.pager&&a(b.p.pager).slideUp("fast");
b.p.toppager&&a(b.p.toppager).slideUp("fast");if(b.p.toolbar[0]===true){b.p.toolbar[1]=="both"&&a(b.grid.ubDiv).slideUp("fast");a(b.grid.uDiv).slideUp("fast")}b.p.footerrow&&a(".ui-jqgrid-sdiv","#gbox_"+b.p.id).slideUp("fast");a(".ui-jqgrid-titlebar-close span",b.grid.cDiv).removeClass("ui-icon-circle-triangle-n").addClass("ui-icon-circle-triangle-s");b.p.gridstate="hidden"}else if(e=="visible"){a(".ui-jqgrid-hdiv, .ui-jqgrid-bdiv","#gview_"+b.p.id).slideDown("fast");b.p.pager&&a(b.p.pager).slideDown("fast");
b.p.toppager&&a(b.p.toppager).slideDown("fast");if(b.p.toolbar[0]===true){b.p.toolbar[1]=="both"&&a(b.grid.ubDiv).slideDown("fast");a(b.grid.uDiv).slideDown("fast")}b.p.footerrow&&a(".ui-jqgrid-sdiv","#gbox_"+b.p.id).slideDown("fast");a(".ui-jqgrid-titlebar-close span",b.grid.cDiv).removeClass("ui-icon-circle-triangle-s").addClass("ui-icon-circle-triangle-n");b.p.gridstate="visible"}}})},filterToolbar:function(e){e=a.extend({autosearch:true,searchOnEnter:true,beforeSearch:null,afterSearch:null,beforeClear:null,
afterClear:null,searchurl:"",stringResult:false,groupOp:"AND",defaultSearch:"bw"},e||{});return this.each(function(){function b(d,h){var j=a(d);j[0]&&jQuery.each(h,function(){this.data!==undefined?j.bind(this.type,this.data,this.fn):j.bind(this.type,this.fn)})}var c=this;if(!this.ftoolbar){var g=function(){var d={},h=0,j,f,i={},n;a.each(c.p.colModel,function(){f=this.index||this.name;switch(this.stype){case "select":n=this.searchoptions&&this.searchoptions.sopt?this.searchoptions.sopt[0]:"eq";if(j=
a("#gs_"+a.jgrid.jqID(this.name),c.grid.hDiv).val()){d[f]=j;i[f]=n;h++}else try{delete c.p.postData[f]}catch(r){}break;case "text":n=this.searchoptions&&this.searchoptions.sopt?this.searchoptions.sopt[0]:e.defaultSearch;if(j=a("#gs_"+a.jgrid.jqID(this.name),c.grid.hDiv).val()){d[f]=j;i[f]=n;h++}else try{delete c.p.postData[f]}catch(u){}break}});var o=h>0?true:false;if(e.stringResult===true||c.p.datatype=="local"){var l='{"groupOp":"'+e.groupOp+'","rules":[',t=0;a.each(d,function(r,u){if(t>0)l+=",";
l+='{"field":"'+r+'",';l+='"op":"'+i[r]+'",';u+="";l+='"data":"'+u.replace(/\\/g,"\\\\").replace(/\"/g,'\\"')+'"}';t++});l+="]}";a.extend(c.p.postData,{filters:l});a.each(["searchField","searchString","searchOper"],function(r,u){c.p.postData.hasOwnProperty(u)&&delete c.p.postData[u]})}else a.extend(c.p.postData,d);var m;if(c.p.searchurl){m=c.p.url;a(c).jqGrid("setGridParam",{url:c.p.searchurl})}var q=false;if(a.isFunction(e.beforeSearch))q=e.beforeSearch.call(c);q||a(c).jqGrid("setGridParam",{search:o}).trigger("reloadGrid",
[{page:1}]);m&&a(c).jqGrid("setGridParam",{url:m});a.isFunction(e.afterSearch)&&e.afterSearch()},p=a("<tr class='ui-search-toolbar' role='rowheader'></tr>"),k;a.each(c.p.colModel,function(){var d=this,h,j,f,i;j=a("<th role='columnheader' class='ui-state-default ui-th-column ui-th-"+c.p.direction+"'></th>");h=a("<div style='width:100%;position:relative;height:100%;padding-right:0.3em;'></div>");this.hidden===true&&a(j).css("display","none");this.search=this.search===false?false:true;if(typeof this.stype==
"undefined")this.stype="text";f=a.extend({},this.searchoptions||{});if(this.search)switch(this.stype){case "select":if(i=this.surl||f.dataUrl)a.ajax(a.extend({url:i,dataType:"html",success:function(m){if(f.buildSelect!==undefined)(m=f.buildSelect(m))&&a(h).append(m);else a(h).append(m);f.defaultValue&&a("select",h).val(f.defaultValue);a("select",h).attr({name:d.index||d.name,id:"gs_"+d.name});f.attr&&a("select",h).attr(f.attr);a("select",h).css({width:"100%"});f.dataInit!==undefined&&f.dataInit(a("select",
h)[0]);f.dataEvents!==undefined&&b(a("select",h)[0],f.dataEvents);e.autosearch===true&&a("select",h).change(function(){g();return false});m=null}},a.jgrid.ajaxOptions,c.p.ajaxSelectOptions||{}));else{var n;if(d.searchoptions&&d.searchoptions.value)n=d.searchoptions.value;else if(d.editoptions&&d.editoptions.value)n=d.editoptions.value;if(n){i=document.createElement("select");i.style.width="100%";a(i).attr({name:d.index||d.name,id:"gs_"+d.name});var o,l;if(typeof n==="string"){n=n.split(";");for(var t=
0;t<n.length;t++){o=n[t].split(":");l=document.createElement("option");l.value=o[0];l.innerHTML=o[1];i.appendChild(l)}}else if(typeof n==="object")for(o in n)if(n.hasOwnProperty(o)){l=document.createElement("option");l.value=o;l.innerHTML=n[o];i.appendChild(l)}f.defaultValue&&a(i).val(f.defaultValue);f.attr&&a(i).attr(f.attr);f.dataInit!==undefined&&f.dataInit(i);f.dataEvents!==undefined&&b(i,f.dataEvents);a(h).append(i);e.autosearch===true&&a(i).change(function(){g();return false})}}break;case "text":i=
f.defaultValue?f.defaultValue:"";a(h).append("<input type='text' style='width:95%;padding:0px;' name='"+(d.index||d.name)+"' id='gs_"+d.name+"' value='"+i+"'/>");f.attr&&a("input",h).attr(f.attr);f.dataInit!==undefined&&f.dataInit(a("input",h)[0]);f.dataEvents!==undefined&&b(a("input",h)[0],f.dataEvents);if(e.autosearch===true)e.searchOnEnter?a("input",h).keypress(function(m){if((m.charCode?m.charCode:m.keyCode?m.keyCode:0)==13){g();return false}return this}):a("input",h).keydown(function(m){switch(m.which){case 13:return false;
case 9:case 16:case 37:case 38:case 39:case 40:case 27:break;default:k&&clearTimeout(k);k=setTimeout(function(){g()},500)}});break}a(j).append(h);a(p).append(j)});a("table thead",c.grid.hDiv).append(p);this.ftoolbar=true;this.triggerToolbar=g;this.clearToolbar=function(d){var h={},j,f=0,i;d=typeof d!="boolean"?true:d;a.each(c.p.colModel,function(){j=this.searchoptions&&this.searchoptions.defaultValue?this.searchoptions.defaultValue:"";i=this.index||this.name;switch(this.stype){case "select":var q;
a("#gs_"+a.jgrid.jqID(i)+" option",c.grid.hDiv).each(function(s){if(s===0)this.selected=true;if(a(this).text()==j){this.selected=true;q=a(this).val();return false}});if(q){h[i]=q;f++}else try{delete c.p.postData[i]}catch(r){}break;case "text":a("#gs_"+a.jgrid.jqID(i),c.grid.hDiv).val(j);if(j){h[i]=j;f++}else try{delete c.p.postData[i]}catch(u){}break}});var n=f>0?true:false;if(e.stringResult===true||c.p.datatype=="local"){var o='{"groupOp":"'+e.groupOp+'","rules":[',l=0;a.each(h,function(q,r){if(l>
0)o+=",";o+='{"field":"'+q+'",';o+='"op":"eq",';r+="";o+='"data":"'+r.replace(/\\/g,"\\\\").replace(/\"/g,'\\"')+'"}';l++});o+="]}";a.extend(c.p.postData,{filters:o});a.each(["searchField","searchString","searchOper"],function(q,r){c.p.postData.hasOwnProperty(r)&&delete c.p.postData[r]})}else a.extend(c.p.postData,h);var t;if(c.p.searchurl){t=c.p.url;a(c).jqGrid("setGridParam",{url:c.p.searchurl})}var m=false;if(a.isFunction(e.beforeClear))m=e.beforeClear.call(c);m||d&&a(c).jqGrid("setGridParam",
{search:n}).trigger("reloadGrid",[{page:1}]);t&&a(c).jqGrid("setGridParam",{url:t});a.isFunction(e.afterClear)&&e.afterClear()};this.toggleToolbar=function(){var d=a("tr.ui-search-toolbar",c.grid.hDiv);d.css("display")=="none"?d.show():d.hide()}}})},destroyGroupHeader:function(e){if(typeof e=="undefined")e=true;return this.each(function(){var b=this,c,g,p,k,d,h;g=b.grid;var j=a("table.ui-jqgrid-htable thead",g.hDiv),f=b.p.colModel;if(g){c=a("<tr>",{role:"rowheader"}).addClass("ui-jqgrid-labels");
k=g.headers;g=0;for(p=k.length;g<p;g++){d=f[g].hidden?"none":"";d=a(k[g].el).width(k[g].width).removeAttr("rowSpan").css("display",d);c.append(d);h=d.children("span.ui-jqgrid-resize");if(h.length>0)h[0].style.height="";d.children("div")[0].style.top=""}a(j).children("tr.ui-jqgrid-labels").remove();a(j).prepend(c);e===true&&a(b).jqGrid("setGridParam",{groupHeader:null})}})},setGroupHeaders:function(e){e=a.extend({useColSpanStyle:false,groupHeaders:[]},e||{});return this.each(function(){this.p.groupHeader=
e;var b=this,c,g,p=0,k,d,h,j,f,i=b.p.colModel,n=i.length,o=b.grid.headers,l=a("table.ui-jqgrid-htable",b.grid.hDiv),t=l.children("thead").children("tr.ui-jqgrid-labels:last").addClass("jqg-second-row-header");k=l.children("thead");var m,q=l.find(".jqg-first-row-header");if(q.html()===null)q=a("<tr>",{role:"row","aria-hidden":"true"}).addClass("jqg-first-row-header").css("height","auto");else q.empty();var r,u=function(s,v){for(var w=0,x=v.length;w<x;w++)if(v[w].startColumnName===s)return w;return-1};
a(b).prepend(k);k=a("<tr>",{role:"rowheader"}).addClass("ui-jqgrid-labels jqg-third-row-header");for(c=0;c<n;c++){h=o[c].el;j=a(h);g=i[c];d={height:"0px",width:o[c].width+"px",display:g.hidden?"none":""};a("<th>",{role:"gridcell"}).css(d).addClass("ui-first-th-"+b.p.direction).appendTo(q);h.style.width="";d=u(g.name,e.groupHeaders);if(d>=0){d=e.groupHeaders[d];p=d.numberOfColumns;f=d.titleText;for(d=g=0;d<p&&c+d<n;d++)i[c+d].hidden||g++;d=a("<th>",{colspan:String(g),role:"columnheader"}).addClass("ui-state-default ui-th-column-header ui-th-"+
b.p.direction).css({height:"22px","border-top":"0px none"}).html(f);b.p.headertitles&&d.attr("title",d.text());g===0&&d.hide();j.before(d);k.append(h);p=p-1}else if(p===0)if(e.useColSpanStyle)j.attr("rowspan","2");else{a("<th>",{role:"columnheader"}).addClass("ui-state-default ui-th-column-header ui-th-"+b.p.direction).css({display:g.hidden?"none":"","border-top":"0px none"}).insertBefore(j);k.append(h)}else{k.append(h);p--}}i=a(b).children("thead");i.prepend(q);k.insertAfter(t);l.append(i);if(e.useColSpanStyle){l.find("span.ui-jqgrid-resize").each(function(){var s=
a(this).parent();if(s.is(":visible"))this.style.cssText="height: "+s.height()+"px !important; cursor: col-resize;"});l.find("div.ui-jqgrid-sortable").each(function(){var s=a(this),v=s.parent();v.is(":visible")&&s.css("top",(v.height()-s.outerHeight())/2+"px")})}if(a.isFunction(b.p.resizeStop))m=b.p.resizeStop;r=i.find("tr.jqg-first-row-header");b.p.resizeStop=function(s,v){r.find("th").eq(v).width(s);a.isFunction(m)&&m.call(b,s,v)}})}})})(jQuery);
(function(a){a.fn.formbuilder=function(t){var d=a.extend({save_url:false,load_url:false,control_box_target:false,useJson:true,serialize_prefix:"frmb",options_wrap_class:"options-wrap",messages:{save:"Save",add_new_field:"Add New Field...",text:"Text Field",title:"Title",paragraph:"Paragraph",checkboxes:"Checkboxes",radio:"Radio",select:"Select List",text_field:"Text Field",label:"Label",paragraph_field:"Paragraph Field",select_options:"Select Options",add:"Add",checkbox_group:"Checkbox Group",remove_message:"Are you sure you want to remove this element?",
remove:"X",radio_group:"Radio Group",selections_message:"Allow Multiple Selections",hide:"Hide",required:"Required",show:"Show",other:"Include other option"}},t),o="frmb-"+a("ul[id^=frmb-]").length++;return this.each(function(){var n=a(this).append('<ul id="'+o+'" class="frmb"></ul>').find("ul"),b="",l="",j=1,m;a(n).addClass(o);(function(g){var e="",c="",f="",h=o+"-control-box",k=o+"-save-button";e+='<option value="0">'+d.messages.add_new_field+"</option>";e+='<option value="input_text">'+d.messages.text+
"</option>";e+='<option value="textarea">'+d.messages.paragraph+"</option>";e+='<option value="checkbox">'+d.messages.checkboxes+"</option>";e+='<option value="radio">'+d.messages.radio+"</option>";c='<select id="'+h+'" class="frmb-control">'+e+"</select>";f='<input type="submit" id="'+k+'" class="frmb-submit" value="'+d.messages.save+'"/>';g?a(g).append(c):a(n).before(c);a(n).after(f);a("#"+k).click(function(){a("#schema").attr("value",JSON.stringify(a(n).serializeFormList()));a("#form").submit();
return true});a("#"+h).change(function(){var p="frm-t"+(new Date).getTime().toString()+"-item";v(p,a(this).val());a(this).val(0).blur();a("body").animate({scrollTop:a("#"+p).offset().top},500);return false})})(d.control_box_target);var x=function(g){var e="",c=false;a(g[0]).each(function(){var f=g[1][this.valueOf()];if(f.field_type==="input_text")c=[f.label];if(f.field_type==="textarea")c=[f.label];else if(f.field_type==="checkbox"){c=[f.label,f.other];e=[];a.each(f.values,function(){e.push([this.value,
this.checked])})}else if(f.field_type==="radio"){c=[f.label,f.other];e=[];a.each(f.values,function(){e.push([this.value,this.checked])})}else if(f.field_type==="select"){c=[f.label,f.multiple,f.other];e=[];a.each(f.values,function(){e.push([this.value,this.checked])})}else e=[f.values];v(this,f.field_type,e,c,f.required)})},v=function(g,e,c,f,h){b="";l=e;if(typeof c==="undefined")c="";switch(e){case "input_text":y(g,c,f,h);break;case "textarea":z(g,c,f,h);break;case "checkbox":A(g,c,f,h);break;case "radio":B(g,
c,f,h);break;case "select":C(g,c,f,h);break}},y=function(g,e,c,f){e="";if(typeof c==="object")e=c[0];b+="<label>"+d.messages.label+"</label>";b+='<input class="fld-label" id="label-'+j+'" type="text" value="'+unescape(e)+'" />';m="";q(g,d.messages.text,b,f,{required:false,value:false},m)},z=function(g,e,c,f){e="";if(typeof c==="object")e=c[0];b+="<label>"+d.messages.label+"</label>";b+='<input type="text" value="'+unescape(e)+'" />';m="";q(g,d.messages.paragraph_field,b,f,{required:false,value:false},
m)},A=function(g,e,c,f){var h="",k=false;if(c)k=c[1];k={required:true,value:k};if(typeof c==="object")h=c[0];b+='<div class="chk_group">';b+='<div class="frm-fld"><label>'+d.messages.label+"</label>";b+='<input type="text" name="label" value="'+unescape(h)+'" /></div>';b+='<div class="false-label">'+d.messages.select_options+"</div>";b+='<div class="fields '+d.options_wrap_class+'">';if(typeof e==="object")for(i=0;i<e.length;i++)b+=r(e[i]);else b+=r("");b+='<div class="add-area"><a href="#" class="add add_ck">'+
d.messages.add+"</a></div>";b+="</div>";b+="</div>";m="";q(g,d.messages.checkbox_group,b,f,k,m)},r=function(g){var e=false,c="";if(typeof g==="object"){c=g[0];e=g[1]===true||g[1]==="true"?true:false}b="";b+="<div>";b+='<input type="checkbox"'+(e?' checked="checked"':"")+" />";b+='<input type="text" value="'+unescape(c)+'" />';b+='<a href="#" class="remove" title="'+d.messages.remove_message+'">'+d.messages.remove+"</a>";b+="</div>";return b},B=function(g,e,c,f){var h="",k=false;if(c)k=c[1];k={required:true,
value:k};if(typeof c==="object")h=c[0];b+='<div class="rd_group">';b+='<div class="frm-fld"><label>'+d.messages.label+"</label>";b+='<input type="text" name="label" value="'+unescape(h)+'" /></div>';b+='<div class="false-label">'+d.messages.select_options+"</div>";b+='<div class="fields '+d.options_wrap_class+'">';if(typeof e==="object")for(i=0;i<e.length;i++)b+=s(e[i],"frm-"+j+"-fld");else b+=s("","frm-"+j+"-fld");b+='<div class="add-area"><a href="#" class="add add_rd">'+d.messages.add+"</a></div>";
b+="</div>";b+="</div>";m="";q(g,d.messages.radio_group,b,f,k,m)},s=function(g,e){var c=false,f="";if(typeof g==="object"){f=g[0];c=g[1]===true||g[1]==="true"?true:false}b="";b+="<div>";b+='<input type="radio"'+(c?' checked="checked"':"")+' name="radio_'+e+'" />';b+='<input type="text" value="'+unescape(f)+'" />';b+='<a href="#" class="remove" title="'+d.messages.remove_message+'">'+d.messages.remove+"</a>";b+="</div>";return b},C=function(g,e,c,f){var h=false,k="",p=false;if(c)p=c[1];p={required:true,
value:p};if(typeof c==="object"){k=c[0];h=c[1]===true||c[1]==="true"?true:false}b+='<div class="opt_group">';b+='<div class="frm-fld"><label>'+d.messages.label+"</label>";b+='<input type="text" name="label" value="'+unescape(k)+'" /></div>';b+="";b+='<div class="false-label">'+d.messages.select_options+"</div>";b+='<div class="fields '+d.options_wrap_class+'">';b+='<input type="checkbox" name="multiple"'+(h?'checked="checked"':"")+">";b+='<label class="auto">'+d.messages.selections_message+"</label>";
if(typeof e==="object")for(i=0;i<e.length;i++)b+=u(e[i],h);else b+=u("",h);b+='<div class="add-area"><a href="#" class="add add_opt">'+d.messages.add+"</a></div>";b+="</div>";b+="</div>";m="";q(g,d.messages.select,b,f,p,m)},u=function(g,e){return e?r(g):s(g)},q=function(g,e,c,f,h){if(f)f=f===true?true:false;c="";c+='<li id="'+g+'" class="'+l+'">';c+='<div class="legend">';c+='<a id="frm-'+j+'" class="toggle-form" href="#">'+d.messages.hide+"</a> ";c+='<strong id="txt-label-'+j+'">'+e+"</strong></div>";
c+='<div id="frm-'+j+'-fld" class="frm-holder">';c+='<div class="frm-elements">';c+=b;c+='<div class="frm-fld frm-fld-req"><label for="required-'+j+'">'+d.messages.required+"</label>";c+='<input class="required" type="checkbox" value="1" name="required-'+j+'" id="required-'+j+'"'+(f?' checked="checked"':"")+" /></div>";if(h.required){c+='<div class="frm-fld frm-fld-other"><label for="other-'+j+'">'+d.messages.other+"</label>";c+='<input class="other" type="checkbox" value="1" name="other-'+j+'" id="other-'+
j+'"'+(h.value?' checked="checked"':"")+" /></div>"}c+='<a id="del_'+g+'" class="del-button delete-confirm" href="#" label="'+d.messages.remove_message+'"><span>Delete</span></a>';c+="</div>";c+="</div>";c+="</li>";a(n).append(c);a("#frm-"+j+"-item").hide();a("#frm-"+j+"-item").animate({opacity:"show",height:"show"},"slow");j++},w=a("#schema").attr("value");w&&x(JSON.parse(w));a(".remove").live("click",function(){a(this).parent("div").animate({opacity:"hide",height:"hide",marginBottom:"0px"},"fast",
function(){a(this).remove()});return false});a(".toggle-form").live("click",function(){var g=a(this).attr("id");if(a(this).html()===d.messages.hide){a(this).removeClass("open").addClass("closed").html(d.messages.show);a("#"+g+"-fld").animate({opacity:"hide",height:"hide"},"slow");return false}if(a(this).html()===d.messages.show){a(this).removeClass("closed").addClass("open").html(d.messages.hide);a("#"+g+"-fld").animate({opacity:"show",height:"show"},"slow");return false}return false});a(".delete-confirm").live("click",
function(){var g=a(this).attr("id").replace(/del_/,"");confirm(a(this).attr("label"))&&a("#"+g).animate({opacity:"hide",height:"hide",marginBottom:"0px"},"slow",function(){a(this).remove()});return false});a(".add_ck").live("click",function(){a(this).parent().before(r());return false});a(".add_opt").live("click",function(){a(this).parent().before(u("",false));return false});a(".add_rd").live("click",function(){a(this).parent().before(s(false,a(this).parents(".frm-holder").attr("id")));return false})})}})(jQuery);
(function(a){a.fn.serializeFormList=function(t){var d=a.extend({prepend:"ul",is_child:false,attributes:["class"],serialization_attributes:["field_type"]},t),o={},n=[];if(!d.is_child)d.prepend="&"+d.prepend;this.each(function(){a(this).children().each(function(){for(att in d.attributes){var b={};b[d.serialization_attributes[att]]=escape(a(this).attr(d.attributes[att]));if(d.attributes[att]=="class"){b.required=a("#"+a(this).attr("id")+" input.required").attr("checked");switch(a(this).attr(d.attributes[att])){case "input_text":b.label=
escape(a("#"+a(this).attr("id")+" input[type=text]").val());break;case "textarea":b.label=escape(a("#"+a(this).attr("id")+" input[type=text]").val());break;case "checkbox":b.other=a("#"+a(this).attr("id")+" input.other").attr("checked");b.values=[];a("#"+a(this).attr("id")+" input[type=text]").each(function(){if(a(this).attr("name")=="label")b.label=escape(a(this).val());else{var l={};l.value=escape(a(this).val());l.checked=a(this).prev().attr("checked");b.values.push(l)}});break;case "radio":b.other=
a("#"+a(this).attr("id")+" input.other").attr("checked");b.values=[];a("#"+a(this).attr("id")+" input[type=text]").each(function(){if(a(this).attr("name")=="label")b.label=escape(a(this).val());else{var l={};l.value=escape(a(this).val());l.checked=a(this).prev().attr("checked");b.values.push(l)}});break;case "select":b.other=a("#"+a(this).attr("id")+" input.other").attr("checked");b.multiple=a("#"+a(this).attr("id")+" input[name=multiple]").attr("checked");a("#"+a(this).attr("id")+" input[type=text]").each(function(){if(a(this).attr("name")==
"label")b.label=escape(a(this).val());else{var l={};l.value=escape(a(this).val());l.checked=a(this).prev().attr("checked");b.values.push(l)}});break}}o[a(this).attr("id")]=b;n.push(a(this).attr("id"))}})});return[n,o]}})(jQuery);

melange.templates.inherit(function(e,f){function c(){this.widget=jQuery(b.widget_template()).appendTo(b.container());this.deleteMe=function(d){d.data.widget.remove()};this.button_edit=this.widget.find(".button_edit");this.button_delete=this.widget.find(".button_delete");this.button_delete.bind("click",{widget:this.widget},this.deleteMe);this.widget.find(".message")[0].innerHTML=(new Date).getTime()}e={};var a={submit_button:function(){return"#form-register-fieldset-button-row"},container:function(){return"#survey_container"},
menu:{menu:function(){return[a.container(),".survey_menu"].join(" ")},buttons:{radio:function(){return[a.menu.menu(),".radio"].join(" ")},checkbox:function(){return[a.menu.menu(),".checkbox"].join(" ")},short_answer:function(){return[a.menu.menu(),".short_answer"].join(" ")},long_answer:function(){return[a.menu.menu(),".long_answer"].join(" ")}}},menu_template:function(){return"#survey_menu_template"},widget_template:function(){return"#survey_widget_template"}},b={submit_button:function(){return jQuery(a.submit_button())},
container:function(){return jQuery(a.container())},menu:{menu:function(){return jQuery(a.menu.menu())[0]},buttons:{radio:function(){return jQuery(a.menu.buttons.radio())},checkbox:function(){return jQuery(a.menu.buttons.checkbox())},short_answer:function(){return jQuery(a.menu.buttons.short_answer())},long_answer:function(){return jQuery(a.menu.buttons.long_answer())}}},menu_template:function(){return jQuery(a.menu_template())[0].innerHTML},widget_template:function(){return jQuery(a.widget_template())[0].innerHTML}},
g={menu:{buttons:{radio:function(){new c},checkbox:function(){new c},short_answer:function(){new c},long_answer:function(){new c}}}};b.container().insertBefore(b.submit_button()).removeClass("hidden");if(f.previous_content!==undefined)e=f.previous_content;(function(){jQuery(b.container()).append(b.menu_template());jQuery.each(b.menu.buttons,function(d,h){h().bind("click",g.menu.buttons[d])})})()});

(function(){if(window.melange===undefined)throw new Error("Melange not loaded");var f=window.melange;f.seeder=window.melange.seeder=function(){return new f.seeder};var c=f.logging.debugDecorator(f.seeder),e=null,j={name:"NewModel",parameters:{},Description:"KBLA"},k={name:"RelatedModels",parameters:{},Description:"KBLA"};f.error.createErrors([]);c.getData=function(a){jQuery.getJSON("/seeder/get_data",function(d){e=d;e.providers.ReferenceProperty.push(j);e.providers._ReverseReferenceProperty.push(k);
jQuery.each(e.models,function(b,g){jQuery.each(g.properties,function(h,i){i.providers=c.getProviders(i.type)})});a()})};c.getModels=function(){return e.models};c.getModel=function(a){result=null;jQuery.each(this.getModels(),function(d,b){if(b.name===a)result=b});return result};c.getModelChildren=function(a,d){if(d===undefined)d=0;model=c.getModel(a);model.level=d;var b=[model];a=jLinq.from(c.getModels(),"name").contains("parent",a).select();jQuery.each(a,function(g,h){g=c.getModelChildren(h.name,
d+1);b=b.concat(g)});return b};c.getProvidersData=function(){return e.providers};c.getProvidersList=function(){var a=[];jQuery.each(this.getProvidersData(),function(d,b){jQuery.each(b,function(g,h){a.push(h)})});return a};c.getProviders=function(a){return c.getProvidersData()[a]};c.getProvider=function(a){result=null;jQuery.each(this.getProvidersList(),function(d,b){if(b.name===a)result=b});return result};c.getProperties=function(a){for(var d=[],b=this.getModel(a);b!=undefined;){properties_data={name:a,
properties:b.properties};d.push(properties_data);a=b.parent;b=this.getModel(a)}return d};c.sendConfigurationSheet=function(a,d){json=JSON.stringify(a);jQuery.post("/seeder/seed",{xsrf_token:window.xsrf_token,data:json},d)}})();
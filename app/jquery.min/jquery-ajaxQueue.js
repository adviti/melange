(function(i){var f=i.ajax,h={},c=[],e=[];i.ajax=function(a){a=jQuery.extend(a,jQuery.extend({},jQuery.ajaxSettings,a));var g=a.port;switch(a.mode){case "abort":h[g]&&h[g].abort();return h[g]=f.apply(this,arguments);case "queue":var j=a.complete;a.complete=function(){j&&j.apply(this,arguments);jQuery([f]).dequeue("ajax"+g)};jQuery([f]).queue("ajax"+g,function(){f(a)});return;case "sync":var d=c.length;c[d]={error:a.error,success:a.success,complete:a.complete,done:false};e[d]={error:[],success:[],complete:[]};
a.error=function(){e[d].error=arguments};a.success=function(){e[d].success=arguments};a.complete=function(){e[d].complete=arguments;c[d].done=true;if(d==0||!c[d-1])for(var b=d;b<c.length&&c[b].done;b++){c[b].error&&c[b].error.apply(jQuery,e[b].error);c[b].success&&c[b].success.apply(jQuery,e[b].success);c[b].complete&&c[b].complete.apply(jQuery,e[b].complete);c[b]=null;e[b]=null}}}return f.apply(this,arguments)}})(jQuery);

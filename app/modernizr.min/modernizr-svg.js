window.Modernizr=function(e,c,g){function h(a,d){return typeof a===d}function m(a){n.cssText=a}e={};c.head||c.getElementsByTagName("head");var b=c.createElement("modernizr"),n=b.style,o=Object.prototype.toString,l={svg:"http://www.w3.org/2000/svg"};b={};var p=[],f,i={}.hasOwnProperty,j;!h(i,g)&&!h(i.call,g)?(j=function(a,d){return i.call(a,d)}):(j=function(a,d){return d in a&&h(a.constructor.prototype[d],g)});b.svg=function(){return!!c.createElementNS&&!!c.createElementNS(l.svg,"svg").createSVGRect};
b.svgclippaths=function(){return!!c.createElementNS&&/SVG/.test(o.call(c.createElementNS(l.svg,"clipPath")))};for(var k in b)j(b,k)&&(f=k.toLowerCase(),e[f]=b[k](),p.push((e[f]?"":"no-")+f));m("");b=null;e._version="2.0.6";return e}(this,this.document);

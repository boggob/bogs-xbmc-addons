// ==UserScript==
// @name		MusicBrainz: Import from Naxos
// @description		Import releases from Naxos
// @version		2012-04-15
// @author		-
// @namespace		df069240-fe79-11dc-95ff-0800200c9a66
//
// @include		http://naxos.com/catalogue/*
// @include		http://naxos.com/catalogue/item.asp
// @include		http://www.naxos.com/catalogue/item.asp
// @include		http://www.naxos.com/catalogue/*
// @include		www.naxos.com/catalogue/*
// @include		file:///c:/temp/a.html
// @require     http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.js
//
// ==/UserScript==
//**************************************************************************//
var myform = document.createElement("form");
myform.method="post";
myform.action = "http://musicbrainz.org/release/add";
myform.acceptCharset = "UTF-8";
mysubmit = document.createElement("input");
mysubmit.type = "submit";
mysubmit.value = "Add to MusicBrainz";
myform.appendChild(mysubmit);

var div = document.createElement("div");
div.style.top = 0;
div.style.right = 0;
div.style.padding = '10px';




var html = (function() {
  var ELEMENT = this.Node?Node.ELEMENT_NODE:1,
         TEXT = this.Node?Node.TEXT_NODE:   3;
  return function html(el, outer) {
    var i = 0, j = el.childNodes, k = outer?"<" + (m = el.nodeName.toLowerCase()) + attr(el) + ">":"",
        l = j.length, m, n;
    while(i !== l) switch((n = j[i++]).nodeType) {
      case ELEMENT: k += html(n, true); break;
      case TEXT:    k += n.nodeValue;
    } return k + (outer?"</" + m + ">":"");
  }; function attr(el) {
    var i = 0, j = el.attributes, k = new Array(l = j.length), l, m;
    while(i !== l) k[i] = (m = j[i++].nodeName) + "=\"" + el.getAttribute(m) + "\"";
    return (l?" ":"") + k.join(" ");
  }
})();

var artist_sort_order = function(artists) {
	return jQuery.map(
		artists, 
		function (artist) {
			return jQuery.map(
				artist.split(",").reverse(),
				function (s) {return s.trim();}
			).join(" ");
		}
	);
}


function text_node_to_text(node, includeWhitespaceNodes, strip) {
    var textNodes = [], whitespace = /^\s*$/;

    function getTextNodes(node) {
        if (node.nodeType == 3) {
            if (includeWhitespaceNodes || !whitespace.test(node.nodeValue)) {
				var zz= node.nodeValue;
				if (strip) {
					zz= zz.trim();
				}
                textNodes.push(zz);
            }
        } else {
            for (var i = 0, len = node.childNodes.length; i < len; ++i) {
                getTextNodes(node.childNodes[i]);
            }
        }
    }

    getTextNodes(node);
    return textNodes;
}


var naxos_headers = function(el) {
	var y = new Object();
	jQuery.each(jQuery("td.style5 > p"), function() {
		
		var z = text_node_to_text(this, false).join(' ').trim().replace( /\n/, '' ).split(":"); 
		console.log(z);

		y[z[0].trim()] = z[1].trim().split(" ; "); 
	});	  
	
	y['Composer(s)']	= artist_sort_order(y['Composer(s)']);
	y['Artist(s)']		= artist_sort_order(y['Artist(s)']);
	
	return y;
}

	

var naxos_works = function() {
	var works = new Array();
	jQuery("div.works").each(function(idx, para) {
		var work = new Object();
		work["work"]		= text_node_to_text(para, false).join(' ').trim().replace( /\n/, '' );
		work["composers"]	= jQuery(para).prevAll('p.composers').eq(0).find('a').map(function () {return artist_sort_order(text_node_to_text(this, true))}).get();
		work["performers"]	= jQuery(para).next('div.performers').find('td:has(>a)').map(
								function () {
									var xx = new Array(text_node_to_text(this, true));
									xx[0] = artist_sort_order(new Array(xx[0][0]));
									if (xx[0].length == 1) {
										xx[0].push("");
									} else {
										xx[0][1] = xx[0][1].replace(',',"").trim();
									}
									return xx;
								}
							).get();
		
		work["tracks"]	= jQuery(para).next('div.performers').nextUntil('div', 'table').map(function () {
			return new Array(jQuery(this).find('td').find('td').map(function () {return text_node_to_text(this,false,true)}).get());
		}).get();
		
		console.log(work);
		console.log("################################");

		works.push(work);
	});	  
	return works;
}

var  naxos_scrape_fn = function() {
	naxos_scrape = new Object();
	naxos_scrape['headers']	= naxos_headers();		
	naxos_scrape['title']	= jQuery("h1.cdtitle")[0].textContent.trim();		
	naxos_scrape['works']	= naxos_works();
	
	return naxos_scrape;
}


var  musicbrainz_add = function(scape)  {
	add_field("name", 						scape['title']);
	add_field("labels.0.name", 				scape['headers']['Label'][0]);
	add_field("barcode", 					scape['headers']['Barcode'][0]);
	add_field('labels.0.catalog_number',	scape['headers']['Catalogue No'][0]);
	add_field("date.year", 					scape['headers']['Physical Release'][0].split('/')[1]),
	add_field("date.month", 				scape['headers']['Physical Release'][0].split('/')[0]),
	
	add_field("language_id", 				"120");
	add_field("script_id", 					"28");
	add_field("status_id", 					"1");
	add_field("primary_type_id", 			"1");
	add_field("packaging_id", 				"1");
	
	
	var albumartist = scape["headers"]["Artist(s)"];
	for (var idx =0 ; idx < albumartist.length ; idx++) {
		add_field("artist_credit.names.%d.artist.name".replace('%d', idx), albumartist[idx]);
		if (idx + 1 < albumartist.length) {
			add_field("artist_credit.names.%d.join_phrase".replace('%d', idx), " & ");
		}
	}
	
	var medium = 0;
	add_field("mediums.%d.format_id".replace('%d', medium), '1');

	for (var trk = 0 ; trk < scape['works'].length; trk++) {
		var work = scape['works'][trk];
		for (var trkw = 0; trkw < work["tracks"].length ; trkw++) {
			var track = work["tracks"][trkw];
			
			console.log(track);
			console.log(track[0] + '0');
			var label = "mediums.%1.track.%2.%%s".replace('%1', medium).replace('%2', parseInt(track[0] + '0',10)-1);	
			
			var name;
			if (work["work"] == track[1]) {
				name = track[1];
			} else {
				name = work["work"] + ": " + track[1];
			}
			
			add_field(label.replace("%%s", 'name'), name );
			add_field(label.replace("%%s", 'length'), track[2]);
			
			if (work["composers"] != albumartist) {
				for (var perf = 0 ; perf < work["composers"].length ; perf++) {
					add_field(label.replace("%%s", 'artist_credit.names.%d.name'.replace('%d', perf)), work["composers"] [perf]);
					if (perf  + 1 < work["composers"].length) {
						add_field(label.replace("%%s", 'artist_credit.names.%d.join_phrase'.replace('%d', perf)), ' & ');
					}
				}
			}
		}
	}
	
	div.appendChild(myform);
	console.log(html(myform));
	$("td.style5").append(div); 
}


//////////////////////////////////////////////////////////////////////////////

function add_field (name, value) {
	var field = document.createElement("input");
	field.type = "hidden";
	field.name = name;
	field.value = value;
	console.log(new Array(name, value));
	myform.appendChild(field);
}

function callbackFunction() {
	console.log('Hello World!');	  
	var script = document.createElement('script');
	script.src = 'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js';
	document.getElementsByTagName('head')[0].appendChild(script);	
	
	var jQuery = unsafeWindow.jQuery;
	console.log('Hello World!');	  
	naxos_scrape = naxos_scrape_fn();
	console.log(naxos_scrape);	  
	musicbrainz_add(naxos_scrape);
	return 1;
};
callbackFunction();

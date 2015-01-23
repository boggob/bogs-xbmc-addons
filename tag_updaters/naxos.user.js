// ==UserScript==
// @name		MusicBrainz: Import from Naxos
// @description		Import releases from Naxos
// @version		2012-10-07
// @author		bog.gob
// @namespace		https://code.google.com/p/bogs-xbmc-addons/source/browse/trunk/tag_updaters/naxos.user.js
//
// @include		http://naxos.com/catalogue/*
// @include		http://naxos.com/catalogue/item.asp
// @include		http://www.naxos.com/catalogue/item.asp
// @include		http://www.naxos.com/catalogue/*
// @include		www.naxos.com/catalogue/*
// @include     http://musicbrainz.org/release/*



// @include		file:///c:/temp/a.html
// @require     http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.js
//
// ==/UserScript==



//****************************************************************************************************************************************************//

var top_level_func = function() {
	function contentEval(source) {
	  // Check for function input.
	  if ('function' == typeof source) {
		// Execute this function with no arguments, by adding parentheses.
		// One set around the function, required for valid syntax, and a
		// second empty set calls the surrounded function.
		source = '(' + source + ')();'
	  }

	  // Create a script node holding this  source code.
	  var script = document.createElement('script');
	  script.setAttribute("type", "application/javascript");
	  script.textContent = source;

	  // Insert the script node into the page, so it will run, and immediately
	  // remove it to clean up.
	  document.body.appendChild(script);
	  document.body.removeChild(script);
	}

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

	function addJQuery(url, callback) {
	  var script = document.createElement("script");
	  if (url) {
		script.setAttribute("src", url);
	  }
	  script.addEventListener('load', function() {
		var script = document.createElement("script");
		script.textContent = "(" + callback.toString() + ")();";
		document.body.appendChild(script);
	  }, false);
	  document.body.appendChild(script);
	}

	var  getUrlVars = function() {
		var vars = {};
		var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
			vars[key] = value;
		});
		return vars;
	}

	var artist_sort_order = function(artists) {
		return $.map(
			artists, 
			function (artist) {
				return $.map(
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

	var iterate = function(obj) {
		var keys = [];

		for (var key in obj) {
			if (obj.hasOwnProperty(key)) {
				 keys.push([key,obj[key]]);
			}
		}
		return keys;
	}

	var list_to_map = function (elems) {
		var out = new Object();
		$.each(elems, function(idx, elem) {
			if (elem[0] in out) {
				out[elem[0]].push(elem[1]);
			} else {
				out[elem[0]] = [elem[1]];
			}
		});
		return out;
	}


//****************************************************************************************************************************************************//

	var naxos_headers = function(source) {
		var y = new Object();
		$.each($(source).find("td.style5 > p"), function() {
			
			var z = text_node_to_text(this, false).join(' ').trim().replace( /\n/, '' ).split(":"); 
			if (z.length == 2) {
				y[z[0].trim()] = z[1].trim().split(" ; "); 
			}
		});	  
		console.log(y);
		if (y.hasOwnProperty('Composer(s)')) {
			y['Composer(s)']	= artist_sort_order(y['Composer(s)']);
		} else {
			y['Composer(s)']	= []
		}
		
		if (y.hasOwnProperty('Artist(s)')) {
			y['Artist(s)']		= artist_sort_order(y['Artist(s)']);
		} else {
			y['Artist(s)']		= []
		}
		
		console.log(y);
		return y;
	}

		

	var naxos_works = function(source) {
		var works = new Array();
		$(source).find("div.works").each(function(idx, para) {
			var work = new Object();
			work["work"]		= text_node_to_text(para, false).join(' ').trim().replace( /\n/, '' );
			work["composers"]	= $(para).prevAll('p.composers').eq(0).find('a').map(function () {return artist_sort_order(text_node_to_text(this, true))}).get();
			work["performers"]	= $(para).next('div.performers').find('td:has(>a)').map(
									function () {
										var xx = text_node_to_text(this, true);
										if (xx.length == 1) {
											xx.push("");
										} else {
											xx[1] = xx[1].replace(',',"").trim();
										}
										xx[0] = artist_sort_order(new Array(xx[0]))[0];									
										console.log(xx);									
										return new Array(xx);
									}
								).get();
			
			work["tracks"]	= $(para).next('div.performers').nextUntil('div', 'table').map(function () {
				return new Array($(this).find('td').find('td').map(function () {return text_node_to_text(this,false,true)}).get());
			}).get();
			
			console.log(work);
			console.log("################################");

			works.push(work);
		});	  
		return works;
	}

	var  naxos_scrape_fn = function(source, url) {
		console.log('#############');
		naxos_scrape = new Object();
		naxos_scrape["url"]		= url;
		naxos_scrape['headers']	= naxos_headers(source);		
		console.log(naxos_scrape);
		console.log('$$$1');
		naxos_scrape['title']	= $(source).find("h1.cdtitle")[0].textContent.trim();		
		console.log(naxos_scrape);
		console.log('$$$2');
		naxos_scrape['works']	= naxos_works(source);
		console.log(naxos_scrape);
		console.log('$$$3');
		return naxos_scrape;
	}


	var  musicbrainz_add_recording = function(scape)  {
		add_field("edit_note", 					"Imported by ''MusicBrainz_Import_from_Naxos''\nhttps://code.google.com/p/bogs-xbmc-addons/source/browse/trunk/tag_updaters/naxos.user.js\n\nfrom: " + scape["url"]);
		add_field("name", 						scape['title']);
		add_field("labels.0.name", 				scape['headers']['Label'][0]);
		add_field("barcode", 					scape['headers']['Barcode'][0].slice(1,scape['headers']['Barcode'][0].length));
		add_field('labels.0.catalog_number',	scape['headers']['Catalogue No'][0]);
		if (scape['headers'].hasOwnProperty('Physical Release')) {
			add_field("date.year", 					scape['headers']['Physical Release'][0].split('/')[1]);
			add_field("date.month", 				scape['headers']['Physical Release'][0].split('/')[0]);
		}
		

		add_field("script", 					"28");
		add_field("status", 					"Official");
		add_field("type", 						"Album");
		add_field("packaging", 					"Jewel Case");
		add_field("urls.0.url", 				scape['url']);
		add_field("urls.0.link_type", 			"288");
		
		var albumartist = scape["headers"]["Artist(s)"];
		for (var idx =0 ; idx < albumartist.length ; idx++) {
			add_field("artist_credit.names.%d.artist.name".replace('%d', idx), albumartist[idx]);
			if (idx + 1 < albumartist.length) {
				add_field("artist_credit.names.%d.join_phrase".replace('%d', idx), " & ");
			}
		}
		
		var medium = 0;
		add_field("mediums.%d.format".replace('%d', medium), 'CD');

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
				name = name.replace("Op.", "op.").replace("No.", "no.")
				
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
		
	}

	var naxos_relationships = function (scrape) {
		var out = new Object();
		$.each(scrape['works'], function(idx, work) {
			$.each(work['tracks'], function(idx, track) {	
				$.each(work["performers"], function(idx, perf) {	
					console.log(track);
					console.log(parseInt(track[0] + '0',10)-1);
					var tk = parseInt(track[0] + '0',10)-1;
					if (perf in out) {
						out[perf].push(tk.toString());
					} else {
						out[perf] = [(tk + 1).toString()];
					}
				});
			});		
		});
		return out;
	}

	//////////////////////////////////////////////////////////////////////////////


	function naxos_top() {
		window.add_field = add_field = function  (name, value) {
			var field = document.createElement("input");
			field.type = "hidden";
			field.name = name;
			field.value = value;
			console.log(new Array(name, value));
			myform.appendChild(field);
		}
		

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
		
		console.log('Naxos Page');	  
		var script = document.createElement('script');
		script.src = "http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.js";
		document.getElementsByTagName('body')[0].appendChild(script);	
		naxos_scrape = naxos_scrape_fn(document, window.location.href);
		console.log(naxos_scrape);	  
		musicbrainz_add_recording(naxos_scrape);
		
		div.appendChild(myform);
		console.log(html(myform));
		$("td.style5").append(div); 
		
		
		return 1;
	};

	var mb_read_naxos = function(catalog) {
		
		console.log($("table.tbl"));
		$("table.tbl").after(
			$('<div class="naxos"></div>').append(
				$("<label></label>").append(
					$('<input type="checkbox"/>').change(function() {
						$("img.naxos_loading").remove();
						$("div.naxos").after($('<img class ="naxos_loading" src="/static/images/icons/loading.gif"/>'));
						var url = 'http://www.naxos.com/catalogue/item.asp?item_code='+catalog;
						console.log(url);
						if (this.checked) {
							console.log("!!!")
							rel = GM_xmlhttpRequest({
//								synchronous : true,
								method: "GET",
								url: url,
								headers: {
									"User-Agent": "Mozilla/5.0",    // If not specified, navigator.userAgent will be used.
									"Accept": "text/xml"            // If not specified, browser defaults will be used.
								},
								onload : function(response) {
									var $ac = $([
											'<span class="artist autocomplete">',
											'<img class="search" src="/static/images/icons/search.png"/>',
											'<input type="text" class="name"/>',
											'<input type="hidden" class="id"/>',
											'<input type="hidden" class="gid"/>',
											'</span>'
										].join('')
									);
									
								var $sel1 = $([									
									'<select id="id-ar.link_type_id" name="ar.link_type_id">',
									'	<option selected="selected"></option>',
									'	<option value="122">&nbsp;performance</option>',
									'	<option value="156">&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} {guest} {solo} performed</option>',
									'	<option value="148">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;performed {additional} {guest} {solo} {instrument} on</option>',
									'	<option value="149">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;performed {additional} {solo} {guest} {vocal} vocal on</option>',
									'	<option value="150">&nbsp;&nbsp;&nbsp;&nbsp;{orchestra} orchestra {additional:additionally} performed</option>',
									'	<option value="151">&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} conducted</option>',
									'	<option value="152">&nbsp;&nbsp;&nbsp;&nbsp;performed {additional} chorus master on</option>',
									'	<option value="159">&nbsp;compilations</option>',
									'	<option value="147">&nbsp;&nbsp;&nbsp;&nbsp;compiled</option>',
									'	<option value="155">&nbsp;&nbsp;&nbsp;&nbsp;DJ-mixed</option>',
									'	<option value="157">&nbsp;remixes</option>',
									'	<option value="153">&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} remixed</option>',
									'	<option value="154">&nbsp;&nbsp;&nbsp;&nbsp;produced {instrument} material that was {additional:additionally} sampled in</option>',
									'	<option value="297">&nbsp;{additional:additionally} arranged</option>',
									'	<option value="158">&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} arranged {instrument} on</option>',
									'	<option value="299">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;provided {additional} {instrument} instrumentation for</option>',
									'	<option value="300">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} orchestrated</option>',
									'	<option value="298">&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} arranged {vocal} vocal on</option>',
									'	<option value="160">&nbsp;production</option>',
									'	<option value="141">&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} {assistant} {associate} {co:co-}{executive:executive }produced</option>',
									'	<option value="138">&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} {assistant} {associate} {co:co-}{executive:executive }engineered</option>',
									'	<option value="136">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} {assistant} {associate} {co:co-}mastered</option>',
									'	<option value="140">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} {assistant} {associate} {co:co-}audio engineered</option>',
									'	<option value="133">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} {assistant} {associate} {co:co-}sound engineered</option>',
									'	<option value="143">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} {assistant} {associate} {co:co-}mixed</option>',
									'	<option value="128">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} {assistant} {associate} {co:co-}recorded</option>',
									'	<option value="132">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} {assistant} {associate} programmed {instrument:% on}</option>',
									'	<option value="144">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{additional:additionally} {assistant} {associate} {co:co-}edited</option>',
									'	<option value="129">&nbsp;&nbsp;&nbsp;&nbsp;has a miscellaneous role on</option>',
									'	<option value="142">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;provided legal representation for</option>',
									'	<option value="134">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;provided booking for</option>',
									'	<option value="135">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;provided artist &amp; repertoire support for</option>',
									'	<option value="146">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;provided {additional} creative direction on</option>',
									'	<option value="137">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;provided {additional} art direction on</option>',
									'	<option value="130">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;provided {additional} design/illustration on</option>',
									'	<option value="125">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;provided {additional} graphic design on</option>',
									'	<option value="123">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;provided {additional} photography on</option>',
									'	<option value="127">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;published</option>',
									'	<option value="131">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;wrote {additional} liner notes for</option>',
									'</select>'
									].join('')
								);
									
									
									
									
									naxos_scrape = naxos_scrape_fn(response.responseText, url); 
									console.log("%%%%%")
									console.log(naxos_scrape);
									$("img.naxos_loading").remove();
									$("div.naxos").after(
										$('<table class="naxos2" border="1">').append(
											$("<tr>").append( 
												$("<th>").text("Artist"), 
												$("<th>").text("Type"),
												$("<th>").text("Recordings"),
												$("<th>").text("Details")
											),
											$.map(
												iterate(naxos_relationships(naxos_scrape)), 
												function(pairs) {
													var	perf	= pairs[0].split(',')[0];
													var	instr	= pairs[0].split(',')[1];
													var	tracks	= pairs[1].join(', ');
													console.log('%&&&&&&&&&&&&');
													console.log(pairs);
													 
													return $("<tr>").append(
														$("<td>").append(function() {
															var a = $ac.clone();
															a.children("input.name").val(perf);
															return a;
														}()),
														$("<td>").append(instr),
														$("<td>").append(tracks),
														$("<td>").append("Type:",$sel1.clone())
														

													);
												}
											)
										)
									);
									//Update Artist Span with binings (has to be done in native namespace for MB to work)
									location.href = "javascript:(" + function() {
										$('table.naxos2').find('span.autocomplete').each(function () {
											MB.Control.EntityAutocomplete({inputs: $(this)});	
										});
									} + ")()";

								}
							});	

						} else {
							$("div.naxos2").remove();
						}
					}),
					" View Relationships"
				)
			)
		);			
	}
	
	var top = function() {
		console.log(window.location.href.match(/naxos.com\/catalogue\/item.asp\?item_code=/));
		if (window.location.href.match(/naxos.com\/catalogue\/item.asp\?item_code=/)) {
			naxos_top(); 
		} else {
			var RELEASE_MBID	= window.location.pathname.match(/\/release\/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})$/);
			console.log("@@@");
			if (RELEASE_MBID) {
				RELEASE_MBID = RELEASE_MBID[1];
				console.log(RELEASE_MBID);

				var 
					label		= $('a[rel="mo:label"]').text().trim(),
					catalog		= $('span[property="mo:catalogue_number"]').text().trim()
				
				console.log(label);
				console.log(catalog);

				if ($("li.account").length && label == "Naxos" && catalog) {
					mb_read_naxos(catalog);
				}
			}
		 
		 }
	}
	console.log('$$$$1');
	var insert = function () {
		//var jq = $;
		//$ = unsafeWindow.$
		var $ac = $([
						'<span class="artist autocomplete">',
						'<img class="search" src="/static/images/icons/search.png"/>',
						//'<input type="text" class="name"/>',
						'<input aria-haspopup="true" aria-autocomplete="list" role="textbox" autocomplete="off" class="name ui-autocomplete-input" value="" style="width: 170px;" type="text">',
						'<input type="hidden" class="id"/>',
						'<input type="hidden" class="gid"/>',
						'</span>'
					].join('')
				);
		 
		$("table.tbl").after(
			$('<div class="naxos"></div>').append(	 
				function () {
					var a = $ac.clone();
					a.children("input.name").val('AC/DC');
					return a;
				} ()				
			)
		);
		$('div.naxos').find('span.artist.autocomplete').each(function () {
			console.log(this);
			MB.Control.EntityAutocomplete({inputs: $(this)});			
		});
	}
	//contentEval2(insert);	
	top();
}
var activate_forms = function () {
	console.log('!!');

	console.log($('table.naxos2').find('span.artist.autocomplete').toArray());
	$('table.naxos2').find('span.artist.autocomplete').each(function () {
		console.log(this);
		MB.Control.EntityAutocomplete({inputs: $(this)});	
	});
	console.log('!2');	

}

function contentEval2(source) {
	  // Check for function input.
	  if ('function' == typeof source) {
		// Execute this function with no arguments, by adding parentheses.
		// One set around the function, required for valid syntax, and a
		// second empty set calls the surrounded function.
		source = '(' + source + ')();'
	  }

	  // Create a script node holding this  source code.
	  var script = document.createElement('script');
	  script.setAttribute("type", "application/javascript");
	  script.textContent = source;

	  // Insert the script node into the page, so it will run, and immediately
	  // remove it to clean up.
	  document.body.appendChild(script);
	  document.body.removeChild(script);
	}														

console.log('@@@');
top_level_func();

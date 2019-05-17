# -*- coding: utf-8 -*-

import time
import exceptions
import threading
import Queue
import urllib2, urllib
import json
import socket
#import unicodedata
import collections
import pprint
import traceback
import codecs
import re


import iso_3166_1
from HTMLParser import HTMLParser
from xml.sax.saxutils import escape, unescape

import xml_decode



from BeautifulSoup import BeautifulSoup,BeautifulStoneSoup,NavigableString 

class ScaperException(Exception):
	def __init__(self, module, artist, value):
		self.module	= module
		self.value	= value
		self.artist	= artist
	def __str__(self):
		return "Illegal value ({val}) returned from module {mod} looking for term({art})".format(val=self.value, mod= self.module, art = self.artist)

unquote = lambda st : st.replace('&quot;', '"')

class safe(object):
	def __init__(self, obj):
		self.x = obj
	
	def  __getattr__(self, name):		
		return   getattr(self.x, name) if self.x else None
#def escape(st):
#	parsed	= BeautifulSoup(st, convertEntities=BeautifulSoup.HTML_ENTITIES)
#	return HTMLParser.unescape.__func__(HTMLParser, st)


def clean(st, clip = False):
	try:
#		print type(st), repr(st)
		if not st:
			return ""
		else:
#			print ("@", type(st), st)
			#parsed	= BeautifulSoup(st, convertEntities=BeautifulSoup.HTML_ENTITIES)
			#parsed	= HTMLParser.unescape.__func__(HTMLParser, st)
			parsed = st.replace('quot;', '"')
			#parsed	= st
			#upped	= unicode(parsed)
			#downed	= unicodedata.normalize('NFKD', upped)
			downed	= parsed.encode('utf8')
			ret		= "".join(c for c in downed if ord(c) <= 256 or clip)
			return	str(ret)
	except Exception,e:
		print type(e), e, type(st), repr(st)
		print traceback.format_exc()
		raise
		

def mt():
	ts = time.localtime(time.time())
	return "{0}:{1}:{2}".format(ts.tm_hour, ts.tm_min, ts.tm_sec)
	
def geturlbin(url, timeout = 60):
	try:
		print "\tgetting: %s - %s" % (mt(), url)
		req = urllib2.Request(url)
		req.add_header('User-Agent', "bog's_xbmc_scraper/0.0 bog.gob@gmail.com")
		return urllib2.urlopen(req, timeout = timeout).read()
	except urllib2.HTTPError:
		raise
	except urllib2.URLError, e:
		if isinstance(e.reason, socket.timeout):
			return geturlbin(url, timeout)
		else:
			raise
	
	
def geturl(url, timeout = 30, tries = 6):
	delay =1 
	def inner(number):
		try:
			print "\tgetting: %s - %s" % (mt(), url)
			req = urllib2.Request(url)
			req.add_header('User-Agent', "bog's_xbmc_scraper/0.0 bog.gob@gmail.com")
			return urllib2.urlopen(req, timeout = timeout).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')
		except urllib2.HTTPError:
			if number > 0:			
				time.sleep(delay)			
				return inner(number - 1)
			else:
				raise
		except urllib2.URLError, e:
			if isinstance(e.reason, socket.timeout):
				if number > 0:			
					time.sleep(delay)			
					return inner(number - 1)
				else:
					raise
			else:
				raise
		except socket.timeout:
			if number > 0:			
				time.sleep(delay)			
				return inner(number - 1)
			else:
				raise

	start = time.clock()
	ret = inner(tries)
	print "\t", (time.clock() - start)
	return ret

def geturl_delay(url, delay = 1):
	time.sleep(delay)
	return geturl(url)

nested = lambda: collections.defaultdict(nested)

def tidy(el):
	return "" if not el or not el.string else el.string.strip()

def sub(dat):
	return "".join(( content.string if isinstance(content,NavigableString) else sub(BeautifulSoup(content.renderContents()))  for content in dat.contents))
	
	
def extract(dat):
	return escape(sub(dat))

#extract = lambda dat: "".join(( clean(content.string) if isinstance(content,NavigableString) else clean(content.renderContents())  for content in dat.contents))

def stringer(obj, method, *args, **kwargs):
	if obj:
		if not kwargs:
			return getattr(obj,method)(*args)
		else:
			return getattr(obj, method)
	else:
		return []

		

		
		
		

def encode(mp, indent = "  ", depth = 0):
	def test(tag, ii):
		if isinstance(ii, dict):
			return encode(ii,indent,depth+1)
		elif isinstance(ii, basestring):
			return ii
		elif hasattr(v, "__iter__"):
			return list(v)
		else:
			return str(ii)
	
	
	output = lambda indent, depth, tag, val: ("\n{indent}<{tag}>".format(indent= indent * depth, tag = tag),  val, "</{tag}>".format(indent = indent * depth, tag = tag))
	out = []
	for k,v in mp.iteritems():
		val = test(k, v)
		if isinstance(val, list):
			for v in val:
				vi = test(k, v)
				out.extend(output(indent, depth, k, vi))
		else:
			out.extend(output(indent, depth, k, val))

	#print out
	return u"".join(out)


##############################################################
def discogs_query(url, label = None):
	if label:
		print "$" * 40
		print label
	dets = geturl_delay(url)
	print dets
	decoded = json.loads(dets)
	pprint.pprint(decoded)
	return decoded

def discogs_artist_dets(artist):
	for res in discogs_query("http://api.discogs.com/database/search?q={0}&type=artist".format(artist), "query")["results"]:
		if res["uri"].split("/")[-1] == artist:
			record = res
			break
	else:
		return

	artist = discogs_query(record["resource_url"], "artist")

	return discogs_query(record["resource_url"]  + "/releases", "releases")
	

def discogs_artist_scrape(url):
		profileso= {}
		item = BeautifulSoup(geturl_delay(url))
		profiles = stringer(item.find('div', {'class':  'profile'}), 'findAll', "div")
		if profiles:
			for idx, div in enumerate(profiles):
				if div.get("class", None) == "head":
					key = div.string.strip()
					if key == "Profile:":
						profileso[key] = extract(profiles[idx + 1].div)
					elif key == "Members:":
						profileso[key] = [tidy(a) for a in profiles[idx + 1].findAll('a') if a.string]
						profileso["Past Members:"] = [tidy(a.s) for a in profiles[idx + 1].findAll('a') if not a.string]
					elif key == "Sites:":
						profileso[key] = dict( (tidy(a), a['href']) for a in profiles[idx + 1].findAll('a'))
					elif key == "Variations:":
						profileso[key] = [tidy(a) for a in profiles[idx + 1].findAll('a') if a.get('id', None) != "show-more-anvs"]
					else:
						profileso[key] = extract(profiles[idx + 1]	)
			
			profileso['Images'] = [img['src'] for img in [item.find("div", {'class' : 'artist_html_short_wrap'}).find('img') or {}] if img.get('src', None)]

			artwork, hrefs = zip(
				*(
					(it['src'], it.parent['href'])
					for it in item.find('table', {'class':  'discography'}).findAll('img', {'class':  'artwork'})
				)
			)
			albums			= [tidy(it1) for it1 in item.find('table', {'class':  'discography'}).findAll('a', {'href':  lambda h: h in set(hrefs)}) if it.string ]
			profileso['Albums:'] = zip(albums,artwork)

		#pprint.pprint(profileso)
		return profileso

def discogs_lookup_artist(artist, albums, url):
	profileso = discogs_artist_scrape(url)
	inf = None
	if profileso:
		inf =  {
			'artist'		: dict((
				('name',		 artist),
				('biography',	 escape(
									"[B]Discogs[/B][CR]"
									+
									("[CR][B]Variations:[/B][CR]" + ", ".join(profileso["Variations:"]) if "Variations:" in profileso else "")
									+
									("[CR][B]Members:[/B][CR]" + ", ".join(profileso["Members:"]) if "Members:" in profileso else "")
									+
									("[CR][B]Past Members:[/B][CR]" + ", ".join(profileso["Past Members:"]) if "Past Members:" in profileso else "")
									+
									"[CR][B]Links:[/B][CR]" + "[CR]".join((
										"{0} : {1}".format(k,v)
										for k,v in profileso.get("Sites:", {}).iteritems()
									))
									+
									"[CR]"
									+
									profileso.get("Profile:", "")

								)),
				('thumb',		profileso.get('Images', [])),
				('album',		[
									{
										'title'		: album,
									}
									for album, art in profileso['Albums:']
								]),
			))
		}
	return inf
##############################################################
#API Key bd22c2254b47244cc33603a17659b6d2
#http://htbackdrops.com/api/bd22c2254b47244cc33603a17659b6d2/download/12580/fullsize
#http://htbackdrops.com/api/bd22c2254b47244cc33603a17659b6d2/searchXML?mbid=c130b0fb-5dce-449d-9f40-1437f889f7fe&amp;aid=1,5,26

def backdrops_artist(artists, albums, mbid):
	data = geturl_delay("http://htbackdrops.org/api/bd22c2254b47244cc33603a17659b6d2/searchXML?mbid={0}&amp;aid=1,5,26".format(mbid))
	
	soup = BeautifulStoneSoup(data)
	try:
		inf =  {
						'artist'		: collections.OrderedDict((
							('mbid',		 mbid),
							('name',		 ", ".join(artists)),
							('fanart',		["http://htbackdrops.com/api/bd22c2254b47244cc33603a17659b6d2/download/{0}/fullsize".format(image.id.string) for image in soup.findAll('image')]),
						))
				}
		print inf
	except Exception,e:
		print "***", e
		import traceback
		traceback.print_exc()
		print soup
		inf = {}
		
	return inf		
				
##############################################################
#lastfm
#Your API Key is 6a95f3c9de1a78a960f62d7d76cc94c1

def lastfm_artist(artists, albums, mbid):
	data	=  geturl_delay("http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&mbid={0}&api_key=6a95f3c9de1a78a960f62d7d76cc94c1&format=json".format(mbid))
	try:
		res		= json.loads(data)
	except exceptions.ValueError:
		print ("JSON::", data)
		raise
	#pprint.pprint(res)	
	if "error" in res:
		print "\t\t**", res
		return {}
	else:
	
		sim_arts = ""
		sim = res['artist'].get('similar', {})
		if isinstance(sim, dict):
			sim_art = sim.get('artist', [])
			if isinstance(sim_art, list):	
				sim_arts = ", ".join((other['name'] for other in sim_art))
			elif isinstance(sim_art, dict):	
				sim_arts = sim_art['name']


		bio1	= u"[B]{}[/B]{}[CR]{}".format(
			res["artist"]["name"], 
			("\n[CR][B]Similar Artists:[/B]" + sim_arts) if sim_arts else "",			
			sub(BeautifulSoup(res["artist"]["bio"]["content"])),
		) 
				
		
		enclose = lambda  x: [x] if isinstance(x, dict) else x
		inf =  {
					'artist'		: collections.OrderedDict((
						('mbid',		 mbid),
						('name',		 res["artist"]["name"]),
						('genre',		 [
											tag['name']
											for tag in enclose((
												res['artist']['tags'] if not isinstance(res['artist'].get('tags', ""), basestring) else 
												{'tag' : []} 
											)['tag'])
										]),
						
						('biography',	 HTMLParser.unescape.__func__(HTMLParser, bio1)),
						('thumb',		sorted([img['#text'] for img in res['artist']['image'] if img['#text']], key = lambda img: "{0:0>10}".format(img.split('/')[-2] if len(img.split('/')) else "0"), reverse = True)),
						('formed', 		res['artist'].get('yearformed', "")), 
					))
				}
				
		for k,v in inf["artist"].iteritems():
			inf["artist"][k] = escape(v) if isinstance(v, basestring)  else [escape(vv) for vv in v]

		return inf
	
def lastfm_album(album, mbid):
	data	=  geturl_delay("http://ws.audioscrobbler.com/2.0/?method=album.getinfo&mbid={0}&api_key=6a95f3c9de1a78a960f62d7d76cc94c1&format=json".format(mbid))
	try:
		res		= json.loads(data)
	except exceptions.ValueError:
		print ("JSON::", data)
		raise
		
	#pprint.pprint(res)
	if "error" in res:
		inf = {}
		print "\t", res
	else:
		inf =  {
					'album'		: dict((
						('title',		 escape(album)),
						('artist',		 escape(res['album']['artist'])),
						('releasedate',	res['album']['releasedate']),


						('track',		 [
											{
												'title'		: extract(BeautifulSoup(track['name'])),
												'position'	: idx + 1,
												'duration'	: track['duration'],
											}
											for idx, track in enumerate(
												res['album']['tracks']['track'] 
													if 
														isinstance(res['album'].get('tracks', ""), dict) 
														and
														isinstance(res['album']['tracks'].get('track', ""), list)
													else  
												[]
											)
										]),
						
						('style',		 [
											extract(BeautifulSoup(tag['name']))
											for tag in (
												res['album']['toptags']['tag'] 
													if 
													isinstance(res['album'].get('toptags', ""), dict) 
													and
													isinstance(res['album']['toptags'].get('tag', ""), list)
													else 
												[]
											)
										]),
						('review',	 	"[B]Lastfm[/B][CR]" + (extract(BeautifulSoup((res['album']["wiki"]["content"] or "").replace('&quot;', '"'))) if 'wiki' in res['album'] else "")),
						('thumb',		sorted([img['#text'] for img in res['album']['image'] if img['#text']], key = lambda img: "{0:0>10}".format(img.split('/')[-2] if len(img.split('/')) else "0"), reverse = True)),
					))
				}
	thumbs = inf.get('thumb', [])			
	if thumbs:
		inf['thumb'] = thumbs[0]

	return inf	
	

##############################################################
#http://musicbrainz.org/doc/XML_Web_Service/Version_2
LUCENE_ESCAPED = set('+ - && || ! ( ) { } [ ] ^ " ~ * ? : \\'.split())

def lucene_format(st):
	return "".join(c if c not in LUCENE_ESCAPED else "\\{0}".format(c)  for c in st ).lower()

def lucene_query_iter(*args, **kwargs):
	if 'sep' not in kwargs:
		kwargs['sep'] = " AND "

	if 'top' not in kwargs:
		outer	= "{0}"
		sep		= " AND "
	else:
		outer = "({0})"
		sep		= " OR "

	res = 	sep.join((
			'"{0}"'.format(lucene_format(clean(arg)))														if isinstance(arg, basestring) else
			'{0}:"{1}"'.format(lucene_format(clean(arg.keys()[0])), lucene_format(clean(arg.values()[0])))	if isinstance(arg, dict) else
			 lucene_query_iter(top = False,  *arg)
			for arg in args
			if arg
		))

	return outer.format(res)




def brainz_query(typ, *args, **kwargs):
	return brainz_query_direct(typ, [], args, kwargs.iteritems())


def brainz_query_direct(typ, raw, args = [], pairs = []):
	return geturl_delay(
		"http://www.musicbrainz.org/ws/2/{0}/?query={1}".format(
			typ,
			urllib.quote(" AND ".join(
				[
					arg.lower()
					for arg in raw
				] +
				[
					'"%s"' % lucene_format(arg)
					for arg in args

				] +
				[
					'{0}:"{1}"'.format(
						k,
						lucene_format(arg)
					)
					for k,v in pairs
					if v is not None
				]
			))
		)
	)


def brainz_lookup(typ, id, flags):
	return geturl_delay(
		"http://musicbrainz.org/ws/2/{0}/{1}?inc={2}".format(
			typ,
			id,
			"+".join(flags)
		)
	)
	
def brainz_lookup_artist_by_mb(artist, mbid, classical = False):	
	BeautifulStoneSoup.NESTABLE_TAGS['artist'] = ['relation']
	#print mbid
	item = BeautifulStoneSoup(brainz_lookup("artist", mbid, ("artist-rels", "release-rels", "url-rels", "work-rels", 'tags')))
	#("artist-credits","labels","recordings","artist-rels","label-rels","recording-rels","release-rels","url-rels","work-rels")))
	#print item.prettify().strip()

	band = item.find('artist')
	links = dict(
					(rel1["type"],  tidy(rel1.target))
					for rel1 in stringer(item.find('relation-list', {'target-type' :"url"}), 'findAll', 'relation')
			)
	artists = [
				{
					"name"			: tidy( (art.artist.find('sort-name') or art.artist.find('name')) if classical else art.artist.find('name')),
#					"sort-name"		: tidy(art.artist.find('sort-name')),
					"mbid"			: art.artist['id'],
					'yearsactive'	: [tidy(art.begin)] + ([tidy(art.end)] if tidy(art.end) else []),

				}
				for art in stringer(item.find('relation-list', {'target-type' :"artist"}), 'findAll', 'relation', {'type' : 'member of band'})
		]
	if not band:
		return {'artist' : {"name" : {}}}, 
	inf =  {
		'artist'		: dict((
			('name',		 artist or "".join((safe(item.find('sort-name') or item.find('name')) if classical else item.find('name')).contents or [])), 
#					('sort-name',	 tidy(band.find('sort-name'))),
			('yearsactive',	 			[
						data
						for obj in ([band.find('life-span')] if band else [])
						if obj
						for attr in ('begin', 'end')
						for data in [tidy(getattr(obj, attr))]
						if data
					]
			),
			('genre',		 [tidy(tg.find('name')) for tg in sorted(stringer(item.find('tag-list'), "findAll", 'tag'), key = lambda t: int(t['count'])) ]),
			('mbid',		 band['id']),
			('formed',		 iso_3166_1.ISO_3166_1.get(tidy(band.find('country')), tidy(band.find('country')))),
			('biography',	 (
								"[B]Music Brainz[/B][CR][B]Artists[/B]: " + ", ".join((
									artisti['name']
									for artisti in artists
								))
								+
								"[CR][B]Links[/B][CR]" + "[CR]".join((
									"{0} : {1}".format(k,v)
									for k,v in links.iteritems()
								))

							)),
			('album',		[
								{
									'title'		: tidy(rel.release.title),
									'year'		: tidy(rel.release.date),
#											'mbid'		: rel.release['id'],
#											'barcode'	: tidy(rel.release.barcode)
								}
								for rel in stringer(item.find('relation-list', {'target-type' :["release"]}), 'findAll', 'relation', {'type' : ['producer']} )
							] +
							(
								[] if not classical else
								[
									{
										'title'		: tidy(rel.work.title),
										'year'		: tidy(rel.work.date),
										#'mbid'		: rel.work['id'],
										#'barcode'	: tidy(rel.work.barcode)
									}
									for rel in stringer(item.find('relation-list', {'target-type' :['work']}), 'findAll', 'relation', {'type' : ['composer']} )
								]
							)
			),
							
							
		))
	}
	#pprint.pprint(inf)
	val = inf
	#print "$"*40
	#print val
	return val, links

def brainz_lookup_artist_mb(artist, albums, classical = False):
	if artist:
		if classical:
			artist_sort = artist.split(',')
			if artist_sort > 1:
				artist_sort = " ".join(a.strip() for a in artist_sort[::-1])
				extra = [artist_sort]
			else:
				extra = []
				
			soup = BeautifulStoneSoup(brainz_query_direct("artist", [lucene_query_iter(
				[{'tag' : 'classical' }],
				[artist]+ [ extra]
				
			)]))
			soup_mbids = soup.findAll("artist")

		elif albums:
			soup = BeautifulStoneSoup(brainz_query_direct("release", [lucene_query_iter(
				[{'release': album}  for album in albums], 
				[{'artist' : artist}]
			)]))
			soup_mbids = [rel.artist  for rel in soup.findAll("release")]
		else:
			soup = BeautifulStoneSoup(brainz_query_direct("artist", [lucene_query_iter(
				{'artist' : artist}
			)]))
			soup_mbids = soup.findAll("artist")


		for artistf in soup_mbids:
			disamb = artistf.find('disambiguation')
			if disamb and disamb > 0:
				print "\t{0}, {1}, {2}  - {3} ({4}) {5}".format("??", clean(artist), tidy(artistf.find('name')), artistf['ext:score'], tidy(disamb), artistf['id'])

		if not soup_mbids:
			raise ScaperException("MB", clean(artist), "MBID not found")
		soup_mbid = soup_mbids[0]
		#Likely Error
		if soup_mbid['id'] ==  "1cb79018-6057-4fc6-b155-143b9fd91b11":
			raise ScaperException("MB", clean(artist), "1cb79018-6057-4fc6-b155-143b9fd91b11")

		if soup_mbid['ext:score'] == "100":
			return soup_mbid['id']

	return None
	

	
def brainz_lookup_artist(artist, mbid, albums, classical = False):
	print (clean(artist), mbid, clean(str(albums)))
	if artist and not mbid:
		mbid = brainz_lookup_artist_mb(artist, albums, classical)

	if mbid:
		 return brainz_lookup_artist_by_mb(artist, mbid, classical)
	else:
		return None, {}
def printer(a):
	print a
	return a


	
##############################################################
def aggregate(infs, fo, classical = False):
		
	def feeder(qu, term):
		while True:
			if not term.empty():
				term.get(block = True)
				term.task_done()
				
				break

			if not qu.empty():			
				yield qu.get(block = True)
				qu.task_done()
			else:
				time.sleep(0.01)
			

	def isol(func, *args):
		try:
			ret =  func(*args)
			return ret
		except ScaperException,e:
			print "**Exception**********", e
			print args
			return None
		except Exception,e:
			print "**Exception**********", e
			print args
			print traceback.format_exc()
			return None
	def dup_rem(itr):
		out = []
		for i, it in enumerate(itr):
			if not any(True for j, it2 in enumerate(itr) if i != j and it == it2):
				out.append(it)
		return out
			
	def merge(aggregated, artist, fo):
		tmp = aggregated[artist]["MB"].copy()
		for keyd in ("DSC", "LFM"):
			if keyd in aggregated[artist]:
				other = aggregated[artist][keyd]
				if other:
					print "\tmerging - " +  keyd
					tmp['artist']['genre']		+= (other['artist'].get('genre', []) or [])
					tmp['artist']['genre']		= dup_rem(tmp['artist']['genre'])
					tmp['artist']['album']		+= other['artist'].get('album', [])
					tmp['artist']['album']		= dup_rem(tmp['artist']['album'])
					tmp['artist']['biography']	+= ("\n[CR]" + other['artist'].get('biography', ""))
					if 'thumb' not in tmp['artist']:
						tmp['artist']['thumb'] = []
					if 	keyd != "DSC":
						tmp['artist']['thumb']		+= other['artist'].get('thumb', [])
		
		#patch in MBID
		tmp['artist']['biography']	= "[B]MBID:[/B]%s\n[CR] %s" % (tmp['artist']['mbid'],  tmp['artist']['biography'])
		del tmp['artist']['mbid']
		
		#Deal with artwork
		tmp['artist']['thumb']				= sorted(tmp['artist'].get('thumb', []), key = lambda img: "{0:0>10}".format(img.split('/')[-2] if len(img.split('/')) >= 2 else "0"), reverse = True)
		if tmp['artist']['thumb']:
			tmp['artist']['fanart']				= {}
			tmp['artist']['fanart']['thumb']	= tmp['artist']['thumb'][0] 
		
		print ("done", clean(artist))
		fo.write(unquote(encode(tmp)))
		fo.flush()
	

	aggregated	= collections.defaultdict(dict)
	def gettr():
		while True:
			producers = [
				(q_o_mb, "MB"),
				(q_o_dsc, "DSC"),
				(q_o_lfm, "LFM"),
			]

			for qu, key in producers:
				if not terminate.empty():
					terminate.get(block = True)
					terminate.task_done()
					print "\tfinalising..."
					for artist in sorted(aggregated.keys()):
						try:
							print clean(artist)
							merge(aggregated, artist, fo)
						except Exception,e:
							print "!!Exception**********", e
							print traceback.format_exc()
							
					return
			
				try:
					if qu.empty():
						time.sleep(0.01)
					else:
						artist, inf = qu.get()
						
						aggregated[artist][key] = inf
						if len(aggregated[artist].keys()) == len(producers):
							merge(aggregated, artist, fo)
							del aggregated[artist]
						qu.task_done()
				except Exception,e:
					print "**Exception**********", e
					print traceback.format_exc()
					qu.task_done()
					
	
	###########################################
	q_mb	= Queue.Queue()
	q_mb2	= Queue.Queue()
	q_o_mb	= Queue.Queue()
	q_o_dsc	= Queue.Queue()
	q_o_lfm	= Queue.Queue()
	terminate = Queue.Queue()
	
	print "" 
	print terminate.empty()
	print "$$$$$$"

		
		
	###########################################

	thd_mb = threading.Thread(
		name="MB",
		target= lambda: [
			[
				q_mb.put((artist, albums, res[1]['discogs']), block = True) if 'discogs' in res[1] else 1 ,
				q_mb2.put((artist, albums, res[0]['artist']['mbid']), block = True),
				q_o_mb.put((artist, res[0]), block = True)
			]
			for artist, mbid, albums in infs
			for res in [isol(brainz_lookup_artist, artist, mbid, albums, classical)]
			if res and res[0]
		],
	)

	thd_disc = threading.Thread(
		name="DC",
		target= lambda: [
			q_o_dsc.put((artist, inf), block = True)
			for artist, albums, url in feeder(q_mb, terminate)
			for inf in [isol(discogs_lookup_artist, artist, albums, url)]
		],
	)

	thd_fm = threading.Thread(
		name="LFM",
		target= lambda: [
			q_o_lfm.put((artist, inf), block = True)
			for artist, albums, mbid in feeder(q_mb2, terminate)
			for inf in [isol(lastfm_artist, artist, albums, mbid)]
			if inf
		],
	)
	thd_aggr = threading.Thread(name="Merge", target= gettr)
	
	thd_exit = threading.Thread(name="Term", target= lambda : [terminate.put(True, block = True) for idx in range(3)])
	###########################################

	print "****Starting"
	fo.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<musicdb>\n')
	
	thd_mb.start()
	
	thd_disc.daemon = True
	thd_disc.start()
	
	thd_fm.daemon = True
	thd_fm.start()
	
	thd_aggr.daemon = True
	thd_aggr.start()
	###########################################
	#Synch Content Threads
	print "****Wait on Join 1"
	thd_mb.join()
	q_mb.join()
	q_mb2.join()
	print "****Wait on Join 2"
	q_o_mb.join()
	print "****Wait on Join 3"
	q_o_dsc.join()
	print "****Wait on Join 4"
	q_o_lfm.join()
	print "****Terminating"
	###########################################
	thd_exit.daemon = True
	thd_exit.start()
	thd_exit.join()
	print "****@@@@@@"
	time.sleep(2.0)
	print terminate.qsize()
	print threading.enumerate()	
	thd_fm.join()
	thd_disc.join()
	print threading.enumerate()	
	
	terminate.join()
	fo.write("\n</musicdb>\n")
	print "****Joined"
	
	time.sleep(1.0)
	if 0:
		for thread in threading.enumerate():
			if thread.isAlive():
				try:
					thread.join(0.5)				
					thread._Thread__stop()
				except:
					print(str(thread.getName()) + ' could not be terminated')
	print aggregated

def scrape_albums(albums, ofile, translate):
	start = time.clock()
	
	############################################
	#xml info
	try:
		mbid_xml_map = {item['album']['mbid'].upper() : item for item in xml_decode.xml_decode(ofile)['musicdb']}
	except:
		mbid_xml_map = {}
		
	
	with codecs.open(ofile, "w", encoding='utf8') as fo:		
		fo.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<musicdb>\n')
		for idx, ((album,mbid), artist) in enumerate(sorted(albums.iteritems())):
			print idx, len(albums), clean(album), mbid
			if mbid:
				for scraper in (mb_albums2, ):
					try:
						xml_item =   mbid_xml_map.get(mbid.upper(), None)
						if not xml_item or xml_item['album']['artist'].strip() != escape(artist).strip():
							tmp = scraper(album, mbid)
						else:
							tmp = xml_item
						if tmp and 'track' in tmp['album']:
							#overwrite to ensure that the artist names stay the same!!
							tmp['album']['artist'] = escape(artist)
							fo.write(translate(unquote(encode(tmp))))
							fo.flush()
							#.encode("utf-8")
							break
						else:
							print "\tneed brainz!!", album
					except Exception, e:
						print "^^^^", e
						print traceback.format_exc()
						
			fo.flush()
		fo.write("\n</musicdb>\n")
	print "\ttime:", (time.clock() - start)


def scrape_artists(artsr, outfile, translate):
	start = time.clock()
	arts	= collections.defaultdict(set)
	for k,v in artsr.iteritems():
		for vv in v:
			arts[vv].add(k)
	
	
	try:
		mbid_xml_map = {mbid : item for item in xml_decode.xml_decode(outfile)['musicdb'] for mbid in item['artist']['mbid'].upper().split('/')}
	except:
		mbid_xml_map = {}
	
	print "%%%%", mbid_xml_map	
	############################################
	#Collect artist info
	collected = {}
	for idx, (mbid, artist) in enumerate(sorted(arts.iteritems())):
		print "\tArtist", idx, len(arts), repr(artist) 
		
		xml_item =   mbid_xml_map.get(mbid.upper(), None)
		if not xml_item:
			try:
				rec = lastfm_artist(artist,[],mbid)
				if "artist" in rec:
					rec["artist"]["fanart"] = {}
					rec["artist"]["fanart"]["thumb"]  = backdrops_artist(artist,[],mbid)["artist"].get("fanart", [])
				collected[mbid] =  rec	
			except Exception, e:
				print e
				import traceback
				print traceback.format_exc()				
				collected['mbid'] = {}
				
		else:
			#change single items to a list
			for attrs in (('genre',), ('thumb',), ('fanart', 'thumb')):
				a		= xml_item['artist']
				save	= xml_item['artist']
				for attr in attrs:
					if a:
						save	= a
						a		= a.get(attr, [])

				if isinstance(a, basestring):
					save[attr] = [a]
			collected[mbid] = xml_item

	############################################	
	#Aggregate and write to disk
	with codecs.open(outfile, "w", encoding='utf8') as fo:		
		fo.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<musicdb>\n')
		dat = ""
		for idx, (artists, mbids) in enumerate(sorted(artsr.iteritems())):
			try:
				dat = [collected[mbid]['artist'] for mbid in mbids if collected[mbid]]
				if dat:
					curr = {'artist' : collections.OrderedDict()}
					curr['artist']['mbid']				= "/".join(d['mbid'] for d in dat)
					curr['artist']['name']				= escape(artists)
					curr['artist']['genre']				= sorted(set(sum((d.get('genre',[]) for d in dat), [])))
					curr['artist']['biography']			= "\n\n[CR]".join(d['biography'] for d in dat)
					curr['artist']['thumb']				= sum((d.get('thumb',[]) for d in dat),[])
					curr['artist']['fanart']			= {}
					print [d["fanart"] for d in dat]
					curr['artist']['fanart']["thumb"]	= sum((d["fanart"]['thumb'] for d in dat if 'fanart' in d),[])
					if dat[0].get('formed', ""):
						curr['artist']['formed']		= dat[0].get('formed', "")
					
					fo.write(translate(unquote(encode(curr))))
				fo.flush()
			except Exception,e:
				print "***"
				print dat			
				print e
				import traceback
				print traceback.format_exc()
				
		fo.write("\n</musicdb>\n")		
	print "\ttime:", (time.clock() - start)		
##############################################################
AMAZON_SERVER = {
    "amazon.jp": {
		"server": "ec1.images-amazon.com",
		"id"    : "09",
	},
    "amazon.co.jp": {
		"server": "ec1.images-amazon.com",
		"id"    : "09",
	},
    "amazon.co.uk": {
		"server": "ec1.images-amazon.com",
		"id"    : "02",
	},
    "amazon.de": {
		"server": "ec2.images-amazon.com",
		"id"    : "03",
	},
    "amazon.com": {
		"server": "ec1.images-amazon.com",
		"id"    : "01",
	},
    "amazon.ca": {
		"server": "ec1.images-amazon.com",
		"id"    : "01",                   # .com and .ca are identical
	},
    "amazon.fr": {
		"server": "ec1.images-amazon.com",
		"id"    : "08"
	},
}

AMAZON_IMAGE_PATH = '/images/P/%s.%s.%sZZZZZZZ.jpg'
AMAZON_ASIN_URL_REGEX = re.compile(r'^http://(?:www.)?(.*?)(?:\:[0-9]+)?/.*/([0-9B][0-9A-Z]{9})(?:[^0-9A-Z]|$)')

def brainz_cover_art(mbid):
	def cover_get(soup):
		div = soup.find('div', {"class" : "cover-art"})
		img =  div.img
		if not img:
			print "\t!!!!", mbid
			return ""
		else:
			if u"src" in dict(img.attrs):
				return img['src']
			else:
				return div.a['href']


	data	=  geturl_delay("http://musicbrainz.org/release/{}".format(mbid))
	if "Release Not Found" in data:
		print "%%%Not found", mbid
		inf = {}
	else:
		soup = BeautifulSoup(data)
		return re.sub(r'^//', 'http://', cover_get(soup))



def mb_albums2(name, mbid):
	
	def cover(soup):
		if soup.find("cover-art-archive").front.string == "true":
			return "http://coverartarchive.org/release/{}/front".format(soup.release["id"])
		else:
			asin_link = soup.find("relation", {"type": "amazon asin"})
			if asin_link:
				match = AMAZON_ASIN_URL_REGEX.match(tidy(asin_link.target))
				if match != None:
					asinHost = match.group(1)
					asin = match.group(2);
					if AMAZON_SERVER.has_key(asinHost):
						serverInfo = AMAZON_SERVER[asinHost]
					else:
						serverInfo = AMAZON_SERVER['amazon.com']
						
					return "http://{}{}".format(serverInfo['server'],  AMAZON_IMAGE_PATH % (asin, serverInfo['id'], 'L') )
				return ""	
			else:	
				return ""	
	
	def relations(relations):
		return "\n".join(
			"{}:{} {}: {}".format(
				tidy(rel.begin),
				tidy(rel.end),
				tidy(rel.find("attribute")) or rel["type"],										
				tidy(rel.artist.find("name"))
			) 
			for rel in relations
			if rel.artist
		) 
		
	
	data	=  geturl_delay("http://musicbrainz.org/ws/2/release/{}?inc=artist-credits+artists+labels+media+url-rels+recordings+recording-rels+recording-level-rels+artist-rels".format(mbid))

	
	soup			= BeautifulSoup(data)
	rel				= soup.release
	album_artists	= 	"".join([
						"{}{}".format(artist.find("name").string, artist.get("joinphrase", "")) 
						for artist in rel.find("artist-credit").findAll("name-credit")
						])
	
	date			= rel.find("date")	
	label			= rel.find('label')
	tracks_raw		= [
							(medium_idx, medium, track)
							for medium_idx, medium in enumerate(rel.findAll("medium"))
							for track in medium.findAll('track')
					]
	relase_rels		= rel.find("relation-list", recursive=False)
	review			= [
							"{}.{} {}\n{}".format(
								medium_idx + 1, 
								track.number.string, 
								track.title.string, 
								relations( track.recording.findAll("relation") ) 
							)
							
							for medium_idx, medium, track in tracks_raw
					] + [
					
						relations( relase_rels.findAll("relation") if relase_rels else [] )
					]
		
	tracks			= [
						{
							'title'		: escape(track.title.string or ""),
							'position'	: "{}.{}".format(medium_idx + 1, track.number.string),
							'duration'	: int(round(float(track.length.string)/1000))  if track.length else None,
						}
						for medium_idx, medium, track in tracks_raw
					]	
					
				

	inf =  {
				'album'		: collections.OrderedDict((
					('mbid',		mbid),
					('title',		escape(name)),
					('artist',		escape(album_artists)),
					('releasedate',	date and date.string),
					('label',		escape(tidy(label and label.find("name").string))),
					('review',		escape("[CR][CR]{}".format("\n".join(review).replace("\n", "[CR]")))),
								
					
					('track',		tracks),
					('thumb',		cover(soup))
				))
			}
	print inf
	return inf	

		
		

	
if __name__ == "__main__":
	tmp = mb_albums2("374df7cd-06b7-32ba-899a-c68c8d1a977c", "374df7cd-06b7-32ba-899a-c68c8d1a977c")
	#tmp = mb_albums2("D9B0B04A-710B-45F3-9327-8DD1D29A0F54", "D9B0B04A-710B-45F3-9327-8DD1D29A0F54")

 	
	print unquote(encode(tmp))
	raise 11
if __name__ == "__main__":
	class flushfile(object):
		def __init__(self, f):
			self.f = f
		def write(self, x):
			self.f.write(x)
			self.f.flush()

	import sys
	sys.stdout = flushfile(sys.stdout)
	#print encode(discogs_lookup_artist("Chicago", "", "http://www.discogs.com/artist/Brother+Jack+McDuff"))
	if 0:
		pprint.pprint(backdrops_artist(['Mozart'], '!!!', 'b972f589-fb0e-474e-b64a-803b0364fa75'))
		raise 1

		
		raise 1
		
		pprint.pprint( lastfm_album(u'Communique', 	'e42b0f81-9191-389c-9ae7-0ad279674a64') )
		
		raise 1
	
	if 0:
		pprint.pprint(lastfm_artist('Birds of Tokyo', "8eec195f-d357-4e0a-bcc7-74fd5c462e6e"))
		raise 1
		print encode(discogs_lookup_artist("Chicago", "", "http://www.discogs.com/artist/Brother+Jack+McDuff"))
		raise 1


	infs = (
		(None, [u'Pulp Fiction', u'Crouching Tiger, Hidden Dragon', u'Burt Bacharach Collection', u'Blues Brothers']),
		('A-Ha', set([])),
		('The Corrs', set([u'Talk On Corners', u'Dreams:The Ultimate Collection'])),
		('St-Germain', set([u'Boulevard', u'Tourist', u'F-Com Live And Rare 2'])),
		('Al Green', set([u"Al Green\'s Greatest Hits"])),
		('Various artists', []),
		('SoundGarden', []), 
		('Massive Attack', []),  
		('Portishead', [])
	)
	#aggregate(sorted(infs), open('c:/temp/of.xml', 'w'))
	infs = (
		(u'Barrios, August\xedn', None, set([])),
#		('Giordani', None, set([])),
#		('Bon, Anna', None, set([])),
		('Adam, Adolphe', 'ece590a3-ae0e-4311-bcf3-ee07cfb7b4f0', set([])),
#		('Chopin, Frederick', 'a4a3478d-1f52-4266-918b-3d250cd1e44a', set([])),
#		('John Williams', "8b8a38a9-a290-4560-84f6-3d4466e8d791", set([])),
		('a-ha', '7364dea6-ca9a-48e3-be01-b44ad0d19897', set([])),
	)	
	aggregate(sorted(infs), codecs.open('c:/temp/of.xml', 'w',encoding='utf8'), classical = True)
	print backdrops_artist(['a-ha'], '!!!', '7364dea6-ca9a-48e3-be01-b44ad0d19897')
	print threading.enumerate()	


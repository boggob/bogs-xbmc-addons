import time
import exceptions
import re
import threading
import Queue
import urllib2, urllib
import json
import unicodedata
import collections
import pprint
import traceback


import iso_3166_1
from HTMLParser import HTMLParser
from xml.sax.saxutils import escape



from BeautifulSoup import BeautifulSoup,BeautifulStoneSoup,NavigableString 

class ScaperException(Exception):
	def __init__(self, module, artist, value):
		self.module	= module
		self.value	= value
		self.artist	= artist
	def __str__(self):
		return "Illegal value ({val}) returned from module {mod} looking for term({art})".format(val=self.value, mod= self.module, art = self.artist)

unquote = lambda st : st.replace('&quot;', '"')

def clean(st, clip = False):
	try:
#		print type(st), repr(st)
		if not st:
			return ""
		else:
#			print ("@", type(st), st)
			#parsed	= BeautifulSoup(st, convertEntities=BeautifulSoup.HTML_ENTITIES)
			#parsed	= HTMLParser.unescape.__func__(HTMLParser, st)
			parsed = st.replace('&quot;', '"')
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
def geturl(url, timeout = 30):
	try:
		print "\tgetting: %s - %s" % (mt(), url)
		req = urllib2.Request(url)
		req.add_header('User-Agent', "bog's_xbmc_scraper/0.0 bog.gob@gmail.com")
		return urllib2.urlopen(req, timeout = timeout).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')
	except urllib2.HTTPError,e:
		return ""
	except urllib2.URLError,e:
		return urllib2.urlopen(req, timeout = timeout).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')
		


def geturl_delay(url, delay = 1):
	time.sleep(delay)
	return geturl(url)

nested = lambda: collections.defaultdict(nested)

def tidy(el):
	return "" if not el or not el.string else el.string.strip()

def extract(dat):
	def sub(dat):
		return "".join(( content.string if isinstance(content,NavigableString) else sub(BeautifulSoup(content.renderContents()))  for content in dat.contents))
	
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
	return "".join(out)


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
						profileso[key] = [tidy(a) for a in profiles[idx + 1].findAll('a')]
					else:
						profileso[key] = extract(profiles[idx + 1]	)
			
			profileso['Images'] = [img['src'] for img in [item.find("div", {'class' : 'artist_html_short_wrap'}).find('img') or {}] if img.get('src', None)]

			artwork, hrefs = zip(
				*(
					(it['src'], it.parent['href'])
					for it in item.find('table', {'class':  'discography'}).findAll('img', {'class':  'artwork'})
				)
			)
			albums			= [tidy(it) for it in item.find('table', {'class':  'discography'}).findAll('a', {'href':  lambda h: h in set(hrefs)}) if it.string]
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
				('biography',	 (
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
#lastfm
#Your API Key is 6a95f3c9de1a78a960f62d7d76cc94c1

def lastfm_artist(artist, albums, mbid):
	data	=  geturl_delay("http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&mbid={0}&api_key=6a95f3c9de1a78a960f62d7d76cc94c1&format=json".format(mbid))
	try:
		res		= json.loads(data)
	except exceptions.ValueError,e:
		print ("JSON::", data)
		raise
		
	#pprint.pprint(res)
	if "error" in res:
		inf = {}
	else:
		bio1	= "[B]Lastfm[/B][CR]" + extract(BeautifulSoup(res["artist"]["bio"]["content"])) 
		sim_arts = ""
		sim = res['artist'].get('similar', {})
		if isinstance(sim, dict):
			sim_art = sim.get('artist', [])
			if isinstance(sim_art, list):	
				sim_arts = ", ".join((other['name'] for other in sim_art))
			elif isinstance(sim_art, dict):	
				sim_arts = sim_art['name']
				
		bio2	= ("\n[CR][B]Similar Artists:[/B][CR]" + sim_arts) if sim_arts else ""
		enclose = lambda  x: [x] if isinstance(x, dict) else x
		inf =  {
					'artist'		: dict((
						('name',		 artist),
						('genre',		 [
											tag['name']
											for tag in enclose((
												res['artist']['tags'] if not isinstance(res['artist'].get('tags', ""), basestring) else 
												{'tag' : []} 
											)['tag'])
										]),
						('mbid',		 mbid),
						('biography',	 HTMLParser.unescape.__func__(HTMLParser, bio1 + bio2)),
						('thumb',		sorted([img['#text'] for img in res['artist']['image'] if img['#text']], key = lambda img: "{0:0>10}".format(img.split('/')[-2] if len(img.split('/')) else "0"), reverse = True)),
					))
				}
	return inf
	
def lastfm_album(album, mbid):
	data	=  geturl_delay("http://ws.audioscrobbler.com/2.0/?method=album.getinfo&mbid={0}&api_key=6a95f3c9de1a78a960f62d7d76cc94c1&format=json".format(mbid))
	try:
		res		= json.loads(data)
	except exceptions.ValueError,e:
		print ("JSON::", data)
		raise
		
	#pprint.pprint(res)
	if "error" in res:
		inf = {}
	else:
		enclose = lambda  x: [x] if isinstance(x, dict) else x
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
					(rel["type"],  tidy(rel.target))
					for rel in stringer(item.find('relation-list', {'target-type' :"url"}), 'findAll', 'relation')
			)
	artists = [
				{
					"name"			: tidy(art.artist.find('name')),
#					"sort-name"		: tidy(art.artist.find('sort-name')),
					"mbid"			: art.artist['id'],
					'yearsactive'	: [tidy(art.begin)] + ([tidy(art.end)] if tidy(art.end) else []),

				}
				for art in stringer(item.find('relation-list', {'target-type' :"artist"}), 'findAll', 'relation', {'type' : 'member of band'})
		]

	inf =  {
		'artist'		: dict((
			('name',		 artist), 
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
	
def brainz_lookup_release_mb(artist, albums, countries):
	soup = BeautifulStoneSoup(brainz_query_direct("release", [lucene_query_iter(
		[{'release': album}  for album in albums], 
		[{'artist' : artist}],
		[{'country': country}  for country in countries], 
	)]))
	soup_mbids = soup.findAll("release")

	for artistf in soup_mbids:
		disamb = artistf.find('disambiguation')
		if disamb and disamb > 0:
			print "\t{0}, {1}, {2}  - {3} ({4}) {5}".format("??", clean(artist), tidy(artistf.find('name')), artistf['ext:score'], tidy(disamb), artistf['id'])

	if not soup_mbids:
		raise ScaperException("MB", clean(artist), "MBID not found")
	mbid_map = collections.defaultdict(set)
	for soup_mbid in soup_mbids:
		if soup_mbid['ext:score'] == "100":
			mbid_map[tidy(soup_mbid.title)].add(soup_mbid["id"])
	
	return mbid_map


	
def brainz_lookup_artist(artist, mbid, albums, classical = False):
	print (clean(artist), mbid, clean(str(albums)))
	if artist and not mbid:
		mbid = brainz_lookup_artist_mb(artist, albums, classical)

	if mbid:
		 return brainz_lookup_artist_by_mb(artist, mbid, classical)
	else:
		return None, {}



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
			return None
		except Exception,e:
			print "**Exception**********", e
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
	
	print "&&" 
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

def scrape_albums(albums):
	import codecs
	with codecs.open("C:/temp/albums.xml", "w", encoding='utf8') as fo:		
		fo.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<musicdb>\n')
		for album, mbid in albums.iteritems():
			print clean(album)
			tmp = lastfm_album(album, 	mbid)
			fo.write(unquote(encode(tmp)))
			fo.flush()
		fo.write("\n</musicdb>\n")


##############################################################

if __name__ == "__main__":
	import codecs
	class flushfile(object):
		def __init__(self, f):
			self.f = f
		def write(self, x):
			self.f.write(x)
			self.f.flush()

	import sys
	sys.stdout = flushfile(sys.stdout)
	
	
	pprint.pprint( lastfm_album(u'Communique', 	'e42b0f81-9191-389c-9ae7-0ad279674a64') )
	
	print "??"
	print
	print brainz_lookup_release_mb('AC/DC', ['Back In Black', 'Dirty Deeds Done Cheap'], [])
	raise 1
	

	if 0:
		pprint.pprint(lastfm_artist('Birds of Tokyo', "8eec195f-d357-4e0a-bcc7-74fd5c462e6e"))
		raise 1
		print encode(discogs_lookup_artist("Chicago", "", "http://www.discogs.com/artist/Chicago+(2)"))
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
		('Kabalevsky, Dmitri Borisovich', '96c39679-7de4-48d1-a9ea-d8840296bb73', set([])),
	)	
	aggregate(sorted(infs), codecs.open('c:/temp/of.xml', 'w',encoding='utf8'), classical = True)
	print threading.enumerate()	

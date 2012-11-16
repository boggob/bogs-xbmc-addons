import	urllib2 , urllib 
import	re
import	collections
from	BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString
import pprint
import json
 
def strings(node):
	return " ".join(
		str(n).strip()
		for n in node.contents
		if isinstance(n,NavigableString)
	)
	
 
def jsonc(st):
	for i,o in (
		('true', 'True'),
		('false', 'False'),
		('null', 'None')
	):
		st = st.replace(i,o)
	return eval(st)
def geturl(url):
	#, headers = {"Accept-Encoding":"gzip"}
	print "getting: %s" % url
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def pretty(st):
	return BeautifulSoup(st, convertEntities=BeautifulSoup.HTML_ENTITIES).prettify().strip()
	
class Scraper(object):
	URLS = {
		"base"		: "http://rageagain.com/",
	}
	
	def __init__(self, folders, play, record):
		self.folders	= folders
		self.play		= play
		self.record		= record
		
	def menu(self, params):
		contents =  geturl(self.URLS['base'] + "#/home")
		soup = BeautifulSoup(contents)
		out = [
				#/episode/top200/1
			{ 
				"url"	: self.URLS['base']+ "tracks/getTop200.json", 
				"title"	: 'Top 200', 
				"folder"	: True,
				"path"	: "browse2",
			}
		]
		
		for item in soup.find('div', {"id":"episodes"}).findAll("a", {"class":"playlist"}):
			print item
			val = { 
				"url"	: self.URLS['base']+ "tracks/getByPlaylistId/{0}.json".format(item["data-playlist_id"]), 
				"title"	: pretty("{0}:{1}:{2}".format(strings(item.findPrevious('h2').span), " ".join(strings(item).split()[::-1]), strings(item.find()))), 
				"folder"	: True,
				"path"	: "browse",
			}
			print val
			out.append(val)
		self.folders(out)
	
	def browse(self, params):
		dat		= geturl(params['url'])
		print dat
		tracks		= jsonc(dat)
		pprint.pprint(tracks)
		
		out = []
		for item, data in sorted(tracks["tracks"].iteritems()):
			print item
			val = { 
				"url"	: self.URLS['base']+ "youtube/get_sources.json?track_id={0}".format(item), 
				"title"	: data.get("artist", "") + ":" + data.get("track",""), 
				"folder"	: False,
				"info"		: {"duration": ":".join(data.get("timeslot", "").split(":")[:-1])},
				"path"	: "details",
			}
			print val
			out.append(val)
		self.folders(out)
	
	def browse2(self, params):
		dat		= geturl(params['url'])
		print dat
		tracks		= jsonc(dat)
		pprint.pprint(tracks)
		
		out = []
		for data in sorted(tracks["tracks"]):
			print data
			val = { 
				"url"	: self.URLS['base']+ "youtube/get_sources.json?track_artist={0}&track_name={1}&track_label={2}".format(urllib.quote(data['artist'] or ""), urllib.quote(data['track'] or ""),urllib.quote(data['label'] or "")), 
				"title"	: data.get("artist", "") + ":" + data.get("track",""), 
				"folder"	: False,
#				"info"		: {"duration": ":".join(data.get("timeslot", "").split(":")[:-1])},
				"path"	: "details",
			}
			print val
			out.append(val)
		self.folders(out)
		
	def details(self, params):
		track		= jsonc(geturl(params['url']))
		pprint.pprint(track)
		
		out = []
		youtube_dat	= geturl("http://www.youtube.com/get_video_info?el=embedded&splay=1&video_id={0}&eurl=http%3A%2F%2Frageagain.com%2F&asv=3&hl=en_GB".format(track["sources"][0]["id"]))
		resp		= dict([(k,urllib.unquote(v)) for p in youtube_dat.split('$')[-1].split('&') for k,v in [p.split('=')] ])
		print "*" *80
		pprint.pprint(resp)
		outs		= resp["url_encoded_fmt_stream_map"].split(',')
		
		print "!" *80
		pprint.pprint(outs)
		out			= outs[1]
		outd		= dict([(k,urllib.unquote(v)) for p in out.split('&') for k,v in [p.split('=')]])
		
		print "~" *80
		pprint.pprint(outd) 
		ret			= outd['url']
		
		val = {
			"url"		: ret + '&signature=' + outd['sig'],
			"duration"	: track['sources'][0]["duration"],
			"name"		: track['sources'][0]["title"],
		}
		print val
		self.play(val)
		


	def playitems(self, params):
		print params
		print "@1"	
		soup = BeautifulSoup(geturl(params['url']))
		id = dict(it.split('=',1) for it in urllib.unquote(soup.find("embed")['flashvars']).split('&'))['vid']
		if 0:
			soup = BeautifulStoneSoup(geturl("http://cosmos.bcst.yahoo.com/rest/v2/pops;id=%s;lmsoverride=1" % id))
			val = {
				"title" : soup.channel.item.title,
				"descr"	: soup.channel.item.description,
				"date"	: soup.channel.item.find("media:pubStart"),
			}
		print "@@"	
		soup = BeautifulStoneSoup(geturl("http://cosmos.bcst.yahoo.com/rest/v2/pops;id=%s;lmsoverride=1;element=stream;bw=1200" % id))
		print soup
		item = soup.channel.item.find('media:content')
		val = {
			"url"		: "%s playpath=%s swfurl=%s swfvfy=true" % (item['url'], item['path'], "http://d.yimg.com/m/up/ypp/au/player.swf"),
			"duration"	: item['duration'],
			"name"		: re.sub(r'<!\[CDATA\[([^\]+])\]\]', '' , soup.channel.item.title.contents[0])
		}
		print ("@2"	,  val)
		if "record" in params:
			self.record(val)
		else:
			self.play(val)
		

		
		

if __name__ == "__main__":
	pass
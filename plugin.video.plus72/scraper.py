import	urllib2 , urllib 
import	re
import	collections
from	BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString
import threading
import pprint

try:
    import json
except ImportError:
    import simplejson as json
 

def geturl(url):
	#, headers = {"Accept-Encoding":"gzip"}
	print "getting: %s" % url
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def pretty(st):
	return BeautifulSoup(st, convertEntities=BeautifulSoup.HTML_ENTITIES).prettify().strip()
	
class Scraper(object):
	URLS = {
		"base"		: "http://au.tv.yahoo.com",
	}
	
	def __init__(self, folders, play, record):
		self.folders	= folders
		self.play		= play
		self.record		= record
		
	def menu(self, params):
		contents =  geturl(self.URLS['base'] + "/plus7/browse/")
		soup = BeautifulSoup(contents)
		out = []
		for item in soup.find('div', {"id":"atoz", "class" : "bd"}).findAll("li"):
			if dict(item.attrs).get("class", None) != "letter":
				print item
				val = { 
					"url"	: item.a["href"], 
					"title"	: pretty(item.h3.a.string),
					"still"	: item.a.img["src"] ,
					"path"	: "browse",
					"folder"	: True,
				}
				print val
				out.append(val)
		return self.folders(out)
	

	
	def browse(self, params):
		soup = BeautifulSoup(geturl(params['url']))
		
		ginf = {}
		hd = str(soup.find('div', {"class" :"mod tv-plus7-info"})).replace('\n', '')
		print ("Y1", hd)
		ginf['genre'] =  re.findall(r"Genre:\s*<strong>(.*?)</strong>", str(soup))[0]
		ginf['mpaa'] =  re.findall(r"Classified:\s*<strong>(.*?)</strong>", str(soup))[0]
		print ("info11", ginf)
		out = []
		for item in soup.find("ul", {"id": "related-episodes", "class" : "featlist"}).findAll("li", {"class" : "clearfix"}):
			#Folders
			print ("!@", item)
			inf = ginf.copy()
			inf["plot"] = (item.div.p.string or "").strip()
			val = { 
				"url"		: "%s%s" % (self.URLS['base'], item.a["href"]), 
				"title"		: pretty(" - ".join(it.string.strip() for it in item.div.h3.findAll('span') if it.string )),
				"path"		: "playitems",
				"still"		: item.a.img["src"] ,
				"info"		: inf,
				"folder"	: False,
			}
			out.append(val)
				
		
		return self.folders(out)


	def playitems(self, params):
		print params
		html = geturl(params['url'])
		id =  re.findall(r'mediaItems": *\[ *{"id":"([^"]+)"', html)[0]
		url = """http://video.query.yahoo.com/v1/public/yql?q=SELECT%20*%20FROM%20yahoo.media.video.streams%20WHERE%20id%3D%22{0}%22%20AND%20format%3D%22mp4%2Cflv%22%20AND%20protocol%3D%22rtmp%2Chttp%22%20AND%20plrs%3D%22xTpWh6wmyPBDXqHw0H0TcW%22%20AND%20offnetwork%3D%22false%22%20AND%20site%3D%22autv_plus7%22%20AND%20lang%3D%22en-AU%22%20AND%20region%3D%22AU%22%20AND%20override%3D%22none%22%3B&env=prod&format=json&callback=YUI.Env.JSONP.yui_3_4_1_4_1356123537781_541""".format(id)
		print url
		vid_json = geturl(url)
		print vid_json
		item = json.loads(re.sub(r'^[^(]+\((.*)\);', r'\1', vid_json))
		mediaObj	= item['query']['results']['mediaObj'][0]
		stream		= mediaObj['streams'][0]
		
		val = {
			"url"		: '%s playpath=%s swfurl=%s swfvfy=true buffer=60000' % (stream['host'], stream['path'], "http://l.yimg.com/rx/builds/3.6.6.8916/assets/player.swf"),
			"duration"	: int(stream['duration']),
			"name"		: mediaObj['meta']['title']
		}
		print ("@2"	,  val)
		if "record" in params:
			return self.record(val)
		else:
			return self.play(val)


if __name__ == "__main__":
	pass
import	urllib2 , urllib 
import	re
import	collections
from	BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString
import threading
import pprint
 

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
		self.folders(out)
	

	
	def browse(self, params):
		soup = BeautifulSoup(geturl(params['url']))
		
		ginf = {}
		hd = str(soup.find('div', {"class" :"mod tv-plus7-info"})).replace('\n', '')
		print ("Y1", hd)
		ginf['genre'] =  re.findall("Genre: *<strong>(.*?)</strong>", hd)[0]
		ginf['mpaa'] =  re.findall("Classified: *<strong>(.*?)</strong>", hd)[0]
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
				
		
		self.folders(out)


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
		item = soup.channel.item.find('media:content')
		val = {
			"url"		: "%s playpath=%s swfurl=%s swfvfy=true" % (item['url'], item['path'], "http://d.yimg.com/m/up/ypp/au/player.swf"),
			"duration"	: item['duration'],
			"name"		: soup.channel.item.title.contents[0]
		}
		print ("@2"	,  val)
		if "record" in params:
			self.record(val)
		else:
			self.play(val)
		

		
		

if __name__ == "__main__":
	pass
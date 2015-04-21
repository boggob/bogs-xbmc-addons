import	urllib2 
from	BeautifulSoup import BeautifulSoup

def geturl(url):
	#, headers = {"Accept-Encoding":"gzip"}
	print "getting: %s" % url
	import httplib
	httplib.HTTPConnection._http_vsn = 11
	httplib.HTTPConnection._http_vsn_str = 'HTTP/1.1'	
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def get_str(item):
	return item.string if item else ""	

ADDON_ID='plugin.video.abc-iview2'



class Scraper(object):
	URLS = {
		"a-z"		: "https://tviview.abc.net.au/iview/feed/sony/?keyword=0-Z",
	}
	
	def __init__(self, folders, play, record):
		self.folders	= folders
		self.play		= play
		self.record		= record
		
		
	def menu(self, params):
		out = []
		xml = geturl(Scraper.URLS["a-z"])
		soup = BeautifulSoup(xml)
		
		print "^^^^^"
		for item in soup.findAll('asset'):
			print "%%%%", get_str(item.asseturl), item		
			if item.asseturl:
				out.append(
					{
						"url"		: get_str(item.asseturl)[:], 
						"title"		: get_str(item.title)[:],
						"path"		: "playitems",
						"still"		: get_str(item.imageurl)[:],
						"info"		: {
							"plot"		: get_str(item.description),
							"duration"	: int(get_str(item.duration))/10,
							"date"		: get_str(item.datecreated).split("T"),
							
						},					
						
						"folder"	: False,
					}
				)
		print out		
		self.folders(out)
	

	

	def playitems(self, params):
		

		val = {
			"url"		: params["url"],
			"name"		: params["name"]
		}
		print ("@2"	,  val)
		if "record" in params:
			self.record(val)
		else:
			self.play(val)


if __name__ == "__main__":
	pass
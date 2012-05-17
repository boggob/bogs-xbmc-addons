import	urllib2 ,urllib
import	re
from	time import localtime, strftime, gmtime
from	BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString
from resources.ooyala.ooyalaCrypto import ooyalaCrypto
from ooyala.MagicNaming import MagicNaming


def geturl(url):
	print ("getting url", url)
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def jsonc(st):
	print ("getting json", st)
	for i,o in (
		('true', 'True'),
		('false', 'False'),
		('null',  'None'),
	):
		st = st.replace(i,o)
	return eval(st)


class MenuItems(object):
	def __init__(self):
		self.base2				= 'http://www.theage.com.au/tv/'

	def menu_main(self, params, addDir):
		mode = params.get('mode', "0")
		out = []
		if mode =="0":
			for item in  jsonc(geturl(self.base2 + 'genre/get_genre_json')):
				rec = {
					"title"	: item["name"], 
					"url"	: "{base}genre/get_genre_data/{genre}/{count}".format(base = self.base2,genre =  urllib.quote(item["name"].replace(' ' , '-')), count = 0), 
					"still": "DefaultFolder.png",
					"genre"		: item["name"] 
				}
				addDir({"name" : rec['title'], "url" : rec["url"], "mode" : int(params.get("mode", "0")) + 1, "done" : 0}, True, rec.get('info',{}), rec['still'])				
			
		elif mode =="1":
			res = jsonc(geturl(params["url"]))
			genres, counts,  = params["url"].split("/")[-2:]
			done = int(params["done"]) + len(res["item"])
			if res["totalResults"] > done:
				addDir({"name" : "Next->{0}/{1}".format(done, res["totalResults"] ), "url" : "{base}genre/get_genre_data/{genre}/{count}".format(base = self.base2,genre =  genres, count = int(counts)+1) , "mode" : params["mode"], "done" : done}, True)
		
			for item in  res["item"]:
				rec = {
					"title"	: item["title"], 
					"url"	: (self.base2 + "episode/getEpisodeRelated?showName=" + urllib.quote(item["title"])),
					"still": ((item.get('largeThumb', "") or item.get('thumbnail', "") or "DefaultFolder.png") + ".jpg").replace(".jpg.jpg", ".jpg").replace('\\',''),
					"info"	: {
						"plot"		: item["description"],
						"genre"		: item["genre"],
						"duration"	: "%s:%s:00" % (item['duration'][1:-1].split(':')[0],item['duration'][1:-1].split(':')[1])
					}
				}
				if "embedCode" in item and item.get("episodeLatestUID", None) is None:
					addDir({"name" : rec['title'], "url" : item["embedCode"] , "mode" : int(params["mode"]) + 2}, True, rec.get('info',{}), rec['still'])
				else:
					addDir({"name" : rec['title'], "url" : rec["url"], "mode" : int(params["mode"]) + 1}, True, rec.get('info',{}), rec['still'])

		elif mode =="2":		
			print geturl(params["url"])
			for item in  jsonc(geturl(params["url"])):
				rec = {	
					"title"	: item["title"], 
					"url"	: item["embedCode"], 
					"still": ((item.get('largeThumb', "") or item.get('thumbnail', "") or "DefaultFolder.png") + ".jpg").replace(".jpg.jpg", ".jpg").replace('\\',''),
					"info"	: {
						"playcount"	: item['playsTotal'],   
						"season"	:	item["season"],
						"episode " : item['episodeNumber'],
						"plot"		: item["description"],
						"genre"		: item["genre"],
						"duration"	: "%s:%s:00" % (item['duration'][1:-1].split(':')[0],item['duration'][1:-1].split(':')[1])
					}
				}
				addDir({"name" : rec['title'], "url" : rec["url"], "mode" : int(params["mode"]) + 1}, False, rec.get('info',{}), rec['still'])				
			
		
		return out				
					
	def menu_play(self, page):
		app			= "ondemand?_fcs_vhost=cp115717.edgefcs.net"
		rtmp		= "rtmp://%s/%s" % (BeautifulSoup(geturl("http://cp115717.edgefcs.net/fcs/ident")).find("ip").string.strip(), app)
		embed_code	= page
		smil		= geturl('http://player.ooyala.com/nuplayer?autoplay=1&hide=all&embedCode=%s' % embed_code)
		decry_smil	= ooyalaCrypto().ooyalaDecrypt(smil)
		playpath	=  "mp4:%s" % (MagicNaming().getVideoUrl(decry_smil)[0].split(':')[-1])
		return "%s app=%s playpath=%s" % (rtmp, app, playpath), (rtmp, app, playpath)


			

			

if __name__ == "__main__":
	from  pprint import PrettyPrinter, pprint

	m = MenuItems()
	print "#" * 20
	menues = []
	m.menu_tree([], menues)
	PrettyPrinter(indent=1).pprint(menues)
	print "#" * 30
	leafs = [i for i in menues if not m.menu_main(i)["children"]]
	print "#" * 30
	shows = list(m.menu_shows(m.menu_main(leafs[30])["url"]))
	PrettyPrinter(indent=1).pprint(shows)
	print "#" * 30
	PrettyPrinter(indent=1).pprint(m.menu_play(shows[2]["url"]))
else:
	SCRAPER = MenuItems()

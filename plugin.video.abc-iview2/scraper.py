import	urllib2
import collections
from	BeautifulSoup import BeautifulSoup

ADDON_ID='plugin.video.abc-iview2'


def geturl(url):
	#, headers = {"Accept-Encoding":"gzip"}
	print "getting: %s" % url
	import httplib
	httplib.HTTPConnection._http_vsn = 11
	httplib.HTTPConnection._http_vsn_str = 'HTTP/1.1'
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def get_str(item):
	return item.string if item else ""



def group_titles(data):
	out = collections.defaultdict(list)

	for d in data:
		parts = d["title"].split("Series")
		if len(parts) > 1:
			out[parts[0]].append(d)
		else:
			parts = d["title"].split("Episode")
			if len(parts) > 1:
				out[parts[0]].append(d)
			else:
				parts = d["title"].split(":")
				if len(parts) > 1:
					out[parts[0]].append(d)
				else:
					out[d["title"]].append(d)

	return out



class Scraper(object):
	URLS = {
		"a-z"		: "https://tviview.abc.net.au/iview/feed/sony/?keyword=0-Z",
	}

	def __init__(self, folders, play, record):
		self.folders	= folders
		self.play		= play
		self.record		= record


	def menu(self, params):

		xml = geturl(Scraper.URLS["a-z"])
		soup = BeautifulSoup(xml)


		print "^^^^^"
		out 		= collections.defaultdict(list)
		all_items	= []
		for item in soup.findAll('asset'):
			print "%%%%", get_str(item.asseturl), item
			if item.asseturl:
				genres	= sorted(si["name"] for si in item.findAll('category'))
				record	= {
							"url"		: get_str(item.asseturl)[:],
							"title"		: get_str(item.title)[:],
							"still"		: get_str(item.imageurl)[:],
							"info"		: {
								"plot"		: get_str(item.description),
								"duration"	: get_str(item.duration),
								"date"		: get_str(item.datecreated).split("T"),
								"mpaa"		: get_str(item.rating),
								"genre"		: " / ".join(genres),
							},
							"path"		: "playitems",
							"folder"	: False,
							"data"	: False,

						}
				all_items.append(record)
				for g in genres:
					out[g].append(record)



		folders = (
					[
						{
							"title" 	: "All",
							"url" 		: "All",
							"path"		: "menu_all",
							"folder"	: True,
							"data"		: sorted(all_items, key = lambda a: a['title'])
						},

					 ] + (
						 [
							{
								"title" 	: g,
								"url" 		: g,

								"path"		: "menu_genres",
								"folder"	: True,
								"data"		: sorted(v, key = lambda a: a['title'])
							}
							for g, v  in sorted(out.iteritems())
						 ]

					 )
					)

		self.folders(folders)

	def menu_genres(self, params):
		print params
		contents = params["data"]
		print 	contents

		self.folders(eval(contents))

	def menu_all(self, params):
		print params
		contents = params["data"]
		print 	contents

		self.folders(eval(contents))



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
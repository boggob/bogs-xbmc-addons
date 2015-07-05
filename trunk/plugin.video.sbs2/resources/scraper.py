import	datetime
import	urllib2 
import	re
from	time import  strftime, gmtime
from	BeautifulSoup import BeautifulSoup


def get_str(item):
	return item.string if item else ""	


def geturl(url):
	#, headers = {"Accept-Encoding":"gzip"}
	print "getting: %s" % url
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def jsonc(st):
	for i,o in (
		('true', 'True'),
		('false', 'False')
	):
		st = st.replace(i,o)
	return eval(st)


class Scraper(object):
	def __init__(self, folders, play, record, bitrate):
		self.folders	= folders
		self.play		= play
		self.record		= record
		self.bitrate	= bitrate
		
	def menu_main(self, params):
		out = []
	
		for days in [1, 7, 14, 356]:
			dates1 =  (datetime.datetime.utcnow() - datetime.datetime(1970,1,1))
			dates2 =  dates1 - datetime.timedelta(days)
		
			rec  =  {
					"title" 	: "Last {} days".format(days),
					"url"		: 'http://www.sbs.com.au/api/video_feed/f/dYtmxB/section-programs?form=json&byPubDate={}~{}&range=1-5000'.format(int(dates2.total_seconds() * 1000), int(dates1.total_seconds() * 1000)),
					
					"path"		: "menu_shows",					
					"folder"	: True,
				}
				
			out.append( rec )
		self.folders(out)

		



	def menu_shows(self, params):
		print params
		res = geturl(params["url"])
				
		jsres = jsonc(res)
		print "%%menu_shows", res
		
		out = []
		for entry in sorted(jsres["entries"], key = lambda x: x["title"]):
			hours, remainder = divmod(int(entry["media$content"][0]['plfile$duration']), 3600)
			minutes, seconds = divmod(remainder, 60)
			#entry["description"], entry['plmedia$defaultThumbnailUrl']
			
			rec  =  {
				"title" 		: entry["title"],
				"still"			: sorted(entry["media$thumbnails"], key = lambda e: e["plfile$height"])[-1]["plfile$downloadUrl"].replace("\\", "") if entry["media$thumbnails"] else None,
				"url"			: 'http://www.sbs.com.au/ondemand/video/single/{}?context=web'.format(entry["id"].split('/')[-1]),
				"info"			: {
					"Country "	: entry.get("pl1$countryOfOrigin", "?"),
					"plot"		: entry["description"],
					"duration"	: "%s" % ((hours * 60) + minutes),
					"mpaa"		: entry.get("media$ratings"),
					"date"		: strftime("%d.%m.%Y",gmtime(entry["pubDate"]/1000)),
					"genre"		: "%s,%s" % (entry.get("pl1$countryOfOrigin", "?"), entry["media$keywords"]),
				},
				
				"path"		: "menu_play",					
				"folder"	: False,
				
			}
				
			try:
				rec["info"]["mpaa"]		= entry["media$ratings"][0]['rating']
			except Exception,e:
				rec["info"]["mpaa"]		= '?'
			print rec	
			out.append( rec )
		self.folders(out)

			

	def menu_play(self, params):
		print params
		contents = geturl(params["url"])
		print contents
		
		out = {}
		fmt = None
		for mtch in re.findall(r'"standard":"(.*)"', contents, re.MULTILINE):
			contents2 =  geturl(mtch.split("&ord=")[0].replace('\\', ''))
			print contents2
			soup = BeautifulSoup(contents2)
			
			if contents2.find('.flv') > -1:

				for item in soup.findAll('video'):
					out[int(item["system-bitrate"])] = item["src"]
				raise out
			else:
				
				if str(soup).find('akamaihd') <= -1:
					for item in soup.findAll('video'):
						out[int(item["system-bitrate"])] = item["src"]
				else:
					for item in soup.findAll('video'):
						splts	= item["src"].split("/managed/")[1].split(',')[0]
						tail= splts if splts.endswith(".mp4") else "{}1500K.mp4".format(splts)
						print "%^^&", item["src"], splts
						val		= {
							"url"		: "http://sbsauvod-f.akamaihd.net/SBS_Production/managed/{}?v=&fp=&r=&g=".format(tail),
							"name"		: item["title"]
						}
						print ("@2"	,  val)
						if "record" in params:
							self.record(val)
						else:
							self.play(val)
						break

		
		

if __name__ == "__main__":
	pass

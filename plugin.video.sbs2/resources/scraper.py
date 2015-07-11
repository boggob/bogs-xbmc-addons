import	datetime
import	urllib2, urllib
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

		for days in [1, 7, 14, 28, 356]:
			dates1 =  (datetime.datetime.utcnow() - datetime.datetime(1970,1,1))
			dates2 =  dates1 - datetime.timedelta(days)

			rec  =  {
					"title" 	: "Last {} days".format(days),
					"url"		: 'http://www.sbs.com.au/api/video_feed/f/dYtmxB/section-programs?form=json&byPubDate={}~{}&range=1-5000'.format(int(dates2.total_seconds() * 1000), int(dates1.total_seconds() * 1000)),

					"path"		: "menu_shows",
					"folder"	: True,
				}

			out.append( rec )

		res = geturl("http://www.sbs.com.au/ondemandcms/sitenav")
		jsres = jsonc(res)
		print  jsres.get("sitenav", [])

		for title, path, url in [
			("Programs",	"menu_shows2",	"http://www.sbs.com.au/api/video_programlist/?upcoming=1"),
			("Last Chance",	"menu_shows",	"http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-video-lastchance?form=json&count=true&byCategories=Section%2FPrograms,Drama%7CComedy%7CDocumentary%7CArts%7CEntertainment%7CFood%7CFactual%7CMovies&sort=expirationDate%7Casc&range=1-200"),

		]:
			rec  =  {
					"title" 	: title,
					"url"		: url,

					"path"		: path,
					"folder"	: True,
				}

			out.append( rec )

		for title, url in (
			[ 	(
					"Movie: {}".format(child["title"]),
					"http://www.sbs.com.au/ondemandcms/sections/%s" % (child["href"].replace("\\", ""))
				)
				for top in jsres.get("sitenav", [])
				if top["title"] == "Movies"
				for section in top["groups"]
				if section["title"] in  ("Genres",)
				for child in section["children"]
			]
		):
			rec  =  {
					"title" 	: title,
					"url"		: url,

					"path"		: "movie_shows",
					"folder"	: True,
				}

			out.append( rec )

		for title, url in (
			[ 	(
					"Movie: {}".format(child["title"]),
					"http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-section-programs?form=json&count=true&sort=metrics.viewCount.lastDay|desc&range=1-12&byCategories=Film,Section/Programs&byRatings=&facets=1&byCustomValue={collections}{%s}" % (urllib.quote_plus(child["title"]))
				)
				for top in jsres.get("sitenav", [])
				if top["title"] == "Movies"
				for section in top["groups"]
				if section["title"] in  ("Collections",)
				for child in section["children"]
			]
		):
			rec  =  {
					"title" 	: title,
					"url"		: url,

					"path"		: "menu_shows",
					"folder"	: True,
				}

			out.append( rec )

		self.folders(out)


	def movie_shows(self, params):
		print params
		contents = geturl(params["url"])
		print 	contents
		soup = BeautifulSoup(contents)

		for mtch in soup.findAll('div', {"data-content-type":"video"}):
			print mtch["data-filter"]
			#"http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-section-programs?form=json&count=true&sort=metrics.viewCount.lastDay|desc&byCustomValue={%s}{%s}" % (section["title"].lower(), child["title"])
			url = "http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-section-programs?form=json&count=true&sort=metrics.viewCount.lastDay|desc&byCategories=Section%2FPrograms,Film,{}".format(urllib.quote_plus(mtch["data-filter"]))
			self._menu_shows({"url" : url})




	def _menu_shows(self, params):
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

	def menu_shows(self, params):
		return self._menu_shows(params)


	def menu_shows2(self, params):
		print params
		res = geturl(params["url"])

		jsres = jsonc(res)
		print "%%menu_shows", res

		out = []
		for entry in sorted(jsres["entries"], key = lambda x: x["name"]):
			if "media$content" in entry:
				hours, remainder = divmod(int(entry["media$content"][0]['plfile$duration']), 3600)
				minutes, seconds = divmod(remainder, 60)
				duration = "%s" % ((hours * 60) + minutes)
			else:
				duration = None

			enc = entry.get("media$content") and entry["media$content"][0]["plfile$assetTypes"] == ['Encrypted']
			rec  =  {
				"title" 		: "{}{}".format( entry["name"], " [Encrypted]" if enc else ""),
				"still"			: entry["thumbnails"]['1280x720'].replace("\\", "") if entry["thumbnails"] else None,
				"url"			: entry.get('url', 'http://www.sbs.com.au/ondemand/video/single/{}?context=web'.format(entry["id"])).replace("\\", "") ,
				"info"			: {
					"plot"		: entry["description"],
					"duration"	: duration,
					"date"		: strftime("%d.%m.%Y",gmtime(entry["pubDate"]/1000)) if "pubDate" in entry else None,
				},

				"path"		: (
								"menu_shows"	if duration is None else
								"menu_play_enc" if entry.get("media$content") and entry["media$content"][0]["plfile$assetTypes"] == ['Encrypted'] else
								"menu_play"
							),
				"folder"	: duration is None,

			}

			try:
				rec["info"]["mpaa"]		= entry["media$ratings"][0]['rating']
			except Exception,e:
				rec["info"]["mpaa"]		= '?'
			print rec
			out.append( rec )
		self.folders(out)

	def menu_play(self, params):
		self._menu_play(params, enc = False)

	def menu_play_enc(self, params):
		self._menu_play(params, enc = True)

	def _menu_play(self, params, enc = False):
		print params
		contents = geturl(params["url"])
		print contents


		search = r'"standard":"([^"]*)"' if not enc else '"([^"]*manifest=m3u[^"]*)"'

		out = {}
		for mtch in re.findall(search, contents, re.MULTILINE):
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
						if not enc:
							splts	= item["src"].split("/managed/")[1].split(',')[0]
							tail= splts if splts.endswith(".mp4") else "{}1500K.mp4".format(splts)
							print "%^^&", item["src"], splts
							val		= {
								"url"		: "http://sbsauvod-f.akamaihd.net/SBS_Production/managed/{}?v=&fp=&r=&g=".format(tail),
								"name"		: item["title"]
							}
						else:
							splts		= item["src"].split("&")[0]
							contents3	= geturl(splts)
							print contents3

							url			= contents3.split("\n")[2]


							val		= {
								"url"		: url,
								"name"		: item["title"]
							}


						print ("@2"	,  val)
						if "record" in params:
							self.record(val, audio=enc)
						elif "recordFlv" in params:
							self.record(val, flv=True, audio=enc)
						else:
							self.play(val)
						break




if __name__ == "__main__":
	pass

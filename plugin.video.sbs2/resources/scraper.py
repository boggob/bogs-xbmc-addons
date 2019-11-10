import	datetime
import	urllib2, urllib
import	re
import	os, os.path
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
		('false', 'False'),
		('null', 'None')
	):
		st = st.replace(i,o)
	return eval(st)


def get_date(field):
	if isinstance(field, long):
		field = field/1000



	if isinstance(field, (int, long)):
		print "^%", field
		return strftime("%d.%m.%Y", gmtime(field))
	else:
		return ".".join(field.split('T')[0].split("-")[::-1])

class Scraper(object):
	def __init__(self, folders, play, record, bitrate, path):
		self.folders	= folders
		self.play		= play
		self.record		= record
		self.bitrate	= bitrate
		self.path		= path

	def menu_main(self, params):
		out = []

		res = geturl("http://www.sbs.com.au/ondemandcms/sitenav")
		jsres = jsonc(res)
		print  jsres.get("sitenav", [])

		for title, path, url in [
			("Programs",	"menu_shows2",	"http://www.sbs.com.au/api/video_programlist/?upcoming=1"),
			("Last Chance",	"menu_shows",	"http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-video-lastchance?form=json&count=true&byCategories=Section%2FPrograms,Drama%7CComedy%7CDocumentary%7CArts%7CEntertainment%7CFood%7CFactual%7CMovies&sort=expirationDate%7Casc&range=1-2000"),

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
				if top and top["title"] == "Movies"
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
					"http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-section-programs?form=json&count=true&sort=metrics.viewCount.lastDay|desc&range=1-12&byCategories=Film,Section/Programs&byRatings=&facets=1&byCustomValue={collections}{%s}&range=1-5000" % (urllib.quote_plus(child["title"]))
				)
				for top in jsres.get("sitenav", [])
				if top and top["title"] == "Movies"
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
			url = "http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-section-programs?form=json&count=true&sort=metrics.viewCount.lastDay|desc&byCategories=Section%2FPrograms,Film,{}&range=1-5000".format(urllib.quote_plus(mtch["data-filter"]))
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
					#"date"		: strftime("%d.%m.%Y",gmtime(entry["pubDate"]/1000)),
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

	def menu_shows_prim(self, params):
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
			def conv_date(date):
				try:
					return datetime.datetime.fromtimestamp( date / 1000).isoformat()
				except Exception, e:
					return datetime.datetime.fromtimestamp( 0).isoformat()
				
			date	= ( 
						entry.get("seasons", []) 
						or 
						[{
							"seasonStartDate" : conv_date( entry.get('media$availableDate', 0)), 
							"seasonEndDate" : conv_date( entry.get('media$expirationDate', 0))
						}] 
					  )[0]
			enc		= entry.get("media$content") and entry["media$content"][0]["plfile$assetTypes"] == ['Encrypted']
			rec  =  {
				"content"			: ({entry.get("genre", None), entry.get("type", None)} - {None}) | set(entry.get("collections",[])),
				"date_end"			: "End_" + date['seasonEndDate'].split("T")[0].rsplit("-", 1)[0],
				"date_start"		: "Start_" + date['seasonStartDate'].split("T")[0].rsplit("-", 1)[0],
				"title" 			: "{}{}".format( entry["name"], " [Encrypted]" if enc else ""),
				"still"				: entry["thumbnails"]['1280x720'].replace("\\", "") if entry.get("thumbnails") and entry["thumbnails"].get("1280x720") else None,
				"url"				: entry.get('url', 'http://www.sbs.com.au/ondemand/video/single/{}?context=web'.format(entry["id"])).replace("\\", "") ,
				"info"				: {
					"plot"			: entry["description"],
					"duration"		: duration,
					"date"			: get_date(entry["latest_episode_available_date"] or entry['pubDate'])   if "latest_episode_available_date" in entry else None,
					"genre"			: entry.get("genre", None) or entry.get("type", None),
					"tagline"		: entry.get("genre", None) or entry.get("type", None),
				},

				"path"		: (
								"menu_shows"	if entry.get("type") != "program_oneoff" else
								"menu_play_enc" if entry.get("media$content") and entry["media$content"][0]["plfile$assetTypes"] == ['Encrypted'] else
								"menu_play"
							),
				"folder"	: duration is None,


			}

			try:
				rec["info"]["mpaa"]		= entry["media$ratings"][0]['rating']
			except Exception,e:
				rec["info"]["mpaa"]		= '?'
			print "%%&", rec
			out.append( rec )
		return out

	def menu_shows2(self, params):
		out = self.menu_shows_prim(params)


		agg = {
			c
			for o in out
			for c in o.get("content", [])
		}
		

		agg2 = {
			o.get("date_end", None)
			for o in out
		}

		agg3 = {
			o.get("date_start", None)
			for o in out
		}
	
		
		out = (
			[
			
				{
					"title" 			: a,
					"url"				: params['url'],

					"path"		: "menu_shows_end",
					"folder"	: True,
					"info"		: {}

				}

				for a in sorted(agg2)[:3]
			
			]
			+
			[
			
				{
					"title" 			: a,
					"url"				: params['url'],

					"path"		: "menu_shows_start",
					"folder"	: True,
					"info"		: {}

				}

				for a in sorted(agg3)[-3:]
			]
			+ 			
			[
				{
					"title" 			: a,
					"url"				: params['url'],

					"path"		: "menu_shows3",
					"folder"	: True,
					"info"		: {}

				}

				for a in sorted(agg)
			]
		)
	
		print "^^&@", out
		self.folders(out)

	def menu_shows3(self, params):
		print "<!!>", params
		out = self.menu_shows_prim(params)

		self.folders([o for o in out if params["name"] in o["content"]])

	def menu_shows_end(self, params):
		print "<!!>", params
		out = self.menu_shows_prim(params)

		self.folders([o for o in out if params["name"] == o["date_end"]])

	def menu_shows_start(self, params):
		print "<!!>", params
		out = self.menu_shows_prim(params)

		self.folders([o for o in out if params["name"] == o["date_start"]])

		

	def menu_play(self, params):
		self._menu_play(params, enc = False)

	def menu_play_enc(self, params):
		self._menu_play(params, enc = True)

	def _menu_play(self, params, enc = False):
		enc = True

		print params
		contents = geturl(params["url"])
		print contents


		search = r'"standard":"([^"]*)"' if not enc else '"([^"]*manifest=m3u[^"]*)"'

		out = {}
		for mtch in re.findall(search, contents, re.MULTILINE):
			url = mtch.split("&ord=")[0].replace('\\', '')
			if "http:"  not in url and "https:"  not in url:
				url = "http:" + url
			contents2 =  geturl(url)
			print "%smil", contents2
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
						subtitles = [(s["src"], s["type"])  for s in item.parent.findAll('textstream')]
						print "%captions", subtitles
						subtitle_files = []
						if subtitles:
							caption_dir = os.path.join(self.path, 'subtitles')
							if not os.path.exists(caption_dir):
								os.makedirs(caption_dir)
							
							for idx, subtitle in enumerate(subtitles):
								caption_file = os.path.join(caption_dir, "{}.txt".format(idx))
								with open(caption_file, 'w') as f:
									f.write(geturl(subtitle[0]))
									f.close()
								
								subtitle_files.append(caption_file)
							
					
						if not enc:
							splts	= item["src"].split("/managed/")[1].split(',')[0]
							tail= splts if splts.endswith(".mp4") else "{}1500K.mp4".format(splts)
							print "%^^&", item["src"], splts
							val		= {
								"url"				: "http://sbsauvod-f.akamaihd.net/SBS_Production/managed/{}?v=&fp=&r=&g=".format(tail),
								"name"				: item["title"],
								"subtitle_files"	: subtitle_files
							}
						else:
							splts		= item["src"].split("&")[0]
							contents3	= geturl(splts)
							print contents3

							urls		= contents3.strip().split("\n")[1:]
							urls_p		= [ (urls[i], urls[i+1]) for i in range(0, len(urls), 2)]
							print urls_p
							urls_s		= sorted(
											(data, url)
											for comm, url in urls_p
											for data in [int(comm.split('BANDWIDTH=')[-1].split(',')[0] or 0)]
										)
										
							print "URLS", urls_s
							url			= urls_s[-1][1]


							val		= {
								"url"				: url,
								"name"				: item["title"],
								"subtitle_files"	: subtitle_files
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

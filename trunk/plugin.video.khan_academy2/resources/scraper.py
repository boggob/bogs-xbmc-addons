import urllib, urllib2, httplib
import re
from  time import localtime
from BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString 
try:
    import json
except ImportError:
    import simplejson as json

def geturl(url):
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		return urllib2.urlopen(req).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

class MenuItems(object):
	def __init__(self):
		self.base				= 'http://www.khanacademy.org/api/v1/playlists'
		self.base2				= 'http://www.khanacademy.org/api/v1/topics/library/compact'
		self.base3				= 'http://www.khanacademy.org'

	def menu_main(self, *args):
		import string
		resp1 = json.loads(geturl(self.base2))
		out = []
		for rec in json.loads(geturl(self.base)):
			if rec["id"] in resp1:
				print resp1[rec["id"]]
				if resp1[rec["id"]]["children"]:
					pref = string.capwords(resp1[rec["id"]]["children"][0]["url"].split("/")[1].replace('---', ' & ').replace('-', ' ')) or "Art History"
					out.append(( "%s:%s" % (pref,  rec["title"].encode('ascii', 'replace')),  rec["id"], rec["description"]	)) 
		return out

	def menu_sub(self, page):
		conn = urllib.urlopen(self.base2)
		resp = json.load(conn)
		conn.close()
		return [(r["title"].encode('ascii', 'replace'),r["url"]) for r in resp[page]["children"]]

	def menu_shows(self, st):
		if st.find(":") > -1:
			url = st
		else:
			url = self.base3 + st
		print "^^%s" % url
		val = geturl(url)		
		return re.findall(r'"video_path": "([^"]+)",', val)[0]

	def menu_play(self, st):
		if st.find(":") == -1:
			url = self.base3 + st
			print url		
			val = geturl(url)	
			print re.findall(r'"video_path": "([^"]+)",', val)[0]
			return re.findall(r'"video_path": "([^"]+)",', val)[0]
		else:
			url = st
			print url
			val = BeautifulSoup(geturl(url))
			iframe =  val.findAll('iframe')[0]["src"]
			print iframe
			if iframe.find("vimeo") > -1:
				id = iframe.split("?")[0].split("/")[-1]
				print id
				vimeo = BeautifulSoup(geturl("http://vimeo.com/moogaloop/load/clip:%s" % id))
				print vimeo
				ret =  'http://www.vimeo.com/moogaloop/play/clip:%s/%s/%s/?q=sd' % (id, vimeo.findAll('request_signature')[0].contents[0], vimeo.findAll('request_signature_expires')[0].contents[0])
				print ret
				req = urllib2.Request(ret)
				req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
				ret = urllib2.urlopen(req).geturl()
			else:
				id = iframe.split("?")[0].split("/")[-1]
				print id
				iurl = 'http://www.youtube.com/get_video_info?%s' % urllib.urlencode({'asv' : '3', 'el' : 'embedded', 'video_id' : id, 'hl' : 'en_GB', 'eurl' : url})
				info = geturl(iurl)
				resp = dict([p.split('=') for p in info.split('$')[-1].split('&') ])
				print resp
				out = resp["url_encoded_fmt_stream_map"]
				ret = urllib.unquote(urllib.unquote(out).split('&')[0].split('=')[-1])

			print ret
			return ret

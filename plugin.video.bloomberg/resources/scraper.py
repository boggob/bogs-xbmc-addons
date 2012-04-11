import urllib, urllib2, httplib
import re
from  time import localtime
import HTMLParser
from resources.ooyala.ooyalaCrypto import ooyalaCrypto
from ooyala.MagicNaming import MagicNaming


from BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString 
try:
    import json
except ImportError:
    import simplejson as json

htmlparser = HTMLParser.HTMLParser()	
	
def geturl(url):
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		return urllib2.urlopen(req).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

class MenuItems(object):
	def __init__(self):
		self.base				= 'http://www.bloomberg.com/tv/shows/'
		self.base2				= 'http://www.bloomberg.com'

	def menu_main(self, path):
		print self.base
		val = BeautifulSoup(geturl(self.base)).find('div', {"class" : "shows_list"})
		out = []
		
		for prog in val.findAll('li', {"class" : "clearfix "}):
			print prog.find('img')
			img		= prog.find('img')["src"]
			parts	= prog.find('h3', {"class" : "title"}).findAll('a')
			if len(parts) > 1:
				url		= parts[1]["href"]
				title	= parts[1].string.strip()
				desc	= prog.find('div', {"class" : "description"}).p.string
				
				
				#print "\n".join([t.string for t in txt.findAll('p') if t.string is not None])
				oo = (title, url, htmlparser.unescape(desc), img)
				print oo
				out.append(oo) 

		return out

	def menu_shows(self, page):
		if page.find(':') < 0:
			page = self.base2 + page
			
		print page			
		val = BeautifulSoup(geturl(page))
		
		groups = val.findAll('div', {'class': 'component', "id" : "shows"})
		if not groups:
			groups = val.findAll('div', {'class': 'video_group clearfix items'})
			
		
		out = []
		for episode in (e for group in groups for e in group.findAll('li')):
			try:
				img = episode.find('img')["src"]
				title = episode.find('img')["alt"].strip()
				url = self.base2  + episode.find('a')['href']
				oo = (title, url, "", img)
				print oo
				out.append(oo) 

			except:
				pass
		return out

	def menu_play(self, page):
		app			= "ondemand?_fcs_vhost=cp115717.edgefcs.net"
		rtmp		= "rtmp://%s/%s" % (BeautifulSoup(geturl("http://cp115717.edgefcs.net/fcs/ident")).find("ip").string.strip(), app)
		pagedata	=	geturl(page)
		embed_code	= pagedata[pagedata.index("var live_embed_code = '"):].split("'")[1]
		smil		= geturl('http://player.ooyala.com/nuplayer?autoplay=1&hide=all&embedCode=%s' % embed_code)
		decry_smil	= ooyalaCrypto().ooyalaDecrypt(smil)
		playpath	=  "mp4:%s" % (MagicNaming().getVideoUrl(decry_smil)[0].split(':')[-1])
		return "%s app=%s playpath=%s" % (rtmp, app, playpath), (rtmp, app, playpath)

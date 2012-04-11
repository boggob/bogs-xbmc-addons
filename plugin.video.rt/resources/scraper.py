import urllib, urllib2, httplib
import re
from  time import localtime
import HTMLParser

from BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString 
try:
    import json
except ImportError:
    import simplejson as json

htmlparser = HTMLParser.HTMLParser()	
	
		
#		return repr("".join(sw(s) for s in urllib2.urlopen(req).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')))
	
def geturl(url):
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		return  urllib2.urlopen(req).read()

		

def pretty(st):
	return BeautifulSoup(st,convertEntities=BeautifulSoup.HTML_ENTITIES).prettify()
	

		
class MenuItems(object):
	def __init__(self):
		self.base				= 'http://rt.com'

	def menu_main(self):
		val = BeautifulSoup(geturl(self.base + '/programs/'),convertEntities=BeautifulSoup.HTML_ENTITIES).find('table', {"class" : "programms mb30"})
		out = []


		for prog in val.findAll('tr'):
			img,txt,vidinfo =  prog.findAll('td')
			#print "\n".join([t.string for t in txt.findAll('p') if t.string is not None])
			oo = (pretty(img.find('img')["alt"]), "%s%s" % (self.base , img.find('a')["href"]), "\n".join( pretty(t.string) for t in txt.findAll('p') if t.string is not None), self.base + img.find('img')["src"] 	)
			print oo
			out.append(oo) 

		return out

	def menu_shows(self, page):
		val = BeautifulSoup(geturl(page),convertEntities=BeautifulSoup.HTML_ENTITIES)

		out = []
		img = self.base + val.find('img', {"class" : "db mb15"})["src"]
		for epp in val.find('table', {"class" : "vat structure"}).findAll('td'):
			date = epp.find('div', {"class" : "topic_img"})
			url = epp.find('div', {"class" : "topic_text"})
			if date and url:
				oo = (date.contents[0].strip().split()[0], pretty(url.h3.a.string), self.base + url.h3.a["href"], pretty(url.contents[2].strip()), img)
				print oo
				out.append(oo) 

		return out

	def menu_play(self, page):
		return self.base + BeautifulSoup(geturl(page),convertEntities=BeautifulSoup.HTML_ENTITIES).find('a', {"class" : "embedvideo"})["href"]

if __name__ == "__main__":
	tst = MenuItems().menu_main()
	#tst = MenuItems().menu_shows("http://rt.com/programs/interview/")
	print 
	print tst
	
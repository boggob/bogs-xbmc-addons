
import urllib
import re
import HTMLParser
import urlparse

# code
import re
import sys
import urllib
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

__XBMC_Revision__ = xbmc.getInfoLabel('System.BuildVersion')
__settings__		= xbmcaddon.Addon(id='plugin.video.c31')
__language__      = __settings__.getLocalizedString
__version__       = __settings__.getAddonInfo('version')
__cwd__           = __settings__.getAddonInfo('path')
__addonname__    = "C31"
__addonid__      = "plugin.video.C31"
__author__        = "D Bozic"
URL = "http://www.c31.org.au/program"


class Myparser(HTMLParser.HTMLParser):
	def __init__(self, base, url, entry_sig):
		HTMLParser.HTMLParser.__init__(self)
		self.links = []
		self.values = []
		self.feeds	= []
		self.feedsv	= []
		self.start	= False
		self.stack_div	= 0
		self.a_div	= 0
		self.entry_sig = entry_sig
		self.base	= base
		self.url	= url
		fil = urllib.urlopen(url)
		contents = fil.read()
		fil.close()
		self.feed(contents)
		self.close()

	def handle_starttag(self, tag, attributes):
		attributes = dict(attributes)
		if tag == "div":
			if attributes and  attributes.get(self.entry_sig[0], None) == self.entry_sig[1]:
				self.start = True

			if self.start:
				self.stack_div += 1
		if self.start and tag == "a":
			self.a_div += 1
			if "href" in attributes:
				self.links.append(urlparse.urljoin(self.base, attributes["href"]))

			if "class" in attributes and attributes["class"] == "show" and "href" in attributes:
				self.feeds.append(urlparse.urljoin(self.base, attributes["href"]))
				self.feedsv.append(attributes["title"])
				#print ";", self.stack_div, attributes["href"], attributes["title"]


	def handle_endtag(self, tag):
		if tag == "div":
			if 	self.stack_div:
				self.stack_div -= 1
			if not self.stack_div:
				self.start = False

		if self.start and tag == "a":
			self.a_div -= 1

	def handle_data(self, data):
		if len(self.links) > len(self.values):
			self.values.append(data)







def addDir(name, url, mode, folder = False):
	url = sys.argv[0]+"?url="+url+"&mode="+str(mode)
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage="")
	liz.setInfo('video', {'Title': name, 'Genre': 'News'})
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=folder)
	return ok

def INDEX(li, sig, mode):
	print li, sig
	parser = Myparser(URL,li, sig)

	for link, data in zip(parser.links, parser.values):
		addDir(data,link, mode + 1,True)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def ITEMS(li, sig, mode):
	parser = Myparser(URL,li, sig)
	for link, data in zip(parser.feeds, parser.feedsv):
		fil = urllib.urlopen(link)
		contents = fil.read()
		for f in re.findall(r'file: "([^"]+.flv)"',  contents):
			addDir(data + f,f, mode + 1)

	xbmcplugin.endOfDirectory(int(sys.argv[1]))



MODE_MAP	= {
	0	: lambda url: INDEX(url, ("class", "col first"), 0),
	1	: lambda url: INDEX(url, ("class", "col-4"), 1),
	2	: lambda url: ITEMS(url, ("id", "tv-guide"), 2),
	3	: lambda url: xbmc.Player().play(url)

}



def clean(args):
	out = {}
	if args[2]:
		for item in (args[2].split("?")[1].split("&")):
			k,v = item.split("=")
			out[k] = v
		out["url"] = urllib.unquote_plus(out["url"])
	else:
		out["mode"] = "0"
		out["url"] = URL

	out["mode"] = int(out["mode"])
	return out


def main():
	params = clean(sys.argv)
	print sys.argv, params

	if params["mode"] != 0:
		MODE_MAP[params["mode"]](params["url"])
	else:
		u = "%s?initial=search" % (sys.argv[0],)
		liz=xbmcgui.ListItem(__language__(30091), iconImage="DefaultFolder.png", thumbnailImage="")
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
		MODE_MAP[params["mode"]](params["url"])




main()
import sys, os
import collections
import urllib, urllib2
import urlparse
import re
import subprocess

import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from resources.BeautifulSoup import BeautifulStoneSoup,NavigableString


##############################################################
__XBMC_Revision__	= xbmc.getInfoLabel('System.BuildVersion')
__settings__		= xbmcaddon.Addon( id=os.path.basename(os.getcwd()))
__language__		= __settings__.getLocalizedString
__version__			= __settings__.getAddonInfo('version')
__cwd__				= __settings__.getAddonInfo('path')
__addonname__		= __settings__.getAddonInfo('name')
__addonid__			= __settings__.getAddonInfo('id')
##############################################################
URL		= "http://mediacenter.dw-world.de/english/video/"
URL2	= 'http://mediacenter.dw-world.de/data/english/video/?Program=%s&pageNr=%s'
URL3	= 'http://mediacenter.dw.de/english/video/?programm=%s&pageNr=%s'


def geturl(url):
	#, headers = {"Accept-Encoding":"gzip"}
	print "Reading %s" % url
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')




def jsonc(st):
	for i,o in (
		('true', 'True'),
		('false', 'False'),
		('null', 'None')
	):
		st = st.replace(i,o)
	return eval(st)



def get_head(base, url, entry_sig):
	print ":U:", url
	contents = geturl(url)
	print "hello1"
	print ":,:", type(contents), contents
	print "hello2"
	xml = BeautifulStoneSoup(contents)

	out = []
	for item in xml.findAll('li', attrs=dict((entry_sig,))):
		#print item["id"], 
		out.append((
			"%s%s:1" % ("",item['id']), 
			item.findAll('a')[0].contents[0]
		))

	return out
		

	
def get_items(params):
	li = params["url"]
	cat, page = li.split(":")
	contents = geturl(URL3 % (cat, page) )
	contents = re.findall(r'mc3.data.items = ({.*});$',contents, re.MULTILINE)[0]
	
	import pprint
	pprint.pprint(jsonc(contents)) 
	for item in sorted(jsonc(contents).values(), key = lambda x: x["datetime"], reverse = True):
		yield {
			"rtmpurl"	: 'rtmp://tv-od.dw.de/flash/',
			"playpath"	: "mp4:%s_sor.mp4" % item["getFlvFile"].replace("\\", ""),
			"swfurl"	: 'http://www.dw.de/js/jwplayer/player.swf',
			"name"		: item["title"],
			"still"		: item["getImages"]['medium']['src'].replace("\\", ""),
			"info"		: {
					"plot"		: item["description"],
					"duration"	: item["getDurationText"].split()[0],
					"date"		: item["getPublicationDate"],
					"aired"		: item["getPublicationDate"],
					"genre"		: item["meta_title"],
					"tvshowtitle"	: item["getRubric"],
			}
		}
		
	
	
##############################################################



def addDir(params, folder = False, info = {}, still="DefaultFolder.png"):
	name = params["name"]
	url	 =  sys.argv[0] + "?" + "&".join(["%s=%s" % (urllib.quote_plus(k),urllib.quote_plus(str(v)))    for k, v in params.items()])
	print "::", url,  params, info, "%%"
	liz=xbmcgui.ListItem(name, iconImage=still, thumbnailImage="")
	if info:
		liz.setInfo("video", info)
		
	if not folder:
		liz.addContextMenuItems( [("Record to disk", "XBMC.RunPlugin(%s?&%s)"   % (sys.argv[0], url.replace("mode=2", "mode=3") ))] )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=folder)
	return ok

def INDEX(params, sig):
	li	= URL
#	print li, sig

	for link, data in get_head(URL2,li, sig):
		addDir( {"name" : data, "url" : link, "mode" : 1}, True)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def ITEMS(params, sig):
	li = params["url"]
	print "::", li
	cat, page = li.split(":")
	addDir({"name" : "Next->", "url" : "%s:%d" % (cat, int(page) + 1), "mode" : 1}, folder = True)

	for rec in get_items(params):
		rec["mode"]		= 2
		rec["pageurl"]	= li
		print "::rec::", rec
		addDir(rec, info = rec["info"], still=rec["still"])
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )	   

	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(lu):
	url = "%s playpath=%s" % (lu["rtmpurl"],lu["playpath"])
	li = xbmcgui.ListItem(lu["name"])
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, li)
		
def record(lu):		
	print lu
	args = __settings__.getSetting( "rtmpdump" ), "-o%s%s" % (__settings__.getSetting( "path" ), lu["playpath"].split("/")[-1]), "--rtmp=%s" % lu["rtmpurl"], "--playpath=%s" % lu["playpath"]
	print args
	subprocess.call(args)
	
##############################################################
MODE_MAP	= {
	0	: lambda params: INDEX(params, ("class", "listItemProgramm")),
	1	: lambda params: ITEMS(params, ("id", "tv-guide")),
	2	: lambda params: play(params),
	3	: lambda params: record(params)
}


def parse_args(args):
	out = {}
	if args[2]:
		for item in (args[2].split("?")[-1].split("&")):
#			print item
			items = item.split("=")
			k,v = items[0], "=".join(items[1:])
			out[k] = urllib.unquote_plus(v)
	else:
		out["mode"]		= "0"

	out["mode"] = int(out["mode"])
	return out


def main():
	try:
		params = parse_args(sys.argv)
		print "##", sys.argv, params
		MODE_MAP[params["mode"]](params)

	except Exception,e :
		import traceback
		print e
		traceback.print_exc()
	
		dialog = xbmcgui.Dialog()
		dialog.ok("Error", str(e))	
main()
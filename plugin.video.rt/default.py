import sys, os
import collections
import urllib
import re
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

from resources.BeautifulSoup import BeautifulStoneSoup,NavigableString
import resources.scraper
reload( resources.scraper)


##############################################################
__XBMC_Revision__	= xbmc.getInfoLabel('System.BuildVersion')
__settings__		= xbmcaddon.Addon( id=os.path.basename(os.getcwd()))
__language__		= __settings__.getLocalizedString
__version__			= __settings__.getAddonInfo('version')
__cwd__				= __settings__.getAddonInfo('path')
__addonname__		= __settings__.getAddonInfo('name')
__addonid__			= __settings__.getAddonInfo('id')
##############################################################


def addDir(params, folder = False, info = {}, still="DefaultFolder.png"):
	name = params["name"]
	url =  sys.argv[0] + "?" + "&".join(["%s=%s" % (urllib.quote_plus(k),urllib.quote_plus(str(v)))    for k, v in params.items()])
	liz=xbmcgui.ListItem(name, iconImage=still, thumbnailImage="")
	if info:
		liz.setInfo("video", info)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=folder)
	return ok

##############################################################
def INDEX(params):
	scraper = resources.scraper.MenuItems()
	addDir({"path" : "Live Stream RT-1", "name" : "Live Stream RT-1", "url" : 'rtmp://fms5.visionip.tv/live app=live   playpath=RT_1 live=true', "mode" : "3"}, False)
			
	for title, url, desc,still in scraper.menu_main():
		#print title, url, desc,still
		addDir({"path" : url, "name" : title, "url" : url, "mode" : "1"}, True, {"plot": desc}, still = still)
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )	
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def ITEMS(params):
	path = params.get("path", None)
	mode = "2"
	scraper = resources.scraper.MenuItems()
	pp =  scraper.menu_shows(path)
	for date,title,url,txt,img  in sorted(pp):
		#print date,title,url,txt
		addDir({"path" : url, "name" : title, "url" : url, "mode" : "2"}, False, info = {"date" : date, "plot" : txt}, still = img)

	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )	   
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

	
def play(params):
	scraper = resources.scraper.MenuItems()
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(scraper.menu_play(params["url"]), xbmcgui.ListItem(params["name"]))

def play2(params):
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(params["url"], xbmcgui.ListItem(params["name"]))
	
	
##############################################################
MODE_MAP	= {
	"0"	: lambda params:	INDEX(params),
	"1"	: lambda url:		ITEMS(url),
	"2"	: lambda url:		play(url),
	"3"	: lambda url:		play2(url)
}


def parse_args(args):
	out = {}
	if args[2]:
		for item in (args[2].split("?")[-1].split("&")):
#			print item
			items = item.split("=")
			k,v = items[0], "=".join(items[1:])
			out[k] = urllib.unquote_plus(v)
	return out


def main():
	params = parse_args(sys.argv)
	print "##", sys.argv, params
	MODE_MAP[params.get("mode", "0")](params)


main()
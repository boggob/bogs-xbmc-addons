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
__settings__		= xbmcaddon.Addon( id=os.path.basename(os.getcwd())) #xbmcaddon.Addon(id='plugin.video.sbs2')
__language__		= __settings__.getLocalizedString
__version__			= __settings__.getAddonInfo('version')
__cwd__				= __settings__.getAddonInfo('path')
__addonname__		= __settings__.getAddonInfo('name')
__addonid__			= __settings__.getAddonInfo('id')
##############################################################


def addDir(params, folder = False, info = {}, still="DefaultFolder.png"):
	name = params["name"]
	url =  sys.argv[0] + "?" + "&".join(["%s=%s" % (urllib.quote_plus(k),urllib.quote_plus(str(v)))    for k, v in params.items()])
	print "::", url,  params, info, "%%"
	liz=xbmcgui.ListItem(name, iconImage=still, thumbnailImage="")
	if info:
		liz.setInfo("video", info)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=folder)
	return ok

##############################################################
def INDEX(params):
	path = params.get("path", None)
	
	scraper = resources.scraper.MenuItems()
	if path is None:
		for title, id, desc in sorted(scraper.menu_main(path)):
			addDir({"path" : id, "name" : title, "url" : id, "mode" : "0"}, True, {"plot": desc})
	else:
		for title, url in sorted(scraper.menu_sub(path)):
			addDir({"path" : url, "name" : title, "url" : url, "mode" : "1"}, True)
		
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def ITEMS(params):
	path = params.get("path", None)
	mode = "2"
	scraper = resources.scraper.MenuItems()
	nodes = scraper.menu_shows(path)

	for node in sorted(nodes):
		addDir({"path" : node["url"], "name" : node["title"], "url" : node["url"], "mode" : "2"}, False, info = node["info"], still = node["thumbnail"])
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

	
def play(params):
	scraper = resources.scraper.MenuItems()
	addon	= xbmcaddon.Addon( id=os.path.basename( os.getcwd() ) )
	bitrate	= addon.getSetting( "vid_quality" )

	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(scraper.menu_play(params["url"]), xbmcgui.ListItem(params["name"]))

##############################################################
MODE_MAP	= {
	"0"	: lambda params:	INDEX(params),
	"1"	: lambda url:		play(url),
	"2"	: lambda url:		play(url)
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
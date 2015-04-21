import sys, os
import urllib
import subprocess
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

import scraper


##############################################################
__XBMC_Revision__	= xbmc.getInfoLabel('System.BuildVersion')
__settings__		= xbmcaddon.Addon( id=scraper.ADDON_ID)
__language__		= __settings__.getLocalizedString
__version__			= __settings__.getAddonInfo('version')
__cwd__				= __settings__.getAddonInfo('path')
__addonname__		= __settings__.getAddonInfo('name')
__addonid__			= __settings__.getAddonInfo('id')
##############################################################


def addDir(params, folder = False, info = {}, still="DefaultFolder.png"):
	name = params["name"]
	liz=xbmcgui.ListItem(name, iconImage=still, thumbnailImage=still)
	url =  sys.argv[0] + "?" + "&".join(["%s=%s" % (urllib.quote_plus(k),urllib.quote_plus(str(v)))    for k, v in params.items()])
	print ("::", url,  params, info, folder, "%%")		
	if info:
		liz.setInfo("video", info)
	if not folder:
		liz.addContextMenuItems( [("Record to disk", "XBMC.RunPlugin(%s?&%s)"   % (sys.argv[0], url + "&record=1"))] )
		
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=folder)
	return ok

##############################################################

	


def folders(params):
	for param in params:
		print "@@",param
		addDir({"name" : param['title'], "url" : param["url"], "path" : param["path"]}, param["folder"], info = param.get("info", {}), still = param.get("still", "DefaultFolder.png"))

	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )	   
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(params):
	print params
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play("{0}".format(params["url"]), xbmcgui.ListItem(params["name"]))

def record(params):		
	print params
	def rpt(c):
		if c not in set(" %*^&$#@!~:"):
			return c
		else:
			return "_"
	name	= '%s.mp4' % ("".join(rpt(c) for c in str(params["name"])))
	url		= params["url"]	
	logs	= "{}/{}/".format(__settings__.getSetting( "path" ),"logs")
		
	args	= (
				__settings__.getSetting( "ffmpeg" ), 
				'-i',  url,
				"-vcodec", "copy",
				"-acodec", "copy", 
				"{}{}".format(__settings__.getSetting( "path" ), name)
			)
	startupinfo = None
	if os.name == 'nt':
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW		
	
	try:
		os.makedirs(logs)
	except OSError:
		pass
	
	print " ".join(args)
	sout = open(logs+name+".fmpeg.out", "w")
	serr = open(logs+name+".ffmpeg.err", "w")
	try:
		xx = subprocess.call(args, stdin= subprocess.PIPE, stdout= sout, stderr= serr,shell= False, startupinfo=startupinfo)
	finally:
		sout.close()
		serr.close()
	#print xx.stdout.read()
	#print xx.stderr.read()	
##############################################################


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
	mode	= params.get("path", "menu")
	print "$$", mode
	sc = scraper.Scraper(folders, play, record)
	getattr(sc, mode)(params)




main()
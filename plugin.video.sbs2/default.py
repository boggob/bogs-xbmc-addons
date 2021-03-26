import sys, os
import urllib, urllib.parse
import subprocess
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

from resources import scraper


##############################################################
ID = 'plugin.video.sbs2' 
__XBMC_Revision__	= xbmc.getInfoLabel('System.BuildVersion')
__settings__		= xbmcaddon.Addon( id=ID)
__language__		= __settings__.getLocalizedString
__version__			= __settings__.getAddonInfo('version')
__cwd__				= __settings__.getAddonInfo('path')
__addonname__		= __settings__.getAddonInfo('name')
__addonid__			= __settings__.getAddonInfo('id')
##############################################################


def addDir(params, folder = False, info = {}, still="DefaultFolder.png"):
	name = params["name"]
	liz=xbmcgui.ListItem(name)
	liz.setArt({'icon': still, 'thumb': still})

	url =  sys.argv[0] + "?" + "&".join(["%s=%s" % (urllib.parse.quote_plus(k),urllib.parse.quote_plus(str(v)))    for k, v in params.items()])
	print ("::", url,  params, info, folder, "%%")		
	if info:
		liz.setInfo("video", info)
	if not folder:
		liz.addContextMenuItems( [
			("Record to disk", "RunPlugin(%s?&%s)"   % (sys.argv[0], url + "&record=1")),
			("Record to disk as flv", "RunPlugin(%s?&%s)"   % (sys.argv[0], url + "&recordFlv=1")),
		] )
		
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=folder)
	return ok

##############################################################

	


def folders(params):
	for param in params:
		print ("@@",param)
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
	print (params)
	
	
	url		= params["url"]
	item	= xbmcgui.ListItem(label=params["name"], path=url)
	if params['subtitle_files']:
		item.setSubtitles(params['subtitle_files'])
	item.addStreamInfo('video', {})
		
	

	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=item)
	player = xbmc.Player()
	player.play(url, item)
	
	

def record(params, flv=False, audio=False):		
	print (params)
	def rpt(c):
		if c not in set(" %*^&$#@!~:?"):
			return c
		else:
			return "_"
	name	= '%s%s' % ("".join(rpt(c) for c in str(params["name"])), ".flv" if flv else ".mp4" )
	url		= params["url"]	#+ "seek=7136"
	logs	= "{}/{}/".format(__settings__.getSetting( "path" ),"logs")
	
	if audio:
		args	= (
					__settings__.getSetting( "ffmpeg" ), 
					"-i",
					url,
					"-vcodec", "copy",
					"-acodec", "copy", 
					"-bsf:a", "aac_adtstoasc",
					"{}{}".format(__settings__.getSetting( "path" ), name)
				)	
	else:
		args	= (
					__settings__.getSetting( "ffmpeg" ), 
					"-i", 
					url,
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
	
	print (" ".join(args))
	sout = open(logs+name+".fmpeg.out", "w")
	serr = open(logs+name+".ffmpeg.err", "w")
	try:
		xx = subprocess.call(args, stdin= subprocess.PIPE, stdout= sout, stderr= serr,shell= False, startupinfo=startupinfo)
	finally:
		sout.close()
		serr.close()
	#print (xx.stdout.read())
	#print (xx.stderr.read())
	
##############################################################
def parse_args(args):
	out = {}
	if args[2]:
		for item in (args[2].split("?")[-1].split("&")):
#			print (item)
			items = item.split("=")
			k,v = items[0], "=".join(items[1:])
			out[k] = urllib.parse.unquote_plus(v)

	return out


def main():
	params	= parse_args(sys.argv)
	print ("##", sys.argv, params)
	mode	= params.get("path", "menu_main")
	print ("$$", mode)
	addon	= xbmcaddon.Addon( id=ID )
	sc		= scraper.Scraper(folders, play, record, int(addon.getSetting( "vid_quality" )), __settings__.getSetting( "path" ))
	getattr(sc, mode)(params)
	

main()

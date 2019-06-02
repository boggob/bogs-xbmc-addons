import sys
import time
import json

try:
	import xbmc
	import xbmcaddon
	import xbmcgui
	import xbmcplugin
	
	def log(msg):
		xbmc.log(msg, xbmc.LOGWARNING)
		
		
	VERSION		= xbmcaddon.Addon().getAddonInfo('version')	
	USE_DISCOGS	= xbmcaddon.Addon().getSetting('usediscogs') == '1'
	LANG		= xbmcaddon.Addon().getSetting('lang')
	
	def sleep(tm):
		xbmc.sleep(int(tm * 1000))

	def user_prefs(details, result):
		return result
	 
	def return_search(data):
		for item in data:
			listitem = xbmcgui.ListItem(item['artist'], offscreen=True)
			listitem.setArt({'thumb': item['thumb']})
			listitem.setProperty('artist.genre', item['genre'])
			listitem.setProperty('artist.born', item['born'])
			listitem.setProperty('relevance', item['relevance'])
			if 'type' in item:
				listitem.setProperty('artist.type', item['type'])
			if 'gender' in item:
				listitem.setProperty('artist.gender', item['gender'])
			if 'disambiguation' in item:
				listitem.setProperty('artist.disambiguation', item['disambiguation'])
			url = {'artist':item['artist']}
			if 'mbid' in item:
				url['mbid'] = item['mbid']
			if 'dcid' in item:
				url['dcid'] = item['dcid']
			xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=json.dumps(url), listitem=listitem, isFolder=True)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	def return_nfourl(item):
		if not item:
			return
		url = {'artist':item['artist'], 'mbid':item['mbartistid']}
		listitem = xbmcgui.ListItem(offscreen=True)
		xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=json.dumps(url), listitem=listitem, isFolder=True)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	def return_resolved(item):
		if not item:
			return
		url = {'artist':item['artist'], 'mbid':item['mbartistid']}
		listitem = xbmcgui.ListItem(path=json.dumps(url), offscreen=True)
		xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))


	def return_details(item):
		if not 'artist' in item:
			return
		listitem = xbmcgui.ListItem(item['artist'], offscreen=True)
		if 'mbartistid' in item:
			listitem.setProperty('artist.musicbrainzid', item['mbartistid'])
		if 'genre' in item:
			listitem.setProperty('artist.genre', item['genre'])
		if 'biography' in item:
			listitem.setProperty('artist.biography', item['biography'])
		if 'styles' in item:
			listitem.setProperty('artist.styles', item['styles'])
		if 'moods' in item:
			listitem.setProperty('artist.moods', item['moods'])
		if 'instruments' in item:
			listitem.setProperty('artist.instruments', item['instruments'])
		if 'disambiguation' in item:
			listitem.setProperty('artist.disambiguation', item['disambiguation'])
		if 'type' in item:
			listitem.setProperty('artist.type', item['type'])
		if 'sortname' in item:
			listitem.setProperty('artist.sortname', item['sortname'])
		if 'active' in item:
			listitem.setProperty('artist.years_active', item['active'])
		if 'born' in item:
			listitem.setProperty('artist.born', item['born'])
		if 'formed' in item:
			listitem.setProperty('artist.formed', item['formed'])
		if 'died' in item:
			listitem.setProperty('artist.died', item['died'])
		if 'disbanded' in item:
			listitem.setProperty('artist.disbanded', item['disbanded'])
		art = {}
		if 'clearlogo' in item:
			art['clearlogo'] = item['clearlogo']
		if 'banner' in item:
			art['banner'] = item['banner']
		if 'clearart' in item:
			art['clearart'] = item['clearart']
		if 'landscape' in item:
			art['landscape'] = item['landscape']
		listitem.setArt(art)
		if 'fanart' in item:
			listitem.setProperty('artist.fanarts', str(len(item['fanart'])))
			for count, fanart in enumerate(item['fanart']):
				listitem.setProperty('artist.fanart%i.url' % (count + 1), fanart['image'])
				listitem.setProperty('artist.fanart%i.preview' % (count + 1), fanart['preview'])
		if 'thumb' in item:
			listitem.setProperty('artist.thumbs', str(len(item['thumb'])))
			for count, thumb in enumerate(item['thumb']):
				listitem.setProperty('artist.thumb%i.url' % (count + 1), thumb['image'])
				listitem.setProperty('artist.thumb%i.preview' % (count + 1), thumb['preview'])
				listitem.setProperty('artist.thumb%i.aspect' % (count + 1), thumb['aspect'])
		if 'albums' in item:
			listitem.setProperty('artist.albums', str(len(item['albums'])))
			for count, album in enumerate(item['albums']):
				listitem.setProperty('artist.album%i.title' % (count + 1), album['title'])
				listitem.setProperty('artist.album%i.year' % (count + 1), album['year'])
		xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	 
except ImportError:
	def log(msg):
		print msg
		
	VERSION		= 1.0
	USE_DISCOGS	= True
	LANG		= 'en'
	sleep		= time.sleep
	

	def user_prefs(details, result):
		return result

	def return_nfourl(item):
		print item
	def return_resolved(item):
		print item

	def return_details(item):
		print item
		
	def return_search(data):
		print data

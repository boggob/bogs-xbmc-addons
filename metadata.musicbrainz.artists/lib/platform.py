import sys
import time
import json

try:
	import xbmc
	from xbmc import LOGDEBUG, LOGINFO, LOGNOTICE, LOGWARNING, LOGERROR, LOGFATAL
	import xbmcaddon
	import xbmcgui
	import xbmcplugin
		
	def log(msg, severity = LOGNOTICE):
		xbmc.log(msg, severity)
	
	def convert(val):
		return int(val) if val != 'disable' else -1
		
	VERSION		= xbmcaddon.Addon().getAddonInfo('version')		
	SETTINGS	= {
					'language'		: xbmcaddon.Addon().getSetting('lang').lower(),
					'misc'			: {
										'timeout'	: int(xbmcaddon.Addon().getSetting('timeout')),
					
									  },					
					'fields'		: {
										'albums'	: xbmcaddon.Addon().getSetting('use_albums') == "true",
										'artist'	: xbmcaddon.Addon().getSetting('use_artist') == "true"
					
									  },
					'ranking'		: {
						'wikidata'		: convert(xbmcaddon.Addon().getSetting('wikidata')),
						'musicbrainz'	: convert(xbmcaddon.Addon().getSetting('musicbrainz')),
						'discogs'		: convert(xbmcaddon.Addon().getSetting('discogs')),
						'allmusic'		: convert(xbmcaddon.Addon().getSetting('allmusic')),
						'theaudiodb'	: convert(xbmcaddon.Addon().getSetting('theaudiodb')),
						'fanarttv'		: convert(xbmcaddon.Addon().getSetting('fanarttv'))
					}
				}
					
	
	def sleep(tm):
		xbmc.sleep(int(tm * 1000))

	 
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
		if 'thumb' in item or 'extras' in item:
			thumbs = item.get('thumb', []) + item.get('extras', []) 
			listitem.setProperty('artist.thumbs', str(len(thumbs)))
			for count, thumb in enumerate(thumbs):
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
	LOGDEBUG	= 1
	LOGINFO		= 2
	LOGNOTICE	= 3
	LOGWARNING	= 4
	LOGERROR	= 5
	LOGFATAL	= 6
	
	def log(msg, severity = LOGNOTICE):
		print msg
		
	VERSION		= 1.0
	
	SETTINGS	= {
					'language'		: 'en',
					'misc'			: {
										'timeout'	: 10,
					
									  },										
					'fields'		: {
										'albums'	: False,
										'artist'	: True
					
									},					
					'ranking'		: {
						'wikidata'		: 1,
						'musicbrainz'	: 2,
						'discogs'		: 3,
						'allmusic'		: 4,
						'theaudiodb'	: 5,
						'fanarttv'		: 6
					}
				}
	
	
	sleep		= time.sleep
	


	def return_nfourl(item):
		print item
	def return_resolved(item):
		print item

	def return_details(item):
		print item
		
	def return_search(data):
		print data

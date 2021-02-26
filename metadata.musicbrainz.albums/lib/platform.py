import sys
import time
import json

try:
	import xbmc
	from xbmc import LOGDEBUG, LOGINFO, LOGWARNING, LOGERROR, LOGFATAL
	import xbmcaddon
	import xbmcgui
	import xbmcplugin
	
	def log(msg, severity = LOGINFO):
		xbmc.log(str(msg), severity)
	
	def convert(val):
		return int(val) if val != 'disable' else -1
		
	VERSION		= xbmcaddon.Addon().getAddonInfo('version')		
	SETTINGS	= {
					'language'		: xbmcaddon.Addon().getSetting('lang').lower(),
					'misc'			: {
										'timeout'	: int(xbmcaddon.Addon().getSetting('timeout')),
										'sortname'	: xbmcaddon.Addon().getSetting('sortname') == "true",
					
									  },					
					'fields'		: {
					
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

	 
	def user_prefs(details, result):
		# user preferences
		lang = 'description' + xbmcaddon.Addon().getSetting('lang')
		if 'theaudiodb' in details:
			if lang in details['theaudiodb']:
				result['description'] = details['theaudiodb'][lang]
			elif 'descriptionEN' in details['theaudiodb']:
				result['description'] = details['theaudiodb']['descriptionEN']
		genre = xbmcaddon.Addon().getSetting('genre')
		if (genre in details) and ('genre' in details[genre]):
			result['genre'] = details[genre]['genre']
		style = xbmcaddon.Addon().getSetting('style')
		if (style in details) and ('styles' in details[style]):
			result['styles'] = details[style]['styles']
		mood = xbmcaddon.Addon().getSetting('mood')
		if (mood in details) and ('moods' in details[mood]):
			result['moods'] = details[mood]['moods']
		theme = xbmcaddon.Addon().getSetting('theme')
		if (theme in details) and ('themes' in details[theme]):
			result['themes'] = details[theme]['themes']
		rating = xbmcaddon.Addon().getSetting('rating')
		if (rating in details) and ('rating' in details[rating]):
			result['rating'] = details[rating]['rating']
			result['votes'] = details[rating]['votes']
		return result

	def return_search(data):
		for count, item in enumerate(data):
			listitem = xbmcgui.ListItem(item['album'], offscreen=True)
			listitem.setArt({'thumb': item['thumb']})
			listitem.setProperty('album.artist', item['artist_description'])
			listitem.setProperty('album.year', item.get('year',''))
			listitem.setProperty('relevance', item['relevance'])
			url = {'artist':item['artist_description'], 'album':item['album']}
			if 'mbalbumid' in item:
				url['mbalbumid'] = item['mbalbumid']
			if 'mbreleasegroupid' in item:
				url['mbreleasegroupid'] = item['mbreleasegroupid']
			if 'dcalbumid' in item:
				url['dcalbumid'] = item['dcalbumid']
			xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=json.dumps(url), listitem=listitem, isFolder=True)
			xbmcplugin.endOfDirectory(int(sys.argv[1]))

	def return_nfourl(item):
		if not item:
			return
		url = {'artist':item['artist_description'], 'album':item['album'], 'mbalbumid':item['mbalbumid'], 'mbreleasegroupid':item['mbreleasegroupid']}
		listitem = xbmcgui.ListItem(offscreen=True)
		xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=json.dumps(url), listitem=listitem, isFolder=True)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	def return_resolved(item):
		if not item:
			return
	
		url = {'artist':item['artist_description'], 'album':item['album'], 'mbalbumid':item['mbalbumid'], 'mbreleasegroupid':item['mbreleasegroupid']}
		listitem = xbmcgui.ListItem(path=json.dumps(url), offscreen=True)
		xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

	def return_details(item):
		if not item:
			return
        
		print ("!!", item)
		listitem = xbmcgui.ListItem(item['album'], offscreen=True)
		if 'mbalbumid' in item:
			listitem.setProperty('album.musicbrainzid', item['mbalbumid'])
			listitem.setProperty('album.releaseid', item['mbalbumid'])
		if 'mbreleasegroupid' in item:
			listitem.setProperty('album.releasegroupid', item['mbreleasegroupid'])
		if 'scrapedmbid' in item:
			listitem.setProperty('album.scrapedmbid', item['scrapedmbid'])
		if 'artist' in item:
			listitem.setProperty('album.artists', str(len(item['artist'])))
			for count, artist in enumerate(item['artist']):
				listitem.setProperty('album.artist%i.name' % (count + 1), artist['artist'])
				listitem.setProperty('album.artist%i.musicbrainzid' % (count + 1), artist.get('mbartistid', ''))
				listitem.setProperty('album.artist%i.sortname' % (count + 1), artist.get('artistsort', ''))
		if 'genre' in item:
			listitem.setProperty('album.genre', item['genre'])
		if 'styles' in item:
			listitem.setProperty('album.styles', item['styles'])
		if 'moods' in item:
			listitem.setProperty('album.moods', item['moods'])
		if 'themes' in item:
			listitem.setProperty('album.themes', item['themes'])
		if 'description' in item:
			listitem.setProperty('album.review', item['description'])
		if 'releasedate' in item:
			listitem.setProperty('album.release_date', item['releasedate'])
		if 'artist_description' in item:
			listitem.setProperty('album.artist_description', item['artist_description'])
		if 'label' in item:
			listitem.setProperty('album.label', item['label'])
		if 'type' in item:
			listitem.setProperty('album.type', item['type'])
		if 'compilation' in item:
			listitem.setProperty('album.compilation', item['compilation'])
		if 'releasetype' in item:
			listitem.setProperty('album.release_type', item['releasetype'])
		if 'year' in item:
			listitem.setProperty('album.year', item['year'])
		if 'rating' in item:
			listitem.setProperty('album.rating', item['rating'])
		if 'userrating' in item:
			listitem.setProperty('album.userrating', item['userrating'])
		if 'votes' in item:
			listitem.setProperty('album.votes', item['votes'])
		art = {}
		if 'discart' in item:
			art['discart'] = item['discart']
		if 'back' in item:
			art['back'] = item['back']
		if 'spine' in item:
			art['spine'] = item['spine']
		if '3dcase' in item:
			art['3dcase'] = item['3dcase']
		if '3dflat' in item:
			art['3dflat'] = item['3dflat']
		if '3dface' in item:
			art['3dface'] = item['3dface']
		listitem.setArt(art)
		if 'thumb' in item:
			listitem.setProperty('album.thumbs', str(len(item['thumb'])))
			for count, thumb in enumerate(item['thumb']):
				listitem.setProperty('album.thumb%i.url' % (count + 1), thumb['image'])
				listitem.setProperty('album.thumb%i.aspect' % (count + 1), thumb['aspect'])
				listitem.setProperty('album.thumb%i.preview' % (count + 1), thumb['preview'])
		xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))
		

	 
except ImportError as e:
	print(e)
	LOGDEBUG	= 1
	LOGINFO		= 2
	LOGWARNING	= 4
	LOGERROR	= 5
	LOGFATAL	= 6
	
	def log(msg, severity = LOGINFO):
		print (msg)
		
	VERSION		= 1.0
	
	SETTINGS	= {
					'language'		: 'en',
					'misc'			: {
										'timeout'	: 10,
										'sortname'	: True,
					
									  },										
					'fields'		: {
					
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
	

	def user_prefs(details, result):
		return result

	def return_nfourl(item):
		pass
	def return_resolved(item):
		pass

	def return_details(item):
		pass
		
	def return_search(data):
		pass

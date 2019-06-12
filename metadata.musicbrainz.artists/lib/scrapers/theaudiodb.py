# -*- coding: UTF-8 -*-
from lib.scrapers.utils	import ScraperType, Action
from lib.url_get		import get_data

AUDIODBKEY = '58424d43204d6564696120'
AUDIODBURL = 'https://www.theaudiodb.com/api/v1/json/%s/%s'
AUDIODBSEARCH = 'search.php?s=%s'
AUDIODBDETAILS = 'artist-mb.php?i=%s'
AUDIODBDISCOGRAPHY = 'discography-mb.php?s=%s'



def theaudiodb_artistdetails(mbid, locale):
	data	= get_data(AUDIODBURL % (AUDIODBKEY, AUDIODBDETAILS % mbid), True)
	locale_	= locale.upper()

	if data.get('artists',[]):
		item = data['artists'][0]
		artistdata = {}
		extras = []
		artistdata['artist'] = item['strArtist']
		# api inconsistent
		if item.get('intFormedYear',''):
			artistdata['formed'] = item['intFormedYear']
		if item.get('intBornYear',''):
			artistdata['born'] = item['intBornYear']
		if item.get('intDiedYear',''):
			artistdata['died'] = item['intDiedYear']
		if item.get('strDisbanded',''):
			artistdata['disbanded'] = item['strDisbanded']
		if item.get('strStyle',''):
			artistdata['styles'] = item['strStyle']
		if item.get('strGenre',''):
			artistdata['genre'] = item['strGenre']
		if item.get('strMood',''):
			artistdata['moods'] = item['strMood']
		if item.get('strGender',''):
			artistdata['gender'] = item['strGender']
			
			
		if item.get('strBiography' + locale_,''):
			artistdata['biography'] = item['strBiography' + locale_]
		if item.get('strMusicBrainzID',''):
			artistdata['mbartistid'] = item['strMusicBrainzID']
		if item.get('strArtistFanart',''):
			fanart = []
			fanartdata = {
				'image' 	: item['strArtistFanart'],
				'preview' 	: item['strArtistFanart'] + '/preview'
			}
			fanart.append(fanartdata)
			if item['strArtistFanart2']:
				fanartdata = {
					'image'		: item['strArtistFanart2'],
					'preview'	: item['strArtistFanart2'] + '/preview'
				}
				fanart.append(fanartdata)
				if item['strArtistFanart3']:
					fanartdata = {
						'image'		: item['strArtistFanart3'],
						'preview'	: item['strArtistFanart3'] + '/preview'
					}
					fanart.append(fanartdata)
			artistdata['fanart'] = fanart
		if item.get('strArtistThumb',''):
			thumbs = [
				{
					'image'		: item['strArtistThumb'],
					'preview'	: item['strArtistThumb'] + '/preview',
					'aspect'	: 'thumb'
				}
			]
			artistdata['thumb'] = thumbs
		if item.get('strArtistLogo',''):
			artistdata['clearlogo'] = item['strArtistLogo']
			extradata = {}
			extradata['image'] = item['strArtistLogo']
			extradata['preview'] = item['strArtistLogo'] + '/preview'
			extradata['aspect'] = 'clearlogo'
			extras.append(extradata)
		if item.get('strArtistClearart',''):
			artistdata['clearart'] = item['strArtistClearart']
			extradata = {}
			extradata['image'] = item['strArtistClearart']
			extradata['preview'] = item['strArtistClearart'] + '/preview'
			extradata['aspect'] = 'clearart'
			extras.append(extradata)
		if item.get('strArtistWideThumb',''):
			artistdata['landscape'] = item['strArtistWideThumb']
			extradata = {}
			extradata['image'] = item['strArtistWideThumb']
			extradata['preview'] = item['strArtistWideThumb'] + '/preview'
			extradata['aspect'] = 'landscape'
			extras.append(extradata)
		if item.get('strArtistBanner',''):
			artistdata['banner'] = item['strArtistBanner']
			extradata = {}
			extradata['image'] = item['strArtistBanner']
			extradata['preview'] = item['strArtistBanner'] + '/preview'
			extradata['aspect'] = 'banner'
			extras.append(extradata)
		if extras:
			artistdata['extras'] = extras
		return artistdata

def theaudiodb_artistalbums(data):
	albums = []
	albumlist = data.get('album',[])
	if albumlist:
		for item in data.get('album',[]):
			albumdata = {}
			albumdata['title'] = item['strAlbum']
			albumdata['year'] = item.get('intYearReleased', '')
			albums.append(albumdata)
	return albums


SCAPER = ScraperType(
			Action('theaudiodb', None, 1),
			Action('theaudiodb', theaudiodb_artistdetails, 1),
		)


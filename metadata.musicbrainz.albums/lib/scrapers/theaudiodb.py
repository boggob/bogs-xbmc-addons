# -*- coding: UTF-8 -*-

from lib.url_get		import get_data
from lib.scrapers.utils import ScraperType, Action

AUDIODBKEY = '58424d43204d6564696120'
AUDIODBURL = 'https://www.theaudiodb.com/api/v1/json/%s/%s'
AUDIODBSEARCH = 'searchalbum.php?s=%s&a=%s'
AUDIODBDETAILS = 'album-mb.php?i=%s'


def theaudiodb_albumdetails(param, locale = "en"):
	url = AUDIODBURL % (AUDIODBKEY, AUDIODBDETAILS % param)
	data = get_data(url, True)
	if not data:
		return

	locale_	= locale.upper()
	
	if data.get('album'):
		item = data['album'][0]
		albumdata = {}
		albumdata['album'] = item['strAlbum']
		if item.get('intYearReleased',''):
			albumdata['year'] = item['intYearReleased']
		if item.get('strStyle',''):
			albumdata['styles'] = item['strStyle']
		if item.get('strGenre',''):
			albumdata['genre'] = item['strGenre']
		if item.get('strLabel',''):
			albumdata['label'] = item['strLabel']
		if item.get('strReleaseFormat',''):
			albumdata['type'] = item['strReleaseFormat']
		if item.get('intScore',''):
			albumdata['rating'] = str(int(float(item['intScore']) + 0.5))
		if item.get('intScoreVotes',''):
			albumdata['votes'] = item['intScoreVotes']
		if item.get('strMood',''):
			albumdata['moods'] = item['strMood']
		if item.get('strTheme',''):
			albumdata['themes'] = item['strTheme']
		if item.get('strMusicBrainzID',''):
			albumdata['mbreleasegroupid'] = item['strMusicBrainzID']
		
		# api inconsistent
		if item.get('strDescription',''):
			albumdata['description'] = item['strDescription']
			
		if item.get('strDescription' + locale_,''):
			albumdata['description'] = item['strDescription' + locale_]

			
		if item.get('strArtist',''):
			albumdata['artist_description'] = item['strArtist']
			artists = []
			artistdata = {}
			artistdata['artist'] = item['strArtist']
			if item.get('strMusicBrainzArtistID',''):
				artistdata['mbartistid'] = item['strMusicBrainzArtistID']
			artists.append(artistdata)
			albumdata['artist'] = artists
		thumbs = []
		extras = []
		if item.get('strAlbumThumb',''):
			thumbdata = {}
			thumbdata['image'] = item['strAlbumThumb']
			thumbdata['preview'] = item['strAlbumThumb'] + '/preview'
			thumbdata['aspect'] = 'thumb'
			thumbs.append(thumbdata)
		if item.get('strAlbumThumbBack',''):
			albumdata['back'] = item['strAlbumThumbBack']
			extradata = {}
			extradata['image'] = item['strAlbumThumbBack']
			extradata['preview'] = item['strAlbumThumbBack'] + '/preview'
			extradata['aspect'] = 'back'
			extras.append(extradata)
		if item.get('strAlbumSpine',''):
			albumdata['spine'] = item['strAlbumSpine']
			extradata = {}
			extradata['image'] = item['strAlbumSpine']
			extradata['preview'] = item['strAlbumSpine'] + '/preview'
			extradata['aspect'] = 'spine'
			extras.append(extradata)
		if item.get('strAlbumCDart',''):
			albumdata['discart'] = item['strAlbumCDart']
			extradata = {}
			extradata['image'] = item['strAlbumCDart']
			extradata['preview'] = item['strAlbumCDart'] + '/preview'
			extradata['aspect'] = 'discart'
			extras.append(extradata)
		if item.get('strAlbum3DCase',''):
			albumdata['3dcase'] = item['strAlbum3DCase']
			extradata = {}
			extradata['image'] = item['strAlbum3DCase']
			extradata['preview'] = item['strAlbum3DCase'] + '/preview'
			extradata['aspect'] = '3dcase'
			extras.append(extradata)
		if item.get('strAlbum3DFlat',''):
			albumdata['3dflat'] = item['strAlbum3DFlat']
			extradata = {}
			extradata['image'] = item['strAlbum3DFlat']
			extradata['preview'] = item['strAlbum3DFlat'] + '/preview'
			extradata['aspect'] = '3dflat'
			extras.append(extradata)
		if item.get('strAlbum3DFace',''):
			albumdata['3dface'] = item['strAlbum3DFace']
			extradata = {}
			extradata['image'] = item['strAlbum3DFace']
			extradata['preview'] = item['strAlbum3DFace'] + '/preview'
			extradata['aspect'] = '3dface'
			extras.append(extradata)
		if thumbs:
			albumdata['thumb'] = thumbs
		if extras:
			albumdata['extras'] = extras
		return albumdata

SCAPER = ScraperType(
			Action('theaudiodb', None, 0),
			Action('theaudiodb', theaudiodb_albumdetails, 1),
		)

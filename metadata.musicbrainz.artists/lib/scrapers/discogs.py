# -*- coding: UTF-8 -*-

import urllib
from lib.scrapers.utils	import ScraperType, Action
from lib.url_get		import get_data


DISCOGSKEY			= 'zACPgktOmNegwbwKWMaC'
DISCOGSSECRET		= 'wGuSOeMtfdkQxtERKQKPquyBwExSHdQq'
DISCOGSURL			= 'https://api.discogs.com/%s'
DISCOGSSEARCH		= 'database/search?q=%s&type=artist&key=%s&secret=%s'
DISCOGSDETAILS		= 'artists/%i?key=%s&secret=%s'
DISCOGSDISCOGRAPHY	= 'artists/%i/releases?sort=format&page=1&per_page=100&key=%s&secret=%s'


def discogs_artistfind(artist):
	url = DISCOGSURL % (DISCOGSSEARCH % (urllib.quote_plus(artist), DISCOGSKEY , DISCOGSSECRET))
	data = get_data(url, True)
	if not data:
		return

	artists = []
	for item in data.get('results',[]):
		artistdata = {}
		artistdata['artist'] = item['title']
		artistdata['thumb'] = item['thumb']
		artistdata['genre'] = ''
		artistdata['born'] = ''
		artistdata['dcid'] = item['id']
		# discogs does not provide relevance, not used by kodi anyway for artists
		artistdata['relevance'] = ''
		artists.append(artistdata)
	return artists


def discogs_artistdetails_(param, locale):
	dcid = int(param.rsplit('/', 1)[1])

	artistresults = discogs_artistdetails(dcid)
	albumresults = discogs_artistalbums(dcid)
	if albumresults:
		artistresults['albums'] = albumresults
	
	return artistresults


def discogs_artistdetails(dcid):
	url = DISCOGSURL % (DISCOGSDETAILS % (dcid, DISCOGSKEY, DISCOGSSECRET))
	data = get_data(url, True)
	if not data:
		return


	artistdata = {}
	artistdata['artist'] = data['name']
	artistdata['biography'] = data['profile']
	if 'images' in data:
		thumbs = []
		for item in data['images']:
			thumbdata = {}
			thumbdata['image'] = item['uri']
			thumbdata['preview'] = item['uri150']
			thumbdata['aspect'] = 'thumb'
			thumbs.append(thumbdata)
		artistdata['thumb'] = thumbs
	return artistdata

def discogs_artistalbums(dcid):
	url = DISCOGSURL % (DISCOGSDISCOGRAPHY % (dcid, DISCOGSKEY, DISCOGSSECRET))
	data = get_data(url, True)
	if not data:
		return

	albums = []
	for item in data['releases']:
		if item['role'] == 'Main':
			albumdata = {}
			albumdata['title'] = item['title']
			albumdata['year'] = str(item.get('year', ''))
			albums.append(albumdata)
	return albums

SCAPER = ScraperType(
			Action('discogs', discogs_artistfind, 1),
			Action('discogs', discogs_artistdetails_, 2),
		)

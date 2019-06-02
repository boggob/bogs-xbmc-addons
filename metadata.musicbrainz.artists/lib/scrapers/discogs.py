# -*- coding: UTF-8 -*-

import urllib
from lib.url_get import get_data
import lib.scrapers.utils


def discogs_artistfind(artist):
	url = lib.scrapers.utils.DISCOGSURL % (lib.scrapers.utils.DISCOGSSEARCH % (urllib.quote_plus(artist), lib.scrapers.utils.DISCOGSKEY , lib.scrapers.utils.DISCOGSSECRET))
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

def discogs_artistdetails(dcid):
	url = lib.scrapers.utils.DISCOGSURL % (lib.scrapers.utils.DISCOGSDETAILS % (dcid, lib.scrapers.utils.DISCOGSKEY, lib.scrapers.utils.DISCOGSSECRET))
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
	url = lib.scrapers.utils.DISCOGSURL % (lib.scrapers.utils.DISCOGSDISCOGRAPHY % (dcid, lib.scrapers.utils.DISCOGSKEY, lib.scrapers.utils.DISCOGSSECRET))
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

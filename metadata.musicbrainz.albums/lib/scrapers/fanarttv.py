# -*- coding: UTF-8 -*-
from lib.url_get		import get_data
from lib.scrapers.utils import ScraperType, Action

FANARTVKEY = 'ed4b784f97227358b31ca4dd966a04f1'
FANARTVURL = 'https://webservice.fanart.tv/v3/music/albums/%s?api_key=%s'


def fanarttv_albumart(param, locale = "en"):
	url = FANARTVURL % (param, FANARTVKEY)
	data = get_data(url, True, True)
	if not data:
		return

	if 'albums' in data:
		albumdata = {}
		thumbs = []
		extras = []
		for mbid, art in data['albums'].items():
			if 'albumcover' in art:
				for thumb in art['albumcover']:
					thumbdata = {}
					thumbdata['image'] = thumb['url']
					thumbdata['preview'] = thumb['url'].replace('/fanart/', '/preview/')
					thumbdata['aspect'] = 'thumb'
					thumbs.append(thumbdata)
			if 'cdart' in art:
				albumdata['discart'] = art['cdart'][0]['url']
				for cdart in art['cdart']:
					extradata = {}
					extradata['image'] = cdart['url']
					extradata['preview'] = cdart['url'].replace('/fanart/', '/preview/')
					extradata['aspect'] = 'discart'
					extras.append(extradata)
		if thumbs:
			albumdata['thumb'] = thumbs
		if extras:
			albumdata['extras'] = extras
		return albumdata

SCAPER = ScraperType(
			Action('fanarttv', None, 0),
			Action('fanarttv', fanarttv_albumart, 1),
		)

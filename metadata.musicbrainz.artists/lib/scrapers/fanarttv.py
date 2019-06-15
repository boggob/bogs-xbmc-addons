# -*- coding: UTF-8 -*-
from lib.scrapers.utils	import ScraperType, Action
from lib.url_get		import get_data


FANARTVKEY = 'ed4b784f97227358b31ca4dd966a04f1'
FANARTVURL = 'https://webservice.fanart.tv/v3/music/%s?api_key=%s'

def fanarttv_artistart(mbid, locale):
	data	= get_data(FANARTVURL % (mbid, FANARTVKEY), True, True)
	if not data:
		return {}

	artistdata = {}
	extras = []
	if 'artistbackground' in data:
		fanart = []
		for item in data['artistbackground']:
			fanartdata = {}
			fanartdata['image'] = item['url']
			fanartdata['preview'] = item['url'].replace('/fanart/', '/preview/')
			fanart.append(fanartdata)
		artistdata['fanart'] = fanart
	if 'artistthumb' in data:
		thumbs = []
		for item in data['artistthumb']:
			thumbdata = {}
			thumbdata['image'] = item['url']
			thumbdata['preview'] = item['url'].replace('/fanart/', '/preview/')
			thumbdata['aspect'] = 'thumb'
			thumbs.append(thumbdata)
		if thumbs:
			artistdata['thumb'] = thumbs
	if 'musicbanner' in data:
		artistdata['banner'] = data['musicbanner'][0]['url']
		for item in data['musicbanner']:
			extradata = {}
			extradata['image'] = item['url']
			extradata['preview'] = item['url'].replace('/fanart/', '/preview/')
			extradata['aspect'] = 'banner'
			extras.append(extradata)
	if 'hdmusiclogo' in data:
		artistdata['clearlogo'] = data['hdmusiclogo'][0]['url']
		for item in data['hdmusiclogo']:
			extradata = {}
			extradata['image'] = item['url']
			extradata['preview'] = item['url'].replace('/fanart/', '/preview/')
			extradata['aspect'] = 'clearlogo'
			extras.append(extradata)
	elif 'musiclogo' in data:
		artistdata['clearlogo'] = data['musiclogo'][0]['url']
		for item in data['musiclogo']:
			extradata = {}
			extradata['image'] = item['url']
			extradata['preview'] = item['url'].replace('/fanart/', '/preview/')
			extradata['aspect'] = 'clearlogo'
			extras.append(extradata)
	if extras:
		artistdata['extras'] = extras
	return artistdata

SCAPER = ScraperType(
			Action('fanarttv', None, 1),
			Action('fanarttv', fanarttv_artistart, 1),
		)


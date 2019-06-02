# -*- coding: UTF-8 -*-

import collections
import hashlib
import json
import pprint
import urllib
import urllib2

from lib.url_get import get_data
import lib.scrapers.utils



URL_MB_RELEASE	= u"http://musicbrainz.org/ws/2/artist/{}?fmt=json&inc=ratings+artist-rels+url-rels+aliases+release-groups+release-group-rels"
URL_WIKI		= u"https://{}.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext&redirects=1&titles={}"
URL_WIKID		= u"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&formatversion=2&props=sitelinks|claims&ids={}"
IMG_URL			= u"https://upload.wikimedia.org/wikipedia/commons/{}/{}{}/{}"


DEBUG 			= True

def make_multimap(it, cls=list):
	items = collections.defaultdict(cls)
	func = "append" if cls is list else "add"
	for k, v in it:
		getattr(items[k], func)(v)
	return items

def merge_multimap(*args, **kwargs):
	"""
	Merges multiple multimaps into one by concatenating the results, all mmap values should be of the same type (either set or list)

	:param args: mmaps
	:param kwargs: if the key word of func is supplied this will be used for unifying the values of the mmaps
	:return: Unified mmap of the concatenated results
	"""
	types = {
		type(val)
		for map_ in args
		for val in map_.itervalues()
	}

	if len(types) > 1:
		raise ValueError("Multiple value types detected {}".format(types))
	elif len(types) < 1 :
		return {}
	else:
		type_	= list(types)[0]
		prop	= (lambda a,b: a.union(b)) if issubclass(type_, set) else (lambda a,b: a + b)
		func	= kwargs.get("func", prop)

		out		= collections.defaultdict(type_)
		for map_ in args:
			for k, v in map_.iteritems():
				out[k] = func(out[k], v)
		return out





def get_sub(data, **kwargs):
	for key, func in kwargs.iteritems():
		curr = data
		x = curr.get(key, NotImplementedError)
		if x != NotImplementedError and isinstance(x, collections.Mapping):
			return func(x)
	return None

def artist_name(artist, locale):
	name = next(
				(
					alias['name'] 
					for alias in artist.get('aliases', []) 
					if alias.get('type', None) == "Artist name" 
					if alias.get('locale', None) == locale
				),
				None
			)
			
	return name or artist['sort-name']


def musicbrainz_artistfind(artist):
	url = lib.scrapers.utils.MUSICBRAINZURL % (lib.scrapers.utils.MUSICBRAINZSEARCH % urllib.quote_plus(artist))
	data = get_data(url, True)
	if not data:
		return


	artists = []
	for item in data.get('artists',[]):
		artistdata = {}
		artistdata['artist'] = item['name']
		artistdata['thumb'] = ''
		artistdata['genre'] = ''
		artistdata['born'] = item['life-span'].get('begin', '')
		if 'type' in item:
			artistdata['type'] = item['type']
		if 'gender' in item:
			artistdata['gender'] = item['gender']
		if 'disambiguation' in item:
			artistdata['disambiguation'] = item['disambiguation']
		artistdata['mbid'] = item['id']
		if item.get('score',1):
			artistdata['relevance'] = str(item['score'] / 100.00)
		artists.append(artistdata)
	return artists



def musicbrainz_arstistdetails(mbid, seperator = u'/', locale = 'en', wiki = False):
	ret		= get_data(URL_MB_RELEASE.format(mbid).encode('utf-8'), True)

				
	urls	= make_multimap( (r['type'] , r['url']['resource'])   for r in ret['relations']  if r['target-type'] == 'url')
	

	artistdata = {}
	artistdata['artist']		= artist_name(ret, locale)
	artistdata['mbartistid']	= ret['id']
	artistdata['type'] 			= ret['type']
	artistdata['gender'] 		= ret['gender']
	artistdata['disambiguation'] = ret['disambiguation']
	if ret.get('life-span','') and ret.get('type',''):
		begin = ret['life-span'].get('begin', '')
		end = ret['life-span'].get('end', '')
		if ret['type'] in ['Group', 'Orchestra', 'Choir']:
			artistdata['formed'] = begin
			artistdata['disbanded'] = end
		elif ret['type'] in ['Person', 'Character']:
			artistdata['born'] = begin
			artistdata['died'] = end
	albums = []
	for item in ret.get('release-groups',[]):
		albumdata = {}
		albumdata['title'] = item.get('title','')
		albumdata['year'] = item.get('first-release-date','')
		albums.append(albumdata)
	if albums:
		artistdata['albums'] = albums

	if urls.get('wikidata'):
		artistdata['wikidata-url']	=  sorted( urls.get('wikidata'))[0]
	if urls.get('allmusic'):
		artistdata['allmusic-url']	= sorted( urls.get('allmusic'))[0]
	if urls.get('discogs'):
		artistdata['discogs-url']	= sorted( urls.get('discogs'))[0]
				
		
	return artistdata

def wikidata_arstistdetails(url, seperator = u'/', locale = 'en'):
	id_		= url.split('/')[-1]
	retw1	= get_data(URL_WIKID.format(id_), True)
	wikip	= next((v['title'] for res in  retw1['entities'].values() for k, v in res['sitelinks'].items() if k == '{}wiki'.format(locale) ), '')
	wikip1 	= urllib2.quote(wikip.encode('UTF-8'))
	retw	= get_data(URL_WIKI.format(locale, wikip1), True) if wikip1 else {}
	wikid	= next(([v['extract']] for v in  retw['query']['pages'].values()), []) if wikip1 else []

	imgs	= [
				{ 'image' :  img, 'preview' :  img, 'aspect' :  img }
				for res in  retw1['entities'].values()
				for imgd in res.get('claims', {}).get('P18', []) 
				if imgd
				for fil in [imgd['mainsnak']['datavalue']['value'].replace(u" ", u"_")]
				for hash_ in [ hashlib.md5(fil.encode('utf-8')).hexdigest() ]
				for img in [IMG_URL.format(hash_[0], hash_[0], hash_[1], fil)]
				
			]	
		
		

	artistdata = {}
	artistdata['biography']		= u"\n\n".join(wikid)
	
	artistdata['thumb']  		=  imgs
	artistdata['fanart']		=  imgs
		
	return artistdata

	
	
	
	

if __name__ == "__main__":
	DEBUG = True

	#pprint.pprint(musicbrainz_arstistdetails('24f1766e-9635-4d58-a4d4-9413f9f98a4c'))
	pprint.pprint(musicbrainz_arstistdetails('fd14da1b-3c2d-4cc8-9ca6-fc8c62ce6988'))
	
	
	#raise 1
	
	
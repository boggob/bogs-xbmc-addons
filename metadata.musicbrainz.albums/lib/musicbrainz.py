# -*- coding: UTF-8 -*-

# -*- coding: UTF-8 -*-

import collections
import hashlib

import pprint
import time
import urllib
import urllib2

from lib.url_get	import get_data
from lib.utils		import MUSICBRAINZURL, MUSICBRAINZSEARCH


URL_MB_RELEASE	= u"https://musicbrainz.org/ws/2/release/{}?fmt=json&inc=genres+release-groups+artists+artist-credits+labels+ratings+recording-level-rels+recordings+artist-rels+place-rels+url-rels+work-rels+area-rels+release-group-rels+aliases"
URL_MB_RELEASEG	= u"http://musicbrainz.org/ws/2/release-group?release={}&fmt=json&inc=genres+artist-credits+ratings+artist-rels+place-rels+url-rels+area-rels"
URL_WIKI		= u"https://{}.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext&redirects=1&titles={}"
URL_WIKID		= u"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&formatversion=2&props=sitelinks|claims&ids={}"
URL_COVER_ARCHV	= u"http://coverartarchive.org/release/{}/{}"
IMG_URL			= u"https://upload.wikimedia.org/wikipedia/commons/{}/{}{}/{}"




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



	
	

def musicbrainz_albumfind(artist_, album):
	url		= MUSICBRAINZURL % (MUSICBRAINZSEARCH % (urllib.quote_plus(album), urllib.quote_plus(artist_), urllib.quote_plus(artist_)))
	result	= get_data(url, True)
	albums	= []
	for item in result.get('releases',[]):
		albumdata = {}
		if item.get('artist-credit'):
			artists = []
			artistdisp = ""
			for artist in item['artist-credit']:
				artistdata = {}
				artistdata['artist'] = artist['artist']['name']
				artistdata['mbartistid'] = artist['artist']['id']
				artistdata['artistsort'] = artist['artist']['sort-name']
				artistdisp = artistdisp + artist['artist']['name']
				artistdisp = artistdisp + artist.get('joinphrase', '')
				artists.append(artistdata)
		albumdata['artist'] = artists
		albumdata['artist_description'] = artistdisp
		if item.get('label-info','') and item['label-info'][0].get('label','') and item['label-info'][0]['label'].get('name',''):
			albumdata['label'] = item['label-info'][0]['label']['name']
		albumdata['album'] = item['title']
		if item.get('release-events',''):
			albumdata['year'] = item['release-events'][0]['date'][:4]
		albumdata['thumb'] = ''
		albumdata['mbalbumid'] = item['id']
		if item.get('release-group',''):
			albumdata['mbreleasegroupid'] = item['release-group']['id']
		if item.get('score',1):
			albumdata['relevance'] = str(item['score'] / 100.00)
		albums.append(albumdata)
	return albums

def musicbrainz_albumdetails(mbid, seperator = u'/', locale = 'en', wiki = False):
	ret		= get_data(URL_MB_RELEASE.format(mbid).encode('utf-8'), True)
	time.sleep(1)
	retg	= get_data(URL_MB_RELEASEG.format(mbid).encode('utf-8'), True)['release-groups']
			
	recordings = [
					u"{}.{} {}: {}\n{}".format(	
						media_idx + 1, 
						track['position'], 
						", ".join(artist_name(a['artist'], locale) for a in track['artist-credit']),
						track['title'],
						u"\n".join(sorted(
							u"  {}:{} {}: {}".format( rel['begin'] or "-", rel['end']  or "-",  rel['type'], rel_t ) 
							for rel in track['recording']['relations'] 
							for rel_t in [get_sub(rel, artist = lambda n: artist_name(n, locale), work = lambda n: n['title'], place = lambda n: n['name'])]
							if rel_t is not None
						))
					)
				
				for media_idx, media in enumerate(ret['media'])
				for track in media['tracks']				
				]
	
	urls = make_multimap( (r['type'] , r['url']['resource'])   for retr in retg for r in retr['relations'] if r['target-type'] == 'url')
	
	if urls.get('wikidata'):
		wikis			= sorted( urls.get('wikidata'))
		wikid, release_date, imgs = wikidata(wikis[0], locale)
	else:
		release_date	= None
		wikid			= []
		imgs			= []
		
	release_date_				= release_date or next(retr['first-release-date'] for retr in retg )	


	albumdata = {}
	albumdata['album'] = ret['title']
	albumdata['mbalbumid'] = ret['id']
	if ret.get('release-group',''):
		albumdata['mbreleasegroupid'] = ret['release-group']['id']
		if ret['release-group']['rating'] and ret['release-group']['rating']['value']:
			albumdata['rating'] = str(int((float(ret['release-group']['rating']['value']) * 2) + 0.5))
			albumdata['votes'] = str(ret['release-group']['rating']['votes-count'])
		if ret['release-group']['secondary-types']:
			albumdata['type'] = '%s / %s' % (ret['release-group']['primary-type'], ret['release-group']['secondary-types'][0])
		if ret['release-group']['secondary-types'] and (ret['release-group']['secondary-types'][0] == 'Compilation'):
			albumdata['compilation'] = 'true'
	if ret.get('release-events',''):
		albumdata['year'] = ret['release-events'][0]['date'][:4]
		albumdata['releasedate'] = ret['release-events'][0]['date']
	if ret.get('label-info','') and ret['label-info'][0].get('label','') and ret['label-info'][0]['label'].get('name',''):
		albumdata['label'] = ret['label-info'][0]['label']['name']
	if ret.get('artist-credit'):
		artists = []
		artistdisp = ''
		for artist in ret['artist-credit']:
			artistdata = {}
			artistdata['artist'] = artist['name']
			artistdata['mbartistid'] = artist['artist']['id']
			artistdata['artistsort'] = artist['artist']['sort-name']
			artistdisp = artistdisp + artist['name']
			artistdisp = artistdisp + artist.get('joinphrase', '')
			artists.append(artistdata)
		albumdata['artist'] = artists
		albumdata['artist_description'] = artistdisp
		
	albumdata['description']	= u"\n\n".join(wikid +  [u"\n\n".join(recordings)])
	albumdata['genre'] 			= seperator.join(n for c, n in sorted(((r['count'], r['name'])  for retr in retg for r in retr['genres']), reverse = True) )
	albumdata['year'] 			= release_date_ and release_date_[:4]
	albumdata['releasedate']	= release_date_
		
	covers						= ret.get('cover-art-archive', {})	
	if covers.get('front'):
		albumdata["discart"]	= URL_COVER_ARCHV.format(mbid, 'front')
		albumdata['thumb'] 		= (
									[
										{
											'image'			: URL_COVER_ARCHV.format(mbid, 'front'),
											'preview'		: URL_COVER_ARCHV.format(mbid, 'front'),
											'aspect'		: 'thumb'	
										}
									]
								  )
								  
	if imgs:	
		albumdata['thumb'] 		= (
									(albumdata['thumb'] or []) 
									+ 
									[
										{
											'image'			: i,
											'preview'		: i,
											'aspect'		: 'thumb'	
										}
										
										for i in imgs
									]
								)								  
	if covers.get('back'):
		albumdata["back"]		= URL_COVER_ARCHV.format(mbid, 'back')
	
	
	
	return albumdata if not wiki else wikid
	
		

def wikidata(url, locale = 'en'):
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

	release	= next((
				imgd['mainsnak']['datavalue']['value']['time'].split('T')[0].replace('+', '')
				for res in  retw1['entities'].values()
				for imgd in res.get('claims', {}).get('P577', []) 
				if imgd				
			), None)
	
	
	return wikid, release, imgs
	

	


def musicbrainz_albumart(data):
	albumdata = {}
	thumbs = []
	extras = []
	for item in data['images']:
		if 'Front' in item['types']:
			thumbdata = {}
			thumbdata['image'] = item['image']
			thumbdata['preview'] = item['thumbnails']['small']
			thumbdata['aspect'] = 'thumb'
			thumbs.append(thumbdata)
		if 'Back' in item['types']:
			albumdata['back'] = item['image']
			backdata = {}
			backdata['image'] = item['image']
			backdata['preview'] = item['thumbnails']['small']
			backdata['aspect'] = 'back'
			extras.append(backdata)
		if 'Medium' in item['types']:
			albumdata['discart'] = item['image']
			discartdata = {}
			discartdata['image'] = item['image']
			discartdata['preview'] = item['thumbnails']['small']
			discartdata['aspect'] = 'discart'
			extras.append(discartdata)
		# exculde spine+back images
		if 'Spine' in item['types'] and len(item['types']) == 1:
			albumdata['spine'] = item['image']
			spinedata = {}
			spinedata['image'] = item['image']
			spinedata['preview'] = item['thumbnails']['small']
			spinedata['aspect'] = 'spine'
			extras.append(spinedata)
	if thumbs:
		albumdata['thumb'] = thumbs
	if extras:
		albumdata['extras'] = extras
	return albumdata


if __name__ == "__main__":


	#pprint.pprint(musicbrainz_albumdetails('be4dfc70-fb62-3589-aeb4-4680cea68c50'))
	#pprint.pprint(musicbrainz_albumdetails('033ab928-e9c7-443d-86dc-5d18393e97b9'))
	#pprint.pprint(musicbrainz_albumdetails('9787a825-5dab-4c89-943d-4b142a03cb56'))
	#pprint.pprint(musicbrainz_albumdetails('a8976979-398a-4d03-9998-c24455885151'))
	#pprint.pprint(musicbrainz_albumdetails('2a06e2db-5d86-4294-8388-3109e6228963'))
	#pprint.pprint(musicbrainz_albumdetails('2a018799-55cb-43f1-a0ae-4a54a319d768'))
	#pprint.pprint(musicbrainz_albumdetails('fd14a4e3-f39a-4fef-afba-36ab8d22902b'))
	#pprint.pprint(musicbrainz_albumdetails('1bb8e966-cc02-3b98-92c3-16c0cbc9cb1b'))
	#pprint.pprint(musicbrainz_albumdetails('72995c3c-db08-4a2d-8823-f5d718b78c3d'))
	pprint.pprint(musicbrainz_albumdetails('35e0a764-99cd-4ecf-af94-96375cb0f9af'))
	#pprint.pprint(musicbrainz_albumdetails('5ef9848e-0a05-4729-9a99-8ff3f645275b'))
	
	#raise 1

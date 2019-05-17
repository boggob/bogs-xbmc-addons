# -*- coding: UTF-8 -*-

import collections
import json
import pprint
import time
import urllib2
import urllib

from musicbrainz import musicbrainz_albumdetails


URL_MB_RELEASE	= u"https://musicbrainz.org/ws/2/release/{}?fmt=json&inc=genres+release-groups+artists+artist-credits+labels+ratings+recording-level-rels+recordings+artist-rels+place-rels+url-rels+work-rels+area-rels+release-group-rels"
URL_MB_RELEASEG	= u"http://musicbrainz.org/ws/2/release-group?release={}&fmt=json&inc=genres+artist-credits+ratings+artist-rels+place-rels+url-rels+area-rels"
URL_WIKI		= u"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext&redirects=1&titles={}"
URL_WIKID		= u"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&formatversion=2&props=sitelinks&ids={}"
URL_COVER_ARCHV	= u"http://coverartarchive.org/release/{}/{}"


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
	else:
		type_	= list(types)[0]
		prop	= (lambda a,b: a.union(b)) if issubclass(type_, set) else (lambda a,b: a + b)
		func	= kwargs.get("func", prop)

		out		= collections.defaultdict(type_)
		for map_ in args:
			for k, v in map_.iteritems():
				out[k] = func(out[k], v)
		return out


def get_data(url, headers = None, encode = False):
	if encode:
		url = url
	try:
		print repr(url)
		req = urllib2.Request(url, headers)
		request = urllib2.urlopen(req)
		response = request.read()
		request.close()
	except Exception, e:
		import traceback
		print "Error getting URL", e
		traceback.print_exc()
		response = ''
	return response



def get_sub(data, delimiter, *args):
	for arg in args:
		curr = data
		for sp in arg.split(delimiter):
			x = curr.get(sp, NotImplementedError)
			if x != NotImplementedError and isinstance(x, collections.Mapping):
				curr = x
			else:
				break
		if x != NotImplementedError:
			return x

def musicbrainz_albumdetails2(mbid, seperator = u'/'):
	ret		= json.loads(get_data(URL_MB_RELEASE.format(mbid).encode('utf-8')))
	time.sleep(1)
	retg	= json.loads(get_data(URL_MB_RELEASEG.format(mbid).encode('utf-8')))['release-groups']
			
	recordings = [
					u"{}.{} {}: {}\n{}".format(	
						media_idx + 1, 
						track['position'], 
						", ".join(a['artist']['name'] for a in track['artist-credit']),
						track['title'],
						u"\n".join(sorted(
							u"  {}:{} {}: {}".format( rel['begin'] or "-", rel['end']  or "-",  rel['type'], get_sub(rel, '.', 'artist.name', 'work.title', 'place.name') ) 
							for rel in track['recording']['relations'] 
							if get_sub(rel, '.', 'artist.name', 'work.title', 'place.name')
						))
					)
				
				for media_idx, media in enumerate(ret['media'])
				for track in media['tracks']				
				]
	
	urls = merge_multimap( 
				make_multimap( (r['type'] , r['url']['resource'])                    for r in ret['relations']  if r['target-type'] == 'url'),
				make_multimap( (r['type'] , r['url']['resource'])   for retr in retg for r in retr['relations'] if r['target-type'] == 'url')
			)
	print urls
	if urls.get('wikipedia'):
		wikis	= sorted( urls.get('wikipedia'),  key = lambda u :  0 if '://en' in u else 1)
		id_		= wikis[0].split('/')[-1]
		id_1	= urllib2.quote(id_.encode('UTF-8'))
		retw	= json.loads(get_data(URL_WIKI.format(id_)), encoding = 'utf-8')
		wikid	= [next((v['extract'] for v in  retw['query']['pages'].values()), None)]
	elif urls.get('wikidata'):
		wikis	= sorted( urls.get('wikidata'))
		id_		= wikis[0].split('/')[-1]
		retw	= json.loads(get_data(URL_WIKID.format(id_)), encoding = 'utf-8')
		wikip	= next((v['title'] for res in  retw['entities'].values() for k, v in res['sitelinks'].items() if k == 'enwiki' ), None)
		wikip1 	= urllib2.quote(wikip.encode('UTF-8'))
		y		= get_data(URL_WIKI.format(wikip1))
		retw	= json.loads(y, encoding = 'utf-8')
		wikid	= [next((v['extract'] for v in  retw['query']['pages'].values()), None)]
		
	else:
		wikid = []

	albumdata					= musicbrainz_albumdetails(ret)			
	albumdata['description']	= u"\n\n".join(wikid +  [u"\n\n".join(recordings)])
	albumdata['genre'] 			= seperator.join(n for c, n in sorted(((r['count'], r['name'])  for retr in retg for r in retr['genres']), reverse = True) )
	albumdata['year'] 			= next(retr['first-release-date'][:4] for retr in retg)
	albumdata['releasedate']	= next(retr['first-release-date'] for retr in retg )
		
		
	if ret.get('cover-art-archive', {}).get('front'):
		albumdata["discart"]	= URL_COVER_ARCHV.format(mbid, 'front')
	if ret.get('cover-art-archive', {}).get('back'):
		albumdata["back"]		= URL_COVER_ARCHV.format(mbid, 'back')
	
	return albumdata
	
	

if __name__ == "__main__":
	#pprint.pprint(musicbrainz_albumdetails2('be4dfc70-fb62-3589-aeb4-4680cea68c50'))
	#pprint.pprint(musicbrainz_albumdetails2('033ab928-e9c7-443d-86dc-5d18393e97b9'))
	#pprint.pprint(musicbrainz_albumdetails2('9787a825-5dab-4c89-943d-4b142a03cb56'))
	#pprint.pprint(musicbrainz_albumdetails2('a8976979-398a-4d03-9998-c24455885151'))
	#pprint.pprint(musicbrainz_albumdetails2('2a06e2db-5d86-4294-8388-3109e6228963'))
	#pprint.pprint(musicbrainz_albumdetails2('2a018799-55cb-43f1-a0ae-4a54a319d768'))
	pprint.pprint(musicbrainz_albumdetails2('fd14a4e3-f39a-4fef-afba-36ab8d22902b'))
	
	pass
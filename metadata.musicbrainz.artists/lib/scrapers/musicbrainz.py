# -*- coding: UTF-8 -*-

import collections
import pprint
import urllib

from lib.alphabet_detector	import AlphabetDetector
from lib.assorted			import make_multimap
from lib.platform			import SETTINGS
from lib.scrapers.utils 	import ScraperType, Action
from lib.url_get			import get_data


URL_MUSICBRAINZ			= 'https://musicbrainz.org/ws/2/artist/%s'
URL_MUSICBRAINZSEARCH	= '?query=artist:"%s"&fmt=json'
URL_MUSICBRAINZDETAILS	= '%s?inc=url-rels+release-groups&type=album&fmt=json'

URL_MB_RELEASE			= u"http://musicbrainz.org/ws/2/artist/{}?fmt=json&inc=ratings+artist-rels+url-rels+aliases+release-groups+release-group-rels"
URL_WIKI				= u"https://{}.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext&redirects=1&titles={}"

AD						= AlphabetDetector()


def get_sub(data, **kwargs):
	for key, func in kwargs.iteritems():
		curr = data
		x = curr.get(key, NotImplementedError)
		if x != NotImplementedError and isinstance(x, collections.Mapping):
			return func(x)
	return None

def artist_name_(artist, locale):
	if AD.only_alphabet_chars(artist['name'], "LATIN"):
		return artist
	else:
		#find localisation
		name1 = next(
					(
						alias
						for alias in artist.get('aliases', [])
						if alias.get('type', None) == "Artist name"
						if alias.get('locale', None) == locale
					),
					None
				)

		#find any latin based localisation
		name2 = next(
					(
						alias
						for alias in artist.get('aliases', [])
						if alias.get('type', None) == "Artist name"
						if AD.only_alphabet_chars(alias['name'], "LATIN")
					),
					None
				)

	return name1 or name2 or artist

def clean_hyphen(s):	
	return s.replace(u'\u2010', '-')
	
def artist_name(artist, locale, sortname= True):	
	ret = artist_name_(artist, locale)
	return ret and clean_hyphen(ret['sort-name' if sortname else 'name'])


def musicbrainz_artistfind(artist):
	url = URL_MUSICBRAINZ % (URL_MUSICBRAINZSEARCH % urllib.quote_plus(artist))
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



def musicbrainz_arstistdetails(mbid, locale = 'en'):
	ret		= get_data(URL_MB_RELEASE.format(mbid).encode('utf-8'), True)

	artistdata = {}
	artistdata['artist']		= clean_hyphen( artist_name(ret, locale, SETTINGS['misc']['sortname']) )
	artistdata['sortname']		= clean_hyphen( artist_name(ret, locale, True) )
	
	artistdata['mbartistid']	= ret['id']
	if ret['type']:
		artistdata['type'] 			= ret['type']
	if ret['gender']:
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
	albums	= [
				{
					'title'	: item.get('title',''),
					'year'	: item.get('first-release-date','')
				}
				for item in ret.get('release-groups',[])
			]
	if albums:
		artistdata['albums'] = albums


	artistdata['urls']	=  make_multimap( (r['type'] , r['url']['resource'])   for r in ret['relations']  if r['target-type'] == 'url')


	return artistdata


SCAPER = ScraperType(
			Action('musicbrainz', musicbrainz_artistfind, 1),
			Action('musicbrainz', musicbrainz_arstistdetails, 1),
		)

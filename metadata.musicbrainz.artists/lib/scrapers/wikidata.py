# -*- coding: UTF-8 -*-

import hashlib
import pprint
import urllib2

from lib.url_get import get_data



URL_WIKI		= u"https://{}.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext&redirects=1&titles={}"
URL_WIKID		= u"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&formatversion=2&props=sitelinks|claims&ids={}"
IMG_URL			= u"https://upload.wikimedia.org/wikipedia/commons/{}/{}{}/{}"
URL_WIKID2		= u"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={}&format=json&props=labels"

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
		
	genres_	= "|".join(
				dat['mainsnak']['datavalue']['value']["id"]
				for res in  retw1['entities'].values()
				for dat in res.get('claims', {}).get('P136', []) 
				if dat
			  )

	retg	= get_data(URL_WIKID2.format(genres_), True) if genres_ else {}
	genres	= [
				dat
				for res in  retg['entities'].values()
				for dat in [res.get('labels', {}).get(locale, {}).get('value', None)]
				if dat
			]	

		

	artistdata = {}
	artistdata['biography']		= u"\n\n".join(wikid)
	artistdata['genre']			= genres
	
	artistdata['thumb']  		=  imgs
	artistdata['fanart']		=  imgs
		
	return artistdata

	

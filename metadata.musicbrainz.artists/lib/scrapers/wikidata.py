# -*- coding: UTF-8 -*-

import hashlib
import urllib2

from lib.scrapers.utils	import ScraperType, Action
from lib.url_get		import get_data


URL_WIKI		= u"https://{}.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext&redirects=1&titles={}"
URL_WIKID		= u"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&formatversion=2&props=sitelinks|claims&ids={}"
IMG_URL			= u"https://upload.wikimedia.org/wikipedia/commons/{}/{}{}/{}"
URL_WIKID2		= u"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={}&format=json&props=labels"


def date_conv(date):
	return (date or "").replace('+', '').replace('-00-00', '').split('T')[0]


def _label(retg, keys, locale):
	return [
				dat
				for key in keys
				for res in  [retg['entities'].get(key, {})]
				for dat in [res.get('labels', {}).get(locale, {}).get('value', None)]
				if dat
			]

def _ps(retw1, pval):
	return 	{v["id"] for v in _getv(retw1, pval) }


def lookups(retw1, locale, *args):
	lookups_ = { (label, fn) : _ps(retw1, p) for label, p, fn  in args }


	retg	= get_data(URL_WIKID2.format("|".join(vv for v in lookups_.values() for vv in v)), True) if lookups_ else {}

	return {label : fn(res) for (label, fn) , q in lookups_.items() for res in [_label(retg, q, locale)] if res}
	
def _getv(retw1, pval):
	return (
		dat['mainsnak']['datavalue']['value']
		for res in  retw1['entities'].values()
		for dat in res.get('claims', {}).get(pval, {})
		if dat
	  )



def wikidata_arstistdetails(url, locale = 'en'):
	id_		= url.split('/')[-1]
	retw1	= get_data(URL_WIKID.format(id_), True)
	wikip	= next((v['title'] for res in  retw1['entities'].values() for k, v in res['sitelinks'].items() if k == '{}wiki'.format(locale) ), '')
	wikip1 	= urllib2.quote(wikip.encode('UTF-8'))
	retw	= get_data(URL_WIKI.format(locale, wikip1), True) if wikip1 else {}
	wikid	= next(([v['extract']] for v in  retw['query']['pages'].values()), []) if wikip1 else []

	imgs	= [
				{ 'image' :  img, 'preview' :  img, 'aspect' :  img }
				
				for p in ('P18', 'P154')
				for imgd in _getv(retw1, p)
				for fil in [imgd.replace(u" ", u"_")]
				for hash_ in [ hashlib.md5(fil.encode('utf-8')).hexdigest() ]
				for img in [IMG_URL.format(hash_[0], hash_[0], hash_[1], fil)]

			]



	artistdata = lookups(
					retw1,
					locale, 
					('genre',	'P136',	lambda a: " / ".join(a)),
					('gender',	'P21',	lambda a: a[0]),
					('type', 	'P31',	lambda a: a[0]),					
				)

	for l, p in (
					('born',	'P569'),
					('died',	'P570'),
					('formed',	'P571'),
					('formed',	'P571'),
					('disbanded',	'P576')
				):
		for dat in  _getv(retw1, p):
			artistdata[l]		= date_conv(dat['time'])
				
	
	years_active =  [date_conv(r['time']) for l, p in 	(('yearsactive_s', 'P2031'), ('yearsactive_e', 'P2032')) for r in _getv(retw1, p)]
	if years_active:
		artistdata['yearsactive']		= years_active

	if wikid:
		artistdata['biography']		= u"\n\n".join(wikid)	
	
	if imgs:
		artistdata['thumb']  		= imgs
		artistdata['fanart']		= imgs




	return artistdata


SCAPER = ScraperType(
			Action('wikidata', None, 1),
			Action('wikidata', wikidata_arstistdetails, 1),
		)


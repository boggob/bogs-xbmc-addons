# -*- coding: UTF-8 -*-

import collections
import json

import time

from lib.awaiter				import Awaiter
from lib.nfo					import nfo_geturl
from lib.platform				import log, SETTINGS, sleep, return_details, return_search, return_nfourl, return_resolved


import lib.scrapers.allmusic	as allmusic
import lib.scrapers.discogs		as discogs
import lib.scrapers.fanarttv	as fanarttv
import lib.scrapers.musicbrainz as musicbrainz
import lib.scrapers.theaudiodb	as theaudiodb
import lib.scrapers.wikidata	as wikidata



class Scraper(object):
	def __init__(self, action, key, artist, url, nfo):
		# get start time in milliseconds
		start = time.time()
		# return a dummy result, this is just for backward compitability with xml based scrapers https://github.com/xbmc/xbmc/pull/11632
		if action == 'resolveid':
			result = self.resolve_mbid(key)
			return_resolved(result)
		# search for artist name matches
		elif action == 'find':
			# both musicbrainz and discogs allow 1 api per second. this query requires 1 musicbrainz api call and optionally 1 discogs api call
			for finder in [musicbrainz.SCAPER.artistfind, discogs.SCAPER.artistfind] :
				res = finder.function(artist)
				if res:
					return_search(res)
					self.wait(finder.wait, 1)
					break
		# return info using artistname / id's
		elif action == 'getdetails':
			url__	= json.loads(url)
			mbid	= url__.get('mbid', '')
			dcid	= url__.get('dcid', '')
			details = {}
			
			delay	= []
			# we have a musicbrainz id
			if mbid:
				scrapers		=  [
									Awaiter(self.get_details, musicbrainz.SCAPER.getdetails, mbid, details),
									Awaiter(self.get_details, theaudiodb.SCAPER.getdetails, mbid, details),
									Awaiter(self.get_details, fanarttv.SCAPER.getdetails, mbid, details)
								]

				# wait for musicbrainz to finish
				scrapers[0].data()

				# check if we have a result:
				for scraper	in [allmusic.SCAPER.getdetails, discogs.SCAPER.getdetails, wikidata.SCAPER.getdetails]:
					url_	= next(iter(details.get('musicbrainz', {}).get('urls', {}).get(scraper.name, [])), None)
					scrapers.append(Awaiter(self.get_details, scraper, url_, details))

				for scraper in scrapers:
					delay.append(scraper.data() or 0)

			# we have a discogs id
			elif dcid:
				result = self.get_details(discogs.SCAPER.getdetails, str(dcid), details)
				delay.append(discogs.SCAPER.getdetails.wait)
				# discogs allow 1 api per second. this query requires 2 discogs api call
			
			log(json.dumps(details))
				
			result	= self.compile_results(details)

			log(json.dumps(result))
			return_details(result)
			self.wait(start, max(delay))
		elif action == 'NfoUrl':
			mbid = nfo_geturl(nfo)
			if mbid:
				result = self.resolve_mbid(mbid)
				return_nfourl(result)



	def wait(self, start, ratelimit):
		diff = ratelimit - (time.time() - start)
		if diff > 0:
			sleep(diff)


	def resolve_mbid(self, mbid):
		# create dummy result
		item = {
			'artist' : '',
			'mbartistid' : mbid
		}
		return item
	

	def get_details(self, scraper, param, details):
		if not param:
			return 0
		elif SETTINGS['ranking'].get(scraper.name, 100) < 0:
			log("skipping: {}".format(scraper.name))
			return 0
		else:
			albumresults = scraper.function(param, locale =  SETTINGS['language'])
			if albumresults:
				details[scraper.name] = albumresults
			return scraper.wait
			


	def compile_results(self, details):
		ranked	= sorted(details, key = lambda k : SETTINGS['ranking'].get(k, 100))
		log(json.dumps(ranked))
		
		#order the results
		result_	= collections.defaultdict(list)
		for site in ranked:
			for k, v in details.get(site, {}).items():
				if SETTINGS['fields'].get(k, True):
					result_[k].append(v) 
				else:
					log("skipping: {} {}".format(site, k))
		
		#return top ranking
		result	= {}	
		for k, v in result_.items():
			if k not in ('thumb', 'fanart', 'extras'):
				result[k] = result_[k][0]
			else:
				result[k] = [ii for i in result_[k] for ii in i]
				
		return result

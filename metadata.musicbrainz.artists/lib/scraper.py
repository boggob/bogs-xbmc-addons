# -*- coding: UTF-8 -*-


import json
from threading import Thread
import time


from lib.nfo import nfo_geturl
from lib.platform				import log, USE_DISCOGS, sleep, user_prefs, return_details, return_search, return_nfourl, return_resolved

from lib.scrapers.allmusic		import allmusic_artistdetails
from lib.scrapers.discogs		import discogs_artistfind, discogs_artistdetails, discogs_artistalbums
#from lib.scrapers.fanarttv		import fanarttv_artistart
from lib.scrapers.musicbrainz	import musicbrainz_artistfind, musicbrainz_arstistdetails, wikidata_arstistdetails
#from lib.scrapers.theaudiodb	import theaudiodb_artistdetails, theaudiodb_artistalbums






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
			return_search(
				self.find_artist(artist, 'musicbrainz')
				or
				self.find_artist(artist, 'discogs')
			)
			self.wait(start, 1)
		# return info using artistname / id's
		elif action == 'getdetails':
			url__	= json.loads(url)
			mbid	= url__.get('mbid', '')
			dcid	= url__.get('dcid', '')
			details = {}
			threads	= []
			delay	= []
			# we have a musicbrainz id
			if mbid:
				# musicbrainz allows 1 api per second.

				scrapers		= [[mbid, 'musicbrainz'], [mbid, 'theaudiodb'], [mbid, 'fanarttv']]
				extrascrapers	= [['allmusic-url', 'allmusic']] + ([] if not USE_DISCOGS else [['discogs-url', 'discogs']]) + [['wikidata-url', 'wikidata']]

				for item in scrapers:
					thread = Thread(target = self.get_details, args = (item[0], item[1], details, delay))
					threads.append(thread)
					thread.start()

				# wait for musicbrainz to finish
				threads[0].join()

				# check if we have a result:
				for key_, site in extrascrapers:
					url_ = details.get('musicbrainz', {}).get(key_)
					if url_:
						thread = Thread(target = self.get_details, args = (url_, site, details, delay))
						threads.append(thread)
						thread.start()

			# we have a discogs id
			else:
				result = self.get_details(dcid, 'discogs', details, delay)
				# discogs allow 1 api per second. this query requires 2 discogs api call

			for thread in threads:
				thread.join()
			log(json.dumps(details))
				
			result_	= self.compile_results(details)
			result	= user_prefs(details, result_)

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

	def find_artist(self, artist, site):

		# musicbrainz
		if site == 'musicbrainz':
			return musicbrainz_artistfind(artist)
		# musicbrainz
		if site == 'discogs':
			return discogs_artistfind(artist)


	def get_details(self, param, site, details, delay):
		if site == 'musicbrainz':
			albumresults = musicbrainz_arstistdetails(param)
			if albumresults:
				details[site] = albumresults
			delay.append(1)
			return details
			
		elif site == 'wikidata':
			albumresults = wikidata_arstistdetails(param)
			if albumresults:
				details[site] = albumresults
			delay.append(1)
			return details

		# discogs
		elif site == 'discogs':
			dcid = int(param.rsplit('/', 1)[1])

			artistresults = discogs_artistdetails(dcid)
			albumresults = discogs_artistalbums(dcid)
			if albumresults:
				artistresults['albums'] = albumresults
			if artistresults:
				details[site] = artistresults
			delay.append(2)
			return details
		elif site == 'allmusic':
			artistresults = allmusic_artistdetails(param + '/discography')
			if artistresults:
				details[site] = artistresults
			delay.append(1)
			return details

		else:
			delay.append(1)
			return details



	def compile_results(self, details):
		result = {}
		thumbs = []
		fanart = []
		extras = []
		# merge metadata results, start with the least accurate sources

		ordered = ['allmusic', 'theaudiodb', 'discogs', 'musicbrainz', 'wikidata']

		for site in ordered:
			for k, v in details.get(site, {}).items():
				result[k] = v
				if k == 'thumb':
					thumbs.append(v)
				elif k == 'fanart':
					fanart.append(v)
				if k == 'extras':
					extras.append(v)

		# provide artwork from all scrapers for getthumb / getfanart option
		if result:
			# the order for extra art does not matter
			result['thumb'] = (
								[item for thumblist in reversed(thumbs) for item in thumblist] +
								[item for thumblist in extras for item in thumblist]
							  )
			result['fanart'] = [item for thumblist in reversed(fanart) for item in thumblist]

		return result



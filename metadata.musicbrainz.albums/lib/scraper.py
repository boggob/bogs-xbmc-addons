# -*- coding: UTF-8 -*-
import json
import time
import _strptime # https://bugs.python.org/issue7980
from threading import Thread

from lib.theaudiodb import theaudiodb_albumdetails
from lib.musicbrainz import musicbrainz_albumfind, musicbrainz_albumart, musicbrainz_albumdetails
from lib.discogs import discogs_albumfind, discogs_albumdetails
from lib.allmusic import allmusic_albumfind, allmusic_albumdetails
from lib.fanarttv import fanarttv_albumart

from lib.nfo import nfo_geturl


from lib.platform				import log, USE_DISCOGS, LANG, sleep, user_prefs, return_details, return_search, return_nfourl, return_resolved



class Scraper(object):
	def __init__(self, action, key, artist, album, url, nfo):
		# get start time in milliseconds
		start = time.time()
		# return a dummy result, this is just for backward compitability with xml based scrapers https://github.com/xbmc/xbmc/pull/11632
		if action == 'resolveid':
			result = self.resolve_mbid(key)
			return_resolved(result)
		# search for artist name / album title matches
		elif action == 'find':
			# both musicbrainz and discogs allow 1 api per second. this query requires 1 musicbrainz api call and optionally 1 discogs api call
			return_search(
				musicbrainz_albumfind(artist, album)
				or
				discogs_albumfind(artist, album)
				or
				allmusic_albumfind(artist, album)
			)
			self.wait(start, 1)	
		# return info using artistname / albumtitle / id's
		elif action == 'getdetails':
			details = {}
			url = json.loads(url)
			artist = url['artist'].encode('utf-8')
			album = url['album'].encode('utf-8')
			mbid = url.get('mbalbumid', '')
			dcid = url.get('dcalbumid', '')
			mbreleasegroupid = url.get('mbreleasegroupid', '')
			threads = []
			scrapers = []
			# we have a musicbrainz album id, but no musicbrainz releasegroupid
			if mbid and not mbreleasegroupid:
				for item in [[mbid, 'musicbrainz'], [mbid, 'coverarchive']]:
					thread = Thread(target = self.get_details, args = (item[0], item[1], details))
					threads.append(thread)
					thread.start()
				# wait for musicbrainz to finish
				threads[0].join()
				# check if we have a result:
				if 'musicbrainz' in details:
					# get the info we need to start the other scrapers
					artist				= details['musicbrainz']['artist_description'].encode('utf-8')
					album				= details['musicbrainz']['album'].encode('utf-8')
					mbreleasegroupid	= details['musicbrainz']['mbreleasegroupid']
					scrapers			= [[mbreleasegroupid, 'theaudiodb'], [mbreleasegroupid, 'fanarttv'], [[artist, album], 'allmusic']] + ([[artist, album, dcid], 'discogs'] if USE_DISCOGS else [])
			# we have a discogs id and artistname and albumtitle
			elif dcid:
				# discogs allows 1 api per second. this query requires 1 discogs api call
				scrapers = [[[artist, album, dcid], 'discogs'], [[artist, album], 'allmusic']]

			else:
				scrapers = [[mbid, 'musicbrainz'], [mbreleasegroupid, 'theaudiodb'], [mbreleasegroupid, 'fanarttv'], [mbid, 'coverarchive'], [[artist, album], 'allmusic']] + ([[artist, album, dcid], 'discogs'] if USE_DISCOGS else [])
				
			for item in scrapers:
				thread = Thread(target = self.get_details, args = (item[0], item[1], details))
				threads.append(thread)
				thread.start()
				
			for thread in threads:
				thread.join()
			result = self.compile_results(details)
			return_details(result)
				
			self.wait(start, 2)
		# extract the mbid from the provided musicbrainz url
		elif action == 'NfoUrl':
			mbid = nfo_geturl(nfo)
			if mbid:
				# create a dummy item
				result = self.resolve_mbid(mbid)
				return_nfourl(result)
					

	def wait(self, start, ratelimit):
		diff = ratelimit - (time.time() - start)
		if diff > 0:
			sleep(diff)


	def resolve_mbid(self, mbid):
		# create dummy result
		item = {}
		item['artist_description'] = ''
		item['album'] = ''
		item['mbalbumid'] = mbid
		item['mbreleasegroupid'] = ''
		return item


	def get_details(self, param, site, details):
		#bypass all other options for now
		if site == 'musicbrainz':
			albumresults = musicbrainz_albumdetails(param)
			if not albumresults:
				return
			details[site] = albumresults
			return details
		else:
			return details		

	def compile_results(self, details):
		result = {}
		thumbs = []
		extras = []
		# merge metadata results, start with the least accurate sources
		for site in ['discogs', 'allmusic', 'theaudiodb', 'musicbrainz', 'coverarchive', 'fanarttv']:
			for k, v in details.get(site, {}).items():
				result[k] = v
				if k == 'thumb':
					thumbs.append(v)
				if k == 'extras':
					extras.append(v)

		# use musicbrainz artist list as they provide mbid's, these can be passed to the artist scraper
		if 'musicbrainz' in details:
			result['artist'] = details['musicbrainz']['artist']
			
		# provide artwork from all scrapers for getthumb / getfanart option
		if result:
			# the order for extra art does not matter
			result['thumb'] = (
								[item for thumblist in reversed(thumbs) for item in thumblist] +
								[item for thumblist in extras for item in thumblist]
							  )
			
		#data = self.user_prefs(details, result)
		return result


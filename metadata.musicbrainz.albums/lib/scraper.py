# -*- coding: UTF-8 -*-
import collections
import json
import time
import _strptime # https://bugs.python.org/issue7980


from lib.awaiter	import Awaiter
import lib.scrapers.allmusic	as allmusic
import lib.scrapers.discogs		as discogs
import lib.scrapers.fanarttv	as fanarttv
import lib.scrapers.musicbrainz as musicbrainz
import lib.scrapers.theaudiodb	as theaudiodb
#import lib.scrapers.wikidata	as wikidata


from lib.nfo import nfo_geturl


from lib.platform				import log, SETTINGS, sleep, return_details, return_search, return_nfourl, return_resolved



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
			for finder in [musicbrainz.SCAPER1.find, discogs.SCAPER.find, discogs.SCAPER.find] :
				res = finder.function(artist, album)
				if res:
					return_search(res)
					self.wait(finder.wait, 1)
					break
			
		# return info using artistname / albumtitle / id's
		elif action == 'getdetails':
			
			url = json.loads(url)
			artist = url['artist'].encode('utf-8')
			album = url['album'].encode('utf-8')
			mbid = url.get('mbalbumid', '')
			dcid = url.get('dcalbumid', '')
			mbreleasegroupid = url.get('mbreleasegroupid', '')
			
			
			delay	= []
			scrapers = []
			details = {}
			
			# we have a musicbrainz album id, but no musicbrainz releasegroupid
			if mbid and  mbreleasegroupid:
				scrapers = [
					Awaiter(self.get_details, musicbrainz.SCAPER1.getdetails, mbid, details),
					Awaiter(self.get_details, musicbrainz.SCAPER2.getdetails, mbid, details),
					Awaiter(self.get_details, theaudiodb.SCAPER.getdetails, mbreleasegroupid, details),
					Awaiter(self.get_details, fanarttv.SCAPER.getdetails, mbreleasegroupid, details),
					Awaiter(self.get_details, allmusic.SCAPER.getdetails, [artist, album], details),
					Awaiter(self.get_details, discogs.SCAPER.getdetails, [artist, album, dcid], details),
				]
				
			# we have a discogs id and artistname and albumtitle
			elif mbid and  not mbreleasegroupid:
				scrapers			= [
										Awaiter(self.get_details, musicbrainz.SCAPER1.getdetails, mbid, details),
										Awaiter(self.get_details, musicbrainz.SCAPER2.getdetails, mbid, details)
									]
			
			
				# wait for musicbrainz to finish
				scrapers[0].data()
				# check if we have a result:
				if 'musicbrainz' in details:
					# get the info we need to start the other scrapers
					artist				= details['musicbrainz']['artist_description'].encode('utf-8')
					album				= details['musicbrainz']['album'].encode('utf-8')
					mbreleasegroupid	= details['musicbrainz']['mbreleasegroupid']
					scrapers			+= [
												Awaiter(self.get_details, theaudiodb.SCAPER.getdetails, mbreleasegroupid, details),
												Awaiter(self.get_details, fanarttv.SCAPER.getdetails, mbreleasegroupid, details),
												Awaiter(self.get_details, allmusic.SCAPER.getdetails, [artist, album], details),
												Awaiter(self.get_details, discogs.SCAPER.getdetails, [artist, album, dcid], details),
											]

			else:
				scrapers = [
							Awaiter(self.get_details, allmusic.SCAPER.getdetails, [artist, album], details),
							Awaiter(self.get_details, discogs.SCAPER.getdetails, [artist, album, dcid], details),
					]
				
				
			#wait for results	
			for item in scrapers:
				delay.append(item.data() or 0.0)
				
			log(json.dumps(details))
				
			result	= self.compile_results(details)

			log(json.dumps(result))

			return_details(result)
				
			self.wait(start, max(delay))
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
					if k == 'description':
						result_[k].append(u"{}from: {}\n{}".format('*' * 80, site, v)) 
					else:
						result_[k].append(v) 
				else:
					log("skipping: {} {}".format(site, k))
		
		#return top ranking
		result	= {}	
		for k, v in result_.items():
			if k == 'description':
				result[k] = "\n\n".join(result_[k])
			elif k not in ('thumb', 'fanart', 'extras'):
				result[k] = result_[k][0]
			else:
				result[k] = [ii for i in result_[k] for ii in i]
				
		return result

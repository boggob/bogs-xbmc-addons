# -*- coding: UTF-8 -*-

import sys
import time
import urllib
import requests
from requests.exceptions import Timeout
import json
from threading import Thread
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from theaudiodb import theaudiodb_artistdetails
from theaudiodb import theaudiodb_artistalbums
from musicbrainz import musicbrainz_artistfind
from musicbrainz import musicbrainz_artistdetails
from discogs import discogs_artistfind
from discogs import discogs_artistdetails
from discogs import discogs_artistalbums
from allmusic import allmusic_artistdetails
from nfo import nfo_geturl
from fanarttv import fanarttv_artistart
from utils import *


def get_data(url, json):
    useragent = {'User-Agent': 'Intergral Artists Scraper/%s ( http://kodi.tv )' % xbmcaddon.Addon().getAddonInfo('version')}
    try:
        response = requests.get(url, headers=useragent, timeout=5)
    except Timeout:
        log('request timed out')
        return
    if response.status_code == 503:
        log('exceeding musicbrainz api limit')
        return
    elif response.status_code == 429:
        log('exceeding discogs api limit')
        return
    if json:
        try:
            return response.json()
        except:
            return
    else:
        return response.text


class Scraper():
    def __init__(self, action, key, artist, url, nfo):
        # get start time in milliseconds
        self.start = int(round(time.time() * 1000))
        # return a dummy result, this is just for backward compitability with xml based scrapers https://github.com/xbmc/xbmc/pull/11632
        if action == 'resolveid':
            result = self.resolve_mbid(key)
            if result:
                self.return_resolved(result)
        # search for artist name matches
        elif action == 'find':
            # both musicbrainz and discogs allow 1 api per second. this query requires 1 musicbrainz api call and optionally 1 discogs api call
            RATELIMIT = 1000
            # try musicbrainz first
            result = self.find_artist(artist, 'musicbrainz')
            if result:
                self.return_search(result)
            # fallback to discogs
            else:
                result = self.find_artist(artist, 'discogs')
                if result:
                    self.return_search(result)
        # return info using artistname / id's
        elif action == 'getdetails':
            details = {}
            url = json.loads(url)
            artist = url['artist'].encode('utf-8')
            mbid = url.get('mbid', '')
            dcid = url.get('dcid', '')
            threads = []
            extrathreads = []
            # we have a musicbrainz id
            if mbid:
                # musicbrainz allows 1 api per second.
                RATELIMIT = 1000
                scrapers = [[mbid, 'musicbrainz'], [mbid, 'theaudiodb'], [mbid, 'fanarttv']]
                for item in scrapers:
                    thread = Thread(target = self.get_details, args = (item[0], item[1], details))
                    threads.append(thread)
                    thread.start()
                # wait for musicbrainz to finish
                threads[0].join()
                # check if we have a result:
                if 'musicbrainz' in details:
                    extrascrapers = []
                    # only scrape allmusic if we have an url provided by musicbrainz
                    if 'allmusic-url' in details['musicbrainz']:
                        extrascrapers.append([details['musicbrainz']['allmusic-url'], 'allmusic'])
                    # only scrape discogs if we have an url provided by musicbrainz and discogs scraping is explicitly enabled (as it is slower)
                    if 'discogs-url' in details['musicbrainz'] and xbmcaddon.Addon().getSetting('usediscogs') == '1':
                        dcid = int(details['musicbrainz']['discogs-url'].rsplit('/', 1)[1])
                        extrascrapers.append([dcid, 'discogs'])
                        # discogs allows 1 api per second. this query requires 2 discogs api calls
                        RATELIMIT = 2000
                    for item in extrascrapers:
                        thread = Thread(target = self.get_details, args = (item[0], item[1], details))
                        extrathreads.append(thread)
                        thread.start()
            # we have a discogs id
            else:
                result = self.get_details(dcid, 'discogs', details)
                # discogs allow 1 api per second. this query requires 2 discogs api call
                RATELIMIT = 2000
            if threads:
                for thread in threads:
                    thread.join()
            if extrathreads:
                for thread in extrathreads:
                    thread.join()
            result = self.compile_results(details)
            if result:
                self.return_details(result)
        elif action == 'NfoUrl':
            mbid = nfo_geturl(nfo)
            if mbid:
                result = self.resolve_mbid(mbid)
                if result:
                    self.return_nfourl(result)
        # get end time in milliseconds
        self.end = int(round(time.time() * 1000))
        # handle musicbrainz and discogs ratelimit
        if action == 'find' or action == 'getdetails':
            if self.end - self.start < RATELIMIT:
                # wait max 1 second
                diff = RATELIMIT - (self.end - self.start)
                xbmc.sleep(diff)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def resolve_mbid(self, mbid):
        # create dummy result
        item = {}
        item['artist'] = ''
        item['mbartistid'] = mbid
        return item

    def find_artist(self, artist, site):
        json = True
        # musicbrainz
        if site == 'musicbrainz':
            url = MUSICBRAINZURL % (MUSICBRAINZSEARCH % urllib.quote_plus(artist))
            scraper = musicbrainz_artistfind
        # musicbrainz
        if site == 'discogs':
            url = DISCOGSURL % (DISCOGSSEARCH % (urllib.quote_plus(artist), DISCOGSKEY , DISCOGSSECRET))
            scraper = discogs_artistfind
        result = get_data(url, json)
        if not result:
            return
        artistresults = scraper(result)
        return artistresults

    def get_details(self, param, site, details):
        if site == 'musicbrainz':
            albumresults = musicbrainz_albumdetails2(param)
            if not albumresults:
                return
            details[site] = albumresults
            return details
        else:
            return details		

    def compile_results(self, details):
        result = {}
        thumbs = []
        fanart = []
        extras = []
        # merge metadata results, start with the least accurate sources
        if 'discogs' in details:
            for k, v in details['discogs'].items():
                result[k] = v
                if k == 'thumb':
                    thumbs.append(v)
        if 'allmusic' in details:
            for k, v in details['allmusic'].items():
                result[k] = v
                if k == 'thumb':
                    thumbs.append(v)
        if 'theaudiodb' in details:
            for k, v in details['theaudiodb'].items():
                result[k] = v
                if k == 'thumb':
                    thumbs.append(v)
                elif k == 'fanart':
                    fanart.append(v)
                if k == 'extras':
                    extras.append(v)
        if 'musicbrainz' in details:
            for k, v in details['musicbrainz'].items():
                result[k] = v
        if 'fanarttv' in details:
            for k, v in details['fanarttv'].items():
                result[k] = v
                if k == 'thumb':
                    thumbs.append(v)
                elif k == 'fanart':
                    fanart.append(v)
                if k == 'extras':
                    extras.append(v)
        # provide artwork from all scrapers for getthumb / getfanart option
        if result:
            # artworks from most accurate sources first
            thumbs.reverse()
            thumbnails = []
            fanart.reverse()
            fanarts = []
            # the order for extra art does not matter
            extraart = []
            for thumblist in thumbs:
                for item in thumblist:
                    thumbnails.append(item)
            for extralist in extras:
                for item in extralist:
                    extraart.append(item)
            # add the extra art to the end of the thumb list
            thumbnails.extend(extraart)
            result['thumb'] = thumbnails
            for fanartlist in fanart:
                for item in fanartlist:
                    fanarts.append(item)
            result['fanart'] = fanarts
        data = self.user_prefs(details, result)
        return data

    def user_prefs(self, details, result):
        # user preferences
        lang = 'biography' + xbmcaddon.Addon().getSetting('lang')
        bio = xbmcaddon.Addon().getSetting('bio')
        if bio == 'theaudiodb' and 'theaudiodb' in details:
            if lang in details['theaudiodb']:
                result['biography'] = details['theaudiodb'][lang]
            elif 'biographyEN' in details['theaudiodb']:
                result['biography'] = details['theaudiodb']['biographyEN']
        elif bio == 'discogs' and 'discogs' in details:
            result['biography'] = details['discogs']['biography']
        discog = xbmcaddon.Addon().getSetting('discog')
        if (discog in details) and ('albums' in details[discog]):
            result['albums'] = details[discog]['albums']
        genre = xbmcaddon.Addon().getSetting('genre')
        if (genre in details) and ('genre' in details[genre]):
            result['genre'] = details[genre]['genre']
        style = xbmcaddon.Addon().getSetting('style')
        if (style in details) and ('styles' in details[style]):
            result['styles'] = details[style]['styles']
        mood = xbmcaddon.Addon().getSetting('mood')
        if (mood in details) and ('moods' in details[mood]):
            result['moods'] = details[mood]['moods']
        return result

    def return_search(self, data):
        for item in data:
            listitem = xbmcgui.ListItem(item['artist'], offscreen=True)
            listitem.setArt({'thumb': item['thumb']})
            listitem.setProperty('artist.genre', item['genre'])
            listitem.setProperty('artist.born', item['born'])
            listitem.setProperty('relevance', item['relevance'])
            if 'type' in item:
                listitem.setProperty('artist.type', item['type'])
            if 'gender' in item:
                listitem.setProperty('artist.gender', item['gender'])
            if 'disambiguation' in item:
                listitem.setProperty('artist.disambiguation', item['disambiguation'])
            url = {'artist':item['artist']}
            if 'mbid' in item:
                url['mbid'] = item['mbid']
            if 'dcid' in item:
                url['dcid'] = item['dcid']
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=json.dumps(url), listitem=listitem, isFolder=True)

    def return_nfourl(self, item):
        url = {'artist':item['artist'], 'mbid':item['mbartistid']}
        listitem = xbmcgui.ListItem(offscreen=True)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=json.dumps(url), listitem=listitem, isFolder=True)

    def return_resolved(self, item):
        url = {'artist':item['artist'], 'mbid':item['mbartistid']}
        listitem = xbmcgui.ListItem(path=json.dumps(url), offscreen=True)
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)

    def return_details(self, item):
        if not 'artist' in item:
            return
        listitem = xbmcgui.ListItem(item['artist'], offscreen=True)
        if 'mbartistid' in item:
            listitem.setProperty('artist.musicbrainzid', item['mbartistid'])
        if 'genre' in item:
            listitem.setProperty('artist.genre', item['genre'])
        if 'biography' in item:
            listitem.setProperty('artist.biography', item['biography'])
        if 'styles' in item:
            listitem.setProperty('artist.styles', item['styles'])
        if 'moods' in item:
            listitem.setProperty('artist.moods', item['moods'])
        if 'instruments' in item:
            listitem.setProperty('artist.instruments', item['instruments'])
        if 'disambiguation' in item:
            listitem.setProperty('artist.disambiguation', item['disambiguation'])
        if 'type' in item:
            listitem.setProperty('artist.type', item['type'])
        if 'sortname' in item:
            listitem.setProperty('artist.sortname', item['sortname'])
        if 'active' in item:
            listitem.setProperty('artist.years_active', item['active'])
        if 'born' in item:
            listitem.setProperty('artist.born', item['born'])
        if 'formed' in item:
            listitem.setProperty('artist.formed', item['formed'])
        if 'died' in item:
            listitem.setProperty('artist.died', item['died'])
        if 'disbanded' in item:
            listitem.setProperty('artist.disbanded', item['disbanded'])
        art = {}
        if 'clearlogo' in item:
            art['clearlogo'] = item['clearlogo']
        if 'banner' in item:
            art['banner'] = item['banner']
        if 'clearart' in item:
            art['clearart'] = item['clearart']
        if 'landscape' in item:
            art['landscape'] = item['landscape']
        listitem.setArt(art)
        if 'fanart' in item:
            listitem.setProperty('artist.fanarts', str(len(item['fanart'])))
            for count, fanart in enumerate(item['fanart']):
                listitem.setProperty('artist.fanart%i.url' % (count + 1), fanart['image'])
                listitem.setProperty('artist.fanart%i.preview' % (count + 1), fanart['preview'])
        if 'thumb' in item:
            listitem.setProperty('artist.thumbs', str(len(item['thumb'])))
            for count, thumb in enumerate(item['thumb']):
                listitem.setProperty('artist.thumb%i.url' % (count + 1), thumb['image'])
                listitem.setProperty('artist.thumb%i.preview' % (count + 1), thumb['preview'])
                listitem.setProperty('artist.thumb%i.aspect' % (count + 1), thumb['aspect'])
        if 'albums' in item:
            listitem.setProperty('artist.albums', str(len(item['albums'])))
            for count, album in enumerate(item['albums']):
                listitem.setProperty('artist.album%i.title' % (count + 1), album['title'])
                listitem.setProperty('artist.album%i.year' % (count + 1), album['year'])
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)

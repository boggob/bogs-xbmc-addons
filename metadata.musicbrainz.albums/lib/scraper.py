# -*- coding: UTF-8 -*-

import sys
import urllib
import urllib2
import json
import time
import _strptime # https://bugs.python.org/issue7980
from threading import Thread
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from theaudiodb import theaudiodb_albumdetails
from musicbrainz import musicbrainz_albumfind
from musicbrainz import musicbrainz_albumdetails
from musicbrainz import musicbrainz_albumart
from musicbrainz2 import musicbrainz_albumdetails2
from discogs import discogs_albumfind
from discogs import discogs_albumdetails
from allmusic import allmusic_albumfind
from allmusic import allmusic_albumdetails
from nfo import nfo_geturl
from fanarttv import fanarttv_albumart
from utils import *


def get_data(url):
    try:
        req = urllib2.Request(url, headers={'User-Agent': 'Intergral Albums Scraper/%s ( http://kodi.tv )' % xbmcaddon.Addon().getAddonInfo('version')})
        request = urllib2.urlopen(req)
        response = request.read()
        request.close()
    except:
        response = ''
    return response


class Scraper():
    def __init__(self, action, key, artist, album, url, nfo):
        # get start time in milliseconds
        self.start = int(round(time.time() * 1000))
        # return a dummy result, this is just for backward compitability with xml based scrapers https://github.com/xbmc/xbmc/pull/11632
        if action == 'resolveid':
            result = self.resolve_mbid(key)
            if result:
                self.return_resolved(result)
        # search for artist name / album title matches
        elif action == 'find':
            # both musicbrainz and discogs allow 1 api per second. this query requires 1 musicbrainz api call and optionally 1 discogs api call
            RATELIMIT = 1000
            # try musicbrainz first
            result = self.find_album(artist, album, 'musicbrainz')
            if result:
                self.return_search(result)
            # fallback to discogs
            else:
                result = self.find_album(artist, album, 'discogs')
                if result:
                    self.return_search(result)
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
            # we have a musicbrainz album id, but no musicbrainz releasegroupid
            if mbid and not mbreleasegroupid:
                # musicbrainz allows 1 api per second.
                RATELIMIT = 1000
                for item in [[mbid, 'musicbrainz'], [mbid, 'coverarchive']]:
                    thread = Thread(target = self.get_details, args = (item[0], item[1], details))
                    threads.append(thread)
                    thread.start()
                # wait for musicbrainz to finish
                threads[0].join()
                # check if we have a result:
                if 'musicbrainz' in details:
                    # get the info we need to start the other scrapers
                    artist = details['musicbrainz']['artist_description'].encode('utf-8')
                    album = details['musicbrainz']['album'].encode('utf-8')
                    mbreleasegroupid = details['musicbrainz']['mbreleasegroupid']
                    scrapers = [[mbreleasegroupid, 'theaudiodb'], [mbreleasegroupid, 'fanarttv'], [[artist, album], 'allmusic']]
                    if xbmcaddon.Addon().getSetting('usediscogs') == '1':
                        scrapers.append([[artist, album, dcid], 'discogs'])
                        # discogs allows 1 api per second. this query requires 2 discogs api calls
                        RATELIMIT = 2000
                    for item in scrapers:
                        thread = Thread(target = self.get_details, args = (item[0], item[1], details))
                        threads.append(thread)
                        thread.start()
            # we have a discogs id and artistname and albumtitle
            elif dcid:
                # discogs allows 1 api per second. this query requires 1 discogs api call
                RATELIMIT = 1000
                for item in [[[artist, album, dcid], 'discogs'], [[artist, album], 'allmusic']]:
                    thread = Thread(target = self.get_details, args = (item[0], item[1], details))
                    threads.append(thread)
                    thread.start()
            # we have musicbrainz album id, musicbrainz releasegroupid, artistname and albumtitle
            else:
                # musicbrainz allows 1 api per second.
                RATELIMIT = 1000
                scrapers = [[mbid, 'musicbrainz'], [mbreleasegroupid, 'theaudiodb'], [mbreleasegroupid, 'fanarttv'], [mbid, 'coverarchive'], [[artist, album], 'allmusic']]
                if xbmcaddon.Addon().getSetting('usediscogs') == '1':
                    scrapers.append([[artist, album, dcid], 'discogs'])
                    # discogs allows 1 api per second. this query requires 2 discogs api calls
                    RATELIMIT = 2000
                for item in scrapers:
                    thread = Thread(target = self.get_details, args = (item[0], item[1], details))
                    threads.append(thread)
                    thread.start()
            for thread in threads:
                thread.join()
            result = self.compile_results(details)
            if result:
                self.return_details(result)
        # extract the mbid from the provided musicbrainz url
        elif action == 'NfoUrl':
            mbid = nfo_geturl(nfo)
            if mbid:
                # create a dummy item
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
        item['artist_description'] = ''
        item['album'] = ''
        item['mbalbumid'] = mbid
        item['mbreleasegroupid'] = ''
        return item

    def find_album(self, artist, album, site):
        # musicbrainz
        if site == 'musicbrainz':
            url = MUSICBRAINZURL % (MUSICBRAINZSEARCH % (urllib.quote_plus(album), urllib.quote_plus(artist), urllib.quote_plus(artist)))
            scraper = musicbrainz_albumfind
        # discogs
        elif site == 'discogs':
            url = DISCOGSURL % (DISCOGSSEARCH % (urllib.quote_plus(album), urllib.quote_plus(artist), DISCOGSKEY , DISCOGSSECRET))
            scraper = discogs_albumfind
        # allmusic
        elif site == 'allmusic':
            url = ALLMUSICURL % (ALLMUSICSEARCH % (urllib.quote_plus(artist), urllib.quote_plus(album)))
            scraper = allmusic_albumfind
        result = get_data(url)
        if not result:
            return
        if not site == 'allmusic':
            result = json.loads(result)
        albumresults = scraper(result)
        return albumresults

    def get_details(self, param, site, details):
        #bypass all other options for now
        albumresults = musicbrainz_albumdetails2(param)
        if not albumresults:
            return
        details[site] = albumresults
        return details

    def compile_results(self, details):
        result = {}
        thumbs = []
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
                if k == 'extras':
                    extras.append(v)
        if 'musicbrainz' in details:
            for k, v in details['musicbrainz'].items():
                result[k] = v
        if 'coverarchive' in details:
            for k, v in details['coverarchive'].items():
                result[k] = v
                if k == 'thumb':
                    thumbs.append(v)
                if k == 'extras':
                    extras.append(v)
        # prefer artwork from fanarttv
        if 'fanarttv' in details:
            for k, v in details['fanarttv'].items():
                result[k] = v
                if k == 'thumb':
                    thumbs.append(v)
                if k == 'extras':
                    extras.append(v)
        # use musicbrainz artist list as they provide mbid's, these can be passed to the artist scraper
        if 'musicbrainz' in details:
            result['artist'] = details['musicbrainz']['artist']
        # provide artwork from all scrapers for getthumb option
        if result:
            # thumb list from most accurate sources first
            thumbs.reverse()
            thumbnails = []
            for thumblist in thumbs:
                for item in thumblist:
                    thumbnails.append(item)
            # the order for extra art does not matter
            extraart = []
            for extralist in extras:
                for item in extralist:
                    extraart.append(item)
            # add the extra art to the end of the thumb list
            thumbnails.extend(extraart)
            result['thumb'] = thumbnails
        data = self.user_prefs(details, result)
        return data

    def user_prefs(self, details, result):
        # user preferences
        lang = 'description' + xbmcaddon.Addon().getSetting('lang')
        if 'theaudiodb' in details:
            if lang in details['theaudiodb']:
                result['description'] = details['theaudiodb'][lang]
            elif 'descriptionEN' in details['theaudiodb']:
                result['description'] = details['theaudiodb']['descriptionEN']
        genre = xbmcaddon.Addon().getSetting('genre')
        if (genre in details) and ('genre' in details[genre]):
            result['genre'] = details[genre]['genre']
        style = xbmcaddon.Addon().getSetting('style')
        if (style in details) and ('styles' in details[style]):
            result['styles'] = details[style]['styles']
        mood = xbmcaddon.Addon().getSetting('mood')
        if (mood in details) and ('moods' in details[mood]):
            result['moods'] = details[mood]['moods']
        theme = xbmcaddon.Addon().getSetting('theme')
        if (theme in details) and ('themes' in details[theme]):
            result['themes'] = details[theme]['themes']
        rating = xbmcaddon.Addon().getSetting('rating')
        if (rating in details) and ('rating' in details[rating]):
            result['rating'] = details[rating]['rating']
            result['votes'] = details[rating]['votes']
        return result

    def return_search(self, data):
        for count, item in enumerate(data):
            listitem = xbmcgui.ListItem(item['album'], offscreen=True)
            listitem.setArt({'thumb': item['thumb']})
            listitem.setProperty('album.artist', item['artist_description'])
            listitem.setProperty('album.year', item.get('year',''))
            listitem.setProperty('relevance', item['relevance'])
            url = {'artist':item['artist_description'], 'album':item['album']}
            if 'mbalbumid' in item:
                url['mbalbumid'] = item['mbalbumid']
            if 'mbreleasegroupid' in item:
                url['mbreleasegroupid'] = item['mbreleasegroupid']
            if 'dcalbumid' in item:
                url['dcalbumid'] = item['dcalbumid']
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=json.dumps(url), listitem=listitem, isFolder=True)

    def return_nfourl(self, item):
        url = {'artist':item['artist_description'], 'album':item['album'], 'mbalbumid':item['mbalbumid'], 'mbreleasegroupid':item['mbreleasegroupid']}
        listitem = xbmcgui.ListItem(offscreen=True)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=json.dumps(url), listitem=listitem, isFolder=True)

    def return_resolved(self, item):
        url = {'artist':item['artist_description'], 'album':item['album'], 'mbalbumid':item['mbalbumid'], 'mbreleasegroupid':item['mbreleasegroupid']}
        listitem = xbmcgui.ListItem(path=json.dumps(url), offscreen=True)
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)

    def return_details(self, item):
        listitem = xbmcgui.ListItem(item['album'], offscreen=True)
        if 'mbalbumid' in item:
            listitem.setProperty('album.musicbrainzid', item['mbalbumid'])
            listitem.setProperty('album.releaseid', item['mbalbumid'])
        if 'mbreleasegroupid' in item:
            listitem.setProperty('album.releasegroupid', item['mbreleasegroupid'])
        if 'scrapedmbid' in item:
            listitem.setProperty('album.scrapedmbid', item['scrapedmbid'])
        if 'artist' in item:
            listitem.setProperty('album.artists', str(len(item['artist'])))
            for count, artist in enumerate(item['artist']):
                listitem.setProperty('album.artist%i.name' % (count + 1), artist['artist'])
                listitem.setProperty('album.artist%i.musicbrainzid' % (count + 1), artist.get('mbartistid', ''))
                listitem.setProperty('album.artist%i.sortname' % (count + 1), artist.get('artistsort', ''))
        if 'genre' in item:
            listitem.setProperty('album.genre', item['genre'])
        if 'styles' in item:
            listitem.setProperty('album.styles', item['styles'])
        if 'moods' in item:
            listitem.setProperty('album.moods', item['moods'])
        if 'themes' in item:
            listitem.setProperty('album.themes', item['themes'])
        if 'description' in item:
            listitem.setProperty('album.review', item['description'])
        if 'releasedate' in item:
            listitem.setProperty('album.release_date', item['releasedate'])
        if 'artist_description' in item:
            listitem.setProperty('album.artist_description', item['artist_description'])
        if 'label' in item:
            listitem.setProperty('album.label', item['label'])
        if 'type' in item:
            listitem.setProperty('album.type', item['type'])
        if 'compilation' in item:
            listitem.setProperty('album.compilation', item['compilation'])
        if 'releasetype' in item:
            listitem.setProperty('album.release_type', item['releasetype'])
        if 'year' in item:
            listitem.setProperty('album.year', item['year'])
        if 'rating' in item:
            listitem.setProperty('album.rating', item['rating'])
        if 'userrating' in item:
            listitem.setProperty('album.userrating', item['userrating'])
        if 'votes' in item:
            listitem.setProperty('album.votes', item['votes'])
        art = {}
        if 'discart' in item:
            art['discart'] = item['discart']
        if 'back' in item:
            art['back'] = item['back']
        if 'spine' in item:
            art['spine'] = item['spine']
        if '3dcase' in item:
            art['3dcase'] = item['3dcase']
        if '3dflat' in item:
            art['3dflat'] = item['3dflat']
        if '3dface' in item:
            art['3dface'] = item['3dface']
        listitem.setArt(art)
        if 'thumb' in item:
            listitem.setProperty('album.thumbs', str(len(item['thumb'])))
            for count, thumb in enumerate(item['thumb']):
                listitem.setProperty('album.thumb%i.url' % (count + 1), thumb['image'])
                listitem.setProperty('album.thumb%i.aspect' % (count + 1), thumb['aspect'])
                listitem.setProperty('album.thumb%i.preview' % (count + 1), thumb['preview'])
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)

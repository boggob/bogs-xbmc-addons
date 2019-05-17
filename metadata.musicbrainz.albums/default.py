# -*- coding: UTF-8 -*-
import sys
import urllib
import urlparse
import socket
from lib.scraper import Scraper


class Main:
    def __init__(self):
        action, key, artist, album, url, nfo = self._parse_argv()
        Scraper(action, key, artist, album, url, nfo)

    def _parse_argv(self):
        params = dict(urlparse.parse_qsl(sys.argv[2].lstrip('?')))
        # actions: resolveid, find, getdetails, NfoUrl
        action = params['action']
        # key: musicbrainz id
        key = params.get('key', '')
        # artist: artistname
        artist = params.get('artist', '')
        # album: albumtitle
        album = params.get('title', '')
        # url: provided by the scraper on previous run
        url = params.get('url', '')
        # nfo: musicbrainz url from .nfo file
        nfo = params.get('nfo', '')
        return action, key, artist, album, url, nfo


if (__name__ == '__main__'):
    socket.setdefaulttimeout(5)
    Main()

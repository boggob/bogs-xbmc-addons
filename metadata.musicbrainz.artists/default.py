# -*- coding: UTF-8 -*-
import sys
import urllib
import urlparse
from lib.scraper import Scraper


class Main:
    def __init__(self):
        action, key, artist, url, nfo = self._parse_argv()
        Scraper(action, key, artist, url, nfo)

    def _parse_argv(self):
        params = dict(urlparse.parse_qsl(sys.argv[2].lstrip('?')))
        action = params['action']
        key = params.get('key', '')
        artist = params.get('artist', '')
        url = params.get('url', '')
        nfo = params.get('nfo', '')
        return action, key, artist, url, nfo


if (__name__ == '__main__'):
    Main()

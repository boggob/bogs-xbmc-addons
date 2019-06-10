# -*- coding: UTF-8 -*-

from collections import namedtuple

Action		= namedtuple('Action', ('name', 'function', 'wait'))
ScraperType	= namedtuple('ScraperType', ('artistfind', 'getdetails'))

_ = """
AUDIODBKEY = '58424d43204d6564696120'
AUDIODBURL = 'https://www.theaudiodb.com/api/v1/json/%s/%s'
AUDIODBSEARCH = 'search.php?s=%s'
AUDIODBDETAILS = 'artist-mb.php?i=%s'
AUDIODBDISCOGRAPHY = 'discography-mb.php?s=%s'




FANARTVKEY = 'ed4b784f97227358b31ca4dd966a04f1'
FANARTVURL = 'https://webservice.fanart.tv/v3/music/%s?api_key=%s'
"""
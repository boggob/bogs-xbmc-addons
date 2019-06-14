# -*- coding: UTF-8 -*-

from collections import namedtuple

Action		= namedtuple('Action', ('name', 'function', 'wait'))
ScraperType	= namedtuple('ScraperType', ('find', 'getdetails'))

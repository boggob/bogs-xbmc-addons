# -*- coding: UTF-8 -*-

import requests
from requests.exceptions import Timeout

from lib.platform import log, VERSION, LOGERROR, SETTINGS



def get_data(url, json_):
	log(url)
	useragent = {'User-Agent': 'Intergral Artists Scraper/{} ( http://kodi.tv )'.format(VERSION) }
	try:
		response = requests.get(url, headers=useragent, timeout=SETTINGS['misc']['timeout'])
	except Timeout:
		log('request timed out', LOGERROR)
		raise
	if response.status_code == 503:
		log('server unavailable', LOGERROR)
		raise
	elif response.status_code == 429:
		log('too many requests', LOGERROR)
		raise
	if json_:
		try:
			return response.json()
		except Exception:
			return
	else:
		return response.text

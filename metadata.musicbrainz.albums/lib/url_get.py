# -*- coding: UTF-8 -*-

import requests
from requests.exceptions import Timeout

from lib.platform import log, VERSION, LOGERROR, SETTINGS



def get_data(url, use_json, ignore_404 = False):
	log(url)
	useragent = {'User-Agent': 'Intergral Artists Scraper/{} ( http://kodi.tv )'.format(VERSION) }
	try:
		response = requests.get(url, headers=useragent, timeout=SETTINGS['misc']['timeout'])
	except Timeout:
		log('request timed out', LOGERROR)
		raise
	
	if response.status_code == 503:
		log('server unavailable', LOGERROR)
		response.raise_for_status()
	elif response.status_code == 429:
		log('too many requests', LOGERROR)
		response.raise_for_status()
	elif response.status_code == 404 and ignore_404:
		return None
	elif response.status_code :
		response.raise_for_status()

	if use_json:
		return response.json()
	else:
		return response.text

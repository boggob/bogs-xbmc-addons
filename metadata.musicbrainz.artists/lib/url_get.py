# -*- coding: UTF-8 -*-

import requests
from requests.exceptions import Timeout

from lib.platform import log, VERSION



def get_data(url, json_):
	log(url)
	useragent = {'User-Agent': 'Intergral Artists Scraper/{} ( http://kodi.tv )'.format(VERSION) }
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
	if json_:
		try:
			return response.json()
		except Exception:
			return
	else:
		return response.text

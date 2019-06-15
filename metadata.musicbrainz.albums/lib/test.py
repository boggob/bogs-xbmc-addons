# -*- coding: UTF-8 -*-

if __name__ == "__main__":
	import json
	import os.path
	import sys

	
	dir_  = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(dir_)
	import lib.scraper
	

	#pprint.pprint(musicbrainz_arstistdetails2('24f1766e-9635-4d58-a4d4-9413f9f98a4c', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
	#pprint.pprint(musicbrainz_arstistdetails2('fd14da1b-3c2d-4cc8-9ca6-fc8c62ce6988', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
	
	with open(r'd:\temp\out.txt', 'w' ) as outh:
		sys.stdout = outh

		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : 'be4dfc70-fb62-3589-aeb4-4680cea68c50', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '033ab928-e9c7-443d-86dc-5d18393e97b9', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '9787a825-5dab-4c89-943d-4b142a03cb56', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : 'a8976979-398a-4d03-9998-c24455885151', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '2a06e2db-5d86-4294-8388-3109e6228963', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '2a018799-55cb-43f1-a0ae-4a54a319d768', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : 'fd14a4e3-f39a-4fef-afba-36ab8d22902b', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '1bb8e966-cc02-3b98-92c3-16c0cbc9cb1b', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '72995c3c-db08-4a2d-8823-f5d718b78c3d', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '35e0a764-99cd-4ecf-af94-96375cb0f9af', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '5ef9848e-0a05-4729-9a99-8ff3f645275b', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '', 'artist': u'Yann Tiersen', 'album' : u'Le Fabuleux Destin d’Amélie Poulain', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '', 'artist': '', 'album' : '', 'dcalbumid': '497852'}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '2e0542d1-5c0b-4600-ab77-64870cc619de', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '22ee7fae-b30a-4c69-9119-ab895901a898', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		#lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : '83efe2a2-f6c7-379b-942f-dfa409463014', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		lib.scraper.Scraper('getdetails', None, None, None, json.dumps({'mbalbumid' : 'cab86b06-ec55-496f-b43a-df9dddfa7de5', 'artist': '', 'album' : '', 'dcalbumid': ''}), None)
		


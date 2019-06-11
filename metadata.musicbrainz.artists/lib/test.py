
if __name__ == "__main__":
	import json
	import os.path
	import sys

	
	dir_  = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(dir_)
	import lib.scraper
	

	#pprint.pprint(musicbrainz_arstistdetails2('24f1766e-9635-4d58-a4d4-9413f9f98a4c'))
	#pprint.pprint(musicbrainz_arstistdetails2('fd14da1b-3c2d-4cc8-9ca6-fc8c62ce6988'))
	
	with open(r'd:\temp\out.txt', 'w' ) as outh:
		sys.stdout = outh
		lib.scraper.Scraper('getdetails', None, None, json.dumps({'mbid' : 'fd14da1b-3c2d-4cc8-9ca6-fc8c62ce6988'}), None)
		#lib.scraper.Scraper('getdetails', None, None, json.dumps({'mbid' : '0a46cf2a-61bd-447d-b8fd-a2b32eb20282'}), None)
		#lib.scraper.Scraper('getdetails', None, None, json.dumps({'mbid' : 'f27ec8db-af05-4f36-916e-3d57f91ecf5e'}), None)
		#lib.scraper.Scraper('getdetails', None, None, json.dumps({'mbid' : '0d21b01f-21f2-419b-8d98-4158ba0c0aa4'}), None)
		#lib.scraper.Scraper('getdetails', None, None, json.dumps({'mbid' : '678d88b2-87b0-403b-b63d-5da7465aecc3'}), None)
		#lib.scraper.Scraper('getdetails', None, None, json.dumps({'mbid' : '2251b277-2dfb-4cf1-83f3-27e29f902440'}), None)
		#lib.scraper.Scraper('getdetails', None, None, json.dumps({'dcid' : 1471648}), None)
		
	
		
	#raise 1
	
	




if __name__ == "__main__":
	import json
	import os.path
	import pprint 
	import sys

	
	dir_  = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(dir_)
	import lib.scraper
	

	#pprint.pprint(musicbrainz_arstistdetails2('24f1766e-9635-4d58-a4d4-9413f9f98a4c'))
	#pprint.pprint(musicbrainz_arstistdetails2('fd14da1b-3c2d-4cc8-9ca6-fc8c62ce6988'))
	
	with open(r'd:\temp\out.txt', 'w' ) as outh:
		sys.stdout = outh
		#lib.scraper.Scraper('getdetails', None, None, json.dumps({'mbid' : 'fd14da1b-3c2d-4cc8-9ca6-fc8c62ce6988'}), None)
		lib.scraper.Scraper('getdetails', None, None, json.dumps({'mbid' : '0a46cf2a-61bd-447d-b8fd-a2b32eb20282'}), None)
		
	#raise 1
	
	



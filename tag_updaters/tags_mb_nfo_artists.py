import collections
import codecs
import os, sys


pt =  os.path.split(__file__)[0]
print pt
sys.path.append(pt)
sys.path.append(os.path.split(__file__)[0])
import scrapers
import tags
import user_input

class flushfile(object):
	def __init__(self, f):
		self.f = f
	def write(self, x):
		self.f.write(x)
		self.f.flush()

import sys
sys.stdout = flushfile(sys.stdout)

####################################
if 1:
	PATHS = [
	r'C:\files\music\Assorted\A-H',
	 r'C:\files\music\Assorted\I-Z',
	 r'C:\files\music\Assorted\No Album',
	 r'C:\files\music\Assorted\Tripple J',	
	 #r'C:\files\music\Assorted',
	 r'C:\files\music\Classical',
	 r'C:\files\music\World',
	 r'C:\files\music\Matilda',
	 r'C:\files\music\musique_wog',
	 r'C:\files\music\Jaz',
	]
	OUTFILE = "C:/files/music/art/artists.xml"
else:
	PATHS = [user_input.input_directory()]
	print PATHS
	OUTFILE = "C:/temp/artists_test.xml"
	


def handler():
	arts		= collections.defaultdict(set)
	for path in PATHS:
		for fi, attr_map, of in tags.get_files(path):
			print " %%", of
			for attr, name in (
				('musicbrainz_artistid', 'artist'),
				('musicbrainz_albumartistid', 'albumartist'),
			):
				id_as	= attr_map[attr][0](fi).strip()
				nma		= attr_map[name][0](fi).strip()
				
				if nma and id_as:
					for spl in ('/', ';', '\\'):
						spl1	= set(id_as.split(spl)) 
						if len(spl1) > 1:
							break
					
					for id_a in spl1:
						arts[nma.upper()].add((nma,id_a.upper()))
					print nma.encode('utf8'),  id_a.upper()
	import pprint
	pprint.pprint(dict(arts))
	cleaned = {}
	for artist, mbid in sorted(arts.iteritems()):
		if len(mbid) == 1:
			cleaned[artist] = list(mbid)[0]
		else:
			print "!!!Non Unique MBID", repr(artist), repr(mbid)
			cleaned[artist] = list(mbid)[0]
	
	with codecs.open(OUTFILE, "w", encoding='utf8') as fo:		
		#scrapers.aggregate(((artist,mbid, []) for artist, mbid in sorted(cleaned.iteritems())), fo, classical = True)
		fo.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<musicdb>\n')
		for idx, (key, (artist,mbid)) in enumerate(sorted(cleaned.iteritems())):
			print "\tArtist", idx, len(cleaned), repr(artist) 
			tmp = scrapers.lastfm_artist(artist,[],mbid) 
			import pprint
			#pprint.pprint(tmp)
			#pprint.pprint(scrapers.encode(tmp))
			fo.write(scrapers.unquote(scrapers.encode(tmp)))
			fo.flush()
		fo.write("\n</musicdb>\n")			



def main():
	print "*****starting"
	handler()
	print "*****done"	
main()
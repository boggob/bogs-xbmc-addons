import collections
import codecs
import os, sys

pt =  os.path.split(__file__)[0]
print pt
sys.path.append(pt)
sys.path.append(os.path.split(__file__)[0])
import scrapers
import tags

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
	 r'C:\files\music\Assorted',
	 r'C:\files\music\Classical',
	 r'C:\files\music\World',
	 r'C:\files\music\Matilda',
	 r'C:\files\music\musique_wog',
	 r'C:\files\music\Jaz',
	]
	OUTFILE = "C:/temp/albums.xml"
else:
	PATHS = [
	 r'C:\temp\aaaa',
	]
	OUTFILE = "C:/temp/albums_test.xml"
	


def handler():
	arts		= collections.defaultdict(set)
	for path in PATHS:
		for fi, attr_map, of in tags.get_files(path):
			for attr, name in (
				('musicbrainz_artistid', 'artist'),
				('musicbrainz_albumartistid', 'albumartist'),
			):
				id_a	= attr_map[attr][0](fi)
				nma		= attr_map[name][0](fi)
				
				if nma and nma.upper().strip() and id_a:
					arts[nma.upper().strip()].add(id_a.upper().strip())
					print "\t%%", nma.encode('utf8'),  arts[nma.upper().strip()]
	import pprint
	pprint.pprint(arts)
	cleaned = {}
	for artist, mbid in sorted(arts.iteritems()):
		if len(mbid) == 1:
			cleaned[artist] = list(mbid)[0]
		else:
			print "!!!Non Unique MBID", repr(artist), mbid
	
	with codecs.open("C:/temp/artists.xml", "w", encoding='utf8') as fo:		
		scrapers.aggregate(((artist,mbid, []) for artist, mbid in sorted(cleaned.iteritems())), fo, classical = True)


def main():
	print "starting"
	handler()
main()
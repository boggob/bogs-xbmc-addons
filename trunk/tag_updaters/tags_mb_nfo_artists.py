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
PATH = r'C:\files\music\Assorted'
#PATH = r'C:\files\music\Classical'
####################################


def handler():
	arts		= collections.defaultdict(set)
	
	for fi, attr_map, of in tags.get_files(PATH):
		for attr, name in (
			('musicbrainz_artistid', 'artist'),
			('musicbrainz_albumartistid', 'albumartist'),
		):
			id_a	= attr_map[attr][0](fi)
			nma		= attr_map[name][0](fi)
			
			if nma:
				arts[nma] = id_a.upper().strip() if id_a else None
				print "\t%%", nma.encode('utf8'),  arts[nma]
	import pprint
	pprint.pprint(arts)

	with codecs.open("C:/temp/artists.xml", "w", encoding='utf8') as fo:		
		scrapers.aggregate(((artist,mbid, []) for artist, mbid in sorted(arts.iteritems())), fo, classical = True)


def main():
	print "starting"
	handler()
main()
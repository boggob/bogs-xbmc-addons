import collections
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
	 r'C:\files\music\Assorted\A-H',
	 r'C:\files\music\Assorted\I-Z',
	 r'C:\files\music\Assorted\No Album',
	 r'C:\files\music\Assorted\Tripple J',
#	 r'C:\files\music\Assorted',
	 r'C:\files\music\Classical',
	 r'C:\files\music\World',
	 r'C:\files\music\Matilda',
	 r'C:\files\music\musique_wog',
	 r'C:\files\music\Jaz',
	]
	OUTFILE = "C:/files/music/art/albums.xml"
else:
	PATHS = [
	 r'C:\temp\aaaa',
	]
	OUTFILE = "C:/temp/albums_test.xml"
	
####################################


def handler():
	arts		= collections.defaultdict(set)
	for path in PATHS:
		for fi, attr_map, of in tags.get_files(path.decode('utf8')):
			print of
			for attr, albumname, artist, albumartist  in (
				('musicbrainz_albumid', 'album', 'artist', 'albumartist'),
			):
				id_a		= attr_map[attr][0](fi)
				nma			= attr_map[albumname][0](fi)
				art_album	= attr_map[albumartist][0](fi)
				art_artist	= attr_map[artist][0](fi)
				
				art2		= art_album if (art_album and u'{}'.format(repr(art_album)) != "u'[]'") else  art_artist
				
				if nma and id_a:
					arts[nma] = (id_a.upper().strip(), art2)
					print "\t%%", nma.encode('utf8'),  id_a.upper().strip(), repr(art2), u'"{}"'.format(repr(art2)),  u'{}'.format(repr(art2)) == "u'[]'", repr(art_album), repr(art_artist)
				else:	
					print "$$", nma.encode('utf8') , id_a, repr(nma)
	import pprint
	pprint.pprint(arts)
	scrapers.scrape_albums(arts, OUTFILE)
	#brainz_album


def main():
	print "starting"
	handler()
main()
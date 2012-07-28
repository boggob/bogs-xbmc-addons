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
PATH = r'C:\files\music\Assorted'
#PATH = r'C:\files\music\Classical'
#PATH = r'C:\temp\aaaa'
####################################


def handler():
	arts		= collections.defaultdict(set)
	
	for fi, attr_map, of in tags.get_files(PATH):
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
				print "$$", nma.encode('utf8') , id_a
	import pprint
	pprint.pprint(arts)
	scrapers.scrape_albums(arts, "C:/temp/albums.xml")
	#brainz_album


def main():
	print "starting"
	handler()
main()
import collections
import os, sys


pt =  os.path.split(__file__)[0]
print pt
sys.path.append(pt)
sys.path.append(os.path.split(__file__)[0])
import scrapers
import tags
import tags_config

if 0:
	class flushfile(object):
		def __init__(self, f):
			self.f = f
			#self.f = open('c:/temp/out.txt' , 'w')
		def write(self, x):
			self.f.write(x)
			self.f.flush()

	import sys
	sys.stdout = flushfile(sys.stdout)
	
####################################


def handler():
	arts		= collections.defaultdict(set)
	for path in tags_config.PATHS:
		for fi, attr_map, of in tags.get_files(path.decode('utf8')):
			for attr, albumname, artist, albumartist  in (
				('musicbrainz_albumid', 'album', 'artist', 'albumartist'),
			):
				id_a		= attr_map[attr][0](fi)
				nma			= attr_map[albumname][0](fi)
				art_album	= attr_map[albumartist][0](fi)
				art_artist	= attr_map[artist][0](fi)
				
				art2		= art_album if (art_album and u'{}'.format(repr(art_album)) != "u'[]'") else  art_artist
				
				if nma and id_a:
					for mbid in id_a.split('\\'):
						arts[nma,mbid.upper().strip()] = (art2)
				else:
					pass
					#print "$$", repr(of), nma.encode('utf8') , id_a, repr(nma)
	import pprint
	pprint.pprint(arts)
	

	scrapers.scrape_albums(arts, tags_config.OUTFILE_ALBUMS, tags_config.translate)
	#brainz_album


def main():
	print "starting"
	handler()
main()
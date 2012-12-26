import collections
from mutagen.mp3 import MP3
from mutagen.id3 import TPE2
import tags
import tags_config

	
####################################

################################################

def update():
	print "starting"
	albums = collections.defaultdict(set)
	for path in tags_config.PATHS:
		for fi, attr_map, of in tags.get_files(path.decode('utf8')):
			for attr, albumname, artalbumid, albumartist  in (
				('musicbrainz_albumid', 'album', 'musicbrainz_albumartistid', 'albumartist'),
			):
				id_a		= attr_map[attr][0](fi)
				nma			= attr_map[albumname][0](fi)
				art_album	= attr_map[albumartist][0](fi)
				art_albumid	= attr_map[artalbumid][0](fi)
				
				albums[nma, id_a].add((art_album, art_albumid))
			

	for (alb_na, alb_id), arts in sorted(albums.iteritems()):
		if len(arts)  > 1:
			for (art_name, art_id) in arts:
				print (alb_na, alb_id), (art_name, art_id)

if __name__ == "__main__":
	update()
# -*- coding: utf-8 -*-

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


def handler_files():
	for path in tags_config.PATHS:
		for fi, attr_map, of in tags.get_files(path.decode('utf8')):
			for attr, albumname, artist, albumartist  in (
				('musicbrainz_albumid', 'album', 'artist', 'albumartist'),
			):
				mb_albumid		= attr_map[attr][0](fi)
				album_name		= attr_map[albumname][0](fi)
				album_artist	= attr_map[albumartist][0](fi)
				artist			= attr_map[artist][0](fi)
				yield  mb_albumid, album_name, artist, album_artist
			

def handler(handler_input):
	arts		= collections.defaultdict(set)
	for mb_albumid, album_name, album_artist, artist in (handler_input or handler_files()):
		art2		= album_artist if (album_artist and u'{}'.format(repr(album_artist)) != "u'[]'") else  artist
		
		if album_name and mb_albumid:
			for mbid in mb_albumid.split('\\'):
				arts[album_name,mbid.upper().strip()] = (art2)
		else:
			pass
			#print "$$", repr(of), album_name.encode('utf8') , mb_albumid, repr(album_name)
	import pprint
	pprint.pprint(arts)
	

	scrapers.scrape_albums(arts, tags_config.OUTFILE_ALBUMS, tags_config.translate)
	#brainz_album
	
	
	

def main():
	print "starting"
	
	if 1:
		#select strMusicBrainzAlbumID,strAlbum,strArtists,null from albumview where strImage is null or strImage = '<thumb/>' and strMusicBrainzAlbumID is not null and strMusicBrainzAlbumID != "" order by strAlbum;
		x = u"""83d37129-3fe5-3161-bb31-3d47c9c5df9c|Bolero / Piano Concert in G major|Ravel, Maurice|
73832579-6785-3b77-b7a5-653007308cdd|Thicker Than Water|Various Artists|"""

		
		
		vals =  [y.split("|") for y in x.split('\n')]
		
		print vals 
		handler(vals)
	
	else:
		handler(None)

main()
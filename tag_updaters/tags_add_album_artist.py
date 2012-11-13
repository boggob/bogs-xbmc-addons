import collections
from mutagen.mp3 import MP3
from mutagen.id3 import TPE2
import glob
"""
Fills in missing album artist info from matching artists

"""
class flushfile(object):
	def __init__(self, f):
		self.f = f
	def write(self, x):
		self.f.write(x)
		self.f.flush()

import sys
sys.stdout = flushfile(sys.stdout)

 
 ####################################
#path = r'C:\files\music\Classical'
#path = r'C:\files\music\Assorted\A-H'
path = r'C:\files\music\Assorted\I-Z'
#path = r'C:\temp\aaa'

################################################

def update(files):
	print "starting"
	albums = collections.defaultdict(list)
	for fi in sorted(files):
		try:
			audio	= MP3(fi)
			album	=  audio.get(u'TALB', None)
			id_a	=  audio.get(u'TPE1', None)
			id_aa	=  audio.get(u'TPE2', None)
			albums[str(album)].append([str(id_a), str(id_aa)])
		except Exception, e:
			print "**", repr(fi), e
			

	for fi in sorted(files):
		try:
			audio	= MP3(fi)
			album	=  audio.get(u'TALB', None)
			id_a	=  audio.get(u'TPE1', None)
			id_aa	=  audio.get(u'TPE2', None)
			
			items	= albums[str(album)]
			artists			= set(artist  for artist, albumartist in items)
			album_artists	= set(albumartist  for artist, albumartist in items)
			if len(artists) == 1 and len(album_artists) == 1:
				if album_artists == set([str(None)]):
					print "udpating", album, artists,album_artists
					audio['TPE2']  = TPE2(id_a.encoding, text=id_a.text)
					#print  audio.pprint()
					audio.save()
				else:
					pass
					
		except Exception, e:
			print "**", repr(fi), e		
	
	for album, items in sorted(albums.iteritems()):
		artists			= set(artist  for artist, albumartist in items)
		album_artists	= set(albumartist  for artist, albumartist in items)
		if len(artists) == 1 and len(album_artists) == 1:
			pass
		elif album_artists != set(['Various Artists']):
			print "%%", album, artists,album_artists

if __name__ == "__main__":
	update(glob.glob(path + '/*.mp3'))
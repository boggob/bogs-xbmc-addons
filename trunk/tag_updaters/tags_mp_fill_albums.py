from mutagen.mp3 import MP3
from mutagen.id3 import TXXX
import glob
import collections
import os, sys

####################################
PATH = r'C:\files\music\Assorted'
PATH = r'C:\temp\aaaa'
################################################

pt =  os.path.split(__file__)[0]
print pt
sys.path.append(pt)
import scrapers

class flushfile(object):
	def __init__(self, f):
		self.f = f
	def write(self, x):
		self.f.write(x)
		self.f.flush()

import sys
sys.stdout = flushfile(sys.stdout)

 
def collect(files, attrs):
	arts		= collections.defaultdict(set)
	arts_albums	= collections.defaultdict(set)

	filesm		= collections.defaultdict(set)
	
	for fi in files:
		try:
			audio = MP3(fi)
			
			for attr, name in  attrs:
				mb = u"TXXX:" + attr
				id_a	=  audio.get(mb, None)
				nma		=  audio.get(name, None)

				if not nma:
					if id_a:
						print "%0", name, mb, id_a, fi
				else:
					nm2		=  audio.get('TPE2', None)
					if nm2 is None:
						nm2 =  audio.get('TPE1', None)
					nm2 = nm2.text[0]
						
					filesm[nma.text[0]].add(fi)
					arts_albums[nm2].add(nma.text[0])
					if id_a:
						for tx in id_a.text:
							id_t = tx.upper().strip()
							arts[nm2].add(id_t)
					else:
						arts[nm2].add(None)	

			

			
			
			
		except Exception, e:
			import traceback
			print traceback.format_exc()
			print "**", repr(fi), repr(e)
		
	
	return arts, arts_albums, filesm

def update(mapp, filesm, attrs):
	for artist, vals in sorted(mapp.iteritems()):
		vals = vals - set([None])
		if len(vals) > 1:
			print ">>", artist, vals
		else:
			for mbid in vals:
				try:
					for fi in filesm[artist]:
						audio = MP3(fi)
						
						for attr, name in attrs:
							mb = u"TXXX:" + attr
							id_a	=  audio.get(mb, None)
							nma		=  audio.get(name, None)
							print "!!", scrapers.clean(nma.text[0]) if nma else "", mbid
							audio[mb] = TXXX(1, attr, mbid.upper())	
							audio.save()

				except Exception, e:
					import traceback
					print traceback.format_exc()
					print "**", repr(fi), repr(e)
					for k,v in audio.iteritems():
						print "\t","\t", repr(k), ':',  repr(v)

		
	
def lookup(amapp, amapp2, filesm, attrs):
	unknowns = set([ None])
	for artist, albums in sorted(amapp2.iteritems()):
		vals = amapp[artist]
		if len(vals - unknowns) == 0:
			try:
				mbids_map = scrapers.brainz_lookup_release_mb(artist, albums, ['AU', 'US', 'GB'])	
				for album, mbids in mbids_map.iteritems():
					print "\t", album, mbids 
					if len(mbids) == 1:
						mbid = list(mbids)[0]
						for fi in filesm[album]:	
							audio = MP3(fi)
							for attr, name in attrs:
								mb = u"TXXX:" + attr
								nma		=  audio.get(name, None)
								audio[mb] = TXXX(1, attr, mbid.upper())		
								audio.save()
			except scrapers.ScaperException, e:
				print e
			except Exception, e:
				import traceback
				print traceback.format_exc()
				print "**", repr(artist), repr(albums), repr(e)
				#break

	
def main():
	print "starting"
	files = sorted(glob.glob(PATH + '/*.mp3'))

	for attrs in (
		(
			(u'MusicBrainz Album Id', 'TALB'),
		),
	
	):
		print "Doing", attrs
		fix, ids, filesm = collect(files, attrs)
		print"#" * 120					
		print fix			
		print"#" * 120				
						
		#update(fix,filesm, attrs)
		lookup(fix,ids, filesm, attrs)
		
		
	
	
if __name__ == "__main__":	
	main()
from mutagen.mp3 import MP3
from mutagen.id3 import TXXX
import glob
import collections
import os, sys

####################################
PATH = r'C:\files\music\Assorted'
PATH = r'C:\files\music\Classical'

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
	ids			= collections.defaultdict(set)
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
					nm	= nma.text[0]
					filesm[nm].add(fi)						
					if id_a:
						for tx in id_a.text:
							id_t = tx.upper().strip()
							arts[nm].add(id_t)
							ids[id_t].add(nm)
					else:
						arts[nm].add(None)	
						ids[None].add(fi)
			

		except Exception, e:
			import traceback
			print traceback.format_exc()
			print "**", repr(fi), repr(e)
		
	
	return arts, ids, filesm

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

		
	
def lookup(mapp, filesm, attrs):
	unknowns = set(['89AD4AC3-39F7-470E-963A-56509C546377', None])
	for artist, vals in sorted(mapp.iteritems()):
		if len(vals - unknowns) == 0:
			try:
				mbid = scrapers.brainz_lookup_artist_mb(artist, [], classical = False)	
				if mbid:		
					for fi in filesm[artist]:	
						audio = MP3(fi)						
						for attr, name in attrs:
							mb = u"TXXX:" + attr
							nma		=  audio.get(name, None)
							if nma and nma.text[0] == artist:

								audio[mb] = TXXX(1, attr, mbid.upper())		
								audio.save()
			except scrapers.ScaperException, e:
				print e
			except Exception, e:
				import traceback
				print traceback.format_exc()
				print "**", repr(fi), repr(e)
				#break

	
def main():
	print "starting"
	files = sorted(glob.glob(PATH + '/*.mp3'))

	for attrs in (
#		(
#			(u'MusicBrainz Album Id', 'TALB'),
#		),
	
		(
			(u'MusicBrainz Artist Id', 'TPE1'),
			(u'MusicBrainz Album Artist Id', 'TPE2')				
		),
	):
		print "Doing", attrs
		fix, ids, filesm = collect(files, attrs)
		print"#" * 120					
		print fix			
		print"#" * 120				
						
		update(fix,filesm, attrs)
		lookup(fix,filesm, attrs)
		
		
	
	
if __name__ == "__main__":	
	main()
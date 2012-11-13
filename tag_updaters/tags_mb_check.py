################################################################################################
#Fills out missing MBID for artist and album artist based on data already in the collection
################################################################################################

from mutagen.mp3 import MP3
from mutagen.id3 import TXXX
import glob
import pprint
import collections

class flushfile(object):
	def __init__(self, f):
		self.f = f
	def write(self, x):
		self.f.write(x)
		self.f.flush()

import sys
sys.stdout = flushfile(sys.stdout)

 
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
print "starting"


def handler(mapp):
	arts		= collections.defaultdict(set)
	ids			= collections.defaultdict(set)
	files = []
	for PATH in PATHS:
		files += glob.glob(PATH + '/*.mp3')
	files = sorted(files)

	for fi in files:
		try:
			audio = MP3(fi)
			
			for attr, name in (
				(u'MusicBrainz Artist Id', 'TPE1'),
				(u'MusicBrainz Album Artist Id', 'TPE2')
			):
				mb = u"TXXX:" + attr
				id_a	=  audio.get(mb, None)
				nma		=  audio.get(name, None)
				if not nma:
					if id_a:
						print "%%", repr(fi)
				else:
					nm	= nma.text[0]
					if id_a:
						for tx in id_a.text:
							id_t = tx.upper().strip()
							arts[nm].add(id_t)	
							ids[id_t].add(nm)
					else:
						if nm in mapp:
							print "!!", repr(nm)
							audio[mb] = TXXX(1, attr, mapp[nm])	
							audio.save()
						else:
							arts[nm].add(None)	
							ids[None].add(nm)
			

		except Exception, e:
			import traceback
			#traceback.print_exc()
			print "**", repr(fi), repr(e)
			
		
	
	return arts, ids

def main():
	fix = {}
	arts, ids = handler({})
	print		
	print		
	print"#" * 120		
	for k,v in sorted(arts.iteritems()):
		if len(v) > 1:
			if len(v) == 2 and None in v:
				fix[k] = [vv for vv in v if vv is not None][0]
			else:
				print repr(k), repr(v)
	
	print"#" * 120					
	pprint.pprint(fix)
	print"#" * 120				
					
	for k,v in ids.iteritems():
		if len(v) > 1:
			print repr(k), repr(v)
	handler(fix)
main()
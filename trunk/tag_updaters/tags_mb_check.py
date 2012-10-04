from mutagen.mp3 import MP3
from mutagen.id3 import TXXX
import glob
import collections

class flushfile(object):
	def __init__(self, f):
		self.f = f
	def write(self, x):
		self.f.write(x)
		self.f.flush()

import sys
sys.stdout = flushfile(sys.stdout)

 
path = r'C:\files\music\Assorted'
print "starting"


def handler(mapp):
	arts		= collections.defaultdict(set)
	ids			= collections.defaultdict(set)
	
	for fi in sorted(glob.glob(path + '/*.mp3')):
		try:
			audio = MP3(fi)
			
			for attr, name in (
				(u'MusicBrainz Artist Id', 'TPE1'),
#				(u'MusicBrainz Album Artist Id', 'TPE2')
			):
				mb = u"TXXX:" + attr
				id_a	=  audio.get(mb, None)
				nma		=  audio.get(name, None)
				if not nma:
					if id_a:
						print "%%", fi
				else:
					nm	= nma.text[0]
					if id_a:
						for tx in id_a.text:
							id_t = tx.upper().strip()
							arts[nm].add(id_t)	
							ids[id_t].add(nm)
					else:
						if nm in mapp:
							print "!!", nm
							audio[mb] = TXXX(1, attr, mapp[nm])	
							audio.save()
						else:
							arts[nm].add(None)	
							ids[None].add(nm)
			

		except Exception, e:
			import traceback
			traceback.print_exc()
			print "**", repr(fi), repr(e)
			for k,v in audio.iteritems():
				print "\t","\t", repr(k), ':',  repr(v)
			
		
	
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
	print fix			
	print"#" * 120				
					
	for k,v in ids.iteritems():
		if len(v) > 1:
			print repr(k), repr(v)
	handler(fix)
main()
from mutagen.mp4 import MP4

from mutagen.id3 import TXXX
import glob

class flushfile(object):
	def __init__(self, f):
		self.f = f
	def write(self, x):
		self.f.write(x)
		self.f.flush()

import sys
sys.stdout = flushfile(sys.stdout)

 
path = r'C:\files\music\Classical'
path = r'C:\temp\aaaa'

print "starting"

for fi in sorted(glob.glob(path + '/*.m4a')):
	try:
		audio = MP4(fi)

		if 1:
			
			for sattr in (
				u'MusicBrainz Album Id',
				u'MusicBrainz Album Artist Id',
				u'MusicBrainz Album Id',
				u'MusicBrainz Track Id',
				u'MusicBrainz TRM Id',
				u'MusicBrainz Disc Id',
				u'MusicIP PUID',
			):
				pref = "----:com.apple.iTunes:"
				attru	= pref + sattr.upper()
				attr	= pref + sattr
				
				print fi, attr 
				if attru in audio:
					print "\t", "###", repr(audio[attru])				
				if attru in audio:
					if attr not in audio:
						audio[attr] = audio[attru]
						del audio[attru]
					elif not audio[attr].upper().strip():
						audio[attr] = audio[attru]
						del audio[attru]	
					elif not audio[attru]:
						del audio[attru]	
					elif audio[attr].upper().strip() != audio[attru].upper().strip():
						print "??", repr(fi), attr, "\t", repr(audio[attr]),  "\t",repr(audio[attru])
						del audio[attru]	
					else:
						del audio[attru]	
						
					for k,v in sorted(audio.iteritems()):
						#k = k.decode('ISO-8859-1')
						audio[k]  = v
						print "\t", repr(k), ':',  repr(v)
					audio.save()


		if 0:
			print fi
			for k,v in audio.iteritems():
				print "\t", repr(k), ':',  repr(v)
			print
	except Exception, e:
		print "**", repr(fi), e
		import traceback
		traceback.print_exc()
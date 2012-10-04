from mutagen.mp3 import MP3
from mutagen.id3 import TXXX
import glob
"""
Deals with bad tag names and redundant data between album artist and artist

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
path = r'C:\files\music\Assorted'
#path = r'C:\temp\aaaa'

################################################



print "starting"

for fi in sorted(glob.glob(path + '/*.mp3')):
	try:
		audio = MP3(fi)

		if 1:
			
			for sattr in (
				u'MusicBrainz Artist Id',
				u'MusicBrainz Album Artist Id',
				u'MusicBrainz Album Id',
				u'albumartist',
			):
				attr = u'TXXX:' + sattr
				attru = attr.upper()
				
				if attru in audio:
					#If normal case tag is not present - replace uppercase verison with the correct case
					if attr not in audio:
						audio[attr] = TXXX(audio[attru].encoding, sattr, audio[attru].text)
						del audio[attru]
					#If normal case tag is not blank - replace uppercase verison with the correct case
					elif not audio[attr].text[0].upper().strip():
						audio[attr] = TXXX(audio[attru].encoding, sattr, audio[attru].text)
						del audio[attru]	
					#If uppercase tag data is blank - remove it
					elif not audio[attru].text[0].upper().strip():
						del audio[attru]	
					#If uppercase tag data is != nornal case tag data - remove it	
					elif audio[attr].text[0].upper().strip() != audio[attru].text[0].upper().strip():
						print "??", repr(fi), attr, "\t", audio[attr],  "\t",audio[attru]
						del audio[attru]	
					#Remove uppercase tag data
					else:
						del audio[attru]	
				
					audio.save()

			########################################################################################
			id_a	=  audio.get(u'TXXX:MusicBrainz Artist Id', None)
			id_aa	=  audio.get(u'TXXX:MusicBrainz Album Artist Id', None)
			
			#If album artist data is == artist data - remove it	
			if id_a and id_aa and id_a.text[0].upper().strip() == id_aa.text[0].upper().strip():
				print "?1", repr(fi), id_a.text[0].upper().strip(), "\t", id_aa.text[0].upper().strip()
				del audio[u'TXXX:MusicBrainz Album Artist Id']
				audio.save()

			########################################################################################	
			id_a	=  audio.get('TPE1', None)
			id_aa	=  audio.get('TPE2', None)

			if id_a and id_aa:
				id_a_t	 = id_a.text[0].upper().strip() 
				id_aa_t	 = id_aa.text[0].upper().strip()
				#If album artist data is == artist data - remove it	
				if id_a_t == id_aa_t or " ".join(id_a_t.split(',')[::-1]).strip() == id_aa_t:
					print "*1", repr(fi)
					del audio['TPE2']
					audio.save()

		if 0:
			print fi
			for k,v in audio.iteritems():
				print "\t", repr(k), ':',  repr(v)
			print
	except Exception, e:
		print "**", repr(fi), e
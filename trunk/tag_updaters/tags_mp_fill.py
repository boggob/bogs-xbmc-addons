from mutagen.mp3 import MP3
from mutagen.id3 import TXXX
import glob
import collections
import os, sys

####################################
PATH = r'C:\files\music\Assorted'
#PATH = r'C:\files\music\Classical'
#PATH = r'C:\files\music\World'
#PATH = r'C:\temp\aaaa'

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

def sortorder_conv(name):
	return " ".join(part.strip() for part in name.split(",")[::-1])
	
def get_all_artists(artist):
	mult = artist.split("&")
	
	if len(mult) > 1:
		return [sortorder_conv(v.strip()) for v in mult]
	else:
		return [sortorder_conv(artist)]

 
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

#force the MBID of all tracks to upper case
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

	
	lookfor = collections.defaultdict(set)
	for artist, vals in sorted(mapp.iteritems()):
		if len(vals - unknowns) == 0:
			for artist_idv in get_all_artists(artist):
				lookfor[artist_idv].add(artist)
				

	
	lookfor_res  = {}
	for artist_idv, artists in sorted(lookfor.iteritems()):
		try:
			mbid = scrapers.brainz_lookup_artist_mb(artist_idv, [], classical = False)
			print "^!", repr(artist_idv), mbid
			
			if mbid:
				lookfor_res[artist_idv] = mbid
		except scrapers.ScaperException, e:
			print e
		except Exception, e:
			import traceback
			print traceback.format_exc()
			print "**", repr(artist_idv), repr(e)
			#break

	lookfor_aggr = 	collections.defaultdict(list)
	for artist, fi in filesm.iteritems():	
		for artist_idv in get_all_artists(artist):
			mbid = lookfor_res.get(artist_idv, "")
			if mbid:
				lookfor_aggr[artist].append(mbid)
		
	for artist, mbid in lookfor_aggr.iteritems():		
		print "$$", repr(artist), mbid
		for fi in filesm[artist]:	
			audio = MP3(fi)						
			for attr, name in attrs:
				mb = u"TXXX:" + attr
				nma		=  audio.get(name, None)
				if nma and nma.text[0] == artist:
 
					audio[mb] = TXXX(1, attr, "/".join(mbid).upper())		
					audio.save()


			
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
						
		#update(fix,filesm, attrs)
		lookup(fix,filesm, attrs)
		
		
	
	
if __name__ == "__main__":	
	main()
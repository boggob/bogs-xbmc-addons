import collections
import codecs
import os, sys


pt =  os.path.split(__file__)[0]
print pt
sys.path.append(pt)
sys.path.append(os.path.split(__file__)[0])
import scrapers
import tags
import user_input

class flushfile(object):
	def __init__(self, f):
		self.f = f
	def write(self, x):
		self.f.write(x)
		self.f.flush()

import sys
sys.stdout = flushfile(sys.stdout)

####################################
if 1:
	PATHS = [
	r'C:\files\music\Assorted\A-H',
	 r'C:\files\music\Assorted\I-Z',
	 r'C:\files\music\Assorted\No Album',
	 r'C:\files\music\Assorted\Tripple J',	
	 #r'C:\files\music\Assorted',
	 r'C:\files\music\Classical',
	 r'C:\files\music\World',
	 r'C:\files\music\Matilda',
	 r'C:\files\music\musique_wog',
	 r'C:\files\music\Jaz',
	]
	OUTFILE = "C:/files/music/art/artists.xml"
else:
	PATHS = [user_input.input_directory()]
	print PATHS
	OUTFILE = "C:/temp/artists_test.xml"
	


def handler():
	arts		= collections.defaultdict(set)
	artsr		= collections.defaultdict(list)
	for path in PATHS:
		for fi, attr_map, of in tags.get_files(path.decode('utf8')):
			print " %%", repr(of)
			for attr, name in (
				('musicbrainz_artistid', 'artist'),
				('musicbrainz_albumartistid', 'albumartist'),
			):
				id_as	= attr_map[attr][0](fi).strip().upper()
				nma		= attr_map[name][0](fi).strip().upper()
				
				if nma and id_as:
					for spl in ('/', ';', '\\'):
						spl1	= list(x.strip() for x in id_as.split(spl)) 
						if len(spl1) > 1:
							break
					
					for id_a in spl1:
						if id_a not in artsr[nma]:											
							artsr[nma].append(id_a)  
						arts[id_a].add(nma)

					print nma.encode('utf8'),  id_a
	import pprint
	pprint.pprint(dict(arts))

	collected = {}
	for idx, (mbid, artist) in enumerate(sorted(arts.iteritems())):
		print "\tArtist", idx, len(arts), repr(artist) 
		collected[mbid] =  scrapers.lastfm_artist(artist,[],mbid)

	
	
	with codecs.open(OUTFILE, "w", encoding='utf8') as fo:		
		fo.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<musicdb>\n')

		for idx, (artists, mbids) in enumerate(sorted(artsr.iteritems())):
			dat = [collected[mbid]['artist'] for mbid in mbids if collected[mbid]]
			if dat:
				curr = {'artist' : collections.OrderedDict()}
				curr['artist']['mbid']			= "/".join(d['mbid'] for d in dat)
				curr['artist']['name']			= scrapers.escape(artists)
				curr['artist']['genre']			= sorted(set(sum((d['genre'] for d in dat), [])))
				curr['artist']['biography']		= "\n\n[CR]".join(d['biography'] for d in dat)
				curr['artist']['thumb']			= sum((d['thumb'] for d in dat),[])
				curr['artist']['formed']		= dat[0]['formed']
				
				fo.write(scrapers.unquote(scrapers.encode(curr)))
			fo.flush()
				
		fo.write("\n</musicdb>\n")			



def main():
	print "*****starting"
	handler()
	print "*****done"	
main()
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
		x = u"""45b3a1de-c198-4ddc-b84b-36dc283ae6ec|The Platinum Collection|Howard Jones|
	9d56bf0a-d795-47c0-b0a6-9f0237481528|Dave Dee, Dozy, Beaky, Mick & Tich|Dave Dee, Dozy, Beaky, Mick & Tich|
	27e0827e-b226-45e5-a794-57c14483d89d|Don Juan / Till Eulenspiegel / Also sprach Zarathustra|Strauss, Richard; Slovak Philharmonic, Košler, Zdeněk|
	138b696e-a104-4f30-8e23-9cc251f124c1|The Great Violinists|Menuhin, Yehudi, Heifetz, Jascha, Kreisler, Fritz, Sammons, Albert, Powell, Maud|
	1d058252-8c4e-4520-8817-ad0328ff365b|Symphonien 1 & 5|Beethoven, Ludwig van; Philadelphia Orchestra, Muti, Riccardo|
	b4394c07-a505-4ecc-8b8e-adeadca140f2|The Great Composers, Volume 2: Brahms: Symphony no. 1 in C minor, op. 68|Brahms, Johannes; SWR Baden-Baden and Freiburg Symphony Orchestra, Horenstein, Jascha|
	7b3f8613-c204-4401-b16a-b503efd939d1|5|Lenny Kravitz|
	667851cb-0f84-3fdd-8882-33902fa16aef|10 000 Hz Legend|Air|
	c6b3f29d-15cd-3f67-8228-0580fa01b194|21|Adele|
	142e1b79-b022-385f-8554-109604ce93f0|Dance the Devil|The Frames|
	b434a801-3c05-46e2-8d43-6a56b77f56c6|Franz Ferdinand|Franz Ferdinand|
	4ccca10d-45dd-31f7-8d34-ff97d09f8a2b|Legend: The Best of Bob Marley and The Wailers|Bob Marley & The Wailers|
	49094ab4-5eea-4535-a354-f8504e4a6c13|Magical Mystery Tour|The Beatles|
	365683ab-1762-4259-9dfd-9532baf725fc|nimrod.|Green Day|
	fdb8a6ee-624d-3dfb-9a68-28e68b9195e1|Numbers: A Pythagorean Theory Tale|Cat Stevens|
	04f1756a-0ca7-3917-ad4d-32f3a018b2f0|Them Crooked Vultures|Them Crooked Vultures|"""
		
		
		vals =  [y.split("|") for y in x.split('\n')]
		
		print vals 
		handler(vals)
	
	else:
		handler()

main()
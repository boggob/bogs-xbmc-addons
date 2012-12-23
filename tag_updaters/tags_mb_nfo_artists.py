import collections
import codecs
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
		def write(self, x):
			self.f.write(x)
			self.f.flush()

	import sys
	sys.stdout = flushfile(sys.stdout)

 
def handler():

	artsr		= collections.defaultdict(list)
	for path in tags_config.PATHS:
		for fi, attr_map, of in tags.get_files(path.decode('utf8')):
			for attr, name in (
				('musicbrainz_artistid', 'artist'),
				('musicbrainz_albumartistid', 'albumartist'),
			):
				id_as	= attr_map[attr][0](fi).strip().upper()
				nma		= attr_map[name][0](fi).strip().upper()
				
				if nma and id_as:
					for spl in ('/', ';', '\\', '\n'):
						spl1	= list(x.strip() for x in id_as.split(spl)) 
						if len(spl1) > 1:
							break
					
					for id_a in spl1:
						if id_a not in artsr[nma]:											
							artsr[nma].append(id_a)  


					#print "\t%", repr(of), nma.encode('utf8'),  id_a
	import pprint
	#pprint.pprint(dict(artsr))
	scrapers.scrape_artists(artsr, tags_config.OUTFILE_ARTISTS, tags_config.translate)
	



def main():
	print "*****starting"
	handler()
	print "*****done"	
main()
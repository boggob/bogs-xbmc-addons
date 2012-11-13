from mutagen.mp3 import MP3
from mutagen.id3 import TXXX
import glob
import collections
import os, sys

####################################
#PATH = r'C:\files\music\Classical'
PATH = r'C:\temp\aaaa'
################################################

pt =  os.path.split(__file__)[0]
print pt
sys.path.append(pt)
import scrapers
import tags

"""
reads all tags from all files
"""

 
def collect():
	arts		= collections.defaultdict(set)
	arts_albums	= collections.defaultdict(set)

	filesm		= collections.defaultdict(set)
	
	for fi, attr_map, of in sorted(tags.get_files(PATH)):
		try:
			print repr(of)
			print fi
			for k,v in  {k : attr_map[k][0](fi) for k in attr_map}.iteritems():
				print '\t', k, repr(v)
			
		except Exception, e:
			import traceback
			print traceback.format_exc()
			print "**", repr(fi), repr(e)
		
	
	return arts, arts_albums, filesm


	
def main():
	print "starting"
	collect()	
		
	
	
if __name__ == "__main__":	
	main()
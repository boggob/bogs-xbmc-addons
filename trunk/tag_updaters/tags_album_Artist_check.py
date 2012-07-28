from mutagen.mp3 import MP3
from mutagen.id3 import TXXX
import glob
import collections
import os, sys

####################################
PATH = r'C:\files\music\Classical'
#PATH = r'C:\temp\aaaa'
################################################

pt =  os.path.split(__file__)[0]
print pt
sys.path.append(pt)
import scrapers
import tags



 
def collect():
	arts		= collections.defaultdict(set)
	arts_albums	= collections.defaultdict(set)

	filesm		= collections.defaultdict(set)
	
	for obj, attr, fi  in tags.get_files(PATH):
		try:
			publisher = obj.get('LABEL', None)
			if publisher:
				if os.path.splitext(fi)[-1] == ".m4a":
					print fi, publisher				
					obj['----:com.apple.iTunes:LABEL'] = publisher
					del obj['LABEL']				
					obj.save()
			
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
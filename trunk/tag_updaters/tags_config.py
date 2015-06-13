import user_input

import unicodedata

class flushfile(object):
	def __init__(self, f):
		self.f = f
	def write(self, x):
		try:
			self.f.write(x.encode('ascii', 'ignore'))
		except:
			self.f.write('\n!!@!')
			self.f.write(str(type(x)))
			self.f.write(repr(x))
			self.f.write('\n')
			
		
		self.f.flush()

import sys
sys.stdout = flushfile(sys.stdout)


####################################
if 1:
	PATHS = [
	 r'\\DISKSTATION\filesc\music\Assorted',
	 r'\\DISKSTATION\filesc\music\Classical',
	 r'\\DISKSTATION\filesc\music\croatian',
	 r'\\DISKSTATION\filesc\music\World',
	 r'\\DISKSTATION\filesc\music\Matilda',
	]
	OUTFILE_ALBUMS	= r'\\DISKSTATION\filesc\music\art\albums.xml'
	OUTFILE_ARTISTS	= r'\\DISKSTATION\filesc\music\art\artists.xml'
	translate	= lambda x: x.replace('\\\\DISKSTATION\\filesc\\music\\art\\albums\\', '/home/user/media/filesc/music/art/albums/').replace('\\\\DISKSTATION\\filesc\\music\\art\\artists\\', '/home/user/media/filesc/music/art/artists/')
else:
	
	#PATHS = [user_input.input_directory()]
	PATHS = [
	 #r'\\DISKSTATION\filesc\music\Matilda',
	#r"c:\temp\music\albums2"
	r'C:\Users\user\Downloads\music',
	
	]
	OUTFILE_ALBUMS	= "C:/temp/music/albums_test.xml"
	OUTFILE_ARTISTS = "C:/temp/music/artists_test.xml"
	
	_pairs = [
	  ('\\\\DISKSTATION\\filesc\\music\\art\\albums\\', '/home/user/media/filesc/music/art/albums/'),
	  ('\\\\DISKSTATION\\filesc\\art\\artists\\', '/home/user/media/filesc/music/art/artists/')
	]
	translate	= lambda x: x.replace(_pairs[0][0], _pairs[0][1]).replace(_pairs[1][0], _pairs[1][1])
	translater	= lambda x: x.replace(_pairs[0][1], _pairs[0][0]).replace(_pairs[1][1], _pairs[1][0])
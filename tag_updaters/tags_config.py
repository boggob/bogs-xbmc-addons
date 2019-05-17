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
if 0:
	PATHS = [
	 r'\\DISKSTATION\music\Assorted',
	 r'\\DISKSTATION\music\Classical',
	 r'\\DISKSTATION\music\croatian',
	 r'\\DISKSTATION\music\World',
	 r'\\DISKSTATION\music\Matilda',
	]
	OUTFILE_ALBUMS	= r'\\DISKSTATION\music\art\albums.xml'
	OUTFILE_ARTISTS	= r'\\DISKSTATION\music\art\artists.xml'
	translate	= lambda x: x.replace('\\\\DISKSTATION\\filesc\\music\\art\\albums\\', '/home/user/media/music/art/albums/').replace('\\\\DISKSTATION\\filesc\\music\\art\\artists\\', '/home/user/media/music/art/artists/')
else:
	
	#PATHS = [user_input.input_directory()]
	PATHS = [
		r'D:\DVD\music',	
	]
	OUTFILE_ALBUMS	= "d:/temp/music/albums_test.xml"
	OUTFILE_ARTISTS = "d:/temp/music/artists_test.xml"
	
	_pairs = [
	  ('\\\\DISKSTATION\\filesc\\music\\art\\albums\\', '/home/user/media/music/art/albums/'),
	  ('\\\\DISKSTATION\\filesc\\art\\artists\\', '/home/user/media/music/art/artists/')
	]
	translate	= lambda x: x.replace(_pairs[0][0], _pairs[0][1]).replace(_pairs[1][0], _pairs[1][1])
	translater	= lambda x: x.replace(_pairs[0][1], _pairs[0][0]).replace(_pairs[1][1], _pairs[1][0])
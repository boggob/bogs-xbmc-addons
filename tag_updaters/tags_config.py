import user_input

####################################
if 0:
	PATHS = [
	 r'\\DISKSTATION\filesc\music\Assorted\A-H',
	 r'\\DISKSTATION\filesc\music\Assorted\I-Z',
	 r'\\DISKSTATION\filesc\music\Assorted\No Album',
	 r'\\DISKSTATION\filesc\music\Assorted\Tripple J',
#	 r'\\DISKSTATION\filesc\music\Assorted',
	 r'\\DISKSTATION\filesc\music\Classical',
	 r'\\DISKSTATION\filesc\music\World',
	 r'\\DISKSTATION\filesc\music\Matilda',
	 r'\\DISKSTATION\filesc\music\musique_wog',
	 r'\\DISKSTATION\filesc\music\Jaz',
	]
	OUTFILE_ALBUMS	= r'\\DISKSTATION\filesc\music\art\albums.xml'
	OUTFILE_ARTISTS	= r'\\DISKSTATION\filesc\music\art\artists.xml'
	translate	= lambda x: x.replace('\\\\DISKSTATION\\filesc\\music\\art\\albums\\', '/home/user/media/filesC/music/art/albums/').replace('\\\\DISKSTATION\\filesc\\music\\art\\artists\\', '/home/user/media/filesC/music/art/artists/')
else:
	class flushfile(object):
		def __init__(self, f):
			self.f = f
		def write(self, x):
			self.f.write(x)
			self.f.flush()

	import sys
	sys.stdout = flushfile(sys.stdout)
	
	#PATHS = [user_input.input_directory()]
	PATHS = [
	 #r'\\DISKSTATION\filesc\music\Matilda',
	#r"c:\temp\music\albums2"
	r'C:\temp\music\albums4',
	
	]
	OUTFILE_ALBUMS	= "C:/temp/albums_test.xml"
	OUTFILE_ARTISTS = "C:/temp/artists_test.xml"
	
	_pairs = [
	  ('\\\\DISKSTATION\\filesc\\music\\art\\albums\\', '/home/user/media/filesc/music/art/albums/'),
	  ('\\\\DISKSTATION\\filesc\\art\\artists\\', '/home/user/media/filesc/music/art/artists/')
	]
	translate	= lambda x: x.replace(_pairs[0][0], _pairs[0][1]).replace(_pairs[1][0], _pairs[1][1])
	translater	= lambda x: x.replace(_pairs[0][1], _pairs[0][0]).replace(_pairs[1][1], _pairs[1][0])
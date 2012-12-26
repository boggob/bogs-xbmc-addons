import user_input

####################################
if 1:
	PATHS = [
	 r'C:\files\music\Assorted\A-H',
	 r'C:\files\music\Assorted\I-Z',
	 r'C:\files\music\Assorted\No Album',
	 r'C:\files\music\Assorted\Tripple J',
#	 r'C:\files\music\Assorted',
	 r'C:\files\music\Classical',
	 r'C:\files\music\World',
	 r'C:\files\music\Matilda',
	 r'C:\files\music\musique_wog',
	 r'C:\files\music\Jaz',
	]
	OUTFILE_ALBUMS	= "C:/files/music/art/albums.xml"
	OUTFILE_ARTISTS	= "C:/files/music/art/artists.xml"
	translate	= lambda x: x.replace('C:\\files\\music\\art\\albums\\', '/home/user/media/filesC/music/art/albums/').replace('C:\\files\\music\\art\\artists\\', '/home/user/media/filesC/music/art/artists/')
else:
	class flushfile(object):
		def __init__(self, f):
			self.f = f
		def write(self, x):
			self.f.write(x)
			self.f.flush()

	import sys
	sys.stdout = flushfile(sys.stdout)
	
	PATHS = [user_input.input_directory()]
	PATHS = [
	 r'C:\temp\aaa',
	]
	OUTFILE_ALBUMS	= "C:/temp/albums_test.xml"
	OUTFILE_ARTISTS = "C:/temp/artists_test.xml"
	translate	= lambda x: x.replace('C:\\files\\music\\art\\albums\\', '/home/user/media/filesC/music/art/albums/').replace('C:\\files\\music\\art\\artists\\', '/home/user/media/filesC/music/art/artists/')
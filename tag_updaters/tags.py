# -*- coding: latin-1 -*-
import os
from mutagen.id3 import TXXX
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.apev2 import APEv2
from mutagen.flac import FLAC


EXT_MAPPING_OBJ = {
	".mp3"	: MP3,
	".m4a"	: MP4,
	".ape"	: APEv2,
	".mpc"	: APEv2,
	".flac"	: FLAC,
}

_extr	= lambda attr: lambda ent : "\\".join([unicode(vl) if vl else None for vl in ent.get(attr, [])])
_extr2	= lambda attr: lambda ent : unicode(ent.get(attr, []))



_upd	= lambda attr: lambda ent, val : ent.update(attr=val)



EXT_MAPPING_ATTR = {
	".mp3"	: {
				"musicbrainz_albumid"		: ( _extr("TXXX:MusicBrainz Album Id") ,		None),
				"musicbrainz_artistid"		: ( _extr("TXXX:MusicBrainz Artist Id"),		None), 
				"musicbrainz_albumartistid"	: ( _extr("TXXX:MusicBrainz Album Artist Id"),	None),		
				"asin"						: ( _extr("TXXX:ASIN"),							None),
				"artist"					: ( _extr2("TPE1"), 							_upd("TPE1")),		
				"albumartist"				: ( _extr2("TPE2"), 							_upd("TPE2")),		
				"album"						: ( _extr2("TALB"),								_upd("TALB")),		
				"genre"						: ( _extr2("TCON"),								_upd("TCON")),		
				"label"						: ( _extr2("label"),							_upd("label")),		
			},
	".m4a"	: {

				"musicbrainz_albumid"		: ( _extr("----:com.apple.iTunes:MUSICBRAINZ ALBUM ID"), 		"MusicBrainz Album Id"),
				"musicbrainz_artistid"		: ( _extr("----:com.apple.iTunes:MUSICBRAINZ ARTIST ID"),		"MusicBrainz Artist Id"),		
				"musicbrainz_albumartistid"	: ( _extr("----:com.apple.iTunes:MUSICBRAINZ ALBUM ARTIST ID"),	"MusicBrainz Album Artist Id"),		
				"asin"						: ( _extr("----:com.apple.iTunes:ASIN"),						"ASIN"),		
				"artist"					: ( _extr("\xa9ART"),											"�ART"),		
				"albumartist"				: ( _extr("aART"),											"aART"),		
				"album"						: ( _extr("\xa9alb"),											"�alb"),		
				"genre"						: ( _extr("\xa9gen"),											"�gen"),
	},

	".ape"	: {
				"musicbrainz_albumid"		: (_extr2("MUSICBRAINZ ALBUM ID"), "MusicBrainz Album Id"),
				"musicbrainz_artistid"		: (_extr2("MUSICBRAINZ ARTIST ID"), "MusicBrainz Artist Id"),		
				"musicbrainz_albumartistid"	: (_extr2("MUSICBRAINZ ALBUMARTIST ID"), "MusicBrainz Album Artist Id"),		
				"asin"						: (_extr2("ASIN"), "ASIN"),		
				"artist"					: (_extr2("Artist"), "�ART"),		
				"albumartist"				: (_extr2("Album Artist"), "aART"),		
				"album"						: (_extr2("Album"), "�alb"),		
				"genre"						: (_extr2("Genre"), "�gen"),		

	},
	".mpc"	: {
				"musicbrainz_albumid"		: (_extr2("MUSICBRAINZ ALBUM ID"), "MusicBrainz Album Id"),
				"musicbrainz_artistid"		: (_extr2("MUSICBRAINZ ARTIST ID"), "MusicBrainz Artist Id"),		
				"musicbrainz_albumartistid"	: (_extr2("MUSICBRAINZ ALBUMARTIST ID"), "MusicBrainz Album Artist Id"),		
				"asin"						: (_extr2("ASIN"), "ASIN"),		
				"artist"					: (_extr2("Artist"), "�ART"),		
				"albumartist"				: (_extr2("Album Artist"), "aART"),		
				"album"						: (_extr2("Album"), "�alb"),		
				"genre"						: (_extr2("Genre"), "�gen"),		

	},

	".flac"	: {
				"musicbrainz_albumid"		: (_extr("MUSICBRAINZ ALBUM ID"), "MusicBrainz Album Id"),
				"musicbrainz_artistid"		: (_extr("MUSICBRAINZ ARTIST ID"), "MusicBrainz Artist Id"),		
				"musicbrainz_albumartistid"	: (_extr("MUSICBRAINZ ALBUMARTIST ID"), "MusicBrainz Album Artist Id"),		
				"asin"						: (_extr("ASIN"), "ASIN"),		
				"artist"					: (_extr("ARTIST"), "�ART"),		
				"albumartist"				: (_extr("ALBUMARTIST"), "aART"),		
				"album"						: (_extr("ALBUM"), "�alb"),		
				"genre"						: (_extr("GENRE"), "�gen"),		
	},
}



def get_files(path):
	out = []
	for fi in sorted(os.listdir(path)):
		if os.path.isdir(fi):
			out.extend(get_files(fi))
		else:
			ext = os.path.splitext(fi)[-1]
			fullpath = os.path.join(path, fi)
			attr_map	= EXT_MAPPING_ATTR.get(ext, None)
			obj_map		= EXT_MAPPING_OBJ.get(ext, None)
			if obj_map:
				try:
					out.append((obj_map(fullpath), attr_map, fi))
				except Exception,e:
					print "***", e
			else:
				print "??", fullpath
	return out
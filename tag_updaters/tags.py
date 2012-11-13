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

_extr	= lambda attr: lambda ent : "\\".join([unicode(vl) for vl in ent.get(attr, []) if vl])
_extr3	= lambda attrs: lambda ent : "\\".join([unicode(vl) if vl else "" for attr in attrs for vl in ent.get(attr, []) if attr])
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

				"musicbrainz_albumid"		: ( _extr3(["----:com.apple.iTunes:MUSICBRAINZ ALBUM ID", "----:com.apple.iTunes:MusicBrainz Album Id"]), 		"MusicBrainz Album Id"),
				"musicbrainz_artistid"		: ( _extr3(["----:com.apple.iTunes:MUSICBRAINZ ARTIST ID", "----:com.apple.iTunes:MusicBrainz Artist Id"]),		"MusicBrainz Artist Id"),		
				"musicbrainz_albumartistid"	: ( _extr3(["----:com.apple.iTunes:MUSICBRAINZ ALBUM ARTIST ID", "----:com.apple.iTunes:MusicBrainz Album Artist Id"]),	"MusicBrainz Album Artist Id"),		
				"asin"						: ( _extr("----:com.apple.iTunes:ASIN"),						"ASIN"),		
				"artist"					: ( _extr("\xa9ART"),											"©ART"),		
				"albumartist"				: ( _extr("aART"),												"aART"),		
				"album"						: ( _extr("\xa9alb"),											"©alb"),		
				"genre"						: ( _extr("\xa9gen"),											"©gen"),
	},

	".ape"	: {
				"musicbrainz_albumid"		: (_extr2("MUSICBRAINZ ALBUM ID"), "MusicBrainz Album Id"),
				"musicbrainz_artistid"		: (_extr2("MUSICBRAINZ ARTIST ID"), "MusicBrainz Artist Id"),		
				"musicbrainz_albumartistid"	: (_extr2("MUSICBRAINZ ALBUMARTIST ID"), "MusicBrainz Album Artist Id"),		
				"asin"						: (_extr2("ASIN"), "ASIN"),		
				"artist"					: (_extr2("Artist"), "©ART"),		
				"albumartist"				: (_extr2("Album Artist"), "aART"),		
				"album"						: (_extr2("Album"), "©alb"),		
				"genre"						: (_extr2("Genre"), "©gen"),		

	},
	".mpc"	: {
				"musicbrainz_albumid"		: (_extr2("MUSICBRAINZ_ALBUMID"), "MusicBrainz Album Id"),
				"musicbrainz_artistid"		: (_extr2("MUSICBRAINZ_ARTIST_ID"), "MusicBrainz Artist Id"),		
				"musicbrainz_albumartistid"	: (_extr2("MUSICBRAINZ_ALBUMARTIST_ID"), "MusicBrainz Album Artist Id"),		
				"asin"						: (_extr2("ASIN"), "ASIN"),		
				"artist"					: (_extr2("Artist"), "©ART"),		
				"albumartist"				: (_extr2("Album Artist"), "aART"),		
				"album"						: (_extr2("Album"), "©alb"),		
				"genre"						: (_extr2("Genre"), "©gen"),		

	},

	".flac"	: {
				"musicbrainz_albumid"		: (_extr("MUSICBRAINZ_ALBUMID"), "MusicBrainz Album Id"),
				"musicbrainz_artistid"		: (_extr("MUSICBRAINZ_ARTIST_ID"), "MusicBrainz Artist Id"),		
				"musicbrainz_albumartistid"	: (_extr("MUSICBRAINZ_ALBUMARTIST_ID"), "MusicBrainz Album Artist Id"),		
				"asin"						: (_extr("ASIN"), "ASIN"),		
				"artist"					: (_extr("ARTIST"), "©ART"),		
				"albumartist"				: (_extr("ALBUMARTIST"), "aART"),		
				"album"						: (_extr("ALBUM"), "©alb"),		
				"genre"						: (_extr("GENRE"), "©gen"),		
	},
}



def get_files(path):
	out = []
	for fi in sorted(os.listdir(path)):
		fullpath = os.path.join(path, fi)
		if os.path.isdir(fullpath):
			out.extend(get_files(fullpath))
		else:
			ext = os.path.splitext(fi)[-1].lower()
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

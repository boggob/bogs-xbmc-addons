import time
import sqlite3

import collections

import xml_decode
import scrapers



def mmap(it, constr = list, adder = None, reverse = False):
	if constr == list:
		adder = getattr(constr, "append")
	elif constr == set:
		adder = getattr(constr, "add")
	out = collections.defaultdict(constr)	
	if reverse:
		for k,v in it:
			adder(out[v], k)
	else:
		for k,v in it:
			adder(out[k], v)

	return out
	
	
def quote(xx):
	return ",".join('"{}"'.format(x) for x in sorted(xx))
	
def escape(s):
	return s.replace("'", "''")
	
def sql(c, stmt):
	#print "**", repr(stmt) 
	try:
		return c.execute(stmt)
	except Exception,e:
		print stmt
		print e
		raise
	
	
def artists_create(c, artists_map):	
	m =	"""
			CREATE TABLE artist ( idArtist integer primary key,  strArtist varchar(256), strMusicBrainzArtistID text,  strBorn text, strFormed text, strGenres text, strMoods text,  strStyles t
		ext, strInstruments text, strBiography text,  strDied text, strDisbanded text, strYearsActive text,  strImage text, strFanart text,  lastScraped varchar(20) default NULL,  dateAdde
		d varchar (20) default NULL);
			"""	

	for mbid, artidsl in artists_map.iteritems():
		for item in artidsl:
			fanart	= [
				t['thumb']
				for r in item.get("fanart", [])
				for t in  (r if isinstance(r, list) else [r] )
			]
			thumbs	= [
				t
				for r in [item.get("thumb", [])] 
				if r
				for t in (r if isinstance(r, list) else [r])
			]
			
			sql(c, u'''
				update artist set 
				
				strArtist          = '{strArtist}',
				strGenres          = '{strGenres}',
				strBiography       = '{strBiography}',
				strImage           = '{strImage}',
				strFanart          = '{strFanart}',
				lastScraped        = '{lastScraped}'
				
				where strMusicBrainzArtistId = '{mbid}' '''.format(
					mbid			= mbid,
					strArtist		= escape(item.get("name", "")),
					strGenres		= escape(u" / ".join(item.get("genre", [])) if not isinstance(item.get("genre", []), basestring) else item.get("genre", [])),
					strBiography	= escape(item.get("biography", "")),
					strImage		= escape(u"".join(u"<thumb>{}</thumb>".format(t) for t in thumbs) if thumbs else  u"<thumb/>"),
					strFanart		= escape(u"".join(u"<fanart><thumb>{}</thumb></fanart>".format(t) for t in fanart) if fanart else u"<fanart/>"),
					lastScraped		= time.strftime("%Y-%m-%d %H:%M:%S")
				)
			)
def intc(i):
	try:
		return int(i)			
	except Exception, e:
		print "!!", e, i
		return  0

def albums_create(c, albums_map):
	m = """
CREATE TABLE album (idAlbum integer primary key,  strAlbum varchar(256), strMusicBrainzAlbumID text,  strArtists text, strGenres text,  iYear integer, idThumb integer,  bCompilatio
n integer not null default '0',  strMoods text, strStyles text, strThemes text,  strReview text, strImage text, strLabel text,  strType text,  iRating integer,  lastScraped varchar
(20) default NULL,  dateAdded varchar (20) default NULL);	
			"""	

	for mbid, artidsl in albums_map.iteritems():
		if mbid:
			cmd = [ (a[0], artidsl[0]) for a in sql(c, '''select idAlbum from album where lower(strMusicBrainzAlbumID) = '{mbid}' '''.format(mbid = mbid.lower()))]
			#print cmd
		else:
			a_map = {a['title'] : a for a in artidsl}
			cmd = [ (a[0], a_map[a[1]]) for a in sql(c, '''select idAlbum, strAlbum from album where strAlbum in ({stralbum}) '''.format(stralbum = quote(a_map)))]		
		for idalbum, item in cmd:		
			thumbs	= [
				t
				for r in [item.get("thumb", [])] 
				if r
				for t in (r if isinstance(r, list) else [r])
			]

			sql(c, u'''
				update album set 
				
				strLabel           = '{strLabel}',
				strReview          = '{strReview}',
				strImage           = '{strImage}',
				lastScraped        = '{lastScraped}'
				where idAlbum      = '{idalbum}' '''.format(
					idalbum			= idalbum,
					strLabel		= escape(item.get("label", "")),
					strReview		= escape(item.get("review", "")),
					strImage		= escape(u"".join(u"<thumb>{}</thumb>".format(t) for t in thumbs) if thumbs else u"<thumb/>"),	
					lastScraped		= time.strftime("%Y-%m-%d %H:%M:%S")
				)
			)
			for trk in item.get("track", []):
				times = trk["duration"].split(":") + [0]
				sql(c, u'''
				insert into albuminfosong ( idAlbumInfo, iTrack, strTitle, iDuration)  	
				values ({idAlbumInfo}, '{iTrack}', '{strTitle}', {iDuration})
			
				 '''.format(
					mbid			= mbid,
					idAlbumInfo		= idalbum,
					iTrack			= trk["position"],
					strTitle		= escape(trk["title"]),	
					iDuration		= (intc(times[0]) * 60) + intc(times[1])
				)
			)

			

	
def nfo_read(ifiles):
	try:
		mbid_artist_map	= collections.defaultdict(list)
		mbid_album_map	= collections.defaultdict(list)
			
		for ifile in ifiles:
			#print xml_decode.xml_decode(ifile)['musicdb']
			for xml_item in xml_decode.xml_decode(ifile)['musicdb']:
				if "artist" in xml_item:
					mbid_artist_map[xml_item["artist"].get("mbid", "").lower()].append(xml_item["artist"])
				else:
					mbid_album_map[xml_item["album"].get("mbid", "").lower()].append(xml_item["album"])
		return mbid_artist_map, mbid_album_map
				
	except Exception,e:
		print "**", e, ifile
		raise e
		
	
def main(db, nfos):
	print db
	try:
		with  sqlite3.connect(db) as conn:
			c = conn.cursor()
		
			artist_map, album_map = nfo_read( nfos )
			
			x= repr(album_map)
			
			artists_create(c, artist_map)
			albums_create(c, album_map)

			# Save (commit) the changes
			conn.commit()

	except Exception,e:
		import traceback
		print e
		traceback.print_exc()
		
if __name__ == "__main__":
	#main(r'\\XBMCBUNTU\Downloads\MyMusic46.db', [r"\\DISKSTATION\filesc\music\art\artists_cached.xml",r"\\DISKSTATION\filesc\music\art\albums_cached.xml"])
	main(
		r'd:\temp\music\MyMusic60.db', 
		[
			r"d:\temp\music\albums_test.xml",			
		]
	)
	print "done"		

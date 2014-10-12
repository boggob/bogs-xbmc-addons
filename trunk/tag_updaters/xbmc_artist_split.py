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

class Artists(object):
	def __init__(self, it):
		self.orig = [
			(a, (m or "").lower())
			for a, m in it
		]

		self.map_orig_id_mbids = {		
			idArtist : [x.strip() for x in mbartids.split(";")]
			for idArtist, strMusicBrainzArtistId in self.orig
			if 	{"/", ";"}  & set(strMusicBrainzArtistId)
			for mbartids in [strMusicBrainzArtistId.replace("/", ";")]
		}
		
		self.map_orig_mbids_id = mmap(self.orig, set, reverse=True)
		
		pairs = [		
			(mbartid, ArtistId)
			for strMusicBrainzArtistIds in self.map_orig_id_mbids.itervalues()
			for mbartid in strMusicBrainzArtistIds
			for ArtistId in self.map_orig_mbids_id.get(mbartid, [None])
		] 
		
		self.map_dups = {
			mbid : artistids	
			for mbid, artistids in mmap(self.orig, set, reverse = True).iteritems()
			if len(artistids) > 1
		
		}
		self.map_mb_id = mmap(pairs, set)
		self.map_id_mb = mmap(pairs, set, reverse = True)


		
		
def art_insert(c, rows):

	for row in rows:
		#insert into art (media_id, media_type, type, url) values (516, 'album','thumb','http://coverartarchive.org/release/85f3295a-addd-4aef-a5ad-b88788d5b079/front');
		q = '''INSERT INTO art (media_id, media_type, type, url) values ('{}','{}','{}','{}')'''.format(*row)
		print q
		c.execute(q)

def artists_get(c):
	return Artists(c.execute('''select idArtist, strMusicBrainzArtistId from artist''')) 

def nfo_read(ifiles):
	try:
		mbid_xml_map = {
			xml_item["artist"]["mbid"].lower() : xml_item["artist"]["name"]
			for ifile in ifiles
			for xml_item in xml_decode.xml_decode(ifile)['musicdb']
		}
	except Exception,e:
		print e
		mbid_xml_map = {}
	return mbid_xml_map
	
	
def artists_scrape(ifile, artists, skip = False):
	nfo_map = nfo_read(ifile)
	missing = set(artists.map_mb_id) - set(nfo_map)
	
	if not skip:
		for mbid in missing:
			#if mbid not in artists.map_orig_mbids_id 
				try:
					nfo_map[mbid] =  scrapers.brainz_lookup_artist_by_mb(None, mbid, True)[0]['artist'	]["name"]
				except:
					nfo_map[mbid] = None
				time.sleep(1)
	else:
		for mbid in missing:
			#if mbid not in nfo_map:
				nfo_map[mbid] =  "1111"
		
			
	return 		nfo_map
	
	
def quote(xx):
	return ",".join('"{}"'.format(x) for x in sorted(xx))
	
def artist_rel_update(artists, nfo, select, insert):
	select = list(select)
	print len(select)
	for idAggr, idArtist in select:
		added = set()
		mbids	= artists.map_orig_id_mbids[idArtist]
		print "@@", idAggr, idArtist, mbids, [artists.map_mb_id[mbid] for mbid in mbids] 
		for idx, mbid in enumerate(mbids):
			if mbid not in added:
				added.add(mbid)
				for id in artists.map_mb_id[mbid]:
					print "!!", id , idArtist, mbid, repr(nfo.get(mbid, None))
					if id != idArtist:
						insert(id, idAggr, idx, nfo.get(mbid, None))
	
def sql(c, stmt):
	print "**", repr(stmt) 
	return c.execute(stmt)
def artsits_create(c, artists, nfo):	

	for mbid, artids in artists.map_mb_id.iteritems():
		if all(x is None for x in artids):
			pass
			sql(c, u'''INSERT INTO artist ( strArtist, strMusicBrainzArtistID) values ('{}','{}')'''.format(nfo[mbid].replace("'", "''"), mbid))
			id = list(sql(c,''' select idArtist  from artist where strMusicBrainzArtistID in ('{}') '''.format(mbid)))[0]
			artists.map_mb_id[mbid]  = id
	
	
		
	
	updates = {
		id : mbids
		for id, mbids in artists.map_orig_id_mbids.iteritems()
		if len(mbids) > 1
	}
	
	artist_rel_update(
		artists, 
		nfo, 
		sql(c, '''select idAlbum, idArtist from album_artist where idArtist in ({}) '''.format(quote(updates))), 
		lambda id, album, idx, strArtist: sql(c, u'''insert into album_artist (idArtist, idAlbum, strJoinPhrase, boolFeatured, iOrder, strArtist) values ('{}','{}','{}','{}','{}','{}') '''.format(id,album,  "/", 0, idx, strArtist.replace("'", "''")))
	)
	print "*****"
	artist_rel_update(
		artists, 
		nfo, 
		sql(c,'''select idSong, idArtist from song_artist where idArtist in ({}) '''.format(quote(updates))), 
		lambda id, song, idx, strArtist: sql(c, u'''insert into song_artist (idArtist, idSong, strJoinPhrase, boolFeatured, iOrder, strArtist) values ('{}','{}','{}','{}','{}','{}') '''.format(id, song,  "/", 0, idx, strArtist.replace("'", "''")))
	)

	sql(c,'''delete from  song_artist where idArtist in ({}) '''.format(quote(updates)))
	sql(c,'''delete from  album_artist where idArtist in ({}) '''.format(quote(updates)))
	sql(c,'''delete from  artist where idArtist in ({}) '''.format(quote(updates)))
	
def fix_dups(c, nfo_map):
	map_album_artists = set() #collections.defaultdict(set)
	for idAlbum, strArtist, idArtist1, idArtist2 in sql(c,"""
		select a1.idalbum, a1.strArtist, a1.idArtist, a2.idArtist 
		from album_artist a1, album_artist a2 
		where 
		a1.idAlbum  = a2.idAlbum and 
		a1.strArtist = a2.strArtist and 
		a1.idartist > a2.idArtist"""
	):
		map_album_artists.add(idArtist1)
		map_album_artists.add(idArtist2)
		
	for idArtist1 in sql(c,"""
		select a1.idArtist 
		from artist a1
		where 
		
		a1.strArtist = '1111'
		"""
	):
		map_album_artists.add(idArtist1[0])
		
	
	print map_album_artists
	for id, mb, st in list(sql(c,'''select idArtist, strMusicBrainzArtistId, strArtist from artist where idArtist in ({}) '''.format(quote(sorted(map_album_artists))))):
		
		mb = mb.strip()
		strArtist = nfo_map.get(mb.lower())
		if strArtist is None or strArtist == "1111":
			res = scrapers.brainz_lookup_artist_by_mb(None, mb, True)
			time.sleep(1)
			#print repr(res)
			strArtist = res[0]['artist'	]["name"]
			
		strArtist = strArtist.replace("'", "''")	
		print "&&", repr(st), mb, repr(strArtist)
		sql(c, u'''update album_artist set strArtist = '{}' where idArtist = '{}' '''.format(strArtist, id,))		
		sql(c, u'''update song_artist set strArtist = '{}' where idArtist = '{}' '''.format(strArtist, id,))
		sql(c, u'''update artist set strArtist = '{}' where idArtist = '{}' '''.format(strArtist, id,))
	

def main(db, nfo):
	print db
	try:
		with  sqlite3.connect(db) as conn:
			c = conn.cursor()
			artists = artists_get(c)
			
			nfo_map = artists_scrape(nfo, artists, skip = True )
			print nfo_map
			artsits_create(c, artists, nfo_map)
			fix_dups(c, nfo_map)
			
			#raise 1
			
			# Save (commit) the changes
			conn.commit()

	except Exception,e:
		import traceback
		print e
		traceback.print_exc()
		
		
#main(r'\\XBMCBUNTU\Downloads\MyMusic46.db', [r"\\DISKSTATION\filesc\music\art\artists_cached.xml"])
main(r'c:\temp\MyMusic46.db', [r"\\DISKSTATION\filesc\music\art\artists_cached.xml"])

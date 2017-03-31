import sqlite3
import collections
import sys
import re

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

def thumb(s):
	dat = re.findall(r'<thumb[^>]*>([^<]+)</thumb>', s[1]) if s[1] else None
	ret = dat[0] if dat else None
	if ret is None:
		print "??", s
	
	return ret

def sql(c, stmt):
	print "**", repr(stmt) 
	return c.execute(stmt)
	
def art_insert(c, rows):
	type_id_map = mmap((r[1] ,r[0]) for r in rows)
	for media_type, ids in type_id_map.iteritems():
		sql(c, ''' delete from art where media_id in ({}) and media_type = '{}' '''.format(quote(ids), media_type))
	for row in rows:
		#insert into art (media_id, media_type, type, url) values (516, 'album','thumb','http://coverartarchive.org/release/85f3295a-addd-4aef-a5ad-b88788d5b079/front');
		sql(c, '''INSERT INTO art (media_id, media_type, type, url) values ('{}','{}','{}','{}')'''.format(*row))

def albums(c):
	# Create table
	art_insert(c,
		list(
			(row[0], 'album', 'thumb', thumb(row))

			for row in sql(c, '''select idAlbum, strImage, strAlbum from albumView''')
			if row[1]
		)
	)
def artists(c):
	# Create table
	art_insert(c,
		list(
			(row[0], 'artist', 'thumb', th)

			for row in sql(c, '''select idArtist, strImage, strArtist from artistView''')
			for th in [thumb(row)]
			if row[1] and th
		)
	)

def artists_fan(c):
	# Create table
	art_insert(c,
		list(
			(row[0], 'artist', 'fanart', th)

			for row in sql(c, '''select idArtist, strFanart, strArtist from artistView''')
			for th in [thumb(row)]
			if row[1] and th
		)
	)
		

def main(db):
	print db
	with  sqlite3.connect(db) as conn:
		c = conn.cursor()
		albums(c)
		artists(c)
		artists_fan(c)
		# Save (commit) the changes
		conn.commit()


		
#main(r'\\XBMCBUNTU\Downloads\MyMusic46.db')
main(r'c:\temp\music\MyMusic48.db')
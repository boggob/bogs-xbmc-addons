# -*- coding: UTF-8 -*-

def discogs_artistfind(data):
    artists = []
    for item in data.get('results',[]):
        artistdata = {}
        artistdata['artist'] = item['title']
        artistdata['thumb'] = item['thumb']
        artistdata['genre'] = ''
        artistdata['born'] = ''
        artistdata['dcid'] = item['id']
        # discogs does not provide relevance, not used by kodi anyway for artists
        artistdata['relevance'] = ''
        artists.append(artistdata)
    return artists

def discogs_artistdetails(data):
    artistdata = {}
    artistdata['artist'] = data['name']
    artistdata['biography'] = data['profile']
    if 'images' in data:
        thumbs = []
        for item in data['images']:
            thumbdata = {}
            thumbdata['image'] = item['uri']
            thumbdata['preview'] = item['uri150']
            thumbdata['aspect'] = 'thumb'
            thumbs.append(thumbdata)
        artistdata['thumb'] = thumbs
    return artistdata

def discogs_artistalbums(data):
    albums = []
    for item in data['releases']:
        if item['role'] == 'Main':
            albumdata = {}
            albumdata['title'] = item['title']
            albumdata['year'] = str(item.get('year', ''))
            albums.append(albumdata)
    return albums

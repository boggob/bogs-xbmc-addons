# -*- coding: UTF-8 -*-

def discogs_albumfind(data):
    albums = []
    masters = []
    # sort results by lowest release id (first version of a release)
    releases = sorted(data.get('results',[]), key=lambda k: k['id']) 
    for item in releases:
        masterid = item['master_id']
        # we are not interested in multiple versions that belong to the same master release
        if masterid not in masters:
            masters.append(masterid)
            albumdata = {}
            albumdata['artist'] = item['title'].split(' - ',1)[0]
            albumdata['artist_description'] = item['title'].split(' - ',1)[0]
            albumdata['album'] = item['title'].split(' - ',1)[1]
            albumdata['year'] = str(item.get('year', ''))
            albumdata['label'] = item['label'][0]
            albumdata['thumb'] = item['thumb']
            albumdata['dcalbumid'] = item['id']
            # discogs does not provide relevance, we need to set it below 0.95 for manual selection to work in kodi
            albumdata['relevance'] = '0.90'
            albums.append(albumdata)
    return albums

def discogs_albumdetails(data):
    albumdata = {}
    albumdata['album'] = data['title']
    if 'styles' in data:
        albumdata['styles'] = ' / '.join(data['styles'])
    albumdata['genres'] = ' / '.join(data['genres'])
    albumdata['year'] = str(data['year'])
    albumdata['label'] = data['labels'][0]['name']
    artists = []
    for artist in data['artists']:
        artistdata = {}
        artistdata['artist'] = artist['name']
        artists.append(artistdata)
    albumdata['artist'] = artists
    albumdata['artist_description'] = data['artists_sort']
    albumdata['rating'] = str(int((float(data['community']['rating']['average']) * 2) + 0.5))
    albumdata['votes'] = str(data['community']['rating']['count'])
    if 'images' in data:
        thumbs = []
        for thumb in data['images']:
            thumbdata = {}
            thumbdata['image'] = thumb['uri']
            thumbdata['preview'] = thumb['uri150']
            # not accurate: discogs can provide any art type, there is no indication if it is an album front cover (thumb)
            thumbdata['aspect'] = 'thumb'
            thumbs.append(thumbdata)
        albumdata['thumb'] = thumbs
    return albumdata

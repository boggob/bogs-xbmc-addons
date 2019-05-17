# -*- coding: UTF-8 -*-

def musicbrainz_albumfind(data):
    albums = []
    for item in data.get('releases',[]):
        albumdata = {}
        if item.get('artist-credit'):
            artists = []
            artistdisp = ""
            for artist in item['artist-credit']:
                artistdata = {}
                artistdata['artist'] = artist['artist']['name']
                artistdata['mbartistid'] = artist['artist']['id']
                artistdata['artistsort'] = artist['artist']['sort-name']
                artistdisp = artistdisp + artist['artist']['name']
                artistdisp = artistdisp + artist.get('joinphrase', '')
                artists.append(artistdata)
        albumdata['artist'] = artists
        albumdata['artist_description'] = artistdisp
        if item.get('label-info','') and item['label-info'][0].get('label','') and item['label-info'][0]['label'].get('name',''):
            albumdata['label'] = item['label-info'][0]['label']['name']
        albumdata['album'] = item['title']
        if item.get('release-events',''):
            albumdata['year'] = item['release-events'][0]['date'][:4]
        albumdata['thumb'] = ''
        albumdata['mbalbumid'] = item['id']
        if item.get('release-group',''):
            albumdata['mbreleasegroupid'] = item['release-group']['id']
        if item.get('score',1):
            albumdata['relevance'] = str(item['score'] / 100.00)
        albums.append(albumdata)
    return albums

def musicbrainz_albumdetails(data):
    albumdata = {}
    albumdata['album'] = data['title']
    albumdata['mbalbumid'] = data['id']
    if data.get('release-group',''):
        albumdata['mbreleasegroupid'] = data['release-group']['id']
        if data['release-group']['rating'] and data['release-group']['rating']['value']:
            albumdata['rating'] = str(int((float(data['release-group']['rating']['value']) * 2) + 0.5))
            albumdata['votes'] = str(data['release-group']['rating']['votes-count'])
        if data['release-group']['secondary-types']:
            albumdata['type'] = '%s / %s' % (data['release-group']['primary-type'], data['release-group']['secondary-types'][0])
        if data['release-group']['secondary-types'] and (data['release-group']['secondary-types'][0] == 'Compilation'):
            albumdata['compilation'] = 'true'
    if data.get('release-events',''):
        albumdata['year'] = data['release-events'][0]['date'][:4]
        albumdata['releasedate'] = data['release-events'][0]['date']
    if data.get('label-info','') and data['label-info'][0].get('label','') and data['label-info'][0]['label'].get('name',''):
        albumdata['label'] = data['label-info'][0]['label']['name']
    if data.get('artist-credit'):
        artists = []
        artistdisp = ''
        for artist in data['artist-credit']:
            artistdata = {}
            artistdata['artist'] = artist['name']
            artistdata['mbartistid'] = artist['artist']['id']
            artistdata['artistsort'] = artist['artist']['sort-name']
            artistdisp = artistdisp + artist['name']
            artistdisp = artistdisp + artist.get('joinphrase', '')
            artists.append(artistdata)
        albumdata['artist'] = artists
        albumdata['artist_description'] = artistdisp
    return albumdata

def musicbrainz_albumart(data):
    albumdata = {}
    thumbs = []
    extras = []
    for item in data['images']:
        if 'Front' in item['types']:
            thumbdata = {}
            thumbdata['image'] = item['image']
            thumbdata['preview'] = item['thumbnails']['small']
            thumbdata['aspect'] = 'thumb'
            thumbs.append(thumbdata)
        if 'Back' in item['types']:
            albumdata['back'] = item['image']
            backdata = {}
            backdata['image'] = item['image']
            backdata['preview'] = item['thumbnails']['small']
            backdata['aspect'] = 'back'
            extras.append(backdata)
        if 'Medium' in item['types']:
            albumdata['discart'] = item['image']
            discartdata = {}
            discartdata['image'] = item['image']
            discartdata['preview'] = item['thumbnails']['small']
            discartdata['aspect'] = 'discart'
            extras.append(discartdata)
        # exculde spine+back images
        if 'Spine' in item['types'] and len(item['types']) == 1:
            albumdata['spine'] = item['image']
            spinedata = {}
            spinedata['image'] = item['image']
            spinedata['preview'] = item['thumbnails']['small']
            spinedata['aspect'] = 'spine'
            extras.append(spinedata)
    if thumbs:
        albumdata['thumb'] = thumbs
    if extras:
        albumdata['extras'] = extras
    return albumdata

# -*- coding: UTF-8 -*-

def fanarttv_albumart(data):
    if 'albums' in data:
        albumdata = {}
        thumbs = []
        extras = []
        for mbid, art in data['albums'].items():
            if 'albumcover' in art:
                for thumb in art['albumcover']:
                    thumbdata = {}
                    thumbdata['image'] = thumb['url']
                    thumbdata['preview'] = thumb['url'].replace('/fanart/', '/preview/')
                    thumbdata['aspect'] = 'thumb'
                    thumbs.append(thumbdata)
            if 'cdart' in art:
                albumdata['discart'] = art['cdart'][0]['url']
                for cdart in art['cdart']:
                    extradata = {}
                    extradata['image'] = cdart['url']
                    extradata['preview'] = cdart['url'].replace('/fanart/', '/preview/')
                    extradata['aspect'] = 'discart'
                    extras.append(extradata)
        if thumbs:
            albumdata['thumb'] = thumbs
        if extras:
            albumdata['extras'] = extras
        return albumdata

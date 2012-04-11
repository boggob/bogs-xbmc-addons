import sys
import re
import logging
import urllib
import xbmcgui
import xbmcplugin
from NetworkTenVideo import NetworkTenVideo, CHANNELS

# Un-comment for verbose debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class Main:
    def __init__( self,params ): 
        if "networkId" not in params:
            for networkID in CHANNELS.keys():
                xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(networkID),url="%s?networkId=%s" % ( sys.argv[0], networkID), isFolder=True)
        else:	
            print params, "++" 
            self.tenClient = NetworkTenVideo(networkID = params['networkId'], token=params['token'])
            # get playlist
            playlistId = params.get('playlistId', "default")
            if playlistId == "default":
                playlist = self.tenClient.getRootPlaylist()
            else:
                playlist = self.tenClient.getPlaylist(playlistId)
            
            # extract tags and use playlist code for path (used for tracking)
            tags = self.tenClient.parsePlaylistForTags(playlist)
            if (tags.has_key('playlist:code')):
                params['path'] += tags['playlist:code'] + '/'
            
            # check if the playlist has children, and display them if so
            if (type(playlist['childPlaylists']) != str and len(playlist['childPlaylists']['playlist'])>0):
                try:
                    for childPlaylist in playlist['childPlaylists']['playlist']:
                        xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(self._parse_title(childPlaylist['title'])),url="%s?playlistId=%s&networkId=%s&path=%s&token=%s" % ( sys.argv[0], childPlaylist['id'], params['networkId'] ,params['path'], self.tenClient.getToken()), isFolder=True, totalItems=len(playlist['childPlaylists']['playlist']))
                except:
                    childPlaylist = playlist['childPlaylists']['playlist']
                    xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(self._parse_title(childPlaylist['title'])),url="%s?playlistId=%s&networkId=%s&path=%s&token=%s" % ( sys.argv[0], childPlaylist['id'], params['networkId'], params['path'], self.tenClient.getToken()), isFolder=True, totalItems=len(playlist['childPlaylists']['playlist']))
                
            elif (type(playlist['mediaList']) != str and len(playlist['mediaList']['media'])>0):
                for item in playlist['mediaList']['media']:
                    listitem = xbmcgui.ListItem(item['title'],thumbnailImage=item['imagePath'] + 'cropped/128x72.png')
                    listitem.setInfo( "video", {'title': item['title'], 'studio': item['creator'], 'plot': item['description']} )
                    xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?mediaIds=%s&networkId=%s&path=%s&token=%s" % ( sys.argv[0], item['id'], params['networkId'], params['path'], self.tenClient.getToken()), totalItems=len(playlist['mediaList']['media']))
                
                # episode part stacking disabled until we can figure out how to call python in between parts to refresh the auth token
                # parse the playlist for episodes then loop through the reverse sorted items array
                #episodes = self.tenClient.parsePlaylistForEpisodes(playlist)
                #for episode in sorted(episodes.items(),reverse=True):
                #    curEpisode = episode[1]
                #    print repr(curEpisode)
                #    
                #    # extract the mediaIds for the episode
                #    mediaIds = ''
                #    for i in sorted(curEpisode['media']):
                #        mediaIds += curEpisode['media'][i]['id'] + ','
                #    mediaIds = mediaIds[0:-1] # truncate last comma
                #    
                #    # add directory item
                #    listitem = xbmcgui.ListItem(self._parse_title(curEpisode['title']))
                #    listitem.setInfo( "video", {'title': curEpisode['title']} )
                #    xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?mediaIds=%s&path=%s&token=%s" % ( sys.argv[0], mediaIds, params['path'], self.tenClient.getToken()), totalItems=len(episodes))
            
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )
        
        
    def _parse_title( self, title ):
        split = title.split('|',1)
        if (len(split) == 2):
            return split[1].strip()
        else:
            return title.strip()
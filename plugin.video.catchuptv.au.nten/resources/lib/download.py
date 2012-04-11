import sys
import re
import logging
import urllib
import xbmc
import xbmcgui
import xbmcplugin, xbmcaddon 
from NetworkTenVideo import NetworkTenVideo
import os
# Un-comment for verbose debugging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class Main:
    def __init__( self, params ): 
        addon = xbmcaddon.Addon( id=os.path.basename(os.getcwd())) 
        bitrate	= int(addon.getSetting( "vid_quality" ))
	
        self.tenClient = NetworkTenVideo(networkID = params['networkId'], token=params['token'])
		
        
        # extract media ids then loop through each, adding to stack url
        mediaIds = params['mediaIds'].split(',')
        print 'DEBUG: there are %s parts, will try to create a stack url' % len(mediaIds)
        url = 'stack://'
        for mediaId in mediaIds:
            # Get media and rtmp args
            media = self.tenClient.getMedia(mediaId, bitrate)
            rtmpUrl = '%s app=%s playpath=%s swfUrl=%s swfVfy=true pageUrl=%s' % (media['host'], media['app'], media['playpath'], media['swfUrl'], media['pageUrl'])
            if 0:
                print 'Using rtmpe url, %s' % rtmpUrl
            
                # Extract media tags and create adPath
                tags = self.tenClient.parsePlaylistForTags(media['media'])
                print repr(tags)
                if (tags.has_key('clip:code')):
                    adPath = params['path'] + tags['clip:code']
                else:
                    adPath = params['path'] + media['name']
            
                # Get advertisement
                adConfig = self.tenClient.getAds(adPath)
                adUrl = adConfig['VideoAdServingTemplate']['Ad']['InLine']['Video']['MediaFiles']['MediaFile']['URL']
                print 'Found advertisement, will show %s' % adUrl
            
                # add urls to stack
                url += adUrl + ' , ' + rtmpUrl + ' , '
                url = url[0:-3] # remove last comma from stack
                print 'Final stack url, %s' % url
            url += rtmpUrl + ' , '
            url = url[0:-3] # remove last comma from stack
        print url
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(url, xbmcgui.ListItem(media['media']['title'], thumbnailImage=media['media']['imagePath'] + 'cropped/128x72.png'))
        

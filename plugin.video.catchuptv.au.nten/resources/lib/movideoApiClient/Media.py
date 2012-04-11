import string
import logging

class Media:
    def __init__(self,parent):
        self.parent = parent
        self._makeRequest = parent._makeRequest
        
    def authorise(self, mediaId):
        """
            Returns a token to allow playback of a track with the CDN.
            
            Arguments:
                mediaId - required, media id number
        """
        logging.debug('Getting Media Token')
        auth = self._makeRequest('authorise/%s' % mediaId)['authorisation']
        import urllib2
        smil = urllib2.urlopen(urllib2.Request("http://api.movideo.com/rest/media/%s/smil?token=%s" % (auth['media']["id"],self.parent.token))).read()
        from etree import ElementTree
        element = ElementTree.fromstring(smil)
        from Xml2Dict import ConvertXmlToDict
        xml = ConvertXmlToDict(element)
        return auth, xml
        
        
    def getMedia(self, mediaId):
        """
            Returns a single media object.
            
            Arguments:
                mediaId - required, media id number
        """
        logging.debug('Getting Media #%s' % mediaId)
        return self._makeRequest('media/%s' % mediaId)['media']
        
    def getActiveInactiveCount(self):
        """
            Returns the total number of Active and Inactive Media for the client.
        """
        logging.debug('Getting Active/Inactive Count')
        data = self._makeRequest('media/count')['count']
        self.parent.activeCount = data['active']
        self.parent.inactiveCount = data['inactive']
        logging.debug('%s Active / %s Inactive' % (data['active'] , data['inactive']))
        return data
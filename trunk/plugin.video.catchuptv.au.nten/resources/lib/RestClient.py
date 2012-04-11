import string
import logging
import urllib, urllib2
class RestClient:
    def __init__(self, base_url, headers={}):
        logging.debug('Creating RestClient class')
        self.base_url = base_url
        self.headers = headers
    
    def request(self, params={}):       
        if (type(self.base_url) == string.Template):
            logging.debug('String Template for base_url detected, using params')
            
            # Convert any sub-elements of dict type to a string
            for param in params:
                if (type(params[param]) == dict):
                    logging.debug('Converting %s to dict' % param)
                    params[param] = urllib.urlencode(params[param])
            
            url = self.base_url.substitute(params)
        else:
            logging.debug('String Base_url detected, adding params after base_url')
            url = self.base_url 
            if (len(params) > 0):
                url += '?' + urllib.urlencode(params)
        
        logging.debug('Making request for %s' % url)
        req = urllib2.urlopen(urllib2.Request(url=url, headers=self.headers))
        data = req.read()
        info = req.info()
        req.close()
        if (info['Content-Type'][0:15] == 'application/xml' or info['Content-Type'][0:8] == 'text/xml'):
            logging.debug('Xml content-type detected, decoding with ElementTree / ConvertXmlToDict')
            try:
                from xml.etree import ElementTree
            except ImportError:
                from etree import ElementTree
            element = ElementTree.fromstring(data)
            from Xml2Dict import ConvertXmlToDict
            return ConvertXmlToDict(element)
        elif (info['Content-Type'][0:16] == 'application/json'):
            logging.debug('JSON content-type detected, leaving')
            return data
        else:
            logging.debug('Unknown content-type, "%s"' % info['Content-Type'])
            return data
import string
import logging

class Application:
    def __init__(self,parent):
        self.parent = parent
        self._makeRequest = parent._makeRequest
        
    def application(self):
        logging.debug('Getting Application')
        self.parent.application = self._makeRequest('application')['application']
        return self.parent.application
    
    def applicationConfig(self):
        logging.debug('Getting Application Config')
        self.parent.applicationconfig = self._makeRequest('applicationconfig')['applicationConfig']
        return self.parent.applicationconfig
    
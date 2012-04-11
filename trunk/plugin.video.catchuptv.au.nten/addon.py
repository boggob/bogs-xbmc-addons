"""
    Plugin for streaming Channel Ten Videos
"""

# main imports
import sys, os
import urllib

# plugin constants (not used)
__plugin__ = "Channel Ten CatchUp TV Video Player"
__pluginid__ = "plugin.video.catchuptv.au.nten"
__author__ = "adammw111"
__url__ = "http://xbmc-catchuptv-au.googlecode.com/"
__svn_url__ = "http://xbmc-catchuptv-au.googlecode.com/svn/"
__useragent__ = "xbmcCatchUpTV/0.2"
__credits__ = "Team XBMC"
__version__ = "0.2.0"
__svn_revision__ = "$Revision: 1 $"
__XBMC_Revision__ = "31542"

# add lib resources to search module path
sys.path.append(os.path.join(os.getcwd(),'resources','lib'))

def _parse_argv( argstr ):
    try:
        # parse sys.argv for params and return result, strip leading ?
        params = dict( urllib.unquote_plus( arg ).split( "=" ) for arg in argstr[ 1 : ].split( "&" ) )
        print "%%", params
    except Exception, e:
        print e	
        # no params passed
        params = {}
    if not params.has_key('path'):
        params['path'] = ''
    if not params.has_key('token'):
        params['token'] = None
    print repr(params)
    return params


if ( __name__ == "__main__" ):
    params = _parse_argv(sys.argv[ 2 ])
    if "settings" in params:
        import os
        import xbmc
        import xbmcaddon
        # open settings
        xbmcaddon.Addon( id=os.path.basename( os.getcwd() ) ).openSettings()
        # refresh listing in case settings changed
        xbmc.executebuiltin( "Container.Refresh" )
    elif "mediaIds" in params:
        import resources.lib.download as plugin
        plugin.Main(params)
    elif "playlistId" in params:
        import resources.lib.playlist as plugin
        plugin.Main(params)
    elif "networkID" in params:
        import resources.lib.playlist as plugin
        plugin.Main(params)
    else:
        import resources.lib.playlist as plugin
        plugin.Main(params)

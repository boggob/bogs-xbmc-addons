"""
	Category module: fetches a list of categories to use as folders
"""

# main imports
import sys, os, re, urllib2, urllib
import comm
import utils

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

BASE_SKIN_THUMBNAIL_PATH = os.path.join(os.getcwd(), 'resources', 'media')
BASE_PLUGIN_THUMBNAIL_PATH = os.path.join(os.getcwd(), 'resources', 'media')

def make_series_list():
	try:
		series_list = comm.get_index()
		series_list.sort()

		# fill media list
		ok = fill_series_list(series_list)
	except:
		# oops print error message
		d = xbmcgui.Dialog()
		message = utils.dialog_error("Unable to fetch listing")
		d.ok(*message)
		utils.log_error();
		ok = False

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)


def fill_series_list(series_list):
	try:
		ok = True
		# enumerate through the list of categories and add the item to the media list
		for s in series_list:
			url = "%s?series_id=%s" % (sys.argv[0], s.get_series_url())
			listitem = xbmcgui.ListItem(s.get_title(), thumbnailImage=s.get_thumbnail())

			# add the item to the media list
			ok = xbmcplugin.addDirectoryItem(
						handle=int(sys.argv[1]), 
						url=url, 
						listitem=listitem, 
						isFolder=True, 
						totalItems=len(series_list)
					)
			# if user cancels, call raise to exit loop
			if (not ok): 
				raise
	except:
		# user cancelled dialog or an error occurred
		utils.log_error()
		ok = False
	return ok


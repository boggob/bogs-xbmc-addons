import	urllib2 
import	re
from	time import localtime, strftime, gmtime
from	BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString
import collections


import resources.lib.comm as comm, resources.lib.classes as classes, resources.lib.config as config


ADDON_ID='plugin.video.abc-iview2'



class Scraper(object):
	URLS = {
		"base"		: "http://www.abc.net.au/tv/iview/",
	}
	
	def __init__(self, folders, play, record):
		self.folders	= folders
		self.play		= play
		self.record		= record
		
	def menu(self, params):
		out = []
		iview_config = comm.get_config()
		category_list = comm.get_categories(iview_config)
		category_list = sorted(category_list, key=lambda k: k['name'].lower())
		category_list.insert(0, {'name':'All', 'keyword':'0-z'})
		for cat in category_list:
			out.append(
				{
					"url"		: cat['keyword'], 
					"title"		: cat['name'],
					"path"		: "browse",
					"folder"	: True,
				
				}
			)
		self.folders(out)
	

	
	def browse(self, params):
		programme = comm.get_programme(comm.get_config(), params['url'])

		out = []
		for s in programme:
			#Folders
		
			val = { 
				"url"		: s.id, 
				"title"		: s.get_list_title(),
				"path"		: "browse2",
				"still"		: s.get_thumbnail() ,
				"info"		: {"plot" : s.description},
				"folder"	: True,
			}
			out.append(val)
				
		
		self.folders(out)

	def browse2(self, params):
		programs = 	comm.get_series_items(comm.get_config(), params['url'])

		out = []
		for p in programs:
			#Folders
			print "$$$", p.get_list_title()
			val = { 
				"url"		: p.make_xbmc_url(), 
				"title"		: p.get_list_title(),
				"path"		: "playitems",
				"still"		: p.get_thumbnail(),
				"info"		: p.get_xbmc_list_item(),
				"folder"	: False,
			}
			out.append(val)
				
		
		self.folders(out)

		
		
	def playitems(self, params):
		iview_config = comm.get_config()
		auth = comm.get_auth(iview_config)

		if auth['rtmp_url'].startswith('http://'):
			auth['rtmp_url'] = iview_config['rtmp_url'] or config.akamai_fallback_server
			auth['playpath_prefix'] = config.akamai_playpath_prefix
			print ("Adobe HDS Not Supported, using fallback server %s" % auth['rtmp_url'])
		
		
		p = classes.Program()
		p.parse_xbmc_url(params['url'])
		playpath = auth['playpath_prefix'] + p.url
		if playpath.split('.')[-1] == 'mp4':
			playpath = 'mp4:' + playpath
	
		# Strip off the .flv or .mp4
		playpath = playpath.split('.')[0]
	
		# rtmp://cp53909.edgefcs.net/ondemand?auth=daEbjbeaCbGcgb6bedYacdWcsdXc7cWbDda-bmt0Pk-8-slp_zFtpL&aifp=v001 
		# playpath=mp4:flash/playback/_definst_/kids/astroboy_10_01_22 swfurl=http://www.abc.net.au/iview/images/iview.jpg swfvfy=true
		rtmp_url = "%s?auth=%s playpath=%s swfurl=%s swfvfy=true" % (auth['rtmp_url'], auth['token'], playpath, config.swf_url)

		
		val = {
			"url"		: rtmp_url,
			"duration"	: int(p.duration or 0),
			"name"		: params['name']#p.get_list_title()
		}
		print ("@2"	,  val)
		if "record" in params:
			self.record(val)
		else:
			self.play(val)


if __name__ == "__main__":
	pass
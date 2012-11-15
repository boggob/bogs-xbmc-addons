import re
import utils
import datetime
import urllib
import time

class Series(object):

	def __init__(self):
		url = ''
		thumbnail = None

	def __repr__(self):
		return self.title

	def __cmp__(self, other):
		return cmp(self.title, other.title)

	def get_title(self):
		""" Return the program title, including the Series X part
			on the end.
		"""
		return utils.descape(self.title)

	def get_series_url(self):
		return self.url.split("/")[-2]

	def get_thumbnail(self):
		if self.thumbnail:
			return self.thumbnail
		else:
			return 'defaultfolder.png'

class Program(object):

	def __init__(self):
		self.id = None
		self.title = ''
		self.description = ''
		self.episode_title = None
		self.episode = None
		self.season = None
		self.category = None
		self.rating = None
		self.duration = 0
		self.date = datetime.datetime.now()
		self.thumbnail = ''
		self.url_path = ''
		self.link = ''
		self.rtmp_host = ''
		self.rtmp_path = ''

	def __repr__(self):
		return self.title

	def __cmp__(self, other):
		return cmp(self.title, other.title)

	def get_title(self):
		""" Return the program title, including the Series X part
			on the end.
		"""
		return utils.descape(self.title)

	def get_episode_title(self):
		""" Return a string of the shorttitle entry, unless its	not 
			available, then we'll just use the program title instead.
		"""
		if self.episode_title:
			return utils.descape(self.episode_title)

	def get_list_title(self):
		""" Return a string of the title, nicely formatted for XBMC list
		"""
		title = self.get_title() 
	
		if (self.get_season() and self.get_episode()):
			# Series and episode information
			title = "%s (S%02dE%02d)" % (title, self.get_season(), self.get_episode())
		else:
			if self.get_episode():
				# Only episode information
				title = "%s (E%02d)" % (title, self.get_episode())
			else:
				if not self.get_episode_title():
					# Date only, no episode information or episode title
					title = "%s (%s)" % (title, self.get_date())

		if self.get_episode_title():
			title = "%s: %s" % (title, self.get_episode_title())

		return title

	def get_description(self):
		""" Return a string the program description, after running it through
			the descape.
		"""
		return utils.descape(self.description)

	def get_category(self):
		""" Return a string of the category. E.g. Comedy
		"""
		if self.category:
			return utils.descape(self.category)

	def get_rating(self):
		""" Return a string of the rating. E.g. PG, MA
		"""
		if self.rating:
			return utils.descape(self.rating)

	def get_duration(self):
		""" Return a string representing the duration of the program.
			E.g. 00:30 (30 minutes) from a given string of seconds
		"""
		if self.duration > 0:
			sec = self.duration
			hrs = sec / 3600
			sec -= 3600*hrs
			mins = sec / 60
			sec -= 60*mins
			return "%s:%s" % (hrs, mins)

	def get_date(self):
		""" Return a string of the date in the format 2010-02-28
			which is useful for XBMC labels.
		"""
		return self.date.strftime("%Y-%m-%d")

	def get_year(self):
		""" Return an integer of the year of publish date
		"""
		return self.date.year

	def get_season(self):
		""" Return an integer of the Series, discovered by a regular
			expression from the orginal title, unless its not available,
			then the year will be returned.
		"""
		if self.season:
			return self.season

	def get_episode(self):
		""" Return an integer of the Episode, discovered by a regular
			expression from the orginal title, unless its not available,
			then a 0 will be returned.
		"""
		if self.episode:
			return self.episode

	def get_thumbnail(self):
		""" Returns the thumbnail
		"""
		return utils.descape(self.thumbnail)
			

	def get_xbmc_list_item(self):
		""" Returns a dict of program information, in the format which
			XBMC requires for video metadata.
		"""
		info_dict = {}
		
		if self.get_title():
			info_dict['tvshowtitle'] = self.get_title()
		if self.get_episode_title():
			info_dict['title'] = self.get_episode_title()
		if self.get_category():
			info_dict['genre'] = self.get_category()
		if self.get_description():
			info_dict['plot'] = self.get_description()
		if self.get_description():
			info_dict['plotoutline'] = self.get_description()
		if self.get_duration():
			info_dict['duration'] = self.get_duration()
		if self.get_year():
			info_dict['year'] = self.get_year()
		if self.get_date():
			info_dict['aired'] = self.get_date()
		if self.get_season():
			info_dict['season'] = self.get_season()
		if self.get_episode():
			info_dict['episode'] = self.get_episode()
		if self.get_rating():
			info_dict['mpaa'] = self.get_rating()

		return info_dict

	def make_xbmc_url(self):
		""" Returns a string which represents the program object, but in
			a format suitable for passing as a URL.
		"""
		d = {}

		if self.id:
			d['id'] = self.id
		if self.title:
			d['title'] = self.title
		if self.episode_title:
			d['episode_title'] = self.episode_title
		if self.description:
			d['description'] = self.description
		if self.duration:
			d['duration'] =  self.duration
		if self.category:
			d['category'] = self.category
		if self.rating:
			d['rating'] = self.rating
		if self.date:
			d['date'] = self.date.strftime("%d/%m/%Y %H:%M:%S")
		if self.thumbnail:
			d['thumbnail'] = self.thumbnail
		if self.url_path:
			d['url_path'] = self.url_path
		
		return utils.make_url(d)		

	def parse_xbmc_url(self, string):
		""" Takes a string input which is a URL representation of the 
			program object
		"""
		d = utils.get_url(string)

		if d.has_key('id'):
			self.id = d['id']
		if d.has_key('title'):
			self.title = d['title']
		if d.has_key('episode_title'):
			self.episode_title = d['episode_title']
		if d.has_key('description'):
			self.description = d['description']
		if d.has_key('duration'):
			self.duration = d['duration']
		if d.has_key('category'):
			self.category = d['category']
		if d.has_key('rating'):
			self.rating = d['rating']
		if d.has_key('date'):
			timestamp = time.mktime(time.strptime(d['date'], '%d/%m/%Y %H:%M:%S'))
			self.date = datetime.date.fromtimestamp(timestamp)
		if d.has_key('thumbnail'):
			self.thumbnail = urllib.unquote_plus(d['thumbnail'])
		if d.has_key('url_path'):
			self.url_path = d['url_path']

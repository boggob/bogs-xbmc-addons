# -*- coding: UTF-8 -*-

import time
import datetime

try:
	from urllib.parse import quote_plus as url_quote
except:
	from urllib import quote_plus as url_quote


from bs4				import BeautifulSoup

from lib.url_get		import get_data
from lib.scrapers.utils import ScraperType, Action

ALLMUSICURL		= 'https://www.allmusic.com/%s'
ALLMUSICSEARCH	= 'search/albums/%s+%s'
ALLMUSICDETAILS	= '%s/releases'



def allmusic_albumfind(artist, album):
	url		= ALLMUSICURL % (ALLMUSICSEARCH % (url_quote(artist), url_quote(album)))
	data	= get_data(url, False)
	soup = BeautifulSoup(data, 'html.parser')
	albums = []
	for item in soup.find_all('li', {'class':'album'}):
		coverdata = item.find('div', {'class':'cover'})
		coverlink = coverdata.find('img', {'class':'lazy'})
		if coverlink:
			coverurl = coverlink.get('data-original')
		else:
			coverurl = ''
		releasedata = item.find('div', {'class':'info'})
		albumdata = releasedata.find('div', {'class':'title'})
		albumname = albumdata.find('a').get_text().strip()
		albumurl = albumdata.find('a').get('href')
		artistdata = releasedata.find('div', {'class':'artist'})
		if not artistdata: # classical album
			continue
		artistname = artistdata.get_text().strip()
		yeardata = releasedata.find('div', {'class':'year'})
		if yeardata:
			yearvalue = yeardata.get_text().strip()
		else:
			yearvalue = ''
		albumdata = {}
		albumdata['artist'] = artistname
		albumdata['album'] = albumname
		albumdata['year'] = yearvalue
		albumdata['thumb'] = coverurl
		albumdata['url'] = albumurl # url
		albumdata['relevance'] = '0'
		albums.append(albumdata)
	return albums

def allmusic_albumdetails(param, locale = "en"):
	found = allmusic_albumfind(param[0], param[1])
	if found:
		# get details
		url = ALLMUSICDETAILS % found[0]['url']
	else:
		return

	data = get_data(url, False)
	if not data:
		return

	

	soup = BeautifulSoup(data, 'html.parser')
	albumdata = {}
	releasedata = soup.find("div", {"class":"release-date"})
	if releasedata:
		dateformat = releasedata.find('span').get_text()
		if len(dateformat) > 4:
			try:
				albumdata['releasedate'] = datetime.datetime(*(time.strptime(dateformat, '%B %d, %Y')[0:3])).strftime('%Y-%m-%d')
			except Exception:
				albumdata['releasedate'] = datetime.datetime(*(time.strptime(dateformat, '%B, %Y')[0:2])).strftime('%Y-%m')
		else:
			albumdata['releasedate'] = releasedata.find('span').get_text()
	genredata = soup.find("div", {"class":"genre"})
	if genredata:
		genrelist = genredata.find_all('a')
		genres = []
		for genre in genrelist:
			genres.append(genre.get_text().rstrip(';'))
		albumdata['genre'] = ' / '.join(genres)
	styledata = soup.find("div", {"class":"styles"})
	if styledata:
		stylelist = styledata.find_all('a')
		styles = []
		for style in stylelist:
			styles.append(style.get_text().rstrip(';'))
		albumdata['styles'] = ' / '.join(styles)
	mooddata =  soup.find('section', {'class':'moods'})
	if mooddata:
		moodlist = mooddata.find_all('a')
		moods = []
		for mood in moodlist:
			moods.append(mood.get_text().rstrip(';'))
		albumdata['moods'] = ' / '.join(moods)
	themedata = soup.find('section', {'class':'themes'})
	if themedata:
		themelist = themedata.find_all('a')
		themes = []
		for theme in themelist:
			themes.append(theme.get_text().rstrip(';'))
		albumdata['themes'] = ' / '.join(themes)
	albumdata['rating'] = soup.find('div', {'itemprop':'ratingValue'}).get_text().strip()
	albumdata['votes'] = ''
	albumdata['album'] = soup.find('h1', {'class':'album-title'}).get_text().strip()
	artistdata = soup.find('h2', {'class':'album-artist'})
	artistlinks = artistdata.find_all('a')
	artistlist = []
	for artistlink in artistlinks:
		artistlist.append(artistlink.get_text())
	artists = []
	for item in artistlist:
		artistinfo = {}
		artistinfo['artist'] = item
		artists.append(artistinfo)
	albumdata['artist'] = artists
	if artistlist:
		albumdata['artist_description'] = artistlist[0]
	yeardata = soup.find('td', {'class':'year'})
	if yeardata:
		albumdata['year'] = yeardata.get_text().strip()
	labeldata = soup.find('td', {'class':'label-catalog'})
	if labeldata:
		albumdata['label'] = labeldata.contents[0].strip()
	thumbdata = soup.find('div', {'class':'album-contain'})
	thumbimg = thumbdata.find('img', {'class':'media-gallery-image'})
	if thumbimg:
		thumbs = []
		thumbdata = {}
		thumbdata['image'] = thumbimg.get('src')
		thumbdata['preview'] = thumbimg.get('src')
		thumbdata['aspect'] = 'thumb'
		thumbs.append(thumbdata)
		albumdata['thumb'] = thumbs
	return albumdata

SCAPER = ScraperType(
			Action('allmusic', allmusic_albumfind, 1),
			Action('allmusic', allmusic_albumdetails, 1),
		)

# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup

from lib.scrapers.utils import ScraperType, Action
from lib.url_get import get_data





def allmusic_artistdetails(url, locale):
	data = get_data(url, False)
	if not data:
		return


	soup = BeautifulSoup(data, 'html.parser')
	artistdata = {}
	if soup.find('h1', {'class':'artist-name'}):
		artistdata['artist'] = soup.find('h1', {'class':'artist-name'}).get_text().strip()
	else:
		# no discography page available for this artist
		return
	yearsdata = soup.find('div', {'class':'active-dates'})
	if yearsdata:
		artistdata['active'] = yearsdata.find('div').get_text()
	begindata = soup.find('div', {'class':'birth'})
	if begindata:
		begin = begindata.find('h4').get_text().strip()
		begindate = ' '.join(begindata.find('div').get_text().split())
		if begin == 'Born':
			artistdata['born'] = begindate
		elif begin == 'Formed':
			artistdata['formed'] = begindate
	enddata = soup.find('div', {'class':'death'})
	if enddata:
		end = enddata.find('h4').get_text().strip()
		enddate = ' '.join(enddata.find('div').get_text().split())
		if end == 'Died':
			artistdata['died'] = enddate
		elif end == 'Disbanded':
			artistdata['disbanded'] = enddate
	genredata = soup.find('div', {'class':'genre'})
	if genredata:
		genrelist = genredata.find_all('a')
		genres = []
		for genre in genrelist:
			genres.append(genre.get_text().rstrip(';'))
		artistdata['genre'] = ' / '.join(genres)
	styledata = soup.find('div', {'class':'styles'})
	if styledata:
		stylelist = styledata.find_all('a')
		styles = []
		for style in stylelist:
			styles.append(style.get_text().rstrip(';'))
		artistdata['styles'] = ' / '.join(styles)
	mooddata = soup.find('section', {'class':'moods'})
	if mooddata:
		moodlist = mooddata.find_all('a')
		moods = []
		for mood in moodlist:
			moods.append(mood.get_text().rstrip(';'))
		artistdata['moods'] = ' / '.join(moods)
	artistalbums = soup.find('tbody')
	if artistalbums:
		albumlist = artistalbums.find_all('tr')
		albums = []
		for item in albumlist:
			albumdata = {}
			albuminfo = item.find('td', {'class':'title'})
			albumdata['title'] = albuminfo.find('a').get_text()
			albumdata['year'] = item.find('td', {'class':'year'}).get_text().strip()
			albums.append(albumdata)
		if albums:
			artistdata['albums'] = albums
	thumbsdata = soup.find('div', {'class':'artist-image'})
	if thumbsdata:
		thumbs = []
		thumbdata = {}
		thumbdata['image'] = thumbsdata.find('img').get('src').rstrip('?partner=allrovi.com')
		thumbdata['preview'] = thumbsdata.find('img').get('src').rstrip('?partner=allrovi.com')
		thumbdata['aspect'] = 'thumb'
		thumbs.append(thumbdata)
		artistdata['thumb'] = thumbs
	return artistdata


SCAPER = ScraperType(
			Action('allmusic', None, 1),
			Action('allmusic', allmusic_artistdetails, 1),
		)

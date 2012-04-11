import	urllib2 
import	re
from	time import localtime, strftime, gmtime
from	BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString


def geturl(url):
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def jsonc(st):
	for i,o in (
		('true', 'True'),
		('false', 'False'),
		('null',  'None'),
	):
		st = st.replace(i,o)
	return eval(st)


class MenuItems(object):
	def __init__(self):
		self.base2				= 'http://www.theage.com.au/tv/type/show'

	def menu_main(self, path):
		next = []
		out = []
		if path is None:
			html = geturl(self.base2)
			soup = BeautifulSoup(html)
			for item in soup.findAll('div', "cN-groupNavigator open accessible simple"):
				for sitem in item.findAll('a'):
					print sitem
					out.append((sitem.next, sitem["href"], "DefaultFolder.png"))
		else:
			print type(path), path
			html = geturl(path)
			soup = BeautifulSoup(html)
			
			for item in soup.findAll('li', attrs={'class' : "next"}):
				for a in item.findAll('a'):
					next.append(("Next->", a["href"],  "DefaultFolder.png"))
			
			for item in soup.findAll('ul', attrs={'class' : "cN-listStoryTV"}):
				for li in item.findAll('li'):
					sers  = li.findAll('a', title = True)
					if not sers:
						continue
					ser		= sers[0]
					pic	= li.findAll('img')
					if pic:
						pic 		= pic[0]["src"]
					else:
						pic 		= 'DefaultVCD.png'	

					out.append((ser["title"], ser["href"],  pic))
					
		return next,out				
					
	def menu_shows(self, path):
		print path
		html = geturl(path)
		soup = BeautifulSoup(html)

		info = {}
		title, genre, description, ovation = soup.findAll('dd')
		print genre
		print genre.findAll("a")
		info["genre"]	= ", ".join([a.next for a in genre.findAll("a")])
		info["plot"]	= description.contents[0]
		
		for item in soup.findAll('ul', attrs={"id" : "paginationContent", 'class' : "cN-listStoryTV listStoryTVShort"}):
			for sitem in item.findAll('li'):
				for anc in sitem.findAll('a', attrs={'class' : "play-video "}):
					temp	= {"info" : info}
					temp["title"]		= anc["title"]
					temp["thumbnail"]	= anc.next["src"]
					temp["url"]			= anc["href"]
				dur =  sitem.find('p')
				temp["info"]["duration"]	= str(dur.next).strip()[1:-1]
				print temp
				yield temp
			
	def menu_play(self, path):
		print path
		html = geturl(path)
		import re
		return set(re.findall(r'"(rtmp://[^"]+)"', html))

			

if __name__ == "__main__":
	from  pprint import PrettyPrinter, pprint

	m = MenuItems()
	print "#" * 20
	menues = []
	m.menu_tree([], menues)
	PrettyPrinter(indent=1).pprint(menues)
	print "#" * 30
	leafs = [i for i in menues if not m.menu_main(i)["children"]]
	print "#" * 30
	shows = list(m.menu_shows(m.menu_main(leafs[30])["url"]))
	PrettyPrinter(indent=1).pprint(shows)
	print "#" * 30
	PrettyPrinter(indent=1).pprint(m.menu_play(shows[2]["url"]))
else:
	SCRAPER = MenuItems()

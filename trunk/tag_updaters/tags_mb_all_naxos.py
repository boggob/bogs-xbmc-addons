import collections
import urllib2
import os, sys
import time
import pprint
"""
Gets all of the naxos releases from musicbrainz
"""

from	BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString

pt =  os.path.split(__file__)[0]
print pt
sys.path.append(pt)
sys.path.append(os.path.split(__file__)[0])
import scrapers
import tags

class flushfile(object):
	def __init__(self, f):
		self.f = f
	def write(self, x):
		self.f.write(x)
		self.f.flush()

import sys
sys.stdout = flushfile(sys.stdout)

####################################
if 1:
	PATHS = [
	 r'C:\files\music\Assorted',
	 r'C:\files\music\Classical',
	 r'C:\files\music\World',
	 r'C:\files\music\Matilda',
	 r'C:\files\music\musique_wog',
	 r'C:\files\music\Jaz',
	]
	OUTFILE = "C:/temp/albums.xml"
else:
	PATHS = [
	 r'C:\temp\aaaa',
	]
	OUTFILE = "C:/temp/albums_test.xml"
	
####################################
def geturl(url):
	#, headers = {"Accept-Encoding":"gzip"}
	print "getting: %s" % url
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')


class Dummy(object):
	def __init__(self):
		self.text = None
	
def handler():
	out = collections.defaultdict(list)
	for i in range(1, 40):
		soup = BeautifulSoup(geturl("http://musicbrainz.org/label/615fa478-3901-42b8-80bc-bf58b1ff0e03?page={}".format(i)))
		for idx, row in  enumerate(soup.find('tbody', about="[mbz:artist/#_]").findAll('tr')):
			print "\t", i, idx
			la	= (row.find('span', property="mo:catalogue_number") or Dummy()).text
			rl	= [(a["about"].split(":")[-1][:-3],a.text)  for a in [row.find('span', property="dct:title rdfs:label")]][0]
			ea	= ((row.find('span', property="mo:ean")) or Dummy()).text
			out[la].append(
				((
					ea,rl[0],rl[1]
				))
			)
			
		time.sleep(2.0)
		
	print
	print "*" * 120
	for la,v in sorted(out.iteritems()):
		for ea,rl0,rl1 in v:
			print "{}\t{}\t{}\t{}".format(la,ea,rl0,rl1)


			


def main():
	print "starting"
	handler()
main()
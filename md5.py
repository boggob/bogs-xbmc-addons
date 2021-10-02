import sys
import hashlib
import os.path
import glob
import pprint
import re


def main():
	di	= sys.path[0]
	
	addons = {}
	for fin in sorted(glob.glob(di + "/*")):
		print (fin)
		if os.path.isdir(fin) and os.path.abspath(fin) != os.path.abspath(di):
			try:
				with open(fin + "/addon.xml", "r") as fi:
					addons[fin] = fi.read()
#					with ZipFile('spam.zip', 'w') as myzip:
#						myzip.write('eggs.txt')					
					
			except IOError as e:
				pass
				
	pprint.pprint(addons)
	with open(di + "/addons.xml", "w") as fo:
		fo.write("<addons>")	
		for k,v in sorted(addons.items()):
			#"\n  <--%s>" % (k) + 
			fo.write("\n  " + "\n".join("  " + st for st in re.sub(r'<\?.*\?>', '',  v).split("\n")).strip())	
		fo.write("\n</addons>")	
	
	with open(di + "/addons.xml") as fi:	
		with open(di + "/addons.xml.md5", "w") as fo:
			fo.write(hashlib.md5(fi.read().encode('utf-8')).hexdigest())

main()
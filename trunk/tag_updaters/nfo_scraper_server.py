import collections
from xml.dom.minidom import parse, parseString
import BaseHTTPServer
import urllib
import codecs
import os.path

import user_input
import scrapers
import tags_config

#################################################
class flushfile(object):
    def __init__(self, f):
        self.f = f
    def write(self, x):
        self.f.write(x)
        self.f.flush()

import sys
sys.stdout = flushfile(sys.stdout)
#################################################


def utf8(s):
	return  s.encode("utf-8")

CASE_INSENSITIVE = True

def myserver(mappings):
	try:
		class HTTPHAndler(BaseHTTPServer.BaseHTTPRequestHandler):
			def do_GET(self):
				try:
					url		= self.path.upper().split("?")
					print url
					
					if len(url) == 2:
						tail	= url[1]
						print type(tail)
						print repr(tail)


						
						
						comm,arg	= tail.split("=")
						argn		= urllib.unquote(arg).strip()
						argn		= argn.upper() if CASE_INSENSITIVE else  argn
						print "&&", repr(argn)
						utail		= utf8(argn.decode("utf-8"))
						print "&&!", utail
						
						xml	= mappings.get(utail, None)
						if xml:
							print "\t", repr(xml[0])
							self.send_response(200)
							self.send_header('Content-type', 'text/xml')
							self.end_headers()
						
							if comm == "search":
								self.wfile.write("""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>""" + "<album><search>"+ arg + "</search>" + xml[0].replace('<album>', ''))
								return
							else:
								self.wfile.write("""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>""" + xml[0])
								return
					self.send_error(404, "File Not Found %s" % self.path)		
				except Exception,e:
					print e
					import traceback
					print traceback.format_exc()
					self.send_error(404, "Trouble with %s: %s" % (self.path, e))
					
				
		print "Starting Server"					
		httpd = BaseHTTPServer.HTTPServer(("", 80), HTTPHAndler)
		httpd.serve_forever()
	finally:
		print "Exiting"
		httpd.socket.close()
		

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def xml_decode(fname):
	rec = collections.defaultdict(list)

	print "Reading XML", fname
	dom1 = parse(fname)
	for album in dom1.getElementsByTagName("album"):
		titles = [t for t in album.getElementsByTagName("title") if t.parentNode == album]
		key = utf8(getText(titles[0].childNodes).strip())
		if len(titles) == 1:
			rec[key.upper() if CASE_INSENSITIVE else key].append(album.toxml("utf-8"))
		else:
			print "??",  [t.toxml("utf-8") for t in album.getElementsByTagName("title")]
			
			
	for artist in dom1.getElementsByTagName("artist"):
		titles = [t for t in artist.getElementsByTagName("name") if t.parentNode == artist]
		key = utf8(getText(titles[0].childNodes).strip())
		if len(titles) == 1:
			rec[key.upper() if CASE_INSENSITIVE else key].append(artist.toxml("utf-8"))
		else:
			print "??",  [t.toxml("utf-8") for t in artist.getElementsByTagName("title")]
	return rec
	
	
def xml_decode2(fname):
	rec = collections.defaultdict(list)
	
	def get_thumbs(dom1, rec, parent):
		mbid = ""
		for mbidn in parent.getElementsByTagName("mbid"):
			mbid = getText(mbidn.childNodes).strip()
		
		filename = ""		
		for idx, thumb in enumerate(x for x in parent.getElementsByTagName("thumb") if x.parentNode == parent):
			if idx == 0:
				filename = utf8(getText(thumb.childNodes).strip())
			#parent.removeChild(thumb)

		if filename:		
			rec[filename].append((mbid, parent.toxml("utf-8")))		
		
	print "Reading XML", fname
	dom1 = parse(fname)
	for  node in dom1.getElementsByTagName("album"):
		get_thumbs(dom1,rec, node)

	for node in dom1.getElementsByTagName("artist"):
		get_thumbs(dom1,rec, node)
	return rec
	

def server(fname):
	rec = xml_decode(fname)
			
	if 1:
		for title, album in sorted(rec.iteritems()):
			print "\t", title
			print "\t\t",  urllib.quote(title).strip()
			print
	myserver(rec)		

def update(fname_in):
	
	dirn, filen	= os.path.split(fname_in)
	prefn, sufn	= os.path.splitext(filen)
	fname_dir	= os.path.join(dirn, prefn)
	fname_out	= os.path.join(dirn, "{}_cached{}".format(prefn, sufn))
	
	print "using\t", fname_in, fname_dir, fname_out

	rec = xml_decode2(fname_in)

	def new_name(fname_dir, mbid):
		stub = mbid.replace('/','-')
		if len(stub) > 100:
			stub = stub[:100]
		ret=  r'%s\%s.jpg' % (fname_dir, stub)
		return ret
			
	with codecs.open(fname_out, "w", encoding='utf8') as foo:		
		foo.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<musicdb>\n')

		for idx, (filename, items) in enumerate(sorted(rec.iteritems())):
			if not all(
				os.path.exists(new_name(fname_dir, mbid)) 
				for mbid, itemo in items
			):
				try:
					contents = scrapers.geturlbin(filename)
				except Exception,e:
					contents = False
					print
					print "^^^", e
					print filename,items
					import traceback
					print traceback.format_exc()
				
			else:
				contents = True
			
			for mbid, itemo in items:
				nn = itemo.decode('utf8')
				fname_new = new_name(fname_dir, mbid)
				print "\t",  idx, mbid, filename, fname_new

				if contents:
					if contents != True:
						with open(fname_new, 'wb') as fo:
							fo.write(contents)				
					nn = nn.replace(filename, fname_new)
				nn = tags_config.translate(nn)
					#print nn
				#print type(nn)
				#print repr(nn)
				foo.write(nn)
				foo.write("\n")
				foo.flush()
		foo.write("\n</musicdb>\n")			


		
if __name__ == "__main__":
	#server(user_input.input_file())
	update(r'C:\files\music\art\albums.xml')
	update(r'C:\files\music\art\artists.xml')


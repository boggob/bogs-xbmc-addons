import collections
from xml.dom.minidom import parse, parseString
import codecs
import pprint

from xml.sax.saxutils import escape, unescape
#################################################

def fill(items):
	items = list(items)
	
	if len(set(k for k,v in items)) == 1:
		return [{k:v} for k,v in items]
	else:
		out = collections.OrderedDict()
		for k,v in items:
			if k in out:
				out[k].append(v)
			else:
				out[k] = [v]
				
		return collections.OrderedDict( (k, (v if len(v) > 1 else v[0])) for k,v in out.iteritems())
		

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def dcode_rec(node):
	data = []
	for snode in (node.childNodes or []):
		if snode.nodeType != snode.TEXT_NODE:
			data.append(dcode_rec(snode))
		else:
			txt = snode.data.strip()
			if txt:
				data.append(txt)
	

	if all(isinstance(d, basestring) for d in data):
		return {unescape(node.nodeName): unescape(''.join(data))}
	else:
		return { unescape(node.nodeName): fill( (k,v) for rdata in data for k,v in rdata.iteritems())}
		
		
	
	
def xml_decode(fname):
	print "Reading XML", fname
	try:
		dom1 = parse(fname)
		ret =  dcode_rec(dom1)
		return ret['#document'][0]
	except IOError:
		return {}

unquote = lambda st : st.replace('&quot;', '"')
def xml_encode(outf, data):
	with codecs.open(outf, "w", encoding='utf8') as outfh:		
		outfh.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<musicdb>\n')
		for dat in data:
			outfh.write(encode(dat))
			outfh.write("\n")
		outfh.write("\n</musicdb>\n")

		
def encode(mp, indent = "  ", depth = 0):
	#print "\n\n**", mp
	def test(tag, ii):
		if isinstance(ii, dict):
			return encode(ii,indent,depth+1)
		elif isinstance(ii, basestring):
			return escape(ii)
		elif hasattr(v, "__iter__"):
			return list(encode(vv, indent, depth + 1) if isinstance(vv, dict) else vv for vv in v)
		else:
			return str(ii)
	
	
	output = lambda indent, depth, tag, val: ("\n{indent}<{tag}>".format(indent= indent * depth, tag = tag),  val, "</{tag}>".format(indent = indent * depth, tag = tag))
	out = []
	for k,v in mp.iteritems():
		val = test(k, v)
		if isinstance(val, list):
			for v in val:
				vi = "".join(test(k, v))
				out.extend(output(indent, depth, k, vi))
		else:
			out.extend(output(indent, depth, k, val))

	#print out
	return "".join(out)
	
	
		
if __name__ == "__main__":
	import scrapers
	#server(user_input.input_file())
	#pprint.pprint(xml_decode(r'C:\files\music\art\albums.xml'))
	res = xml_decode(r'C:\files\music\art\albums.xmls')
	with open(r'c:\temp\a.txt','w') as fi:
		fi.write(pprint.pformat((res)))
	with codecs.open(r'c:\temp\b.xml', "w", encoding='utf8') as fo:		
		fo.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<musicdb>\n')	
		for item in res.get('musicdb', []):
			fo.write(scrapers.unquote(scrapers.encode(item)))	
		fo.write('\n</musicdb>')	
		


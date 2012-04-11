import hashlib
import os.path,sys






di	= sys.path[0]
with open(di + "/addons.xml") as fi:
	with open(di + "/addons.xml.md5", "w") as fo:
		fo.write(hashlib.md5(fi.read()).hexdigest())


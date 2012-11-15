import os

NAME = 'Plus7'
VERSION = '1.0'

try:
	uname = os.uname()
	os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
	os_string = ''

user_agent = '%s v%s plugin for XBMC %s' % (NAME, VERSION, os_string)

index_url = "http://au.tv.yahoo.com/plus7/browse/"

series_url = "http://au.tv.yahoo.com/plus7/%s/"
program_url = "http://au.tv.yahoo.com%s"
program_info_url = "http://cosmos.bcst.yahoo.com/rest/v2/pops;id=%s;lmsoverride=1"
stream_info_url = "http://cosmos.bcst.yahoo.com/rest/v2/pops;id=%s;lmsoverride=1;element=stream;bw=1200"

# Used for "SWF verification", a stream obfuscation technique
swf_url     = "http://d.yimg.com/m/up/ypp/au/player.swf"

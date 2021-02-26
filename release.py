import os, os.path
from zipfile import ZipFile
import shutil
import xml.etree.ElementTree
import subprocess

def get_files(path, filt = (lambda file, ext:True)):
	out = []
	for fi in sorted(os.listdir(path)):
		fullpath = os.path.join(path, fi)
		if os.path.isdir(fullpath):
			out.extend(get_files(fullpath, filt))
		else:
			ext = os.path.splitext(fi)[-1].lower()
			if filt(fi, ext):
				try:
					out.append(os.path.join(path, fi))
				except Exception,e:
					print "***", e, fullpath
			else:
				pass
	return out


def root():
	return   os.path.dirname(os.path.realpath(__file__))

def mkdir(path):
	import os
	import errno

	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise
	
def archive(name, path, files):
	with ZipFile(name, 'w') as myzip:
		for file in files:
			myzip.write(file, file[len(path) + 1:])
			

def copy(src_path, dest_path, file):
	shutil.copyfile(os.path.join(src_path, file), os.path.join(dest_path, file))			

def parse(addon):


	e = xml.etree.ElementTree.parse(addon).getroot()
	return e.attrib['version']
	
def module(dest_path, addon):

	version 	= parse(addon)

	addon_path				= os.path.split(addon)[0]
	addon_top, addon_name 	= os.path.split(addon_path)
	file_name				= "{}-{}.zip".format(addon_name, version)
	print addon_path
	mkdir(os.path.join(dest_path, os.path.split(addon_path)[1]))
	
	archive(os.path.join(dest_path, addon_name, file_name), addon_top, get_files(addon_path))
		
	
def main(dest_path):
	top 		= root()
	
	addons		= get_files(top, filt =(lambda file, ext: os.path.split(file)[1].lower() == "addon.xml"))
	for addon in addons:
		module(dest_path, addon)
	
	print top + r'\md5.py'
	execfile(top + r'\md5.py', {})
	
	copy(top, dest_path, "addons.xml")
	copy(top, dest_path, "addons.xml.md5")
	
	os.chdir(top)
	try:
		print subprocess.check_output([r"C:\apps\Git\bin\git.exe", "add", "*"], stderr=subprocess.STDOUT, shell=True)
		print subprocess.check_output([r"C:\apps\Git\bin\git.exe", "commit", "-m", "'Updated code'"], stderr=subprocess.STDOUT, shell=True)
		print subprocess.check_output([r"C:\apps\Git\bin\git.exe", "push"], stderr=subprocess.STDOUT, shell=True)

		os.chdir(dest_path)
		print subprocess.check_output([r"C:\apps\Git\bin\git.exe", "add", "*"], stderr=subprocess.STDOUT, shell=True)
		print subprocess.check_output([r"C:\apps\Git\bin\git.exe", "commit", "-m", "'Updated code'"], stderr=subprocess.STDOUT, shell=True)
		print subprocess.check_output([r"C:\apps\Git\bin\git.exe", "push"], stderr=subprocess.STDOUT, shell=True)
	except subprocess.CalledProcessError as e:
		print "Exception on process, rc=", e.returncode, "output=", e.output		
		raise	
main(r'D:\files\xbmc\denis\bogs-kodi-release')	
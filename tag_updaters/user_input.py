import Tkinter,tkFileDialog
import os

def input_file():
	root = Tkinter.Tk()
	file = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a file')
	if file != None:
		return file

def input_directory():		
	root = Tkinter.Tk()
	dirname = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')
	if len(dirname ) > 0:
		return dirname

		
def input_paths():
	def	recurse(path):
		print path
		out = [path]
		for fi in sorted(os.listdir(path)):
			fi =  os.path.join(path, fi)
			if os.path.isdir(fi):
				out.append(fi)
				out.extend(recurse(fi))
		return out
		
	return recurse(input_directory())
	
	

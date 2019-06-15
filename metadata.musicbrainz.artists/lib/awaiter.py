from threading import Thread


class Awaiter(object):
	def __init__(self, func, *args, **kwargs):
		self.ret = []
		self._exception = None
		def inner_():
			try:
				self.ret.append(func(*args, **kwargs))
			except Exception as e:
				self._exception = e
				raise
			
		self.thread = Thread(target = inner_)

		self.start()

	def start(self):
		self.thread.start()
		return self
	
	def data(self):
		self.thread.join()
		return next(iter(self.ret), None)
		
	def excepttion(self):
		self.thread.join()
		return self._exception
	
		
		
		
		

import collections



def make_multimap(it, cls=list):
	items = collections.defaultdict(cls)
	func = "append" if cls is list else "add"
	for k, v in it:
		getattr(items[k], func)(v)
	return items

def merge_multimap(*args, **kwargs):
	types = {
		type(val)
		for map_ in args
		for val in map_.itervalues()
	}

	if len(types) > 1:
		raise ValueError("Multiple value types detected {}".format(types))
	elif len(types) < 1 :
		return {}
	else:
		type_	= list(types)[0]
		prop	= (lambda a,b: a.union(b)) if issubclass(type_, set) else (lambda a,b: a + b)
		func	= kwargs.get("func", prop)

		out		= collections.defaultdict(type_)
		for map_ in args:
			for k, v in map_.iteritems():
				out[k] = func(out[k], v)
		return out



class XDict(dict):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.args = args
		self.kws = kwargs
	
	def __getattribute__(self, attr):
		try:
			return super().__getattribute__(attr)
		except AttributeError:
			return super().__getitem__(attr)


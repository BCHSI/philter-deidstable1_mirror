


class CoordinateMap:
	""" 
		Hits are stored in a coordinate map data structure
		This class abstracts out alot of the maintainence needed for a map

	"""
	def __init__(self):
		""" internal data structure maps fielpaths to a map of int:string (coordinate start --> value)

		{ "data/foo.txt": {123:"bar", 124:"baz"} }

		"""
		self.map = {}

	def add(self, fn, coord, value, overlap=False):
		"""  adds a new coordinate to the coordinate map
			if overlap is false, this will reject any overlapping hits (usually from multiple regex scan runs)
		"""
		if fn not in self.map:
			self.map***REMOVED***fn***REMOVED*** = {}

		if not overlap:
			if coord in self.map***REMOVED***fn***REMOVED***:
				raise Exception('adding coordinate multiple times Exception', coord)

			for i in range(coord, coord+len(value)):
				if i in self.map***REMOVED***fn***REMOVED***:
					raise Exception('Overlapping coordinates found', coord, value)

		self.map***REMOVED***fn***REMOVED******REMOVED***coord***REMOVED*** = value
		return True, None

	def remove(self, fn, coord, value):
		""" """
		if fn not in self.map:
			raise Exception('Filename does not exist', fn)
		if coord in self.map***REMOVED***fn***REMOVED***:
			raise Exception('Adding coordinate multiple times Exception')
		del self.map***REMOVED***fn***REMOVED******REMOVED***coord***REMOVED***
		return True, None

	def scan(self):
		""" does an inorder scan of the coordinates and their values"""
		for fn in self.map:
			coords = self.map***REMOVED***fn***REMOVED***.keys()
			coords.sort()
			for coord in coords:
				yield fn,coord,self.map***REMOVED***fn***REMOVED******REMOVED***coord***REMOVED***

	def keys(self):
		for fn in self.map:
			yield fn

	def filecoords(self, filename):
		""" 
			generator does an inorder scan of the coordinates for this file
		"""
		if filename not in self.map:
			raise Exception('Filename not found', filename)
		coords = sorted(self.map***REMOVED***filename***REMOVED***.keys())
		for coord in coords:
			yield coord,self.map***REMOVED***filename***REMOVED******REMOVED***coord***REMOVED***

	def does_exist(self, filename, index):
		""" Simple check to see if this index is a hit (start of coordinates)"""
		if i in self.map***REMOVED***filename***REMOVED***:
			return True
		return False

	def does_overlap(self, filename, start, stop):
		""" Check if this coordinate overlaps with any existing range"""
		for i in range(start, stop):
			if i in self.map***REMOVED***filename***REMOVED***:
				return True
		return False

	def calc_overlap(self, filename, start, stop):
		""" given a set of coordinates, will calculate all overlaps 
			perf: stop after we know we won't hit any more
			perf: use binary search approach
		"""
		
		overlaps = ***REMOVED******REMOVED***
		for s in self.map***REMOVED***filename***REMOVED***:
			e = self.map***REMOVED***filename***REMOVED******REMOVED***s***REMOVED***
			if s >= start or s <= stop:
				#We found an overlap
				if e <= stop:
					overlaps.append({"start":s, "stop":e})
				else:
					overlaps.append({"start":s, "stop":stop})
			elif e >= start or e <= stop:
				if s >= start:
					overlaps.append({"start":s, "stop":e})
				else:
					overlaps.append({"start":start, "stop":e})
		return overlaps





	def add_file(self, filename):
		""" add our fileto map, may not have any coordinates"""
		self.map***REMOVED***filename***REMOVED*** = {}






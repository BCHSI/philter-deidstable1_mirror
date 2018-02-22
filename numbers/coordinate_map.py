


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
		self.coord2pattern = {} #keeps reference of the patterns that matched this coorinate (can be multiple patterns)

	def add(self, fn, start, stop, overlap=False, pattern=""):
		"""  adds a new coordinate to the coordinate map
			if overlap is false, this will reject any overlapping hits (usually from multiple regex scan runs)
		"""
		if fn not in self.map:
			self.map***REMOVED***fn***REMOVED*** = {}

		if not overlap:
			if start in self.map***REMOVED***fn***REMOVED***:
				raise Exception('adding coordinate multiple times Exception', start)

			for i in range(start, stop):
				if i in self.map***REMOVED***fn***REMOVED***:
					raise Exception('Overlapping coordinates found', start, i, fn)

		self.map***REMOVED***fn***REMOVED******REMOVED***start***REMOVED*** = stop
		self.add_pattern(fn,start,stop,pattern)
		return True, None

	def add_pattern(self, filename, start, stop, pattern):
		""" adds this pattern to this start coord """
		if filename not in self.coord2pattern:
			self.coord2pattern***REMOVED***filename***REMOVED*** = {}
		if start not in self.coord2pattern***REMOVED***filename***REMOVED***:
			self.coord2pattern***REMOVED***filename***REMOVED******REMOVED***start***REMOVED*** = ***REMOVED******REMOVED***
		self.coord2pattern***REMOVED***filename***REMOVED******REMOVED***start***REMOVED***.append(pattern)

	def add_extend(self, filename, start, stop, pattern=""):
		"""  adds a new coordinate to the coordinate map
			if overlaps with another, will extend to the larger size
		"""
		if filename not in self.map:
			self.map***REMOVED***filename***REMOVED*** = {}
		overlaps = self.max_overlap(filename, start, stop)

		def clear_overlaps(filename, lst):
			for o in lst:
				del self.map***REMOVED***filename***REMOVED******REMOVED***o***REMOVED***"orig"***REMOVED******REMOVED***

		if len(overlaps) == 0:
			#no overlap, just save these coordinates
			self.map***REMOVED***filename***REMOVED******REMOVED***start***REMOVED*** = stop
			self.add_pattern(filename,start,stop,pattern)
		elif len(overlaps) == 1:
			clear_overlaps(filename, overlaps)
			#1 overlap, save this value
			o = overlaps***REMOVED***0***REMOVED***
			self.map***REMOVED***filename***REMOVED******REMOVED***o***REMOVED***"start"***REMOVED******REMOVED*** = o***REMOVED***"stop"***REMOVED***
			self.add_pattern(filename,start,stop,pattern)
		else:
			clear_overlaps(filename, overlaps)
			#greater than 1 overlap, by default this is sorted because of scan order
			o1 = overlaps***REMOVED***0***REMOVED***
			o2 = overlaps***REMOVED***-1***REMOVED***
			self.map***REMOVED***filename***REMOVED******REMOVED***o1***REMOVED***"start"***REMOVED******REMOVED*** = o2***REMOVED***"stop"***REMOVED***
			self.add_pattern(filename,start,stop,pattern)

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

	def max_overlap(self, filename, start, stop):
		""" given a set of coordinates, will calculate max of all overlaps 
			perf: stop after we know we won't hit any more
			perf: use binary search approach
		"""
		
		overlaps = ***REMOVED******REMOVED***
		for s in self.map***REMOVED***filename***REMOVED***:
			e = self.map***REMOVED***filename***REMOVED******REMOVED***s***REMOVED***
			if start >= s and start <= e:
				#We found an overlap
				if stop >= e:
					overlaps.append({"orig":s, "start":s, "stop":stop})
				else:
					overlaps.append({"orig":s, "start":s, "stop":e})
				
			elif stop >= s and stop <= e:
				if start <= s:
					overlaps.append({"orig":s, "start":start, "stop":e})
				else:
					overlaps.append({"orig":s, "start":s, "stop":e})
				
		return overlaps


	def add_file(self, filename):
		""" add our fileto map, may not have any coordinates"""
		self.map***REMOVED***filename***REMOVED*** = {}






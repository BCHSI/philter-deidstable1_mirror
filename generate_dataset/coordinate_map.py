


class CoordinateMap:
	""" 
		Hits are stored in a coordinate map data structure
		This class stores start coordinates for any matches found for this pattern

	"""
	def __init__(self, pattern={"title":"untitled"}, debug=False):
		""" internal data structure maps fielpaths to a map of int:string (coordinate start --> value)

		{ "data/foo.txt": {123:"bar", 124:"baz"} }

		"""
		self.map = {}
		self.coord2pattern = {} #keeps reference of the patterns that matched this coorinate (can be multiple patterns)
		self.pattern = pattern
		self.debug = debug

	def add(self, fn, start, stop, overlap=False, pattern=""):
		"""  adds a new coordinate to the coordinate map
			if overlap is false, this will reject any overlapping hits (usually from multiple regex scan runs)
		"""
		if fn not in self.map:
			self.map[fn] = {}

		if not overlap:
			if start in self.map[fn]:
				raise Exception('adding coordinate multiple times Exception', start)

			for i in range(start, stop):
				if i in self.map[fn]:
					raise Exception('Overlapping coordinates found', start, i, fn)

		self.map[fn][start] = stop
		self.add_pattern(fn,start,stop,pattern)
		return True, None

	def add_pattern(self, filename, start, stop, pattern):
		""" adds this pattern to this start coord """
		if filename not in self.coord2pattern:
			self.coord2pattern[filename] = {}
		if start not in self.coord2pattern[filename]:
			self.coord2pattern[filename][start] = []
		self.coord2pattern[filename][start].append(pattern)

	def add_extend(self, filename, start, stop, pattern=""):
		"""  adds a new coordinate to the coordinate map
			if overlaps with another, will extend to the larger size
		"""

		if self.debug:
			print("add_extend", start, stop)

		if filename not in self.map:
			self.map[filename] = {}
		overlaps = self.max_overlap(filename, start, stop)

	
		def clear_overlaps(filename, lst):
			for o in lst:
				del self.map[filename][o["orig_start"]]

		if len(overlaps) == 0:
			#no overlap, just save these coordinates
			self.map[filename][start] = stop
			self.add_pattern(filename,start,stop,pattern)
		elif len(overlaps) == 1:
			clear_overlaps(filename, overlaps)
			#1 overlap, save this value
			o = overlaps[0]
			self.map[filename][o["new_start"]] = o["new_stop"]
			self.add_pattern(filename,start,stop,pattern)
		else:
			clear_overlaps(filename, overlaps)
			#greater than 1 overlap, by default this is sorted because of scan order
			o1 = overlaps[0]
			o2 = overlaps[-1]
			self.map[filename][o2["new_start"]] = o1["new_stop"]
			self.add_pattern(filename,start,stop,pattern)

		return True, None

	def remove(self, fn, coord, value):
		""" """
		if fn not in self.map:
			raise Exception('Filename does not exist', fn)
		if coord in self.map[fn]:
			raise Exception('Adding coordinate multiple times Exception')
		del self.map[fn][coord]
		return True, None

	def scan(self):
		""" does an inorder scan of the coordinates and their values"""
		for fn in self.map:
			coords = self.map[fn].keys()
			coords.sort()
			for coord in coords:
				yield fn,coord,self.map[fn][coord]

	def keys(self):
		for fn in self.map:
			yield fn

	def filecoords(self, filename):
		""" 
			generator does an inorder scan of the coordinates for this file
		"""
		if filename not in self.map:
			return
			#raise Exception('Filename not found', filename)
		coords = sorted(self.map[filename].keys())
		for coord in coords:
			yield coord,self.map[filename][coord]

	def does_exist(self, filename, index):
		""" Simple check to see if this index is a hit (start of coordinates)"""
		if i in self.map[filename]:
			return True
		return False

	def does_overlap(self, filename, start, stop):
		""" Check if this coordinate overlaps with any existing range"""
		for i in range(start, stop):
			if i in self.map[filename]:
				return True
		return False

	def calc_overlap(self, filename, start, stop):
		""" given a set of coordinates, will calculate all overlaps 
			perf: stop after we know we won't hit any more
			perf: use binary search approach
		"""
		
		overlaps = []
		for s in self.map[filename]:
			e = self.map[filename][s]
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
		
		overlaps = []
		for s in self.map[filename]:
			e = self.map[filename][s]
			if start >= s and start <= e:
				#We found an overlap
				if stop >= e:
					overlaps.append({"orig_start":s, "orig_end":e, "new_start":s, "new_stop":stop})
				else:
					overlaps.append({"orig_start":s, "orig_end":e, "new_start":s, "new_stop":e})
				
			elif stop >= s and stop <= e:
				if start <= s:
					overlaps.append({"orig_start":s, "orig_end":e, "new_start":start, "new_stop":e})
				else:
					overlaps.append({"orig_start":s, "orig_end":e, "new_start":s, "new_stop":e})
				
		return overlaps


	def add_file(self, filename):
		""" add our fileto map, may not have any coordinates"""
		self.map[filename] = {}






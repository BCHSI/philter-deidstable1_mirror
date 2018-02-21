


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
			self.map[fn] = {}

		if not overlap:
			if coord in self.map[fn]:
				raise Exception('adding coordinate multiple times Exception', coord)

			for i in range(coord, coord+len(value)):
				if i in self.map[fn]:
					raise Exception('Overlapping coordinates found', coord, value)

		self.map[fn][coord] = value
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
			raise Exception('Filename not found', filename)
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





	def add_file(self, filename):
		""" add our fileto map, may not have any coordinates"""
		self.map[filename] = {}






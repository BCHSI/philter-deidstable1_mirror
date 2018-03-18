import numpy

class CoordinateMap:
	""" 
		Hits are stored in a coordinate map data structure
		This class stores start coordinates for any matches found for this pattern

	"""
	def __init__(self, pattern={"title":"untitled"}, debug=False):
		""" internal data structure maps filepaths to a map of int:string (coordinate start --> stop)

		map is the internal structure of 
	    { filename : { startcoordinate : stop_coordinate}}
	    eg: { "data/foo.txt": {123:126, 19:25} }


	    coord2pattern keeps reference of the patterns 
		that matched this coorinate (can be multiple patterns)

		all_coords keeps a reference of all coordinates mapped by filename, 
		allowing us to easily check if these coordinates have been matched yet

		"""
		self.map = {}
		self.coord2pattern = {} 
		self.pattern = pattern
		self.debug = debug
		self.all_coords = {} 

	def add(self, filename, start, stop, overlap=False, pattern=""):
		"""  adds a new coordinate to the coordinate map
			 if overlap is false, this will reject any overlapping hits (usually from multiple regex scan runs)
		"""
		if filename not in self.map:
			self.map***REMOVED***filename***REMOVED*** = {}

		if filename not in self.all_coords:
			self.all_coords***REMOVED***filename***REMOVED*** = {}

		if overlap == False:
			if self.does_overlap(filename, start, stop):
				return False, "Error, overlaps were found: {} {} {}".format(filename, start, stop)

		#add our start / stop coordinates
		self.map***REMOVED***filename***REMOVED******REMOVED***start***REMOVED*** = stop
		#add these coordinates to our all_coords map
		for i in range(start,stop):
			self.all_coords***REMOVED***filename***REMOVED******REMOVED***i***REMOVED*** = 1
		
		if pattern != "":
			self.add_pattern(filename, start, stop, pattern)
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
		# if filename == "./data/i2b2_notes/167-02.txt":
		
		if self.debug:
			print("add_extend", start, stop)

		if filename not in self.map:
			self.map***REMOVED***filename***REMOVED*** = {}
		overlaps = self.max_overlap(filename, start, stop)
		# if filename == "./data/i2b2_notes/167-02.txt":
		# 	print(self.map)
	
		def clear_overlaps(filename, lst):
			for o in lst:
				self.remove(filename, o***REMOVED***"orig_start"***REMOVED***, o***REMOVED***"orig_end"***REMOVED***)

		if len(overlaps) == 0:
			#no overlap, just save these coordinates
			self.add(filename,start,stop,pattern=pattern, overlap=True)
			# if filename == "./data/i2b2_notes/167-02.txt":
			# 	print("No overlaps:")
			# 	print(filename,start,stop,pattern)
		elif len(overlaps) == 1:
			clear_overlaps(filename, overlaps)	
			#1 overlap, save this value
			o = overlaps***REMOVED***0***REMOVED***
			self.add(filename,o***REMOVED***"new_start"***REMOVED***,o***REMOVED***"new_stop"***REMOVED***,pattern=pattern, overlap=True)
			# if filename == "./data/i2b2_notes/167-02.txt":
			# 	print("One overlap:")			
			# 	print(filename,start,stop,pattern)
		else:
			clear_overlaps(filename, overlaps)
			#greater than 1 overlap, by default this is sorted because of scan order
			o1 = overlaps***REMOVED***0***REMOVED***
			o2 = overlaps***REMOVED***-1***REMOVED***
			self.add(filename,o2***REMOVED***"new_start"***REMOVED***, o1***REMOVED***"new_stop"***REMOVED***,pattern=pattern, overlap=True)
			# if filename == "./data/i2b2_notes/167-02.txt":
			# 	print("Multiple overlaps:")			
			# 	print(filename,start,stop,pattern)

		return True, None

	def remove(self, filename, start, stop):
		""" Removes this coordinate pairing from the map, all_coords, and coord2pattern"""
		if filename not in self.map:
			raise Exception('Filename does not exist', filename)
		#delete from our map structure
		if start in self.map***REMOVED***filename***REMOVED***:
			del self.map***REMOVED***filename***REMOVED******REMOVED***start***REMOVED***
		#delete any of these coordinates in our all_coords data structure
		for i in range(start, stop+1):
			if i in self.all_coords:
				del self.all_coords***REMOVED***i***REMOVED***
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

	def get_coords(self, filename, start):
		stop = self.map***REMOVED***filename***REMOVED******REMOVED***start***REMOVED***
		return start,stop

	def filecoords(self, filename):
		""" 
			generator does an inorder scan of the coordinates for this file
		"""
		if filename not in self.map:
			return
			#raise Exception('Filename not found', filename)
		coords = sorted(self.map***REMOVED***filename***REMOVED***.keys())
		for coord in coords:
			yield coord,self.map***REMOVED***filename***REMOVED******REMOVED***coord***REMOVED***

	def does_exist(self, filename, index):
		""" Simple check to see if this index is a hit (start of coordinates)"""
		if index in self.map***REMOVED***filename***REMOVED***:
			return True
		return False

	def does_overlap(self, filename, start, stop):
		""" Check if this coordinate overlaps with any existing range"""
		for i in range(start, stop+1):
			if i in self.all_coords:
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
		self.map***REMOVED***filename***REMOVED*** = {}






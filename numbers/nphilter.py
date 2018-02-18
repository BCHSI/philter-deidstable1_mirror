
import re
import json
import os
import chardet

from chardet.universaldetector import UniversalDetector
from coordinate_map import CoordinateMap

class NPhilter:
    """ 
        General filtering class with a focus on numbers
    """

    def __init__(self, config):
        self.debug = config["debug"]
        self.finpath = config["finpath"]
        self.foutpath = config["foutpath"]

        #regex
        self.regexpatternfile = config["regex"]
        self.patterns = {"extract":[], "filter":[]} # filtration, extraction and other patterns
        self.compiled_patterns = {} #maps keyword to actual re compiled pattern object
        self.precompile()

        #data structures
        self.coord_maps = {
            'extract':CoordinateMap(),
            'filter':CoordinateMap(),
        }

    def precompile(self):
        """ precompiles our regex to speed up pattern matching"""
        extract_patterns = []
        rpf = json.load(open(self.regexpatternfile, "r"))
        for r in rpf["patterns"]:

            regex = open(r["regex"],"r").read().strip()
            if r["type"] not in self.patterns:
                self.patterns[r["type"]] = [regex]
            else:
                self.patterns[r["type"]].append(regex)

        print(self.patterns)

        #now compile these patterns
        for pat_type in self.patterns:
            regex_string = "|".join(self.patterns[pat_type])
            
            #check if this group type exists
            if pat_type in rpf["groups"]:
                prepend_regex = rpf["groups"][pat_type]["prepend_regex"]
                append_regex  = rpf["groups"][pat_type]["append_regex"]
                self.compiled_patterns[pat_type] = re.compile(prepend_regex+regex_string+append_regex)
            else:
                self.compiled_patterns[pat_type] = re.compile(regex_string)

            print(pat_type, self.compiled_patterns[pat_type])

    def mapcoords(self, task):
        """ Runs the set of regex on the input data 
            generating a coordinate map of hits given (dry run doesn't transform)
        """
        regex = self.compiled_patterns[task]

        if not os.path.exists(self.foutpath):
            os.makedirs(self.foutpath)

        for root, dirs, files in os.walk(self.finpath):
            for f in files:
                filename = root+f
                encoding = self.detect_encoding(root+f)
                txt = open(filename,"r", encoding=encoding['encoding']).read()
                
                #output_txt = re.sub(regex, ".", txt)
                for m in regex.finditer(txt):
                    #print(m.start(), m.group())
                    self.coord_maps[task].add(f, m.start(), m.group())

    def transform(self, coord_map=self.coord_map['extract'], replacement="**PHI{}**"):
        """ transform
            turns input files into output files 
            protected health information reduced to the replacement character

           
            replacement: the replacement string
        """
        for fn in coord_map.keys():
            with open(self.foutpath+filename, "w") as f:     
                contents = []
                for coord,val in coord_map.filecoords(filename):
                    contents.append(val)
                #inverse, we save only the coordinates
                f.write("**PHI**".join(contents))

    def detect_encoding(self, fp):
        detector = UniversalDetector()
        with open(fp, "rb") as f:
            for line in f:
                detector.feed(line)
                if detector.done: 
                    break
            detector.close()
        return detector.result

    def analyze(self):
        """ calculates the effectiveness of the philtering / extraction"""
        pass


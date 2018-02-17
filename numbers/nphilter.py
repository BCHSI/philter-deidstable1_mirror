
import re
import json
import os
import chardet

from chardet.universaldetector import UniversalDetector

class NPhilter:
    """ 
        General filtering class with a focus on numbers
    """

    def __init__(self, config):
        self.debug = config***REMOVED***"debug"***REMOVED***
        self.finpath = config***REMOVED***"finpath"***REMOVED***
        self.foutpath = config***REMOVED***"foutpath"***REMOVED***

        #regex
        self.regexpatternfile = config***REMOVED***"regex"***REMOVED***
        self.patterns = {"extract":***REMOVED******REMOVED***} # filtration, extraction and other patterns
        self.compiled_patterns = {} #maps keyword to actual re compiled pattern object
        self.precompile()

    def precompile(self):
        """ precompiles our regex to speed up pattern matching"""
        extract_patterns = ***REMOVED******REMOVED***
        rpf = json.load(open(self.regexpatternfile, "r"))
        for r in rpf***REMOVED***"patterns"***REMOVED***:

            regex = open(r***REMOVED***"regex"***REMOVED***,"r").read().strip()
            if r***REMOVED***"type"***REMOVED*** not in self.patterns:
                self.patterns***REMOVED***r***REMOVED***"type"***REMOVED******REMOVED*** = ***REMOVED***regex***REMOVED***
            else:
                self.patterns***REMOVED***r***REMOVED***"type"***REMOVED******REMOVED***.append(regex)

        print(self.patterns)

        #now compile these patterns
        for pat_type in self.patterns:
            regex_string = "|".join(self.patterns***REMOVED***pat_type***REMOVED***)
            
            #check if this group type exists
            if pat_type in rpf***REMOVED***"groups"***REMOVED***:
                prepend_regex = rpf***REMOVED***"groups"***REMOVED******REMOVED***pat_type***REMOVED******REMOVED***"prepend_regex"***REMOVED***
                append_regex  = rpf***REMOVED***"groups"***REMOVED******REMOVED***pat_type***REMOVED******REMOVED***"append_regex"***REMOVED***
                self.compiled_patterns***REMOVED***pat_type***REMOVED*** = re.compile(prepend_regex+regex_string+append_regex)
            else:
                self.compiled_patterns***REMOVED***pat_type***REMOVED*** = re.compile(regex_string)

            print(pat_type, self.compiled_patterns***REMOVED***pat_type***REMOVED***)
        
    def run(self, task):
        """ Runs the set of regex on the input data """
        regex = self.compiled_patterns***REMOVED***task***REMOVED***

        if not os.path.exists(self.foutpath):
            os.makedirs(self.foutpath)

        for root, dirs, files in os.walk(self.finpath):
            for f in files:
                encoding = self.detect_encoding(root+f)
                txt = open(root+f,"r", encoding=encoding***REMOVED***'encoding'***REMOVED***).read()
                
                #output_txt = re.sub(regex, ".", txt)
                for m in regex.finditer(txt):
                    print(m.start(), m.group())
                break

                # with open(self.foutpath+f, "w") as f:
                #   f.write(output_txt)

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
        """ calculates the effectiveness of the philtering"""
        pass


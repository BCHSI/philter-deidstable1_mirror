
import re
import json
import os
import nltk
import itertools
import chardet
import pickle
from chardet.universaldetector import UniversalDetector
from nltk.stem.wordnet import WordNetLemmatizer
from coordinate_map import CoordinateMap
from nltk.tag.stanford import StanfordNERTagger
import subprocess
import numpy


class Philter:
    """ 
        General text filtering class,
        can filter using whitelists, blacklists, regex's and POS
    """
    def __init__(self, config):
        if "debug" in config:
            self.debug = config***REMOVED***"debug"***REMOVED***
        if "errorcheck" in config:
            self.errorcheck = config***REMOVED***"errorcheck"***REMOVED***
        if "parallel" in config:
            self.parallel = config***REMOVED***"parallel"***REMOVED***
        if "freq_table" in config:
            self.freq_table = config***REMOVED***"freq_table"***REMOVED***                       
        if "finpath" in config:
            if not os.path.exists(config***REMOVED***"finpath"***REMOVED***):
                raise Exception("Filepath does not exist", config***REMOVED***"finpath"***REMOVED***)
            self.finpath = config***REMOVED***"finpath"***REMOVED***
        if "foutpath" in config:
            if not os.path.exists(config***REMOVED***"foutpath"***REMOVED***):
                raise Exception("Filepath does not exist", config***REMOVED***"foutpath"***REMOVED***)
            self.foutpath = config***REMOVED***"foutpath"***REMOVED***
        if "anno_folder" in config:
            if not os.path.exists(config***REMOVED***"anno_folder"***REMOVED***):
                raise Exception("Filepath does not exist", config***REMOVED***"foutpath"***REMOVED***)
            self.anno_folder = config***REMOVED***"anno_folder"***REMOVED***

        if "outformat" in config:
            self.outformat = config***REMOVED***"outformat"***REMOVED***
        else:
            raise Exception("Output format undefined")
        
        if "ucsfformat" in config:
            self.ucsf_format = config***REMOVED***"ucsfformat"***REMOVED***
       
        if "filters" in config:
            if not os.path.exists(config***REMOVED***"filters"***REMOVED***):
                raise Exception("Filepath does not exist", config***REMOVED***"filters"***REMOVED***)
            self.patterns = json.loads(open(config***REMOVED***"filters"***REMOVED***, "r").read())

        if "xml" in config:
            if not os.path.exists(config***REMOVED***"xml"***REMOVED***):
                raise Exception("Filepath does not exist", config***REMOVED***"xml"***REMOVED***)
            self.xml = json.loads(open(config***REMOVED***"xml"***REMOVED***, "r").read())

        if "stanford_ner_tagger" in config:
            if not os.path.exists(config***REMOVED***"stanford_ner_tagger"***REMOVED******REMOVED***"classifier"***REMOVED***) and config***REMOVED***"stanford_ner_tagger"***REMOVED******REMOVED***"download"***REMOVED*** == False:
                raise Exception("Filepath does not exist", config***REMOVED***"stanford_ner_tagger"***REMOVED******REMOVED***"classifier"***REMOVED***)
            else:
                #download the ner data
                process = subprocess.Popen("cd generate_dataset && ./download_ner.sh".split(), stdout=subprocess.PIPE)
                output, error = process.communicate()
            self.stanford_ner_tagger_classifier = config***REMOVED***"stanford_ner_tagger"***REMOVED******REMOVED***"classifier"***REMOVED***
            if not os.path.exists(config***REMOVED***"stanford_ner_tagger"***REMOVED******REMOVED***"jar"***REMOVED***):
                raise Exception("Filepath does not exist", config***REMOVED***"stanford_ner_tagger"***REMOVED******REMOVED***"jar"***REMOVED***)
            self.stanford_ner_tagger_jar = config***REMOVED***"stanford_ner_tagger"***REMOVED******REMOVED***"jar"***REMOVED***
                #we lazy load our tagger only if there's a corresponding pattern

      
        self.stanford_ner_tagger = None

        #All coordinate maps stored here
        self.coordinate_maps = ***REMOVED******REMOVED***

        #initialize our patterns
        self.init_patterns()


    def init_patterns(self):
        """ given our input pattern config will load our sets and pre-compile our regex"""

        known_pattern_types = set(***REMOVED***"regex", "set", "stanford_ner", "pos_matcher", "match_all"***REMOVED***)
        require_files = set(***REMOVED***"regex", "set"***REMOVED***)
        require_pos = set(***REMOVED***"pos_matcher"***REMOVED***)
        set_filetypes = set(***REMOVED***"pkl", "json"***REMOVED***)
        regex_filetypes = set(***REMOVED***"txt"***REMOVED***)
        reserved_list = set(***REMOVED***"data", "coordinate_map"***REMOVED***)

        #first check that data is formatted, can be loaded etc. 
        for i,pattern in enumerate(self.patterns):

            if pattern***REMOVED***"type"***REMOVED*** in require_files and not os.path.exists(pattern***REMOVED***"filepath"***REMOVED***):
                raise Exception("Config filepath does not exist", pattern***REMOVED***"filepath"***REMOVED***)
            for k in reserved_list:
                if k in pattern:
                    raise Exception("Error, Keyword is reserved", k, pattern)
            if pattern***REMOVED***"type"***REMOVED*** not in known_pattern_types:
                raise Exception("Pattern type is unknown", pattern***REMOVED***"type"***REMOVED***)
            if pattern***REMOVED***"type"***REMOVED*** == "set":
                if pattern***REMOVED***"filepath"***REMOVED***.split(".")***REMOVED***-1***REMOVED*** not in set_filetypes:
                    raise Exception("Invalid filteype", pattern***REMOVED***"filepath"***REMOVED***, "must be of", set_filetypes)
                self.patterns***REMOVED***i***REMOVED******REMOVED***"data"***REMOVED*** = self.init_set(pattern***REMOVED***"filepath"***REMOVED***)  
            elif pattern***REMOVED***"type"***REMOVED*** == "regex":
                if pattern***REMOVED***"filepath"***REMOVED***.split(".")***REMOVED***-1***REMOVED*** not in regex_filetypes:
                    raise Exception("Invalid filteype", pattern***REMOVED***"filepath"***REMOVED***, "must be of", regex_filetypes)
                self.patterns***REMOVED***i***REMOVED******REMOVED***"data"***REMOVED*** = self.precompile(pattern***REMOVED***"filepath"***REMOVED***)
                #print(self.precompile(pattern***REMOVED***"filepath"***REMOVED***))
    def precompile(self, filepath):
        """ precompiles our regex to speed up pattern matching"""
        regex = open(filepath,"r").read().strip()
        return re.compile(regex)
               
    def init_set(self, filepath):
        """ loads a set of words, (must be a dictionary or set shape) returns result"""
        map_set = {}
        if filepath.endswith(".pkl"):
            try:
                with open(filepath, "rb") as pickle_file:
                    map_set = pickle.load(pickle_file)
            except UnicodeDecodeError:
                with open(filepath, "rb") as pickle_file:
                    map_set = pickle.load(pickle_file, encoding = 'latin1')
        elif filepath.endswith(".json"):
            map_set = json.loads(open(filepath, "r").read())

        else:
            raise Exception("Invalid filteype",filepath)
        return map_set

    def map_coordinates(self, in_path="", allowed_filetypes=set(***REMOVED***"txt", "ano"***REMOVED***)):
        """ Runs the set, or regex on the input data 
            generating a coordinate map of hits given 
            (this performs a dry run on the data and doesn't transform)
        """

        if not os.path.exists(in_path):
            raise Exception("Filepath does not exist", in_path)
        
        #create coordinate maps for each pattern
        for i,pat in enumerate(self.patterns):
            self.patterns***REMOVED***i***REMOVED******REMOVED***"coordinate_map"***REMOVED*** = CoordinateMap()

        for root, dirs, files in os.walk(in_path):
            for f in files:

                filename = root+f

                if filename.split(".")***REMOVED***-1***REMOVED*** not in allowed_filetypes:
                    if self.debug and self.parallel == False:
                        print("Skipping: ", filename)
                    continue                
                #self.patterns***REMOVED***i***REMOVED******REMOVED***"coordinate_map"***REMOVED***.add_file(filename)

                encoding = self.detect_encoding(filename)
                txt = open(filename,"r", encoding=encoding***REMOVED***'encoding'***REMOVED***).read()

                # if self.debug:
                #     print("Transforming", pat)

                for i,pat in enumerate(self.patterns):
                    if pat***REMOVED***"type"***REMOVED*** == "regex":
                        self.map_regex(filename=filename, text=txt, pattern_index=i)
                    elif pat***REMOVED***"type"***REMOVED*** == "set":
                        self.map_set(filename=filename, text=txt, pattern_index=i)
                    elif pat***REMOVED***"type"***REMOVED*** == "stanford_ner":
                        self.map_ner(filename=filename, text=txt, pattern_index=i)
                    elif pat***REMOVED***"type"***REMOVED*** == "pos_matcher":
                        self.map_pos(filename=filename, text=txt, pattern_index=i)
                    elif pat***REMOVED***"type"***REMOVED*** == "match_all":
                        self.match_all(filename=filename, text=txt, pattern_index=i)
                    else:
                        raise Exception("Error, pattern type not supported: ", pat***REMOVED***"type"***REMOVED***)

        #clear out any data to save ram
        for i,pat in enumerate(self.patterns):
            if "data" in pat:
                del self.patterns***REMOVED***i***REMOVED******REMOVED***"data"***REMOVED***

                
    def map_regex(self, filename="", text="", pattern_index=-1, pre_process= r"***REMOVED***^a-zA-Z0-9\.***REMOVED***"):
        """ Creates a coordinate map from the pattern on this data
            generating a coordinate map of hits given (dry run doesn't transform)
        """
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))
        coord_map = self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED***
        regex = self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"data"***REMOVED***

        # All regexes except matchall
        if regex != re.compile('.'):
            matches = regex.finditer(text)
            
            for m in matches:
                # if filename == './data/i2b2_notes/312-04.txt':
                #     print(m)
                coord_map.add_extend(filename, m.start(), m.start()+len(m.group()))
        
            self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED*** = coord_map
        
        #### MATCHALL ####
        elif regex == re.compile('.'):
         
            # Split note the same way we would split for set or POS matching

            matchall_list = re.split("(\s+)", text)
            matchall_list_cleaned = ***REMOVED******REMOVED***
            for item in matchall_list:
                if len(item) > 0:
                    if item.isspace() == False:
                        split_item = re.split("(\s+)", re.sub(pre_process, " ", item))
                        for elem in split_item:
                            if len(elem) > 0:
                                matchall_list_cleaned.append(elem)
                    else:
                        matchall_list_cleaned.append(item)

            start_coordinate = 0
            for word in matchall_list_cleaned:
                start = start_coordinate
                stop = start_coordinate + len(word)
                word_clean = re.sub(r"***REMOVED***^a-zA-Z0-9***REMOVED***+", "", word.lower().strip())
                if len(word_clean) == 0:
                    #got a blank space or something without any characters or digits, move forward
                    start_coordinate += len(word)
                    continue

                if regex.match(word_clean):
                    coord_map.add_extend(filename, start, stop)
                    
                #advance our start coordinate
                start_coordinate += len(word)

            self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED*** = coord_map



    def match_all(self, filename="", text="", pattern_index=-1):
        """ Simply maps to the entirety of the file """
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))

        coord_map = self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED***
        #add the entire length of the file
        coord_map.add(filename, 0, len(text))
        print(0, len(text))
        self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED*** = coord_map


    def map_set(self, filename="", text="", pattern_index=-1,  pre_process= r"***REMOVED***^a-zA-Z0-9\.***REMOVED***"):
        """ Creates a coordinate mapping of words any words in this set"""
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))

        map_set = self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"data"***REMOVED***
        coord_map = self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED***
        
        #get part of speech we will be sending through this set
        #note, if this is empty we will put all parts of speech through the set
        check_pos = False
        pos_set = set(***REMOVED******REMOVED***)
        if "pos" in self.patterns***REMOVED***pattern_index***REMOVED***:
            pos_set = set(self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"pos"***REMOVED***)
        if len(pos_set) > 0:
            check_pos = True

        # Use pre-process to split sentence by spaces AND symbols, while preserving spaces in the split list
        lst = re.split("(\s+)", text)
        cleaned = ***REMOVED******REMOVED***
        for item in lst:
            if len(item) > 0:
                if item.isspace() == False:
                    split_item = re.split("(\s+)", re.sub(pre_process, " ", item))
                    for elem in split_item:
                        if len(elem) > 0:
                            cleaned.append(elem)
                else:
                    cleaned.append(item)

        pos_list = nltk.pos_tag(cleaned)
        # if filename == './data/i2b2_notes/160-03.txt':
        #     print(pos_list)
        start_coordinate = 0
        for tup in pos_list:
            word = tup***REMOVED***0***REMOVED***
            pos  = tup***REMOVED***1***REMOVED***
            start = start_coordinate
            stop = start_coordinate + len(word)

            # This converts spaces into empty strings, so we know to skip forward to the next real word
            word_clean = re.sub(r"***REMOVED***^a-zA-Z0-9***REMOVED***+", "", word.lower().strip())
            if len(word_clean) == 0:
                #got a blank space or something without any characters or digits, move forward
                start_coordinate += len(word)
                continue

            if check_pos == False or (check_pos == True and pos in pos_set):
                # if word == 'exlap':
                #     print(pos)
                #     print(filename)
                #     print(pos_set)
                #     print(check_pos)

                if word_clean in map_set or word in map_set:
                    coord_map.add_extend(filename, start, stop)
                    #print("FOUND: ",word, "COORD: ",  text***REMOVED***start:stop***REMOVED***)
                else:
                    #print("not in set: ",word, "COORD: ",  text***REMOVED***start:stop***REMOVED***)
                    #print(word_clean)
                    pass
                    
            #advance our start coordinate
            start_coordinate += len(word)

        self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED*** = coord_map

    def map_pos(self, filename="", text="", pattern_index=-1, pre_process= r"***REMOVED***^a-zA-Z0-9\.***REMOVED***"):
        """ Creates a coordinate mapping of words which match this part of speech (POS)"""
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))

        if "pos" not in self.patterns***REMOVED***pattern_index***REMOVED***:
            raise Exception("Mapping POS must include parts of speech", pattern_index, "pattern length", len(patterns))
            
        coord_map = self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED***
        pos_set = set(self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"pos"***REMOVED***)
        
        # Use pre-process to split sentence by spaces AND symbols, while preserving spaces in the split list
        lst = re.split("(\s+)", text)
        cleaned = ***REMOVED******REMOVED***
        for item in lst:
            if len(item) > 0:
                if item.isspace() == False:
                    split_item = re.split("(\s+)", re.sub(pre_process, " ", item))
                    for elem in split_item:
                        if len(elem) > 0:
                            cleaned.append(elem)
                else:
                    cleaned.append(item)

        pos_list = nltk.pos_tag(cleaned)
        # if filename == './data/i2b2_notes/160-03.txt':
        #     print(pos_list)
        start_coordinate = 0
        for tup in pos_list:
            word = tup***REMOVED***0***REMOVED***
            pos  = tup***REMOVED***1***REMOVED***
            start = start_coordinate
            stop = start_coordinate + len(word)
            word_clean = re.sub(r"***REMOVED***^a-zA-Z0-9***REMOVED***+", "", word.lower().strip())
            if len(word_clean) == 0:
                #got a blank space or something without any characters or digits, move forward
                start_coordinate += len(word)
                continue

            if pos in pos_set:    
                coord_map.add_extend(filename, start, stop)
                #print("FOUND: ",word,"POS",pos, "COORD: ",  text***REMOVED***start:stop***REMOVED***)
                
            #advance our start coordinate
            start_coordinate += len(word)

        self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED*** = coord_map

    def map_ner(self, filename="", text="", pattern_index=-1, pre_process= r"***REMOVED***^a-zA-Z0-9***REMOVED***+"):
        """ map NER tagging"""
      
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))

        #load and create an NER tagger if it doesn't exist
        if self.stanford_ner_tagger == None:
            classifier_path = self.stanford_ner_tagger_classifier #'/usr/local/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz'
            jar_path = self.stanford_ner_tagger_jar #'/usr/local/stanford-ner/stanford-ner.jar'     
            self.stanford_ner_tagger = StanfordNERTagger(classifier_path,jar_path)
        
        coord_map = self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED***
        pos_set = set(***REMOVED******REMOVED***)
        if "pos" in self.patterns***REMOVED***pattern_index***REMOVED***:
            pos_set = set(self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"pos"***REMOVED***)
        if len(pos_set) > 0:
            check_pos = True

        lst = re.split("(\s+)", text)
        cleaned = ***REMOVED******REMOVED***
        for item in lst:
            if len(item) > 0:
                cleaned.append(item)
        
        ner_no_spaces = self.stanford_ner_tagger.tag(cleaned)
        #get our ner tags
        ner_set = {}
        for tup in ner_no_spaces:
            ner_set***REMOVED***tup***REMOVED***0***REMOVED******REMOVED*** = tup***REMOVED***1***REMOVED***
        ner_set_with_locations = {}
        start_coordinate = 0
        for w in cleaned:
            if w in ner_set:
                ner_set_with_locations***REMOVED***w***REMOVED*** = (ner_set***REMOVED***w***REMOVED***, start_coordinate)
            start_coordinate += len(w)


        #for the text, break into words and mark POS
        #with the parts of speech labeled, match any of these to our coordinate
        #add these coordinates to our coordinate map
        start_coordinate = 0
        for word in cleaned:

            word_clean = re.sub(pre_process, "", word.lower().strip())
            if len(word_clean) == 0:
                #got a blank space or something without any characters or digits, move forward
                start_coordinate += len(word)
                continue
            
            if word in ner_set_with_locations:
                ner_tag = ner_set_with_locations***REMOVED***word***REMOVED******REMOVED***0***REMOVED***
                start = ner_set_with_locations***REMOVED***word***REMOVED******REMOVED***1***REMOVED***
                if ner_tag in pos_set:
                    stop = start + len(word)
                    coord_map.add_extend(filename, start, stop)
                    print("FOUND: ",word, "NER: ", ner_tag, start, stop)
            
                    
            #advance our start coordinate
            start_coordinate += len(word)

        self.patterns***REMOVED***pattern_index***REMOVED******REMOVED***"coordinate_map"***REMOVED*** = coord_map

    def folder_walk(self, folder):
        """ utility func will make a generator to walk a folder
            returns root_directory,filename

            for example: 
            foo/, bar001.txt
            foo/, bar002.txt

        """
        for root, dirs, files in os.walk(folder):
            for filename in files:
                yield root,filename

    def transform(self, 
            replacement=" **PHI** ",
            out_path="",
            in_path=""):
        """ transform
            turns input files into output PHI files 
            protected health information will be replaced by the replacement character

            transform the data 
            ORDER: Order is preserved prioritiy, 
            patterns at spot 0 will have priority over patterns at index 2 

            **Anything not caught in these passes will be assumed to be PHI
        """
        
        if self.debug and self.parallel == False:
            print("running transform")

        if not os.path.exists(in_path):
            raise Exception("File input path does not exist", in_path)
        
        if not os.path.exists(out_path):
            raise Exception("File output path does not exist", out_path)


        #keeps a record of all phi coordinates and text
        data = {}

        #create our final exclude and include maps, priority order
        for root,f in self.folder_walk(in_path):

            filename = root+f

            encoding = self.detect_encoding(filename)
            txt = open(filename,"r", encoding=encoding***REMOVED***'encoding'***REMOVED***).read()
            #record we use to evaluate our effectiveness
            data***REMOVED***filename***REMOVED*** = {"text":txt, "phi":***REMOVED******REMOVED***,"non-phi":***REMOVED******REMOVED***}

            #create an intersection map of all coordinates we'll be removing
            exclude_map = CoordinateMap()

            exclude_map.add_file(filename)

            #create an interestion map of all coordinates we'll be keeping
            include_map = CoordinateMap()

            include_map.add_file(filename)
            for i,pattern in enumerate(self.patterns):
                coord_map = pattern***REMOVED***"coordinate_map"***REMOVED***
                exclude = pattern***REMOVED***"exclude"***REMOVED***

                for start,stop in coord_map.filecoords(filename):
                    if exclude:
                        if not include_map.does_overlap(filename, start, stop):
                            exclude_map.add_extend(filename, start, stop)
                            data***REMOVED***filename***REMOVED******REMOVED***"phi"***REMOVED***.append({"start":start, "stop":stop, "word":txt***REMOVED***start:stop***REMOVED***})
                    else:
                        if not exclude_map.does_overlap(filename, start, stop):
                            #print("include", start, stop, txt***REMOVED***start:stop***REMOVED***)
                            include_map.add_extend(filename, start, stop)
                            data***REMOVED***filename***REMOVED******REMOVED***"non-phi"***REMOVED***.append({"start":start, "stop":stop, "word":txt***REMOVED***start:stop***REMOVED***})
                        else:
                            pass
                            #print("include overlapped", start, stop, txt***REMOVED***start:stop***REMOVED***)

            #now we transform the text
            fbase, fext = os.path.splitext(f)
            outpathfbase = out_path + fbase
            if self.outformat == "asterisk":
                with open(outpathfbase+".txt", "w") as f:
                    contents = self.transform_text_asterisk(txt, filename, 
                                                            include_map,
                                                            exclude_map)
                    f.write(contents)
                    
            elif self.outformat == "i2b2":
                with open(outpathfbase+".xml", "w") as f:
                    contents = self.transform_text_i2b2(data***REMOVED***filename***REMOVED***)
                    f.write(contents)
            else:
                raise Exception("Outformat not supported: ",
                                self.outformat)
                

        if self.debug: #output our data for eval
            json.dump(data, open("./data/coordinates.json", "w"), indent=4)

    # infilename needed for addressing maps
    def transform_text_asterisk(self, txt, infilename,
                                include_map, exclude_map):
        last_marker = 0
        current_chunk = ***REMOVED******REMOVED***
        punctuation_matcher = re.compile(r"***REMOVED***^a-zA-Z0-9****REMOVED***")

        #read the text by character, any non-punc non-overlaps will be replaced
        contents = ***REMOVED******REMOVED***
        for i in range(0, len(txt)):

            if i < last_marker:
                continue
            
            if include_map.does_exist(infilename, i):
                #add our preserved text
                start,stop = include_map.get_coords(infilename, i)
                contents.append(txt***REMOVED***start:stop***REMOVED***)
                last_marker = stop
            elif punctuation_matcher.match(txt***REMOVED***i***REMOVED***):
                contents.append(txt***REMOVED***i***REMOVED***)
            else:
                contents.append("*")

        return "".join(contents)

    def transform_text_i2b2(self, tagdata):
        """creates a string in i2b2-XML format"""
        root = "Philter"
        contents = ***REMOVED******REMOVED***
        
        contents.append("<?xml version=\"1.0\" ?>\n")
        contents.append("<"+root+">\n")
        contents.append("<TEXT><!***REMOVED***CDATA***REMOVED***")
        contents.append(tagdata***REMOVED***'text'***REMOVED***)
        contents.append("***REMOVED******REMOVED***></TEXT>\n")
        contents.append("<TAGS>\n")
        for i in range(len(tagdata***REMOVED***'phi'***REMOVED***)):
            tagcategory = "OTHER" # TODO: replace with actual category
            phitype = "OTHER" # TODO: replace with actual phi type
            contents.append("<")
            contents.append(phitype)
            contents.append(" id=\"P")
            contents.append(str(i))
            contents.append("\" start=\"")
            contents.append(str(tagdata***REMOVED***'phi'***REMOVED******REMOVED***i***REMOVED******REMOVED***'start'***REMOVED***))
            contents.append("\" end=\"")
            contents.append(str(tagdata***REMOVED***'phi'***REMOVED******REMOVED***i***REMOVED******REMOVED***'stop'***REMOVED***))
            contents.append("\" text=\"")
            contents.append(tagdata***REMOVED***'phi'***REMOVED******REMOVED***i***REMOVED******REMOVED***'word'***REMOVED***)
            contents.append("\" TYPE=\"")
            contents.append(phitype)
            contents.append("\" comment=\"\" />\n")
        contents.append("</TAGS>\n")
        contents.append("</"+root+">\n")
        
        return "".join(contents)
                
    def detect_encoding(self, fp):
        if not os.path.exists(fp):
            raise Exception("Filepath does not exist", fp)

        detector = UniversalDetector()
        with open(fp, "rb") as f:
            for line in f:
                detector.feed(line)
                if detector.done: 
                    break
            detector.close()
        return detector.result

    def phi_context(self, filename, word, word_index, words, context_window=10):
        """ helper function, creates our phi data type with source file, and context window"""
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        left_index = word_index - context_window
        if left_index < 0:
            left_index = 0

        right_index = word_index + context_window
        if right_index >= len(words):
            right_index = len(words) - 1
        window = words***REMOVED***left_index:right_index***REMOVED***

        #get which patterns matched this word
        num_spaces = len(words***REMOVED***:word_index***REMOVED***)
        

        return {"filename":filename, "phi":word, "context":window}


    def seq_eval(self,
            note_lst, 
            anno_lst, 
            punctuation_matcher=re.compile(r"***REMOVED***^a-zA-Z0-9*\.***REMOVED***"), 
            text_matcher=re.compile(r"***REMOVED***a-zA-Z0-9***REMOVED***"), 
            phi_matcher=re.compile(r"\*+")):
        """ 
            Compares two sequences item by item, 
            returns generator which yields: 
            classifcation, word

            classifications can be TP, FP, FN, TN 
            corresponding to True Positive, False Positive, False Negative and True Negative
        """
        

        start_coordinate = 0
        for note_word, anno_word in list(zip(note_lst, anno_lst)):
            #print(note_word, anno_word)
            ##### Get coordinates ######
            start = start_coordinate
            stop = start_coordinate + len(note_word)
            note_word_stripped = re.sub(r"***REMOVED***^a-zA-Z0-9\*\.***REMOVED***+", "", note_word.strip())
            anno_word_stripped = re.sub(r"***REMOVED***^a-zA-Z0-9\*\.***REMOVED***+", "", anno_word.strip())
            if len(note_word_stripped) == 0:
                #got a blank space or something without any characters or digits, move forward
                start_coordinate += len(note_word)
                continue

            
            if phi_matcher.search(anno_word):
                #this contains phi
                
                if note_word == anno_word:
                    yield "TP", note_word, start_coordinate

                else:
                    if text_matcher.search(anno_word):

                        #print("COMPLEX", note_word, anno_word)

                        #this is a complex edge case, 
                        #the phi annotation has some characters *'ed, and some not, 
                        #find the overlap and report any string of chars in anno as FP
                        #and any string of chars in note as FN
                        fn_words = ***REMOVED******REMOVED***
                        fp_words = ***REMOVED******REMOVED***

                        fn_chunk = ***REMOVED******REMOVED***
                        fp_chunk = ***REMOVED******REMOVED***
                        for n,a in list(zip(note_word, anno_word)):
                            if n == a:
                                #these characters match, clear our chunks
                                if len(fp_chunk) > 0:
                                    fp_words.append("".join(fp_chunk))
                                    fp_chunk = ***REMOVED******REMOVED***
                                if len(fn_chunk) > 0:
                                    fn_words.append("".join(fn_words))
                                    fn_chunk = ***REMOVED******REMOVED***
                                
                                continue 
                            if a == "*" and n != "*":
                                fn_chunk.append(n)
                            elif a != "*" and n == "*":
                                fp_chunk.append(a)

                        #clear any remaining chunks
                        if len(fp_chunk) > 0:
                            fp_words.append("".join(fp_chunk))
                        if len(fn_chunk) > 0:
                            fn_words.append("".join(fn_words))

                        #now drain the difference
                        for w in fn_words:
                            yield "FN", w, start_coordinate
                        for w in fp_words:
                            yield "FP", w, start_coordinate

                    else:
                        #simpler case, anno word is completely blocked out except punctuation
                        yield "FN", note_word, start_coordinate

            else:
                if note_word.isspace() == False:
                    #this isn't phi
                    if note_word == anno_word:
                        #print(note_word, anno_word, "TN")
                        yield "TN", note_word, start_coordinate
                    else:
                        #print(note_word, anno_word, "FP")
                        yield "FP", anno_word, start_coordinate

            #advance our start coordinate
            start_coordinate += len(note_word) 


    def eval(self,
        config,
        anno_path="data/i2b2_anno/",
        anno_suffix="_phi_reduced.ano", 
        in_path="data/i2b2_results/",
        summary_output="data/phi/summary.json",
        phi_matcher=re.compile("\*+"),
        only_digits=False,
        fn_output="data/phi/fn.json",
        fp_output="data/phi/fp.json",
        fn_tags_context = "data/phi/fn_tags_context.txt",
        fp_tags_context = "data/phi/fp_tags_context.txt",
        fn_tags_nocontext = "data/phi/fn_tags.txt",
        fp_tags_nocontext = "data/phi/fp_tags.txt",
        pre_process=r":|\,|\-|\/|_|~", #characters we're going to strip from our notes to analyze against anno        
        pre_process2= r"***REMOVED***^a-zA-Z0-9***REMOVED***",
        punctuation_matcher=re.compile(r"***REMOVED***^a-zA-Z0-9\*\.***REMOVED***")):
        """ calculates the effectiveness of the philtering / extraction

            only_digits = <boolean> will constrain evaluation on philtering of only digit types
        """

        if not os.path.exists(anno_path):
            raise Exception("Anno Filepath does not exist", anno_path)
        if not os.path.exists(in_path):
            raise Exception("Input Filepath does not exist", in_path)
        if not os.path.exists(fn_output):
            raise Exception("False Negative Filepath does not exist", fn_output)
        if not os.path.exists(fp_output):
            raise Exception("False Positive Filepath does not exist", fp_output)
        if self.debug and self.parallel == False:
            print("eval")
        
        summary = {
            "total_false_positives":0,
            "total_false_negatives":0,
            "total_true_positives": 0,
            "total_true_negatives": 0,
            "false_positives":***REMOVED******REMOVED***, #non-phi words we think are phi
            "true_positives": ***REMOVED******REMOVED***, #phi words we correctly identify
            "false_negatives":***REMOVED******REMOVED***, #phi words we think are non-phi
            "true_negatives": ***REMOVED******REMOVED***, #non-phi words we correctly identify
            "summary_by_file":{}
        }
        summary_coords = {
            "summary_by_file":{}
        }

        all_fn = ***REMOVED******REMOVED***
        all_fp = ***REMOVED******REMOVED***

        for root, dirs, files in os.walk(in_path):

            for f in files:
                if not f.endswith(".txt"): # TODO: come up with something better
                    continue               #       to ensure one to one txt file
                                           #       comparisons with anno_path
                #local values per file
                false_positives = ***REMOVED******REMOVED*** #non-phi we think are phi
                false_positives_coords = ***REMOVED******REMOVED***
                true_positives  = ***REMOVED******REMOVED*** #phi we correctly identify
                true_positives_coords = ***REMOVED******REMOVED***
                false_negatives = ***REMOVED******REMOVED*** #phi we think are non-phi
                false_negatives_coords = ***REMOVED******REMOVED***
                true_negatives  = ***REMOVED******REMOVED*** #non-phi we correctly identify
                true_negatives_coords = ***REMOVED******REMOVED***

                philtered_filename = root+f
                anno_filename = anno_path+''.join(f.split(".")***REMOVED***0***REMOVED***)+anno_suffix

                # if len(anno_suffix) > 0:
                #     anno_filename = anno_folder+f.split(".")***REMOVED***0***REMOVED***+anno_suffix

                if not os.path.exists(philtered_filename):
                    raise Exception("FILE DOESNT EXIST", philtered_filename)
                
                if not os.path.exists(anno_filename):
                    #print("FILE DOESNT EXIST", anno_filename)
                    continue

                encoding1 = self.detect_encoding(philtered_filename)
                philtered = open(philtered_filename,"r", encoding=encoding1***REMOVED***'encoding'***REMOVED***).read()
                
                          
                philtered_words = re.split("(\s+)", philtered)
                # if f == '110-01.txt':
                #     print(philtered_words)
                #     print(len("".join(philtered_words)))
                philtered_words_cleaned = ***REMOVED******REMOVED***
                for item in philtered_words:
                    if len(item) > 0:
                        if item.isspace() == False:
                            split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                            for elem in split_item:
                                if len(elem) > 0:
                                    philtered_words_cleaned.append(elem)
                        else:
                            philtered_words_cleaned.append(item)
                
                encoding2 = self.detect_encoding(anno_filename)
                anno = open(anno_filename,"r", encoding=encoding2***REMOVED***'encoding'***REMOVED***).read()              
                
                anno_words = re.split("(\s+)", anno)
                # if f == '110-01.txt':
                #     print(anno_words)
                #     print(len("".join(anno_words)))
                anno_words_cleaned = ***REMOVED******REMOVED***
                for item in anno_words:
                    if len(item) > 0:
                        if item.isspace() == False:
                            split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                            for elem in split_item:
                                if len(elem) > 0:
                                    anno_words_cleaned.append(elem)
                        else:
                            anno_words_cleaned.append(item)

                for c,w,r in self.seq_eval(philtered_words_cleaned, anno_words_cleaned):

                    # Double check that we aren't adding blank spaces or single punctionation characters to our lists
                    if w.isspace() == False and (re.sub(r"***REMOVED***^a-zA-Z0-9\****REMOVED***+", "", w) != ""):

                        if c == "FP":
                            false_positives.append(w)
                            false_positives_coords.append(***REMOVED***w,r***REMOVED***)
                            # if w == "she" or w == "no" or w == "he" or w == "increased" or w == "wave" or w == "In" or w == "AS":
                            #     print(w)
                            #     print(f)

                        elif c == "FN":
                            false_negatives.append(w)
                            false_negatives_coords.append(***REMOVED***w,r***REMOVED***)
                        elif c == "TP":
                            true_positives.append(w)
                            true_positives_coords.append(***REMOVED***w,r***REMOVED***)
                        elif c == "TN":
                            true_negatives.append(w)
                            true_negatives_coords.append(***REMOVED***w,r***REMOVED***)

                #update summary
                summary***REMOVED***"summary_by_file"***REMOVED******REMOVED***philtered_filename***REMOVED*** = {"false_positives":false_positives,"false_negatives":false_negatives, "num_false_negatives":len(false_negatives)}
                summary***REMOVED***"total_true_positives"***REMOVED*** = summary***REMOVED***"total_true_positives"***REMOVED*** + len(true_positives)
                summary***REMOVED***"total_false_positives"***REMOVED*** = summary***REMOVED***"total_false_positives"***REMOVED*** + len(false_positives)
                summary***REMOVED***"total_false_negatives"***REMOVED*** = summary***REMOVED***"total_false_negatives"***REMOVED*** + len(false_negatives)
                summary***REMOVED***"total_true_negatives"***REMOVED*** = summary***REMOVED***"total_true_negatives"***REMOVED*** + len(true_negatives)
                all_fp = all_fp + false_positives
                all_fn = all_fn + false_negatives


                # Create coordinate summaries
                summary_coords***REMOVED***"summary_by_file"***REMOVED******REMOVED***philtered_filename***REMOVED*** = {"false_positives":false_positives_coords,"false_negatives":false_negatives_coords}


        if summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_negatives"***REMOVED*** > 0:
            recall = summary***REMOVED***"total_true_positives"***REMOVED***/(summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_negatives"***REMOVED***)
        elif summary***REMOVED***"total_false_negatives"***REMOVED*** == 0:
            recall = 1.0

        if summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_positives"***REMOVED*** > 0:
            precision = summary***REMOVED***"total_true_positives"***REMOVED***/(summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_positives"***REMOVED***)
        elif summary***REMOVED***"total_true_positives"***REMOVED*** == 0:
            precision = 0.0

        if summary***REMOVED***"total_true_negatives"***REMOVED***+summary***REMOVED***"total_false_positives"***REMOVED*** > 0:
            retention = summary***REMOVED***"total_true_negatives"***REMOVED***/(summary***REMOVED***"total_true_negatives"***REMOVED***+summary***REMOVED***"total_false_positives"***REMOVED***)
        else:
            retention = 0.0
        
        if self.debug and self.parallel == False:
            #save the phi we missed
            json.dump(summary, open(summary_output, "w"), indent=4)
            json.dump(all_fn, open(fn_output, "w"), indent=4)
            json.dump(all_fp, open(fp_output, "w"), indent=4)
            
            print("true_negatives", summary***REMOVED***"total_true_negatives"***REMOVED***,"true_positives", summary***REMOVED***"total_true_positives"***REMOVED***, "false_negatives", summary***REMOVED***"total_false_negatives"***REMOVED***, "false_positives", summary***REMOVED***"total_false_positives"***REMOVED***)
            print("Global Recall: {:.2%}".format(recall))
            print("Global Precision: {:.2%}".format(precision))
            print("Global Retention: {:.2%}".format(retention))

        ###################### Get phi tags #####################
        if self.errorcheck and self.parallel == False:
            print("error checking")
        if self.errorcheck:
            # Get xml summary
            phi = self.xml
            # Create dictionary to hold fn tags
            fn_tags = {}
            fp_tags = {}
            # Keep track of recall and precision for each category
            rp_summaries = {
                "names_fns": 0,
                "names_tps": 0, 
                "dates_fns":0,
                "dates_tps":0,
                "id_fns":0,
                "id_tps":0,
                "contact_fns":0,
                "contact_tps":0,
                "location_fns":0,
                "location_tps":0,
                "organization_fns":0,
                "organization_tps":0,
                "age_fns":0,
                "age_tps":0
                # "profession_fns":0,
                # "profession_tps":0              
            }
            # Create dictionaries for unigram and bigram PHI/non-PHI frequencies
            # Diciontary values look like: ***REMOVED***phi_count, non-phi_count***REMOVED***
            unigram_dict = {}
            bigram_dict = {}

            # Loop through all filenames in summary
            for fn in summary_coords***REMOVED***'summary_by_file'***REMOVED***:
                
                current_summary =  summary_coords***REMOVED***'summary_by_file'***REMOVED******REMOVED***fn***REMOVED***

                # Get corresponding info in phi_notes
                note_name = fn.split('/')***REMOVED***3***REMOVED***
                anno_name = note_name.split('.')***REMOVED***0***REMOVED*** + ".xml"


                text = phi***REMOVED***anno_name***REMOVED******REMOVED***'text'***REMOVED***
                lst = re.split("(\s+)", text)
                cleaned = ***REMOVED******REMOVED***
                cleaned_coords = ***REMOVED******REMOVED***
                for item in lst:
                    if len(item) > 0:
                        if item.isspace() == False:
                            split_item = re.split("(\s+)", re.sub(r"***REMOVED***^a-zA-Z0-9\.***REMOVED***", " ", item))
                            for elem in split_item:
                                if len(elem) > 0:
                                    cleaned.append(elem)
                        else:
                            cleaned.append(item)
             
                # Get coords for POS tags
                start_coordinate = 0
                pos_coords = ***REMOVED******REMOVED***
                for item in cleaned:
                    pos_coords.append(start_coordinate)
                    start_coordinate += len(item)

                pos_list = nltk.pos_tag(cleaned)


                cleaned_with_pos = {}
                for i in range(0,len(pos_list)):
                    cleaned_with_pos***REMOVED***str(pos_coords***REMOVED***i***REMOVED***)***REMOVED*** = ***REMOVED***pos_list***REMOVED***i***REMOVED******REMOVED***0***REMOVED***, pos_list***REMOVED***i***REMOVED******REMOVED***1***REMOVED******REMOVED***

                ########## Get FN tags ##########
                phi_list = phi***REMOVED***anno_name***REMOVED******REMOVED***'phi'***REMOVED***
                # print(cleaned)
                # print(pos_coords)


                ######### Create unigram and bigram frequency tables #######
                if self.freq_table:

                    # Create separate cleaned list/coord list without spaces
                    cleaned_nospaces = ***REMOVED******REMOVED***
                    coords_nospaces = ***REMOVED******REMOVED***
                    for i in range(0,len(cleaned)):
                        if cleaned***REMOVED***i***REMOVED***.isspace() == False:
                            cleaned_nospaces.append(cleaned***REMOVED***i***REMOVED***)
                            coords_nospaces.append(pos_coords***REMOVED***i***REMOVED***)

                    # Loop through all single words and word pairs, and compare with PHI list
                    for i in range(0,len(cleaned_nospaces)-1):
                        #cleaned_nospaces***REMOVED***i***REMOVED***= word, coords_nospaces***REMOVED***i***REMOVED*** = start coordinate
                        unigram_word = cleaned_nospaces***REMOVED***i***REMOVED***.replace('\n','').replace('\t','').replace(' ','').lower()
                        bigram_word = " ".join(***REMOVED***cleaned_nospaces***REMOVED***i***REMOVED***.replace('\n','').replace('\t','').replace(' ','').lower(),cleaned_nospaces***REMOVED***i+1***REMOVED***.replace('\n','').replace('\t','').replace(' ','').lower()***REMOVED***)
                        unigram_start = coords_nospaces***REMOVED***i***REMOVED***
                        bigram_start1 = coords_nospaces***REMOVED***i***REMOVED***
                        bigram_start2 = coords_nospaces***REMOVED***i+1***REMOVED***

                        # Loop through PHI list and compare ranges
                        for phi_item in phi_list:
                            phi_start = phi_item***REMOVED***'start'***REMOVED***
                            phi_end = phi_item***REMOVED***'end'***REMOVED***
                            if unigram_start in range(int(phi_start), int(phi_end)):
                                # This word is PHI and hasn't been added to the dictionary yet
                                if unigram_word not in unigram_dict:
                                    unigram_dict***REMOVED***unigram_word***REMOVED*** = ***REMOVED***1, 0***REMOVED***
                               # This word is PHI and has already been added to the dictionary
                                else:
                                    unigram_dict***REMOVED***unigram_word***REMOVED******REMOVED***0***REMOVED*** += 1
                            else:
                                # This word is not PHI and hasn't been aded to the dictionary yet
                                if unigram_word not in unigram_dict:
                                    unigram_dict***REMOVED***unigram_word***REMOVED*** = ***REMOVED***0, 1***REMOVED***
                               # This word is not PHI and has already been added to the dictionary
                                else:
                                    unigram_dict***REMOVED***unigram_word***REMOVED******REMOVED***1***REMOVED*** += 1                               
                            if bigram_start1 in range(int(phi_start), int(phi_end)) and bigram_start2 in range(int(phi_start), int(phi_end)):
                                # This word is PHI and hasn't been added to the dictionary yet
                                if bigram_word not in bigram_dict:
                                    bigram_dict***REMOVED***bigram_word***REMOVED*** = ***REMOVED***1, 0***REMOVED***
                               # This word is PHI and has already been added to the dictionary
                                else:
                                    bigram_dict***REMOVED***bigram_word***REMOVED******REMOVED***0***REMOVED*** += 1                                
                            else:
                                # This word is not PHI and hasn't been aded to the dictionary yet
                                if bigram_word not in bigram_dict:
                                    bigram_dict***REMOVED***bigram_word***REMOVED*** = ***REMOVED***0, 1***REMOVED***
                               # This word is not PHI and has already been added to the dictionary
                                else:
                                    bigram_dict***REMOVED***bigram_word***REMOVED******REMOVED***1***REMOVED*** += 1



                # Get tokenized PHI list and number of PHI for each category
                names_cleaned = ***REMOVED******REMOVED***
                dates_cleaned = ***REMOVED******REMOVED***
                ids_cleaned = ***REMOVED******REMOVED***
                contact_cleaned = ***REMOVED******REMOVED***
                locations_cleaned = ***REMOVED******REMOVED***
                organizations_cleaned =***REMOVED******REMOVED***
                age_cleaned =***REMOVED******REMOVED***

                for phi_dict in phi_list:
                    # Names
                    if phi_dict***REMOVED***'TYPE'***REMOVED*** == 'DOCTOR' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'PATIENT' or phi_dict***REMOVED***'TYPE'***REMOVED*** == "Patient_Name_or_Family_Member_Name" or phi_dict***REMOVED***'TYPE'***REMOVED*** == "Provider_Name":
                        lst = re.split("(\s+)", phi_dict***REMOVED***'text'***REMOVED***)
                        for item in lst:
                            if len(item) > 0:
                                if item.isspace() == False:
                                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                                    for elem in split_item:
                                        if len(elem) > 0:
                                            names_cleaned.append(elem)
                                else:
                                    names_cleaned.append(item)
                    # Dates
                    if phi_dict***REMOVED***'TYPE'***REMOVED*** == 'DATE' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'Date':
                        lst = re.split("(\s+)", phi_dict***REMOVED***'text'***REMOVED***)
                        for item in lst:
                            if len(item) > 0:
                                if item.isspace() == False:
                                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                                    for elem in split_item:
                                        if len(elem) > 0:
                                            dates_cleaned.append(elem)
                                else:
                                    dates_cleaned.append(item)
                    # IDs
                    if phi_dict***REMOVED***'TYPE'***REMOVED*** == 'MEDICALRECORD' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'IDNUM' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'DEVICE' or phi_dict***REMOVED***'TYPE'***REMOVED*** == "URL_IP" or phi_dict***REMOVED***'TYPE'***REMOVED*** == "Social_Security" or phi_dict***REMOVED***'TYPE'***REMOVED*** == "Medical_Record_ID" or phi_dict***REMOVED***'TYPE'***REMOVED*** == "Account_Number" or phi_dict***REMOVED***'TYPE'***REMOVED*** == "Certificate_or_License" or phi_dict***REMOVED***'TYPE'***REMOVED*** == "Vehicle_or_Device_ID" or phi_dict***REMOVED***'TYPE'***REMOVED*** == "Unique_Patient_Id" or phi_dict***REMOVED***'TYPE'***REMOVED*** == "Biometric_ID_or_Face_Photo":
                        lst = re.split("(\s+)", phi_dict***REMOVED***'text'***REMOVED***)
                        for item in lst:
                            if len(item) > 0:
                                if item.isspace() == False:
                                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                                    for elem in split_item:
                                        if len(elem) > 0:
                                            ids_cleaned.append(elem)
                                else:
                                    ids_cleaned.append(item) 

                    # Contact info                    
                    if phi_dict***REMOVED***'TYPE'***REMOVED*** == 'USERNAME' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'PHONE' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'EMAIL' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'FAX' or phi_dict***REMOVED***'TYPE'***REMOVED*** == "Phone_Fax" or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'Email':
                        lst = re.split("(\s+)", phi_dict***REMOVED***'text'***REMOVED***)
                        for item in lst:
                            if len(item) > 0:
                                if item.isspace() == False:
                                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                                    for elem in split_item:
                                        if len(elem) > 0:
                                            contact_cleaned.append(elem)
                                else:
                                    contact_cleaned.append(item)           

                    # Locations                    
                    if phi_dict***REMOVED***'TYPE'***REMOVED*** == 'CITY' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'STATE' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'ZIP' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'STREET' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'LOCATION-OTHER' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'Address':
                        lst = re.split("(\s+)", phi_dict***REMOVED***'text'***REMOVED***)
                        for item in lst:
                            if len(item) > 0:
                                if item.isspace() == False:
                                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                                    for elem in split_item:
                                        if len(elem) > 0:
                                            locations_cleaned.append(elem)
                                else:
                                    locations_cleaned.append(item)  


                    # Organizations                    
                    if phi_dict***REMOVED***'TYPE'***REMOVED*** == 'HOSPITAL':
                        lst = re.split("(\s+)", phi_dict***REMOVED***'text'***REMOVED***)
                        for item in lst:
                            if len(item) > 0:
                                if item.isspace() == False:
                                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                                    for elem in split_item:
                                        if len(elem) > 0:
                                            organizations_cleaned.append(elem)
                                else:
                                    organizations_cleaned.append(item)                
                
                    # Age >90                    
                    if phi_dict***REMOVED***'TYPE'***REMOVED*** == 'AGE' or phi_dict***REMOVED***'TYPE'***REMOVED*** == 'Age':
                        lst = re.split("(\s+)", phi_dict***REMOVED***'text'***REMOVED***)
                        for item in lst:
                            if len(item) > 0:
                                if item.isspace() == False:
                                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                                    for elem in split_item:
                                        if len(elem) > 0:
                                            age_cleaned.append(elem)
                                else:
                                    age_cleaned.append(item)                  


                fn_tag_summary = {}
                names_fn_counter = 0
                dates_fn_counter = 0
                id_fn_counter = 0
                contact_fn_counter = 0
                location_fn_counter = 0
                organization_fn_counter = 0
                age_fn_counter = 0
                #profession_fn_counter = 0

                if current_summary***REMOVED***'false_negatives'***REMOVED*** != ***REMOVED******REMOVED*** and current_summary***REMOVED***'false_negatives'***REMOVED*** != ***REMOVED***""***REMOVED***:              
                    counter = 0
                    current_fns = current_summary***REMOVED***'false_negatives'***REMOVED***

                    for word in current_fns:
                        counter += 1
                        false_negative = word***REMOVED***0***REMOVED***
                        start_coordinate_fn = word***REMOVED***1***REMOVED***
                      
                        for phi_item in phi_list:                           
                            phi_text = phi_item***REMOVED***'text'***REMOVED***
                            phi_type = phi_item***REMOVED***'TYPE'***REMOVED***
                            phi_id = phi_item***REMOVED***'id'***REMOVED***
                            if self.ucsf_format:
                                phi_start = int(phi_item***REMOVED***'spans'***REMOVED***.split('~')***REMOVED***0***REMOVED***)
                                phi_end = int(phi_item***REMOVED***'spans'***REMOVED***.split('~')***REMOVED***1***REMOVED***)                               
                            else:
                                phi_start = phi_item***REMOVED***'start'***REMOVED***
                                phi_end = phi_item***REMOVED***'end'***REMOVED***

                            # Names FNs
                            if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == "DOCTOR" or phi_type == "PATIENT" or phi_type == "Patient_Name_or_Family_Member_Name" or phi_type == "Provider_Name"):
                                rp_summaries***REMOVED***"names_fns"***REMOVED*** += 1
                                names_fn_counter += 1

                            # Dates FNs
                            if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == "DATE" or phi_type == 'Date'):
                                rp_summaries***REMOVED***"dates_fns"***REMOVED*** += 1
                                dates_fn_counter += 1


                            # ID FNs
                            if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == "MEDICALRECORD" or phi_type == "IDNUM" or phi_type == "DEVICE" or phi_type == "URL_IP" or phi_type == "Social_Security" or phi_type == "Medical_Record_ID" or phi_type == "Account_Number" or phi_type == "Certificate_or_License" or phi_type == "Vehicle_or_Device_ID" or phi_type == "Unique_Patient_Id" or phi_type == "Biometric_ID_or_Face_Photo"):
                                rp_summaries***REMOVED***"id_fns"***REMOVED*** += 1
                                id_fn_counter += 1

                            # Contact FNs
                            if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == "USERNAME" or phi_type == "PHONE" or phi_type == "EMAIL" or phi_type == "FAX" or phi_type == "Phone_Fax" or phi_type == 'Email'):
                                rp_summaries***REMOVED***"contact_fns"***REMOVED*** += 1
                                contact_fn_counter += 1 
                            
                            # Location FNs
                            if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == 'CITY' or phi_type == 'STATE' or phi_type == 'ZIP' or phi_type == 'STREET' or phi_type == 'LOCATION-OTHER' or phi_type == 'Address'):
                                rp_summaries***REMOVED***"location_fns"***REMOVED*** += 1
                                location_fn_counter += 1                               

                            # Organization FNs
                            if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == 'HOSPITAL'):
                                rp_summaries***REMOVED***"organization_fns"***REMOVED*** += 1
                                organization_fn_counter += 1  

                            # Age FNs
                            if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == 'AGE' or phi_type == 'Age'):
                                rp_summaries***REMOVED***"age_fns"***REMOVED*** += 1
                                age_fn_counter += 1 
                                # print(word) 
                            
                            # profession FNs
                            # if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == 'PROFESSION'):
                            #     rp_summaries***REMOVED***"profession_fns"***REMOVED*** += 1
                            #     profession_fn_counter += 1  

                            # Find PHI match: fn in text, coord in range
                            if start_coordinate_fn in range(int(phi_start), int(phi_end)):
                                # Get PHI tag
                                phi_tag = phi_type
                                # Get POS tag
                                pos_tag = cleaned_with_pos***REMOVED***str(start_coordinate_fn)***REMOVED******REMOVED***1***REMOVED***
                                
                                # Get 15 characters surrounding FN on either side
                                fn_context = ''
                                context_start = start_coordinate_fn - 15
                                context_end = start_coordinate_fn + len(false_negative) + 15
                                if context_start >= 0 and context_end <= len(text)-1:
                                    fn_context = text***REMOVED***context_start:context_end***REMOVED***
                                elif context_start >= 0 and context_end > len(text)-1:
                                    fn_context = text***REMOVED***context_start:***REMOVED***
                                else:
                                    fn_context = text***REMOVED***:context_end***REMOVED***
                                # if fn == './data/i2b2_results/137-03.txt':
                                #     print(fn_context)                  
                                
                                # Get fn id, to distinguish betweem multiple entries
                                fn_id = "N" + str(counter)
                                ###### Create output dicitonary with id/word/pos/phi
                                fn_tag_summary***REMOVED***fn_id***REMOVED*** = ***REMOVED***false_negative, phi_tag, pos_tag, fn_context***REMOVED***
                                # if phi_tag == 'AGE':
                                #     print(word)
                 
                if fn_tag_summary != {}:
                    fn_tags***REMOVED***fn***REMOVED*** = fn_tag_summary

                # Update recall/precision dictionary
                rp_summaries***REMOVED***'names_tps'***REMOVED*** += (len(names_cleaned) - names_fn_counter)
                rp_summaries***REMOVED***'dates_tps'***REMOVED*** += (len(dates_cleaned) - dates_fn_counter)
                rp_summaries***REMOVED***'id_tps'***REMOVED*** += (len(ids_cleaned) - id_fn_counter)
                rp_summaries***REMOVED***'contact_tps'***REMOVED*** += (len(contact_cleaned) - contact_fn_counter)
                rp_summaries***REMOVED***'location_tps'***REMOVED*** += (len(locations_cleaned) - location_fn_counter)
                rp_summaries***REMOVED***'organization_tps'***REMOVED*** += (len(organizations_cleaned) - organization_fn_counter)
                rp_summaries***REMOVED***'age_tps'***REMOVED*** += (len(age_cleaned) - age_fn_counter)
                #rp_summaries***REMOVED***'profession_tps'***REMOVED*** += (len(profession_cleaned) - profession_fn_counter)

                ####### Get FP tags #########
                fp_tag_summary = {}

                if current_summary***REMOVED***'false_positives'***REMOVED*** != ***REMOVED******REMOVED*** and current_summary***REMOVED***'false_positives'***REMOVED*** != ***REMOVED***""***REMOVED***:              

                    current_fps = current_summary***REMOVED***'false_positives'***REMOVED***
                    counter = 0
                    for word in current_fps:
                        counter += 1
                        false_positive = word***REMOVED***0***REMOVED***
                        start_coordinate_fp = word***REMOVED***1***REMOVED***
                     
                        pos_entry = cleaned_with_pos***REMOVED***str(start_coordinate_fp)***REMOVED***

                        pos_tag = pos_entry***REMOVED***1***REMOVED***

                        # Get 15 characters surrounding FP on either side
                        fp_context = ''
                        context_start = start_coordinate_fp - 15
                        context_end = start_coordinate_fp + len(false_positive) + 15
                        if context_start >= 0 and context_end <= len(text)-1:
                            fp_context = text***REMOVED***context_start:context_end***REMOVED***
                        elif context_start >= 0 and context_end > len(text)-1:
                            fp_context = text***REMOVED***context_start:***REMOVED***
                        else:
                            fp_context = text***REMOVED***:context_end***REMOVED***


                        fp_id = "P" + str(counter)
                        fp_tag_summary***REMOVED***fp_id***REMOVED*** = ***REMOVED***false_positive, pos_tag, fp_context***REMOVED***

                if fp_tag_summary != {}:
                    fp_tags***REMOVED***fn***REMOVED*** = fp_tag_summary
            
            # Create frequency table outputs
            if self.freq_table:
                # Unigram table
                with open('./data/phi/unigram_freq_table.csv','w') as f:
                    f.write('unigram,phi_count,non-phi_count\n')
                    for key in unigram_dict:
                        word = key
                        phi_count = unigram_dict***REMOVED***key***REMOVED******REMOVED***0***REMOVED***
                        non_phi_count = unigram_dict***REMOVED***key***REMOVED******REMOVED***1***REMOVED***
                        f.write(word + ',' + str(phi_count) + ',' + str(non_phi_count) + '\n')
                with open('./data/phi/bigranm_freq_table.csv','w') as f:
                    f.write('bigram,phi_count,non-phi_count\n')
                    for key in bigram_dict:
                        term = key
                        phi_count = bigram_dict***REMOVED***key***REMOVED******REMOVED***0***REMOVED***
                        non_phi_count = bigram_dict***REMOVED***key***REMOVED******REMOVED***1***REMOVED***
                        f.write(term + ',' + str(phi_count) + ',' + str(non_phi_count) + '\n')

            
            # Get names recall
            if rp_summaries***REMOVED***'names_tps'***REMOVED*** != 0:
                names_recall = (rp_summaries***REMOVED***'names_tps'***REMOVED***-rp_summaries***REMOVED***'names_fns'***REMOVED***)/rp_summaries***REMOVED***'names_tps'***REMOVED***
            if (rp_summaries***REMOVED***'names_tps'***REMOVED***-rp_summaries***REMOVED***'names_fns'***REMOVED***) < 0 or rp_summaries***REMOVED***'names_tps'***REMOVED*** == 0:
                names_recall = 0
            
            # Get dates recall
            if rp_summaries***REMOVED***'dates_tps'***REMOVED*** != 0:
                dates_recall = (rp_summaries***REMOVED***'dates_tps'***REMOVED***-rp_summaries***REMOVED***'dates_fns'***REMOVED***)/rp_summaries***REMOVED***'dates_tps'***REMOVED***
            if (rp_summaries***REMOVED***'dates_tps'***REMOVED***-rp_summaries***REMOVED***'dates_fns'***REMOVED***) < 0 or rp_summaries***REMOVED***'dates_tps'***REMOVED*** == 0:
                dates_recall = 0            
            
            # Get ids recall
            if rp_summaries***REMOVED***'id_tps'***REMOVED*** != 0:
                ids_recall = (rp_summaries***REMOVED***'id_tps'***REMOVED***-rp_summaries***REMOVED***'id_fns'***REMOVED***)/rp_summaries***REMOVED***'id_tps'***REMOVED***
            if (rp_summaries***REMOVED***'id_tps'***REMOVED***-rp_summaries***REMOVED***'id_fns'***REMOVED***) < 0 or rp_summaries***REMOVED***'id_tps'***REMOVED*** == 0:
                ids_recall = 0            
            
            # Get contact recall
            if rp_summaries***REMOVED***'contact_tps'***REMOVED*** != 0:
                contact_recall = (rp_summaries***REMOVED***'contact_tps'***REMOVED***-rp_summaries***REMOVED***'contact_fns'***REMOVED***)/rp_summaries***REMOVED***'contact_tps'***REMOVED***
            if (rp_summaries***REMOVED***'contact_tps'***REMOVED***-rp_summaries***REMOVED***'contact_fns'***REMOVED***) < 0 or rp_summaries***REMOVED***'contact_tps'***REMOVED*** == 0:
                contact_recall = 0            
            
            # Get location recall
            if rp_summaries***REMOVED***'location_tps'***REMOVED*** != 0:
                location_recall = (rp_summaries***REMOVED***'location_tps'***REMOVED***-rp_summaries***REMOVED***'location_fns'***REMOVED***)/rp_summaries***REMOVED***'location_tps'***REMOVED***
            if (rp_summaries***REMOVED***'location_tps'***REMOVED***-rp_summaries***REMOVED***'location_fns'***REMOVED***) < 0 or rp_summaries***REMOVED***'location_tps'***REMOVED*** == 0:
                location_recall = 0
            
            # Get organization recall
            if rp_summaries***REMOVED***'organization_tps'***REMOVED*** != 0:
                organization_recall = (rp_summaries***REMOVED***'organization_tps'***REMOVED***-rp_summaries***REMOVED***'organization_fns'***REMOVED***)/rp_summaries***REMOVED***'organization_tps'***REMOVED***
            if (rp_summaries***REMOVED***'organization_tps'***REMOVED***-rp_summaries***REMOVED***'organization_fns'***REMOVED***) < 0 or rp_summaries***REMOVED***'organization_tps'***REMOVED*** == 0:
                organization_recall = 0             
            

            # Get age recall
            if rp_summaries***REMOVED***'age_tps'***REMOVED*** != 0:
                age_recall = (rp_summaries***REMOVED***'age_tps'***REMOVED***-rp_summaries***REMOVED***'age_fns'***REMOVED***)/rp_summaries***REMOVED***'age_tps'***REMOVED***
            if age_recall < 0 or rp_summaries***REMOVED***'age_tps'***REMOVED*** == 0:
                age_recall = 0 
            

            # Print to terminal
            print("Names Recall: " + "{:.2%}".format(names_recall))
            print("Dates Recall: " + "{:.2%}".format(dates_recall))
            print("IDs Recall: " + "{:.2%}".format(ids_recall))
            print("Contact Recall: " + "{:.2%}".format(contact_recall))
            print("Location Recall: " + "{:.2%}".format(location_recall))
            print("Organization Recall: " + "{:.2%}".format(organization_recall))
            print("Age>=90 Recall: " + "{:.2%}".format(age_recall))
            # print("Profession Recall: " + "{:.2%}".format(profession_recall))

            ######## Summarize FN results #########
            
            ##### With and without context #####
            
            # With context:
            # Condensed tags will contain id, word, PHI tag, POS tag, occurrences
            fn_tags_condensed_context = {}
            # Stores lists that represent distinct groups of words, PHI and POS tags
            fn_tags_condensed_list_context = ***REMOVED******REMOVED***
            
            # No context:
            # Condensed tags will contain id, word, PHI tag, POS tag, occurrences
            fn_tags_condensed = {}
            # Stores lists that represent distinct groups of words, PHI and POS tags
            fn_tags_condensed_list = ***REMOVED******REMOVED***

            # Keep track of how many distinct combinations we've added to each list
            context_counter = 0
            nocontext_counter = 0
            for fn in fn_tags:
                file_dict = fn_tags***REMOVED***fn***REMOVED*** 
                for subfile in file_dict:
                    current_list_context = file_dict***REMOVED***subfile***REMOVED***
                    current_list_nocontext = current_list_context***REMOVED***:3***REMOVED***
                    
                    word = current_list_context***REMOVED***0***REMOVED***
                    phi_tag = current_list_context***REMOVED***1***REMOVED***
                    pos_tag = current_list_context***REMOVED***2***REMOVED***
                    fn_context = current_list_context***REMOVED***3***REMOVED***.replace("\n"," ")
                    #Context
                    if current_list_context not in fn_tags_condensed_list_context:                      
                        fn_tags_condensed_list_context.append(current_list_context)
                        key_name = "uniq" + str(context_counter)
                        fn_tags_condensed_context***REMOVED***key_name***REMOVED*** = ***REMOVED***word, phi_tag, pos_tag, fn_context, 1***REMOVED***
                        context_counter += 1
                    else:
                        uniq_id_index = fn_tags_condensed_list_context.index(current_list_context)
                        uniq_id = "uniq" + str(uniq_id_index)
                        fn_tags_condensed_context***REMOVED***uniq_id***REMOVED******REMOVED***4***REMOVED*** += 1

                    # No context
                    if current_list_nocontext not in fn_tags_condensed_list:   
                        fn_tags_condensed_list.append(current_list_nocontext)
                        key_name = "uniq" + str(nocontext_counter)
                        fn_tags_condensed***REMOVED***key_name***REMOVED*** = ***REMOVED***word, phi_tag, pos_tag, 1***REMOVED***
                        nocontext_counter += 1
                    else: 
                        uniq_id_index = fn_tags_condensed_list.index(current_list_nocontext)
                        uniq_id = "uniq" + str(uniq_id_index)
                        fn_tags_condensed***REMOVED***uniq_id***REMOVED******REMOVED***3***REMOVED*** += 1

            ####### Summariz FP results #######

            # With context
            # Condensed tags will contain id, word, POS tag, occurrences
            fp_tags_condensed_context = {}
            # Stores lists that represent distinct groups of wordss and POS tags
            fp_tags_condensed_list_context = ***REMOVED******REMOVED***

            # No context
            # Condensed tags will contain id, word, POS tag, occurrences
            fp_tags_condensed = {}
            # Stores lists that represent distinct groups of wordss and POS tags
            fp_tags_condensed_list = ***REMOVED******REMOVED***

            # Keep track of how many distinct combinations we've added to each list
            context_counter = 0
            nocontext_counter = 0
            for fp in fp_tags:
                file_dict = fp_tags***REMOVED***fp***REMOVED*** 
                for subfile in file_dict:
                    current_list_context = file_dict***REMOVED***subfile***REMOVED***
                    current_list_nocontext = current_list_context***REMOVED***:2***REMOVED***

                    word = current_list_context***REMOVED***0***REMOVED***
                    pos_tag = current_list_context***REMOVED***1***REMOVED***
                    fp_context = current_list_context***REMOVED***2***REMOVED***.replace("\n"," ")

                    # Context
                    if current_list_context not in fp_tags_condensed_list_context:
                        fp_tags_condensed_list_context.append(current_list_context)
                        key_name = "uniq" + str(context_counter)
                        fp_tags_condensed_context***REMOVED***key_name***REMOVED*** = ***REMOVED***word, pos_tag, fp_context, 1***REMOVED***
                        context_counter += 1
                    else:
                        uniq_id_index = fp_tags_condensed_list_context.index(current_list_context)
                        uniq_id = "uniq" + str(uniq_id_index)
                        fp_tags_condensed_context***REMOVED***uniq_id***REMOVED******REMOVED***3***REMOVED*** += 1          

                    # No Context
                    if current_list_nocontext not in fp_tags_condensed_list:
                        fp_tags_condensed_list.append(current_list_nocontext)
                        key_name = "uniq" + str(nocontext_counter)
                        fp_tags_condensed***REMOVED***key_name***REMOVED*** = ***REMOVED***word, pos_tag, 1***REMOVED***
                        nocontext_counter += 1
                    else:
                        uniq_id_index = fp_tags_condensed_list.index(current_list_nocontext)
                        uniq_id = "uniq" + str(uniq_id_index)
                        fp_tags_condensed***REMOVED***uniq_id***REMOVED******REMOVED***2***REMOVED*** += 1 

            # Write FN and FP results to outfolder
            # Conext
            with open(fn_tags_context, "w") as fn_file:
                fn_file.write("key" + "|" + "note_word" + "|" + "phi_tag" + "|" + "pos_tag" + "|" + "context" + "|" + "occurrences"+"\n")
                for key in fn_tags_condensed_context:
                    current_list = fn_tags_condensed_context***REMOVED***key***REMOVED***
                    fn_file.write(key + "|" + current_list***REMOVED***0***REMOVED*** + "|" + current_list***REMOVED***1***REMOVED*** + "|" + current_list***REMOVED***2***REMOVED*** + "|" + current_list***REMOVED***3***REMOVED*** + "|" + str(current_list***REMOVED***4***REMOVED***)+"\n")
            
            with open(fp_tags_context, "w") as fp_file:
                fp_file.write("key" + "|" + "note_word" + "|" + "pos_tag" + "|" + "context" + "|" + "occurrences"+"\n")
                for key in fp_tags_condensed_context:
                    current_list = fp_tags_condensed_context***REMOVED***key***REMOVED***
                    fp_file.write(key + "|" + current_list***REMOVED***0***REMOVED*** + "|" + current_list***REMOVED***1***REMOVED***  + "|" +  current_list***REMOVED***2***REMOVED*** + "|" + str(current_list***REMOVED***3***REMOVED***)+"\n")

            # No context
            with open(fn_tags_nocontext, "w") as fn_file:
                fn_file.write("key" + "|" + "note_word" + "|" + "phi_tag" + "|" + "pos_tag" + "|" + "occurrences"+"\n")
                for key in fn_tags_condensed:
                    current_list = fn_tags_condensed***REMOVED***key***REMOVED***
                    fn_file.write(key + "|" + current_list***REMOVED***0***REMOVED*** + "|" + current_list***REMOVED***1***REMOVED*** + "|" + current_list***REMOVED***2***REMOVED*** + "|" + str(current_list***REMOVED***3***REMOVED***)+"\n")
            
            with open(fp_tags_nocontext, "w") as fp_file:
                fp_file.write("key" + "|" + "note_word" + "|" + "pos_tag" + "|" + "occurrences"+"\n")
                for key in fp_tags_condensed:
                    current_list = fp_tags_condensed***REMOVED***key***REMOVED***
                    fp_file.write(key + "|" + current_list***REMOVED***0***REMOVED*** + "|" + current_list***REMOVED***1***REMOVED***  + "|" +  str(current_list***REMOVED***2***REMOVED***)+"\n")            
            
            if self.parallel:
                # Get info on whitelist, blacklist, POS
                patterns = json.loads(open(config***REMOVED***"filters"***REMOVED***, "r").read())
                current_whitelist = ''
                current_blacklist = ''
                current_pos = ''
                for config_dict in patterns:
                    if config_dict***REMOVED***'type'***REMOVED*** == 'set' and config_dict***REMOVED***'exclude'***REMOVED*** == True:
                        current_blacklist = config_dict***REMOVED***'filepath'***REMOVED***.split('/')***REMOVED***-1***REMOVED***.split('.')***REMOVED***0***REMOVED***
                        current_pos = str(config_dict***REMOVED***'pos'***REMOVED***).replace(" ","")
                    if config_dict***REMOVED***'type'***REMOVED*** == 'set' and config_dict***REMOVED***'exclude'***REMOVED*** == False:
                        current_whitelist = config_dict***REMOVED***'filepath'***REMOVED***.split('/')***REMOVED***-1***REMOVED***.split('.')***REMOVED***0***REMOVED***
                
                print(current_whitelist + " " + current_blacklist + " " + current_pos + " " + "{:.2%}".format(names_recall) + " " + "{:.2%}".format(dates_recall) + " "+ "{:.2%}".format(ids_recall) + " "+ "{:.2%}".format(contact_recall) + " "+ "{:.2%}".format(location_recall) + " " + "{:.2%}".format(precision) + " " + "{:.2%}".format(retention))
    
    def getphi(self, 
            anno_folder="data/i2b2_anno/", 
            anno_suffix="_phi_reduced.ano", 
            data_folder="data/i2b2_notes/", 
            output_folder="i2b2_phi", 
            filter_regex=None):
        """ get's phi from existing data to build up a data model
        data structure to hold our phi and classify phi we find
            {
                "foo.txt":***REMOVED***
                    {
                        "phi":"1/1/2019",
                        "context":"The data was 1/1/2019 and the patient was happy",
                        "class":"numer" //number, string ... 
                    },...
                ***REMOVED***,...
            }
        """
        if self.debug:
            print("getphi")


        #use config if exists
        if self.anno_folder != None:
            anno_folder = self.anno_folder

        if self.anno_suffix != "":
            anno_suffix = self.anno_suffix

        phi = {}
        word_counts = {}
        not_phi = {}
        window_size = 10 #amount of words surrounding word to grab

        for root, dirs, files in os.walk(data_folder):
           
            for f in files:
               
                if not os.path.exists(root+f):
                    raise Exception("FILE DOESNT EXIST", root+f)

                if len(anno_suffix) > 0:
                    if not os.path.exists(anno_folder+f.split(".")***REMOVED***0***REMOVED***+anno_suffix):
                        print("FILE DOESNT EXIST", anno_folder+f.split(".")***REMOVED***0***REMOVED***+anno_suffix)
                        continue
                else:
                    if not os.path.exists(anno_folder+f):
                        print("FILE DOESNT EXIST", anno_folder+f)
                        continue

                orig_filename = root+f
                encoding1 = self.detect_encoding(orig_filename)
                orig = open(orig_filename,"r", encoding=encoding1***REMOVED***'encoding'***REMOVED***).read()

                orig_words = re.split("\s+", orig)

                anno_filename = anno_folder+f.split(".")***REMOVED***0***REMOVED***+anno_suffix
                encoding2 = self.detect_encoding(anno_filename)
                anno = open(anno_filename,"r", encoding=encoding2***REMOVED***'encoding'***REMOVED***).read()
                anno_words = re.split("\s+", anno)

                anno_dict = {}
                orig_dict = {}

                for w in anno_words:
                    anno_dict***REMOVED***w***REMOVED*** = 1

                for i,w in enumerate(orig_words):

                    #check for edge cases that should not be "words"
                    x = w.replace("_","").strip()
                    if len(x) == 0:
                        continue

                    #add all words to our counts
                    if w not in word_counts:
                        word_counts***REMOVED***w***REMOVED*** = 0
                    word_counts***REMOVED***w***REMOVED*** += 1

                    #check if this word is phi
                    if w not in anno_dict:

                        left_index = i - 10
                        if left_index < 0:
                            left_index = 0

                        right_index = i + 10
                        if right_index >= len(orig_words):
                            right_index = len(orig_words) - 1
                        window = orig_words***REMOVED***left_index:right_index***REMOVED***
                        if f not in phi:
                            phi***REMOVED***f***REMOVED*** = ***REMOVED******REMOVED***

                        c = "string"
                        if re.search("\d+", w):
                            c = "number"

                        phi***REMOVED***f***REMOVED***.append({"phi":w,"context":window,"class":c})
                    else:
                        #add all words to our counts
                        if w not in not_phi:
                            not_phi***REMOVED***w***REMOVED*** = 0
                        not_phi***REMOVED***w***REMOVED*** += 1

        #save our phi with context
        json.dump(phi, open("data/phi/phi_context.json", "w"), indent=4)

        #save all phi word counts
        counts = {}
        num_phi = {}
        string_phi = {}
        
        for f in phi:
            for d in phi***REMOVED***f***REMOVED***:
                if d***REMOVED***"phi"***REMOVED*** not in counts:
                    counts***REMOVED***d***REMOVED***"phi"***REMOVED******REMOVED*** = 0
                counts***REMOVED***d***REMOVED***"phi"***REMOVED******REMOVED*** += 1
                if d***REMOVED***"class"***REMOVED*** == "number":
                    if d***REMOVED***"phi"***REMOVED*** not in num_phi:
                        num_phi***REMOVED***d***REMOVED***"phi"***REMOVED******REMOVED*** = 0
                    num_phi***REMOVED***d***REMOVED***"phi"***REMOVED******REMOVED*** += 1
                else:
                    if d***REMOVED***"phi"***REMOVED*** not in string_phi:
                        string_phi***REMOVED***d***REMOVED***"phi"***REMOVED******REMOVED*** = 0
                    string_phi***REMOVED***d***REMOVED***"phi"***REMOVED******REMOVED*** += 1

        #save all phi counts
        json.dump(counts, open("data/phi/phi_counts.json", "w"), indent=4)
        #save phi number counts
        json.dump(num_phi, open("data/phi/phi_number_counts.json", "w"), indent=4)
        #save phi string counts
        json.dump(string_phi, open("data/phi/phi_string_counts.json", "w"), indent=4)
        #save our total word counts
        json.dump(word_counts, open("data/phi/word_counts.json", "w"), indent=4)
        #save our total non_phi counts
        json.dump(not_phi, open("data/phi/non_phi_counts.json", "w"), indent=4)
        
        #get all non_phi counts by number or string
        non_phi_number = {}
        non_phi_string = {}
        for w in word_counts:
            if re.search("\d+", w):
                if w not in non_phi_number:
                    non_phi_number***REMOVED***w***REMOVED*** = 0
                non_phi_number***REMOVED***w***REMOVED*** += 1
            else:
                if w not in non_phi_string:
                    non_phi_string***REMOVED***w***REMOVED*** = 0
                non_phi_string***REMOVED***w***REMOVED*** += 1

        #save all phi string counts
        json.dump(non_phi_number, open("data/phi/non_phi_number_counts.json", "w"), indent=4)

        #save all phi number counts
        json.dump(non_phi_string, open("data/phi/non_phi_string_counts.json", "w"), indent=4)


    def mapphi(self, 
            phi_path="data/phi/phi_counts.json", 
            out_path="data/phi/phi_map.json",
            sorted_path="data/phi/phi_sorted.json",  
            digit_char="`", 
            string_char="?"):
        """ given all examples of the phi, creates a general representation 
            
            digit_char = this is what digits are replaced by
            string_char = this is what strings are replaced by
            any_char = this is what any random characters are replaced with
        """
        if self.debug:
            print("mapphi")

        d = json.load(open(phi_path, "r"))

        phi_map = {}

        for phi in d:
            wordlst = ***REMOVED******REMOVED***
            phi_word = phi***REMOVED***"phi"***REMOVED***
            for c in phi_word:
                if re.match("\d+", c):
                    wordlst.append(digit_char)
                elif re.match("***REMOVED***a-zA-Z***REMOVED***+", c):
                    wordlst.append(string_char)
                else:
                    wordlst.append(c)
            word = "".join(wordlst)
            if word not in phi_map:
                phi_map***REMOVED***word***REMOVED*** = {'examples':{}}
            if phi_word not in phi_map***REMOVED***word***REMOVED******REMOVED***'examples'***REMOVED***:
                phi_map***REMOVED***word***REMOVED******REMOVED***'examples'***REMOVED******REMOVED***phi_word***REMOVED*** = ***REMOVED******REMOVED***
            phi_map***REMOVED***word***REMOVED******REMOVED***'examples'***REMOVED******REMOVED***phi_word***REMOVED***.append(phi) 

        #save the count of all representations
        for k in phi_map:
            phi_map***REMOVED***k***REMOVED******REMOVED***"count"***REMOVED*** = len(phi_map***REMOVED***k***REMOVED******REMOVED***"examples"***REMOVED***.keys())

        #save all representations
        json.dump(phi_map, open(out_path, "w"), indent=4)

        #save an ordered list of representations so we can prioritize regex building
        items = ***REMOVED******REMOVED***
        for k in phi_map:
            items.append({"pattern":k, "examples":phi_map***REMOVED***k***REMOVED******REMOVED***"examples"***REMOVED***, "count":len(phi_map***REMOVED***k***REMOVED******REMOVED***"examples"***REMOVED***.keys())})

        items.sort(key=lambda x: x***REMOVED***"count"***REMOVED***, reverse=True)
        json.dump(items, open(sorted_path, "w"), indent=4)




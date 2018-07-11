
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
        if "verbose" in config:
            self.verbose = config["verbose"]
        if "run_eval" in config:
            self.run_eval = config["run_eval"]
        if "freq_table" in config:
            self.freq_table = config["freq_table"]                       
        if "finpath" in config:
            if not os.path.exists(config["finpath"]):
                raise Exception("Filepath does not exist", config["finpath"])
            self.finpath = config["finpath"]
        if "foutpath" in config:
            if not os.path.exists(config["foutpath"]):
                raise Exception("Filepath does not exist", config["foutpath"])
            self.foutpath = config["foutpath"]
        #if "anno_folder" in config:
        #    if not os.path.exists(config["anno_folder"]):
        #        raise Exception("Filepath does not exist", config["foutpath"])
        #    self.anno_folder = config["anno_folder"]
        
        if "coords" in config:
            self.coords = config["coords"]
        else:
            raise Exception("Coordinate outpath undefined")

        if "outformat" in config:
            self.outformat = config["outformat"]
        else:
            raise Exception("Output format undefined")
        
        if "ucsfformat" in config:
            self.ucsf_format = config["ucsfformat"]
       
        if "filters" in config:
            if not os.path.exists(config["filters"]):
                raise Exception("Filepath does not exist", config["filters"])
            self.patterns = json.loads(open(config["filters"], "r").read())

        if "xml" in config:
            if not os.path.exists(config["xml"]):
                raise Exception("Filepath does not exist", config["xml"])
            self.xml = json.loads(open(config["xml"], "r", encoding='utf-8').read())

        if "stanford_ner_tagger" in config:
            if not os.path.exists(config["stanford_ner_tagger"]["classifier"]) and config["stanford_ner_tagger"]["download"] == False:
                raise Exception("Filepath does not exist", config["stanford_ner_tagger"]["classifier"])
            else:
                pass
                #download the ner data
                ##process = subprocess.Popen("cd generate_dataset && ./download_ner.sh".split(), stdout=subprocess.PIPE)
                ##output, error = process.communicate()
            self.stanford_ner_tagger_classifier = config["stanford_ner_tagger"]["classifier"]
            #####if not os.path.exists(config["stanford_ner_tagger"]["jar"]):
            #####    raise Exception("Filepath does not exist", config["stanford_ner_tagger"]["jar"])
            self.stanford_ner_tagger_jar = config["stanford_ner_tagger"]["jar"]
                #we lazy load our tagger only if there's a corresponding pattern

      
        self.stanford_ner_tagger = None

        #All coordinate maps stored here
        self.coordinate_maps = []

        #initialize our patterns
        self.init_patterns()


    def init_patterns(self):
        """ given our input pattern config will load our sets and pre-compile our regex"""

        known_pattern_types = set(["regex", "set", "stanford_ner", "pos_matcher", "match_all"])
        require_files = set(["regex", "set"])
        require_pos = set(["pos_matcher"])
        set_filetypes = set(["pkl", "json"])
        regex_filetypes = set(["txt"])
        reserved_list = set(["data", "coordinate_map"])

        #first check that data is formatted, can be loaded etc. 
        #print(self.patterns)
        for i,pattern in enumerate(self.patterns):

            if pattern["type"] in require_files and not os.path.exists(pattern["filepath"]):
                raise Exception("Config filepath does not exist", pattern["filepath"])
            #TODO: what does this do exactly?
            for k in reserved_list:
                if k in pattern:
                    raise Exception("Error, Keyword is reserved", k, pattern)
            if pattern["type"] not in known_pattern_types:
                raise Exception("Pattern type is unknown", pattern["type"])
            if pattern["type"] == "set":
                if pattern["filepath"].split(".")[-1] not in set_filetypes:
                    raise Exception("Invalid filteype", pattern["filepath"], "must be of", set_filetypes)
                self.patterns[i]["data"] = self.init_set(pattern["filepath"])  
            elif pattern["type"] == "regex":
                if pattern["filepath"].split(".")[-1] not in regex_filetypes:
                    raise Exception("Invalid filteype", pattern["filepath"], "must be of", regex_filetypes)
                self.patterns[i]["data"] = self.precompile(pattern["filepath"])
                #print(self.precompile(pattern["filepath"]))
    
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

    def map_coordinates(self, in_path="", allowed_filetypes=set(["txt", "ano"])):
        """ Runs the set, or regex on the input data 
            generating a coordinate map of hits given 
            (this performs a dry run on the data and doesn't transform)
        """

        if not os.path.exists(in_path):
            raise Exception("Filepath does not exist", in_path)
        
        #create coordinate maps for each pattern
        for i,pat in enumerate(self.patterns):
            self.patterns[i]["coordinate_map"] = CoordinateMap()

        #TODO: what is the point of dirs (it's never used)?
        for root, dirs, files in os.walk(in_path):
            for f in files:

                filename = root+f

                if filename.split(".")[-1] not in allowed_filetypes:
                    if self.verbose:
                        print("Skipping: ", filename)
                    continue                
                #self.patterns[i]["coordinate_map"].add_file(filename)

                encoding = self.detect_encoding(filename)
                txt = open(filename,"r", encoding=encoding['encoding']).read()


                for i,pat in enumerate(self.patterns):
                    if pat["type"] == "regex":
                        self.map_regex(filename=filename, text=txt, pattern_index=i)
                    elif pat["type"] == "set":
                        self.map_set(filename=filename, text=txt, pattern_index=i)
                    elif pat["type"] == "stanford_ner":
                        self.map_ner(filename=filename, text=txt, pattern_index=i)
                    elif pat["type"] == "pos_matcher":
                        self.map_pos(filename=filename, text=txt, pattern_index=i)
                    elif pat["type"] == "match_all":
                        self.match_all(filename=filename, text=txt, pattern_index=i)
                    else:
                        raise Exception("Error, pattern type not supported: ", pat["type"])

        #clear out any data to save ram
        for i,pat in enumerate(self.patterns):
            if "data" in pat:
                del self.patterns[i]["data"]

                
    def map_regex(self, filename="", text="", pattern_index=-1, pre_process= r"[^a-zA-Z0-9\.]"):
        """ Creates a coordinate map from the pattern on this data
            generating a coordinate map of hits given (dry run doesn't transform)
        """

        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))
        coord_map = self.patterns[pattern_index]["coordinate_map"]
        regex = self.patterns[pattern_index]["data"]

        # All regexes except matchall
        if regex != re.compile('.'):
            matches = regex.finditer(text)
            
            for m in matches:
                #if filename == './data/i2b2_notes_updated/373-04.txt':
                # if self.patterns[pattern_index]["title"] == "YYYY/MM-YYYY/MM":
                # if 'a ' in m.group():
                #     print(self.patterns[pattern_index]["title"])
                #     print(m.group())
                #     print(filename)
                #     print('\n')
                
                coord_map.add_extend(filename, m.start(), m.start()+len(m.group()))
        
            self.patterns[pattern_index]["coordinate_map"] = coord_map
        
        #TODO: what does the match all section do exactly? Why do we need it if it's matching everything? Can't we just discard the whole thing.
        #### MATCHALL ####
        elif regex == re.compile('.'):
         
            # Split note the same way we would split for set or POS matching

            matchall_list = re.split("(\s+)", text)
            matchall_list_cleaned = []
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
                word_clean = re.sub(r"[^a-zA-Z0-9]+", "", word.lower().strip())
                if len(word_clean) == 0:
                    #got a blank space or something without any characters or digits, move forward
                    start_coordinate += len(word)
                    continue

                if regex.match(word_clean):
                    coord_map.add_extend(filename, start, stop)
                    
                #advance our start coordinate
                start_coordinate += len(word)

            self.patterns[pattern_index]["coordinate_map"] = coord_map



    def match_all(self, filename="", text="", pattern_index=-1):
        """ Simply maps to the entirety of the file """
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))

        coord_map = self.patterns[pattern_index]["coordinate_map"]
        #add the entire length of the file
        coord_map.add(filename, 0, len(text))
        print(0, len(text))
        self.patterns[pattern_index]["coordinate_map"] = coord_map


    def map_set(self, filename="", text="", pattern_index=-1,  pre_process= r"[^a-zA-Z0-9\.]"):
        """ Creates a coordinate mapping of words any words in this set"""
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))

        map_set = self.patterns[pattern_index]["data"]
        coord_map = self.patterns[pattern_index]["coordinate_map"]
        
        #get part of speech we will be sending through this set
        #note, if this is empty we will put all parts of speech through the set
        check_pos = False
        pos_set = set([])
        if "pos" in self.patterns[pattern_index]:
            pos_set = set(self.patterns[pattern_index]["pos"])
        if len(pos_set) > 0:
            check_pos = True

        # Use pre-process to split sentence by spaces AND symbols, while preserving spaces in the split list
        lst = re.split("(\s+)", text)
        cleaned = []
        for item in lst:
            if len(item) > 0:
                #TODO: if we are removing white space then how come we need to check if the resulting split is space?
                #Nevermind. figured it out.
                if item.isspace() == False:
                    #TODO: why are we splitting what we already split before?
                    #On a second thought, I think this is because we want to split by symbols also (and not only whitespace).
                    split_item = re.split("(\s+)", re.sub(pre_process, " ", item))
                    for elem in split_item:
                        if len(elem) > 0:
                            #TODO: Shoudn't we check for whitespace here before adding? e,g, "the-school" gives: ['the', ' ', 'school']
                            cleaned.append(elem)
                else:
                    cleaned.append(item)

        pos_list = nltk.pos_tag(cleaned)
        # if filename == './data/i2b2_notes/160-03.txt':
        #     print(pos_list)
        start_coordinate = 0
        for tup in pos_list:
            word = tup[0]
            pos  = tup[1]
            start = start_coordinate
            stop = start_coordinate + len(word)

            # This converts spaces into empty strings, so we know to skip forward to the next real word
            #TODO: ^ converts spaces AND SYMBOLS into empty... right?
            word_clean = re.sub(r"[^a-zA-Z0-9]+", "", word.lower().strip())
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
                    #print("FOUND: ",word, "COORD: ",  text[start:stop])
                else:
                    #print("not in set: ",word, "COORD: ",  text[start:stop])
                    #print(word_clean)
                    pass
                    
            #advance our start coordinate
            start_coordinate += len(word)

        self.patterns[pattern_index]["coordinate_map"] = coord_map

    def map_pos(self, filename="", text="", pattern_index=-1, pre_process= r"[^a-zA-Z0-9\.]"):
        """ Creates a coordinate mapping of words which match this part of speech (POS)"""
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))

        if "pos" not in self.patterns[pattern_index]:
            raise Exception("Mapping POS must include parts of speech", pattern_index, "pattern length", len(patterns))
            
        coord_map = self.patterns[pattern_index]["coordinate_map"]
        pos_set = set(self.patterns[pattern_index]["pos"])
        
        # Use pre-process to split sentence by spaces AND symbols, while preserving spaces in the split list
        lst = re.split("(\s+)", text)
        cleaned = []
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
            word = tup[0]
            pos  = tup[1]
            start = start_coordinate
            stop = start_coordinate + len(word)
            word_clean = re.sub(r"[^a-zA-Z0-9]+", "", word.lower().strip())
            if len(word_clean) == 0:
                #got a blank space or something without any characters or digits, move forward
                start_coordinate += len(word)
                continue

            if pos in pos_set:    
                coord_map.add_extend(filename, start, stop)
                #print("FOUND: ",word,"POS",pos, "COORD: ",  text[start:stop])
                
            #advance our start coordinate
            start_coordinate += len(word)

        self.patterns[pattern_index]["coordinate_map"] = coord_map

    def map_ner(self, filename="", text="", pattern_index=-1, pre_process= r"[^a-zA-Z0-9]+"):
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
        
        coord_map = self.patterns[pattern_index]["coordinate_map"]
        pos_set = set([])
        if "pos" in self.patterns[pattern_index]:
            pos_set = set(self.patterns[pattern_index]["pos"])
        if len(pos_set) > 0:
            check_pos = True

        lst = re.split("(\s+)", text)
        cleaned = []
        for item in lst:
            if len(item) > 0:
                cleaned.append(item)
        
        ner_no_spaces = self.stanford_ner_tagger.tag(cleaned)
        #get our ner tags
        ner_set = {}
        for tup in ner_no_spaces:
            ner_set[tup[0]] = tup[1]
        ner_set_with_locations = {}
        start_coordinate = 0
        for w in cleaned:
            if w in ner_set:
                ner_set_with_locations[w] = (ner_set[w], start_coordinate)
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
                ner_tag = ner_set_with_locations[word][0]
                start = ner_set_with_locations[word][1]
                if ner_tag in pos_set:
                    stop = start + len(word)
                    coord_map.add_extend(filename, start, stop)
                    print("FOUND: ",word, "NER: ", ner_tag, start, stop)
            
                    
            #advance our start coordinate
            start_coordinate += len(word)

        self.patterns[pattern_index]["coordinate_map"] = coord_map

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
        
        if self.verbose:
            print("RUNNING TRANSFORM")

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
            txt = open(filename,"r", encoding=encoding['encoding']).read()
            #record we use to evaluate our effectiveness
            data[filename] = {"text":txt, "phi":[],"non-phi":[]}

            #create an intersection map of all coordinates we'll be removing
            exclude_map = CoordinateMap()

            exclude_map.add_file(filename)

            #create an interestion map of all coordinates we'll be keeping
            include_map = CoordinateMap()

            include_map.add_file(filename)
            #TODO: why not just {for pattern in self.patterns: }
            for i,pattern in enumerate(self.patterns):
                coord_map = pattern["coordinate_map"]
                exclude = pattern["exclude"]
                # self.patterns[pattern_index]["title"]

                for start,stop in coord_map.filecoords(filename):
                    if exclude:
                        if not include_map.does_overlap(filename, start, stop):
                            exclude_map.add_extend(filename, start, stop)
                            data[filename]["phi"].append({"start":start, "stop":stop, "word":txt[start:stop]})
                    #if include
                    else:
                        if not exclude_map.does_overlap(filename, start, stop):
                            #print("include", start, stop, txt[start:stop])
                            include_map.add_extend(filename, start, stop)
                            data[filename]["non-phi"].append({"start":start, "stop":stop, "word":txt[start:stop]})
                        else:
                            pass
                            #print("include overlapped", start, stop, txt[start:stop])

            #now we transform the text
            #TODO: why are diffrent ways of splitting file name being used si
            fbase, fext = os.path.splitext(f)
            outpathfbase = out_path + fbase
            if self.outformat == "asterisk":
                with open(outpathfbase+".txt", "w", encoding='utf-8') as f:
                    contents = self.transform_text_asterisk(txt, filename, 
                                                            include_map,
                                                            exclude_map)
                    f.write(contents)
                    
            elif self.outformat == "i2b2":
                with open(outpathfbase+".xml", "w") as f:
                    contents = self.transform_text_i2b2(data[filename])
                    f.write(contents)
            else:
                raise Exception("Outformat not supported: ",
                                self.outformat)
                

        if self.run_eval: #output our data for eval
            json.dump(data, open(self.coords, "w"), indent=4)

    # infilename needed for addressing maps
    def transform_text_asterisk(self, txt, infilename,
                                include_map, exclude_map):
        last_marker = 0
        current_chunk = []
        punctuation_matcher = re.compile(r"[^a-zA-Z0-9*]")

        #read the text by character, any non-punc non-overlaps will be replaced
        contents = []
        for i in range(0, len(txt)):

            if i < last_marker:
                continue
            
            if include_map.does_exist(infilename, i):
                #add our preserved text
                start,stop = include_map.get_coords(infilename, i)
                contents.append(txt[start:stop])
                last_marker = stop
            elif punctuation_matcher.match(txt[i]):
                contents.append(txt[i])
            else:
                contents.append("*")

        return "".join(contents)

    def transform_text_i2b2(self, tagdata):
        """creates a string in i2b2-XML format"""
        root = "Philter"
        contents = []
        
        contents.append("<?xml version=\"1.0\" ?>\n")
        contents.append("<"+root+">\n")
        contents.append("<TEXT><![CDATA[")
        contents.append(tagdata['text'])
        contents.append("]]></TEXT>\n")
        contents.append("<TAGS>\n")
        for i in range(len(tagdata['phi'])):
            tagcategory = "OTHER" # TODO: replace with actual category
            phitype = "OTHER" # TODO: replace with actual phi type
            contents.append("<")
            contents.append(phitype)
            contents.append(" id=\"P")
            contents.append(str(i))
            contents.append("\" start=\"")
            contents.append(str(tagdata['phi'][i]['start']))
            contents.append("\" end=\"")
            contents.append(str(tagdata['phi'][i]['stop']))
            contents.append("\" text=\"")
            contents.append(tagdata['phi'][i]['word'])
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
        window = words[left_index:right_index]

        #get which patterns matched this word
        num_spaces = len(words[:word_index])
        

        return {"filename":filename, "phi":word, "context":window}
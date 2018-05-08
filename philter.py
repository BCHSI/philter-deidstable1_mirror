
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
            self.debug = config["debug"]
        if "errorcheck" in config:
            self.errorcheck = config["errorcheck"]
        if "parallel" in config:
            self.parallel = config["parallel"]
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
        if "anno_folder" in config:
            if not os.path.exists(config["anno_folder"]):
                raise Exception("Filepath does not exist", config["foutpath"])
            self.anno_folder = config["anno_folder"]

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
                #download the ner data
                process = subprocess.Popen("cd generate_dataset && ./download_ner.sh".split(), stdout=subprocess.PIPE)
                output, error = process.communicate()
            self.stanford_ner_tagger_classifier = config["stanford_ner_tagger"]["classifier"]
            if not os.path.exists(config["stanford_ner_tagger"]["jar"]):
                raise Exception("Filepath does not exist", config["stanford_ner_tagger"]["jar"])
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
        for i,pattern in enumerate(self.patterns):

            if pattern["type"] in require_files and not os.path.exists(pattern["filepath"]):
                raise Exception("Config filepath does not exist", pattern["filepath"])
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

        for root, dirs, files in os.walk(in_path):
            for f in files:

                filename = root+f

                if filename.split(".")[-1] not in allowed_filetypes:
                    if self.debug and self.parallel == False:
                        print("Skipping: ", filename)
                    continue                
                #self.patterns[i]["coordinate_map"].add_file(filename)

                encoding = self.detect_encoding(filename)
                txt = open(filename,"r", encoding=encoding['encoding']).read()

                # if self.debug:
                #     print("Transforming", pat)

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
                if 'ACID' in m.group():
                    print(self.patterns[pattern_index]["title"])
                    print(m.group())
                
                coord_map.add_extend(filename, m.start(), m.start()+len(m.group()))
        
            self.patterns[pattern_index]["coordinate_map"] = coord_map
        
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

            # This converts spaces into empty strings, so we know to skip forward to the next real word
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
            txt = open(filename,"r", encoding=encoding['encoding']).read()
            #record we use to evaluate our effectiveness
            data[filename] = {"text":txt, "phi":[],"non-phi":[]}

            #create an intersection map of all coordinates we'll be removing
            exclude_map = CoordinateMap()

            exclude_map.add_file(filename)

            #create an interestion map of all coordinates we'll be keeping
            include_map = CoordinateMap()

            include_map.add_file(filename)
            for i,pattern in enumerate(self.patterns):
                coord_map = pattern["coordinate_map"]
                exclude = pattern["exclude"]

                for start,stop in coord_map.filecoords(filename):
                    if exclude:
                        if not include_map.does_overlap(filename, start, stop):
                            exclude_map.add_extend(filename, start, stop)
                            data[filename]["phi"].append({"start":start, "stop":stop, "word":txt[start:stop]})
                    else:
                        if not exclude_map.does_overlap(filename, start, stop):
                            #print("include", start, stop, txt[start:stop])
                            include_map.add_extend(filename, start, stop)
                            data[filename]["non-phi"].append({"start":start, "stop":stop, "word":txt[start:stop]})
                        else:
                            pass
                            #print("include overlapped", start, stop, txt[start:stop])

            #now we transform the text
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
                

        if self.debug: #output our data for eval
            json.dump(data, open("./data/coordinates.json", "w"), indent=4)

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


    def seq_eval(self,
            note_lst, 
            anno_lst, 
            punctuation_matcher=re.compile(r"[^a-zA-Z0-9*\.]"), 
            text_matcher=re.compile(r"[a-zA-Z0-9]"), 
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
            note_word_stripped = re.sub(r"[^a-zA-Z0-9\*\.]+", "", note_word.strip())
            anno_word_stripped = re.sub(r"[^a-zA-Z0-9\*\.]+", "", anno_word.strip())
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
                        fn_words = []
                        fp_words = []

                        fn_chunk = []
                        fp_chunk = []
                        for n,a in list(zip(note_word, anno_word)):
                            if n == a:
                                #these characters match, clear our chunks
                                if len(fp_chunk) > 0:
                                    fp_words.append("".join(fp_chunk))
                                    fp_chunk = []
                                if len(fn_chunk) > 0:
                                    fn_words.append("".join(fn_words))
                                    fn_chunk = []
                                
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
        pre_process2= r"[^a-zA-Z0-9]",
        punctuation_matcher=re.compile(r"[^a-zA-Z0-9\*\.]")):
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
            "false_positives":[], #non-phi words we think are phi
            "true_positives": [], #phi words we correctly identify
            "false_negatives":[], #phi words we think are non-phi
            "true_negatives": [], #non-phi words we correctly identify
            "summary_by_file":{}
        }
        summary_coords = {
            "summary_by_file":{}
        }

        all_fn = []
        all_fp = []

        for root, dirs, files in os.walk(in_path):

            for f in files:
                if not f.endswith(".txt"): # TODO: come up with something better
                    continue               #       to ensure one to one txt file
                                           #       comparisons with anno_path
                #local values per file
                false_positives = [] #non-phi we think are phi
                false_positives_coords = []
                true_positives  = [] #phi we correctly identify
                true_positives_coords = []
                false_negatives = [] #phi we think are non-phi
                false_negatives_coords = []
                true_negatives  = [] #non-phi we correctly identify
                true_negatives_coords = []

                philtered_filename = root+f
                anno_filename = anno_path+''.join(f.split(".")[0])+anno_suffix

                # if len(anno_suffix) > 0:
                #     anno_filename = anno_folder+f.split(".")[0]+anno_suffix

                if not os.path.exists(philtered_filename):
                    raise Exception("FILE DOESNT EXIST", philtered_filename)
                
                if not os.path.exists(anno_filename):
                    #print("FILE DOESNT EXIST", anno_filename)
                    continue

                encoding1 = self.detect_encoding(philtered_filename)
                philtered = open(philtered_filename,"r").read()
                
                          
                philtered_words = re.split("(\s+)", philtered)
                # if f == '110-01.txt':
                #     print(philtered_words)
                #     print(len("".join(philtered_words)))
                philtered_words_cleaned = []
                for item in philtered_words:
                    if len(item) > 0:
                        if item.isspace() == False:
                            split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                            for elem in split_item:
                                if len(elem) > 0:
                                    philtered_words_cleaned.append(elem)
                        else:
                            philtered_words_cleaned.append(item)
                #print(len(philtered))
                # if f == '167937985.txt':
                #     print('Results text:')
                #     print(philtered)
                encoding2 = self.detect_encoding(anno_filename)
                anno = open(anno_filename,"r").read()              
                
                anno_words = re.split("(\s+)", anno)
                # if f == '110-01.txt':
                #     print(anno_words)
                #     print(len("".join(anno_words)))
                anno_words_cleaned = []
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
                    if w.isspace() == False and (re.sub(r"[^a-zA-Z0-9\*]+", "", w) != ""):

                        if c == "FP":
                            false_positives.append(w)
                            false_positives_coords.append([w,r])
                            # if w == "she" or w == "no" or w == "he" or w == "increased" or w == "wave" or w == "In" or w == "AS":
                            #     print(w)
                            #     print(f)

                        elif c == "FN":
                            false_negatives.append(w)
                            false_negatives_coords.append([w,r])
                        elif c == "TP":
                            true_positives.append(w)
                            true_positives_coords.append([w,r])
                        elif c == "TN":
                            true_negatives.append(w)
                            true_negatives_coords.append([w,r])

                #update summary
                summary["summary_by_file"][philtered_filename] = {"false_positives":false_positives,"false_negatives":false_negatives, "num_false_negatives":len(false_negatives)}
                summary["total_true_positives"] = summary["total_true_positives"] + len(true_positives)
                summary["total_false_positives"] = summary["total_false_positives"] + len(false_positives)
                summary["total_false_negatives"] = summary["total_false_negatives"] + len(false_negatives)
                summary["total_true_negatives"] = summary["total_true_negatives"] + len(true_negatives)
                all_fp = all_fp + false_positives
                all_fn = all_fn + false_negatives


                # Create coordinate summaries
                summary_coords["summary_by_file"][philtered_filename] = {"false_positives":false_positives_coords,"false_negatives":false_negatives_coords}


        if summary["total_true_positives"]+summary["total_false_negatives"] > 0:
            recall = summary["total_true_positives"]/(summary["total_true_positives"]+summary["total_false_negatives"])
        elif summary["total_false_negatives"] == 0:
            recall = 1.0

        if summary["total_true_positives"]+summary["total_false_positives"] > 0:
            precision = summary["total_true_positives"]/(summary["total_true_positives"]+summary["total_false_positives"])
        elif summary["total_true_positives"] == 0:
            precision = 0.0

        if summary["total_true_negatives"]+summary["total_false_positives"] > 0:
            retention = summary["total_true_negatives"]/(summary["total_true_negatives"]+summary["total_false_positives"])
        else:
            retention = 0.0
        
        if self.debug and self.parallel == False:
            #save the phi we missed
            json.dump(summary, open(summary_output, "w"), indent=4)
            json.dump(all_fn, open(fn_output, "w"), indent=4)
            json.dump(all_fp, open(fp_output, "w"), indent=4)
            
            print("true_negatives", summary["total_true_negatives"],"true_positives", summary["total_true_positives"], "false_negatives", summary["total_false_negatives"], "false_positives", summary["total_false_positives"])
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
            # i2b2:
            if not self.ucsf_format:
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
                }
            # ucsf:
            if self.ucsf_format:   
                rp_summaries = { 
                    "account_number_fns": 0,
                    "account_number_tps": 0,
                    "address_fns": 0,
                    "address_tps": 0, 
                    "age_fns":0,
                    "age_tps":0,
                    "biometric_or_photo_id_fns": 0,
                    "biometric_or_photo_id_tps": 0,
                    "certificate_license_id_fns": 0,
                    "certificate_license_id_tps": 0,
                    "date_fns":0,
                    "date_tps":0,
                    "email_fns":0,
                    "email_tps":0,
                    "initials_fns": 0,
                    "initials_tps": 0 ,
                    "mrn_id_fns": 0,
                    "mrn_id_tps": 0,
                    "patient_family_name_fns": 0,
                    "patient_family_name_tps": 0,
                    "phone_fax_fns":0,
                    "phone_fax_tps":0,
                    "provider_name_fns": 0,
                    "provider_name_tps": 0,
                    "social_security_fns":0,
                    "social_security_tps":0,
                    "unclear_fns": 0,
                    "unclear_tps": 0,
                    "unique_patient_id_fns": 0,
                    "unique_patient_id_tps": 0,                         
                    "url_ip_fns":0,
                    "url_ip_tps":0, 
                    "vehicle_device_id_fns": 0,
                    "vehicle_device_id_tps": 0        
                }

            # Create dictionaries for unigram and bigram PHI/non-PHI frequencies
            # Diciontary values look like: [phi_count, non-phi_count]
            unigram_dict = {}
            bigram_dict = {}

            # Loop through all filenames in summary
            for fn in summary_coords['summary_by_file']:
                
                current_summary =  summary_coords['summary_by_file'][fn]

                # Get corresponding info in phi_notes
                note_name = fn.split('/')[3]
                
                try:
                    anno_name = note_name.split('.')[0] + ".xml"
                    text = phi[anno_name]['text']
                except KeyError:
                    anno_name = note_name.split('.')[0] + ".txt.xml"
                    text = phi[anno_name]['text']
                    # except KeyError:
                    #     anno_name = note_name.split('.')[0] + "_nounicode.txt.xml"
                    #     text = phi[anno_name]['text']                       

                lst = re.split("(\s+)", text)
                cleaned = []
                cleaned_coords = []
                for item in lst:
                    if len(item) > 0:
                        if item.isspace() == False:
                            split_item = re.split("(\s+)", re.sub(r"[^a-zA-Z0-9\.]", " ", item))
                            for elem in split_item:
                                if len(elem) > 0:
                                    cleaned.append(elem)
                        else:
                            cleaned.append(item)
                # if anno_name == '167937985.txt.xml':
                #     print(anno_name)
                #     #print(cleaned)
                #     print('Anno text:')
                #     print(text)
                
                # Get coords for POS tags
                start_coordinate = 0
                pos_coords = []
                for item in cleaned:
                    pos_coords.append(start_coordinate)
                    start_coordinate += len(item)

                #print(pos_coords)
                pos_list = nltk.pos_tag(cleaned)


                cleaned_with_pos = {}
                for i in range(0,len(pos_list)):
                    cleaned_with_pos[str(pos_coords[i])] = [pos_list[i][0], pos_list[i][1]]

                ########## Get FN tags ##########
                phi_list = phi[anno_name]['phi']
                # print(cleaned)
                # print(pos_coords)


                ######### Create unigram and bigram frequency tables #######
                if self.freq_table:

                    # Create separate cleaned list/coord list without spaces
                    cleaned_nospaces = []
                    coords_nospaces = []
                    for i in range(0,len(cleaned)):
                        if cleaned[i].isspace() == False:
                            cleaned_nospaces.append(cleaned[i])
                            coords_nospaces.append(pos_coords[i])

                    # Loop through all single words and word pairs, and compare with PHI list
                    for i in range(0,len(cleaned_nospaces)-1):
                        #cleaned_nospaces[i]= word, coords_nospaces[i] = start coordinate
                        unigram_word = cleaned_nospaces[i].replace('\n','').replace('\t','').replace(' ','').lower()
                        bigram_word = " ".join([cleaned_nospaces[i].replace('\n','').replace('\t','').replace(' ','').lower(),cleaned_nospaces[i+1].replace('\n','').replace('\t','').replace(' ','').lower()])
                        unigram_start = coords_nospaces[i]
                        bigram_start1 = coords_nospaces[i]
                        bigram_start2 = coords_nospaces[i+1]

                        # Loop through PHI list and compare ranges
                        for phi_item in phi_list:
                            phi_start = phi_item['start']
                            phi_end = phi_item['end']
                            if unigram_start in range(int(phi_start), int(phi_end)):
                                # This word is PHI and hasn't been added to the dictionary yet
                                if unigram_word not in unigram_dict:
                                    unigram_dict[unigram_word] = [1, 0]
                               # This word is PHI and has already been added to the dictionary
                                else:
                                    unigram_dict[unigram_word][0] += 1
                            else:
                                # This word is not PHI and hasn't been aded to the dictionary yet
                                if unigram_word not in unigram_dict:
                                    unigram_dict[unigram_word] = [0, 1]
                               # This word is not PHI and has already been added to the dictionary
                                else:
                                    unigram_dict[unigram_word][1] += 1                               
                            if bigram_start1 in range(int(phi_start), int(phi_end)) and bigram_start2 in range(int(phi_start), int(phi_end)):
                                # This word is PHI and hasn't been added to the dictionary yet
                                if bigram_word not in bigram_dict:
                                    bigram_dict[bigram_word] = [1, 0]
                               # This word is PHI and has already been added to the dictionary
                                else:
                                    bigram_dict[bigram_word][0] += 1                                
                            else:
                                # This word is not PHI and hasn't been aded to the dictionary yet
                                if bigram_word not in bigram_dict:
                                    bigram_dict[bigram_word] = [0, 1]
                               # This word is not PHI and has already been added to the dictionary
                                else:
                                    bigram_dict[bigram_word][1] += 1


                # Get tokenized PHI list and number of PHI for each category
                #### i2b2
                if not self.ucsf_format:

                    names_fn_counter = 0
                    dates_fn_counter = 0
                    id_fn_counter = 0
                    contact_fn_counter = 0
                    location_fn_counter = 0
                    organization_fn_counter = 0
                    age_fn_counter = 0 

                    names_cleaned = []
                    dates_cleaned = []
                    ids_cleaned = []
                    contact_cleaned = []
                    locations_cleaned = []
                    organizations_cleaned =[]
                    age_cleaned =[]

                    for phi_dict in phi_list:
                        # Tokenize words
                        lst = re.split("(\s+)", phi_dict['text'])
                        for item in lst:
                            if len(item) > 0:
                                if item.isspace() == False:
                                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                                    for elem in split_item:
                                        if len(elem) > 0:
                                            if phi_dict['TYPE'] == 'DOCTOR' or phi_dict['TYPE'] == 'PATIENT':
                                                names_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'DATE':
                                                dates_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'MEDICALRECORD' or phi_dict['TYPE'] == 'IDNUM' or phi_dict['TYPE'] == 'DEVICE':
                                                ids_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'USERNAME' or phi_dict['TYPE'] == 'PHONE' or phi_dict['TYPE'] == 'EMAIL' or phi_dict['TYPE'] == 'FAX':
                                                contact_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'CITY' or phi_dict['TYPE'] == 'STATE' or phi_dict['TYPE'] == 'ZIP' or phi_dict['TYPE'] == 'STREET' or phi_dict['TYPE'] == 'LOCATION-OTHER' or phi_dict['TYPE'] == 'HOSPITAL':
                                                locations_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'HOSPITAL':
                                                organizations_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'AGE':
                                                age_cleaned.append(elem)
                                else:
                                    if phi_dict['TYPE'] == 'DOCTOR' or phi_dict['TYPE'] == 'PATIENT':
                                        names_cleaned.append(item)
                                    if phi_dict['TYPE'] == 'DATE':
                                        dates_cleaned.append(elem)
                                    if phi_dict['TYPE'] == 'MEDICALRECORD' or phi_dict['TYPE'] == 'IDNUM' or phi_dict['TYPE'] == 'DEVICE':
                                        ids_cleaned.append(elem)
                                    if phi_dict['TYPE'] == 'USERNAME' or phi_dict['TYPE'] == 'PHONE' or phi_dict['TYPE'] == 'EMAIL' or phi_dict['TYPE'] == 'FAX':
                                        contact_cleaned.append(elem)
                                    if phi_dict['TYPE'] == 'CITY' or phi_dict['TYPE'] == 'STATE' or phi_dict['TYPE'] == 'ZIP' or phi_dict['TYPE'] == 'STREET' or phi_dict['TYPE'] == 'LOCATION-OTHER' or phi_dict['TYPE'] == 'HOSPITAL':
                                        locations_cleaned.append(elem)
                                    if phi_dict['TYPE'] == 'HOSPITAL':
                                        organizations_cleaned.append(elem)
                                    if phi_dict['TYPE'] == 'AGE':
                                        age_cleaned.append(elem)


                #### ucsf
                if self.ucsf_format:

                    account_number_fn_counter = 0
                    address_fn_counter = 0
                    age_fn_counter = 0
                    biometric_or_photo_id_fn_counter = 0
                    certificate_license_id_fn_counter = 0
                    date_fn_counter = 0
                    email_fn_counter = 0
                    initials_fn_counter = 0
                    mrn_id_fn_counter = 0
                    patient_family_name_fn_counter = 0
                    phone_fax_fn_counter = 0
                    provider_name_fn_counter = 0
                    social_security_fn_counter = 0
                    unclear_fn_counter = 0
                    unique_patient_id_fn_counter = 0                      
                    url_ip_fn_counter = 0
                    vehicle_device_id_fn_counter = 0
                    

                    account_number_cleaned = []
                    address_cleaned = []
                    age_cleaned = []
                    biometric_or_photo_id_cleaned =[]
                    certificate_license_id_cleaned =[]
                    date_cleaned = []
                    email_cleaned = []
                    initials_cleaned = []
                    mrn_id_cleaned = []
                    patient_family_name_cleaned = []
                    phone_fax_cleaned = []
                    provider_name_cleaned = []
                    social_security_cleaned = []
                    unclear_cleaned = []
                    unique_patient_id_cleaned = []                       
                    url_ip_cleaned = [] 
                    vehicle_device_id_cleaned = []
                    
                    
                    for phi_dict in phi_list:
                        # Tokenize words
                        lst = re.split("(\s+)", phi_dict['text'])
                        for item in lst:
                            if len(item) > 0:
                                if item.isspace() == False:
                                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                                    for elem in split_item:
                                        if len(elem) > 0:
                                            if phi_dict['TYPE'] == "Account_Number":
                                                account_number_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'Address':
                                                address_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'Age':
                                                age_cleaned.append(elem)
                                            if phi_dict['TYPE'] == "Biometric_ID_or_Face_Photo":
                                                biometric_or_photo_id_cleaned.append(elem)
                                            if phi_dict['TYPE'] == "Certificate_or_License":
                                                certificate_license_id_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'Date':
                                                date_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'Email':
                                                email_cleaned.append(elem)
                                            if phi_dict['TYPE'] == "Initials":
                                                initials_cleaned.append(elem) 
                                            if phi_dict['TYPE'] == "Medical_Record_ID":
                                                mrn_id_cleaned.append(elem)
                                            if phi_dict['TYPE'] == "Patient_Name_or_Family_Member_Name":
                                                patient_family_name_cleaned.append(elem)
                                            if phi_dict['TYPE'] == "Phone_Fax":
                                                age_cleaned.append(elem)  
                                            if phi_dict['TYPE'] == "Provider_Name":
                                                provider_name_cleaned.append(elem)
                                            if phi_dict['TYPE'] == "Social_Security":
                                                social_security_cleaned.append(elem)
                                            if phi_dict['TYPE'] == 'Unclear':
                                                unclear_cleaned.append(elem)                                 
                                            if phi_dict['TYPE'] == "Unique_Patient_Id":
                                                unique_patient_id_cleaned.append(elem)
                                            if phi_dict['TYPE'] == "URL_IP":
                                                url_ip_cleaned.append(elem)
                                            if phi_dict['TYPE'] == "Vehicle_or_Device_ID":
                                                vehicle_device_id_cleaned.append(elem)
 
                                else:
                                    if phi_dict['TYPE'] == "Account_Number":
                                        account_number_cleaned.append(item)
                                    if phi_dict['TYPE'] == 'Address':
                                        address_cleaned.append(elem)
                                    if phi_dict['TYPE'] == 'Age':
                                        age_cleaned.append(elem)
                                    if phi_dict['TYPE'] == "Biometric_ID_or_Face_Photo":
                                        biometric_or_photo_id_cleaned.append(elem)
                                    if phi_dict['TYPE'] == "Certificate_or_License":
                                        certificate_license_id_cleaned.append(elem)
                                    if phi_dict['TYPE'] == 'Date':
                                        date_cleaned.append(elem)
                                    if phi_dict['TYPE'] == 'Email':
                                        email_cleaned.append(elem)
                                    if phi_dict['TYPE'] == "Initials":
                                        initials_cleaned.append(elem)  
                                    if phi_dict['TYPE'] == "Medical_Record_ID":
                                        mrn_id_cleaned.append(elem)
                                    if phi_dict['TYPE'] == "Patient_Name_or_Family_Member_Name":
                                        patient_family_name_cleaned.append(elem)
                                    if phi_dict['TYPE'] == "Phone_Fax":
                                        phone_fax_cleaned.append(elem)
                                    if phi_dict['TYPE'] == "Provider_Name":
                                        provider_name_cleaned.append(elem)
                                    if phi_dict['TYPE'] == "Social_Security":
                                        social_security_cleaned.append(elem)
                                    if phi_dict['TYPE'] == 'Unclear':
                                        unclear_cleaned.append(elem) 
                                    if phi_dict['TYPE'] == "Unique_Patient_Id":
                                        unique_patient_id_cleaned.append(elem)
                                    if phi_dict['TYPE'] == "URL_IP":
                                        url_ip_cleaned.append(elem)
                                    if phi_dict['TYPE'] == "Vehicle_or_Device_ID":
                                        vehicle_device_id_cleaned.append(elem)                                     

                fn_tag_summary = {}

                if current_summary['false_negatives'] != [] and current_summary['false_negatives'] != [""]:              
                    counter = 0
                    current_fns = current_summary['false_negatives']

                    for word in current_fns:
                        counter += 1
                        false_negative = word[0]
                        start_coordinate_fn = word[1]
                      
                        for phi_item in phi_list:                           
                            phi_text = phi_item['text']
                            phi_type = phi_item['TYPE']
                            phi_id = phi_item['id']
                            if self.ucsf_format:
                                phi_start = int(phi_item['spans'].split('~')[0])
                                phi_end = int(phi_item['spans'].split('~')[1])                               
                            else:
                                phi_start = phi_item['start']
                                phi_end = phi_item['end']


                            #### i2b2
                            if not self.ucsf_format:
                                # Names FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == "DOCTOR" or phi_type == "PATIENT"):
                                    rp_summaries["names_fns"] += 1
                                    names_fn_counter += 1
                                # Dates FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == "DATE"):
                                    rp_summaries["dates_fns"] += 1
                                    dates_fn_counter += 1
                                # ID FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == "MEDICALRECORD" or phi_type == "IDNUM" or phi_type == "DEVICE"):
                                    rp_summaries["id_fns"] += 1
                                    id_fn_counter += 1
                                # Contact FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == "USERNAME" or phi_type == "PHONE" or phi_type == "EMAIL" or phi_type == "FAX"):
                                    rp_summaries["contact_fns"] += 1
                                    contact_fn_counter += 1 
                                # Location FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == 'CITY' or phi_type == 'STATE' or phi_type == 'ZIP' or phi_type == 'STREET' or phi_type == 'LOCATION-OTHER' or phi_type == 'HOSPITAL'):
                                    rp_summaries["location_fns"] += 1
                                    location_fn_counter += 1                               
                                # Organization FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == 'HOSPITAL'):
                                    rp_summaries["organization_fns"] += 1
                                    organization_fn_counter += 1  
                                # Age FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and (phi_type == 'AGE'):
                                    rp_summaries["age_fns"] += 1
                                    age_fn_counter += 1 
                                    # print(word) 
                            
                            #### ucsf
                            if self.ucsf_format:
                                # Account number FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "Account_Number":
                                    rp_summaries["account_number_fns"] += 1
                                    account_number_fn_counter += 1
                                # Address FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == 'Address':
                                    rp_summaries["address_fns"] += 1
                                    address_fn_counter += 1
                                # Age FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == 'Age':
                                    rp_summaries["age_fns"] += 1
                                    age_fn_counter += 1
                                # Biometric id/photo FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "Biometric_ID_or_Face_Photo":
                                    rp_summaries["biometric_or_photo_id_fns"] += 1
                                    biometric_or_photo_id_fn_counter += 1                                
                                # Certificate/license FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "Certificate_or_License":
                                    rp_summaries["certificate_license_id_fns"] += 1
                                    certificate_license_id_fn_counter += 1                               
                                # Date FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == 'Date':
                                    rp_summaries["date_fns"] += 1
                                    date_fn_counter += 1  
                                # Email FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == 'Email':
                                    rp_summaries["email_fns"] += 1
                                    email_fn_counter += 1
                                # Initials FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == 'Initials':
                                    rp_summaries["initials_fns"] += 1
                                    initials_fn_counter += 1                               
                                # MRN FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "Medical_Record_ID":
                                    rp_summaries["mrn_id_fns"] += 1
                                    mrn_id_fn_counter += 1
                                # Patient name FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "Patient_Name_or_Family_Member_Name":
                                    rp_summaries["patient_family_name_fns"] += 1
                                    patient_family_name_fn_counter += 1
                                # phone/fax FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "Phone_Fax":
                                    rp_summaries["phone_fax_fns"] += 1
                                    phone_fax_fn_counter += 1
                                # provider name FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "Provider_Name":
                                    rp_summaries["provider_name_fns"] += 1
                                    provider_name_fn_counter += 1 
                                # SSN FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "Social_Security":
                                    rp_summaries["social_security_fns"] += 1
                                    social_security_fn_counter += 1                               
                                # unclear FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == 'Unclear':
                                    rp_summaries["unclear_fns"] += 1
                                    unclear_fn_counter += 1  
                                # unique patient FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "Unique_Patient_Id":
                                    rp_summaries["unique_patient_id_fns"] += 1
                                    unique_patient_id_fn_counter += 1

                                # url/ip FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "URL_IP":
                                    rp_summaries["url_ip_fns"] += 1
                                    url_ip_fn_counter += 1

                                # vehicle/device id FNs
                                if (start_coordinate_fn in range(int(phi_start), int(phi_end))) and phi_type == "Vehicle_or_Device_ID":
                                    rp_summaries["vehicle_device_id_fns"] += 1
                                    vehicle_device_id_fn_counter += 1


                            # Find PHI match: fn in text, coord in range
                            if start_coordinate_fn in range(int(phi_start), int(phi_end)):
                                # Get PHI tag
                                phi_tag = phi_type
                                # Get POS tag
                                pos_tag = cleaned_with_pos[str(start_coordinate_fn)][1]
                                
                                # Get 15 characters surrounding FN on either side
                                fn_context = ''
                                context_start = start_coordinate_fn - 15
                                context_end = start_coordinate_fn + len(false_negative) + 15
                                if context_start >= 0 and context_end <= len(text)-1:
                                    fn_context = text[context_start:context_end]
                                elif context_start >= 0 and context_end > len(text)-1:
                                    fn_context = text[context_start:]
                                else:
                                    fn_context = text[:context_end]
                                # if fn == './data/i2b2_results/137-03.txt':
                                #     print(fn_context)                  
                                
                                # Get fn id, to distinguish betweem multiple entries
                                fn_id = "N" + str(counter)
                                ###### Create output dicitonary with id/word/pos/phi
                                fn_tag_summary[fn_id] = [false_negative, phi_tag, pos_tag, fn_context]
                                # if phi_tag == 'AGE':
                                #     print(word)
                 
                if fn_tag_summary != {}:
                    fn_tags[fn] = fn_tag_summary

                # Update recall/precision dictionary
                #### i2b2
                if not self.ucsf_format:

                    rp_summaries['names_tps'] += (len(names_cleaned) - names_fn_counter)
                    rp_summaries['dates_tps'] += (len(dates_cleaned) - dates_fn_counter)
                    rp_summaries['id_tps'] += (len(ids_cleaned) - id_fn_counter)
                    rp_summaries['contact_tps'] += (len(contact_cleaned) - contact_fn_counter)
                    rp_summaries['location_tps'] += (len(locations_cleaned) - location_fn_counter)
                    rp_summaries['organization_tps'] += (len(organizations_cleaned) - organization_fn_counter)
                    rp_summaries['age_tps'] += (len(age_cleaned) - age_fn_counter)
                
                if self.ucsf_format:

                    rp_summaries['account_number_tps'] += (len(account_number_cleaned) - account_number_fn_counter)
                    rp_summaries['address_tps'] += (len(address_cleaned) - address_fn_counter)
                    rp_summaries['age_tps'] += (len(age_cleaned) - age_fn_counter)
                    rp_summaries['biometric_or_photo_id_tps'] += (len(biometric_or_photo_id_cleaned) - biometric_or_photo_id_fn_counter)
                    rp_summaries['certificate_license_id_tps'] += (len(certificate_license_id_cleaned) - certificate_license_id_fn_counter)
                    rp_summaries['date_tps'] += (len(date_cleaned) - date_fn_counter)
                    rp_summaries['email_tps'] += (len(email_cleaned) - email_fn_counter)
                    rp_summaries['initials_tps'] += (len(initials_cleaned) - initials_fn_counter)
                    rp_summaries['mrn_id_tps'] += (len(mrn_id_cleaned) - mrn_id_fn_counter)
                    rp_summaries['patient_family_name_tps'] += (len(patient_family_name_cleaned) - patient_family_name_fn_counter)
                    rp_summaries['phone_fax_tps'] += (len(phone_fax_cleaned) - phone_fax_fn_counter)
                    rp_summaries['provider_name_tps'] += (len(provider_name_cleaned) - provider_name_fn_counter)
                    rp_summaries['social_security_tps'] += (len(social_security_cleaned) - social_security_fn_counter)
                    rp_summaries['unclear_tps'] += (len(unclear_cleaned) - unclear_fn_counter)
                    rp_summaries['unique_patient_id_tps'] += (len(unique_patient_id_cleaned) - unique_patient_id_fn_counter)
                    rp_summaries['url_ip_tps'] += (len(url_ip_cleaned) - url_ip_fn_counter)
                    rp_summaries['vehicle_device_id_tps'] += (len(vehicle_device_id_cleaned) - vehicle_device_id_fn_counter)
                #rp_summaries['profession_tps'] += (len(profession_cleaned) - profession_fn_counter)

                ####### Get FP tags #########
                fp_tag_summary = {}
                #print(cleaned_with_pos)
                if current_summary['false_positives'] != [] and current_summary['false_positives'] != [""]:              

                    current_fps = current_summary['false_positives']
                    counter = 0
                    #print(current_fps)
                    for word in current_fps:
                        counter += 1
                        false_positive = word[0]
                        start_coordinate_fp = word[1]
                     
                        pos_entry = cleaned_with_pos[str(start_coordinate_fp)]

                        pos_tag = pos_entry[1]

                        # Get 15 characters surrounding FP on either side
                        fp_context = ''
                        context_start = start_coordinate_fp - 15
                        context_end = start_coordinate_fp + len(false_positive) + 15
                        if context_start >= 0 and context_end <= len(text)-1:
                            fp_context = text[context_start:context_end]
                        elif context_start >= 0 and context_end > len(text)-1:
                            fp_context = text[context_start:]
                        else:
                            fp_context = text[:context_end]


                        fp_id = "P" + str(counter)
                        fp_tag_summary[fp_id] = [false_positive, pos_tag, fp_context]

                if fp_tag_summary != {}:
                    fp_tags[fn] = fp_tag_summary
            
            # Create frequency table outputs
            if self.freq_table:
                # Unigram table
                with open('./data/phi/unigram_freq_table.csv','w') as f:
                    f.write('unigram,phi_count,non-phi_count\n')
                    for key in unigram_dict:
                        word = key
                        phi_count = unigram_dict[key][0]
                        non_phi_count = unigram_dict[key][1]
                        f.write(word + ',' + str(phi_count) + ',' + str(non_phi_count) + '\n')
                with open('./data/phi/bigranm_freq_table.csv','w') as f:
                    f.write('bigram,phi_count,non-phi_count\n')
                    for key in bigram_dict:
                        term = key
                        phi_count = bigram_dict[key][0]
                        non_phi_count = bigram_dict[key][1]
                        f.write(term + ',' + str(phi_count) + ',' + str(non_phi_count) + '\n')

            # get specific recalls
            # i2b2
            if not self.ucsf_format:
                # Get names recall
                if rp_summaries['names_tps'] != 0:
                    names_recall = (rp_summaries['names_tps']-rp_summaries['names_fns'])/rp_summaries['names_tps']
                if (rp_summaries['names_tps']-rp_summaries['names_fns']) < 0 or rp_summaries['names_tps'] == 0:
                    names_recall = 0
                
                # Get dates recall
                if rp_summaries['dates_tps'] != 0:
                    dates_recall = (rp_summaries['dates_tps']-rp_summaries['dates_fns'])/rp_summaries['dates_tps']
                if (rp_summaries['dates_tps']-rp_summaries['dates_fns']) < 0 or rp_summaries['dates_tps'] == 0:
                    dates_recall = 0            
                
                # Get ids recall
                if rp_summaries['id_tps'] != 0:
                    ids_recall = (rp_summaries['id_tps']-rp_summaries['id_fns'])/rp_summaries['id_tps']
                if (rp_summaries['id_tps']-rp_summaries['id_fns']) < 0 or rp_summaries['id_tps'] == 0:
                    ids_recall = 0            
                
                # Get contact recall
                if rp_summaries['contact_tps'] != 0:
                    contact_recall = (rp_summaries['contact_tps']-rp_summaries['contact_fns'])/rp_summaries['contact_tps']
                if (rp_summaries['contact_tps']-rp_summaries['contact_fns']) < 0 or rp_summaries['contact_tps'] == 0:
                    contact_recall = 0            
                
                # Get location recall
                if rp_summaries['location_tps'] != 0:
                    location_recall = (rp_summaries['location_tps']-rp_summaries['location_fns'])/rp_summaries['location_tps']
                if (rp_summaries['location_tps']-rp_summaries['location_fns']) < 0 or rp_summaries['location_tps'] == 0:
                    location_recall = 0
                
                # Get organization recall
                if rp_summaries['organization_tps'] != 0:
                    organization_recall = (rp_summaries['organization_tps']-rp_summaries['organization_fns'])/rp_summaries['organization_tps']
                if (rp_summaries['organization_tps']-rp_summaries['organization_fns']) < 0 or rp_summaries['organization_tps'] == 0:
                    organization_recall = 0             
            
                # Get age recall
                if rp_summaries['age_tps'] != 0:
                    age_recall = (rp_summaries['age_tps']-rp_summaries['age_fns'])/rp_summaries['age_tps']
                if (rp_summaries['age_tps']-rp_summaries['age_fns']) < 0 or rp_summaries['age_tps'] == 0:
                    age_recall = 0 
            

                # Print to terminal
                print('\n')
                print("Names Recall: " + "{:.2%}".format(names_recall))
                print("Dates Recall: " + "{:.2%}".format(dates_recall))
                print("IDs Recall: " + "{:.2%}".format(ids_recall))
                print("Contact Recall: " + "{:.2%}".format(contact_recall))
                print("Location Recall: " + "{:.2%}".format(location_recall))
                print("Organization Recall: " + "{:.2%}".format(organization_recall))
                print("Age>=90 Recall: " + "{:.2%}".format(age_recall))
                print('\n')

            # ucsf
            if self.ucsf_format:

                # account # recall
                if rp_summaries['account_number_fns'] != 0:
                    if rp_summaries['account_number_tps'] != 0 and (rp_summaries['account_number_tps']-rp_summaries['account_number_fns']) > 0:
                        account_number_recall = (rp_summaries['account_number_tps']-rp_summaries['account_number_fns'])/rp_summaries['account_number_tps']
                    else:
                        account_number_recall = 0
                else:
                    account_number_recall = 1
                
                # address recall
                if rp_summaries['address_fns'] != 0:
                    if rp_summaries['address_tps'] != 0 and (rp_summaries['address_tps']-rp_summaries['address_fns']) > 0:
                        address_recall = (rp_summaries['address_tps']-rp_summaries['address_fns'])/rp_summaries['address_tps']
                    else:
                        address_recall = 0
                else:
                    address_recall = 1        
                
                # Age recall
                if rp_summaries['age_fns'] != 0:
                    if rp_summaries['age_tps'] != 0 and (rp_summaries['age_tps']-rp_summaries['age_fns']) > 0:
                        age_recall = (rp_summaries['age_tps']-rp_summaries['age_fns'])/rp_summaries['age_tps']
                    else:
                        age_recall = 0
                else:
                    age_recall = 1        
                
                # biometric_or_photo_id recall
                if rp_summaries['biometric_or_photo_id_fns'] != 0:
                    if rp_summaries['biometric_or_photo_id_tps'] != 0 and (rp_summaries['biometric_or_photo_id_tps']-rp_summaries['biometric_or_photo_id_fns']) > 0:
                        biometric_or_photo_id_recall = (rp_summaries['biometric_or_photo_id_tps']-rp_summaries['biometric_or_photo_id_fns'])/rp_summaries['biometric_or_photo_id_tps']
                    else:
                        biometric_or_photo_id_recall = 0    
                else:
                    biometric_or_photo_id_recall = 1     
                
                # certificate_license_id recall
                if rp_summaries['certificate_license_id_fns'] != 0:
                    if rp_summaries['certificate_license_id_tps'] != 0 and (rp_summaries['certificate_license_id_tps']-rp_summaries['certificate_license_id_fns']) > 0:
                        certificate_license_id_recall = (rp_summaries['certificate_license_id_tps']-rp_summaries['certificate_license_id_fns'])/rp_summaries['certificate_license_id_tps']
                    else:
                        certificate_license_id_recall = 0
                else:
                    certificate_license_id_recall = 1
                
                # date recall
                if rp_summaries['date_fns'] != 0:
                    if rp_summaries['date_tps'] != 0 and (rp_summaries['date_tps']-rp_summaries['date_fns']) > 0:
                        date_recall = (rp_summaries['date_tps']-rp_summaries['date_fns'])/rp_summaries['date_tps']
                    else:
                        date_recall = 0
                else:
                    date_recall = 1      
            
                # email recall
                if rp_summaries['email_fns'] != 0:
                    if rp_summaries['email_tps'] != 0 and (rp_summaries['email_tps']-rp_summaries['email_fns']) > 0:
                        email_recall = (rp_summaries['email_tps']-rp_summaries['email_fns'])/rp_summaries['email_tps']
                    else:
                        email_recall = 0 
                else:
                    email_recall = 1

                # initials recall
                if rp_summaries['initials_fns'] != 0:
                    if rp_summaries['initials_tps'] != 0 and (rp_summaries['initials_tps']-rp_summaries['initials_fns']) > 0:
                        initials_recall = (rp_summaries['initials_tps']-rp_summaries['initials_fns'])/rp_summaries['initials_tps']
                    else:
                        initials_recall = 0 
                else:
                    initials_recall = 1
               
                # mrn id recall
                if rp_summaries['mrn_id_fns'] != 0:
                    if rp_summaries['mrn_id_tps'] != 0 and (rp_summaries['mrn_id_tps']-rp_summaries['mrn_id_fns']) > 0:
                        mrn_id_recall = (rp_summaries['mrn_id_tps']-rp_summaries['mrn_id_fns'])/rp_summaries['mrn_id_tps']
                    else:
                        mrn_id_recall = 0
                else:
                    mrn_id_recall = 1
                
                # patient_family_name recall
                if rp_summaries['patient_family_name_fns'] != 0:
                    if rp_summaries['patient_family_name_tps'] != 0 and (rp_summaries['patient_family_name_tps']-rp_summaries['patient_family_name_fns']) > 0:
                        patient_family_name_recall = (rp_summaries['patient_family_name_tps']-rp_summaries['patient_family_name_fns'])/rp_summaries['patient_family_name_tps']
                    else:
                        patient_family_name_recall = 0    
                else:
                    patient_family_name_recall = 1   
                
                # phone/fax recall
                if rp_summaries['phone_fax_fns'] != 0:
                    if rp_summaries['phone_fax_tps'] != 0 and (rp_summaries['phone_fax_tps']-rp_summaries['phone_fax_fns']) > 0:
                        phone_fax_recall = (rp_summaries['phone_fax_tps']-rp_summaries['phone_fax_fns'])/rp_summaries['phone_fax_tps']
                    else:
                        phone_fax_recall = 0   
                else:
                    phone_fax_recall = 1     
                
                # provider_name recall
                if rp_summaries['provider_name_fns'] != 0:
                    if rp_summaries['provider_name_tps'] != 0 and (rp_summaries['provider_name_tps']-rp_summaries['provider_name_fns']) > 0:
                        provider_name_recall = (rp_summaries['provider_name_tps']-rp_summaries['provider_name_fns'])/rp_summaries['provider_name_tps']
                    else:
                        provider_name_recall = 0  
                else:
                    provider_name_recall = 1      
                
                # social_security recall
                if rp_summaries['social_security_fns'] != 0:
                    if rp_summaries['social_security_tps'] != 0 and (rp_summaries['social_security_tps']-rp_summaries['social_security_fns']) > 0:
                        social_security_recall = (rp_summaries['social_security_tps']-rp_summaries['social_security_fns'])/rp_summaries['social_security_tps']
                    else:
                        social_security_recall = 0
                else:
                    social_security_recall = 1
                
                # unclear recall
                if rp_summaries['unclear_fns'] != 0:
                    if rp_summaries['unclear_tps'] != 0 and (rp_summaries['unclear_tps']-rp_summaries['unclear_fns']) > 0:
                        unclear_recall = (rp_summaries['unclear_tps']-rp_summaries['unclear_fns'])/rp_summaries['unclear_tps']
                    else:
                        unclear_recall = 0   
                else:
                    unclear_recall = 1     
            
                # unique_patient_id recall
                if rp_summaries['unique_patient_id_fns'] != 0:
                    if rp_summaries['unique_patient_id_tps'] != 0 and (rp_summaries['unique_patient_id_tps']-rp_summaries['unique_patient_id_fns']) > 0:
                        unique_patient_id_recall = (rp_summaries['unique_patient_id_tps']-rp_summaries['unique_patient_id_fns'])/rp_summaries['unique_patient_id_tps']
                    else:
                        unique_patient_id_recall = 0    
                else:
                    unique_patient_id_recall = 1
                
                # url_ip recall
                if rp_summaries['url_ip_fns'] != 0:
                    if rp_summaries['url_ip_tps'] != 0 and (rp_summaries['url_ip_tps']-rp_summaries['url_ip_fns']) > 0:
                        url_ip_recall = (rp_summaries['url_ip_tps']-rp_summaries['url_ip_fns'])/rp_summaries['url_ip_tps']
                    else:
                        url_ip_recall = 0  
                else:
                    url_ip_recall = 1    
            
                # vehicle_device_id recall
                if rp_summaries['vehicle_device_id_fns'] != 0:
                    if rp_summaries['vehicle_device_id_tps'] != 0 and (rp_summaries['vehicle_device_id_tps']-rp_summaries['vehicle_device_id_fns']) > 0:
                        vehicle_device_id_recall = (rp_summaries['vehicle_device_id_tps']-rp_summaries['vehicle_device_id_fns'])/rp_summaries['vehicle_device_id_tps']
                    else:
                        vehicle_device_id_recall = 0
                else:
                    vehicle_device_id_recall = 1

                # Print to terminal
                print('\n')
                print("Account Number Recall: " + "{:.2%}".format(account_number_recall))
                print("Address Recall: " + "{:.2%}".format(address_recall))
                print("Age Recall: " + "{:.2%}".format(age_recall))
                print("Biometric ID and Face Photo Recall: " + "{:.2%}".format(biometric_or_photo_id_recall))
                print("Certificate and License Number Recall: " + "{:.2%}".format(certificate_license_id_recall))
                print("Date Recall: " + "{:.2%}".format(date_recall))
                print("Email Recall: " + "{:.2%}".format(email_recall))
                print("Initials Recall: " + "{:.2%}".format(initials_recall))
                print("Medical Record Number Recall: " + "{:.2%}".format(mrn_id_recall))
                print("Patient or Family Member Name Recall: " + "{:.2%}".format(patient_family_name_recall))
                print("Phone and Fax Recall: " + "{:.2%}".format(phone_fax_recall))
                print("Provider Name Recall: " + "{:.2%}".format(provider_name_recall))
                print("Social Security Recall: " + "{:.2%}".format(social_security_recall))
                print("Unclear PHI Recall: " + "{:.2%}".format(unclear_recall))
                print("Unique Patient Identifier Recall: " + "{:.2%}".format(unique_patient_id_recall))
                print("URL and IP Address Recall: " + "{:.2%}".format(url_ip_recall))
                print("Vehicle and Device ID Recall: " + "{:.2%}".format(vehicle_device_id_recall))
                print('\n')


            ######## Summarize FN results #########
            
            ##### With and without context #####
            
            # With context:
            # Condensed tags will contain id, word, PHI tag, POS tag, occurrences
            fn_tags_condensed_context = {}
            # Stores lists that represent distinct groups of words, PHI and POS tags
            fn_tags_condensed_list_context = []
            
            # No context:
            # Condensed tags will contain id, word, PHI tag, POS tag, occurrences
            fn_tags_condensed = {}
            # Stores lists that represent distinct groups of words, PHI and POS tags
            fn_tags_condensed_list = []

            # Keep track of how many distinct combinations we've added to each list
            context_counter = 0
            nocontext_counter = 0

            for fn in fn_tags:
                file_dict = fn_tags[fn] 
                for subfile in file_dict:
                    current_list_context = file_dict[subfile]
                    current_list_nocontext = current_list_context[:3]
                    
                    word = current_list_context[0]
                    phi_tag = current_list_context[1]
                    pos_tag = current_list_context[2]
                    fn_context = current_list_context[3].replace("\n"," ")
                    #Context
                    if current_list_context not in fn_tags_condensed_list_context:                      
                        fn_tags_condensed_list_context.append(current_list_context)
                        key_name = "uniq" + str(context_counter)
                        fn_tags_condensed_context[key_name] = [word, phi_tag, pos_tag, fn_context, 1]
                        context_counter += 1
                    else:
                        uniq_id_index = fn_tags_condensed_list_context.index(current_list_context)
                        uniq_id = "uniq" + str(uniq_id_index)
                        fn_tags_condensed_context[uniq_id][4] += 1

                    # No context
                    if current_list_nocontext not in fn_tags_condensed_list:   
                        fn_tags_condensed_list.append(current_list_nocontext)
                        key_name = "uniq" + str(nocontext_counter)
                        fn_tags_condensed[key_name] = [word, phi_tag, pos_tag, 1]
                        nocontext_counter += 1
                    else: 
                        uniq_id_index = fn_tags_condensed_list.index(current_list_nocontext)
                        uniq_id = "uniq" + str(uniq_id_index)
                        fn_tags_condensed[uniq_id][3] += 1

            ####### Summariz FP results #######

            # With context
            # Condensed tags will contain id, word, POS tag, occurrences
            fp_tags_condensed_context = {}
            # Stores lists that represent distinct groups of wordss and POS tags
            fp_tags_condensed_list_context = []

            # No context
            # Condensed tags will contain id, word, POS tag, occurrences
            fp_tags_condensed = {}
            # Stores lists that represent distinct groups of wordss and POS tags
            fp_tags_condensed_list = []

            # Keep track of how many distinct combinations we've added to each list
            context_counter = 0
            nocontext_counter = 0
            for fp in fp_tags:
                file_dict = fp_tags[fp] 
                for subfile in file_dict:
                    current_list_context = file_dict[subfile]
                    current_list_nocontext = current_list_context[:2]

                    word = current_list_context[0]
                    pos_tag = current_list_context[1]
                    fp_context = current_list_context[2].replace("\n"," ")

                    # Context
                    if current_list_context not in fp_tags_condensed_list_context:
                        fp_tags_condensed_list_context.append(current_list_context)
                        key_name = "uniq" + str(context_counter)
                        fp_tags_condensed_context[key_name] = [word, pos_tag, fp_context, 1]
                        context_counter += 1
                    else:
                        uniq_id_index = fp_tags_condensed_list_context.index(current_list_context)
                        uniq_id = "uniq" + str(uniq_id_index)
                        fp_tags_condensed_context[uniq_id][3] += 1          

                    # No Context
                    if current_list_nocontext not in fp_tags_condensed_list:
                        fp_tags_condensed_list.append(current_list_nocontext)
                        key_name = "uniq" + str(nocontext_counter)
                        fp_tags_condensed[key_name] = [word, pos_tag, 1]
                        nocontext_counter += 1
                    else:
                        uniq_id_index = fp_tags_condensed_list.index(current_list_nocontext)
                        uniq_id = "uniq" + str(uniq_id_index)
                        fp_tags_condensed[uniq_id][2] += 1 

            # Write FN and FP results to outfolder
            # Conext
            with open(fn_tags_context, "w") as fn_file:
                fn_file.write("key" + "|" + "note_word" + "|" + "phi_tag" + "|" + "pos_tag" + "|" + "context" + "|" + "occurrences"+"\n")
                # print(fn_tags_condensed_context)
                for key in fn_tags_condensed_context:
                    current_list = fn_tags_condensed_context[key]
                    fn_file.write(key + "|" + current_list[0] + "|" + current_list[1] + "|" + current_list[2] + "|" + current_list[3] + "|" + str(current_list[4])+"\n")
            
            with open(fp_tags_context, "w") as fp_file:
                fp_file.write("key" + "|" + "note_word" + "|" + "pos_tag" + "|" + "context" + "|" + "occurrences"+"\n")
                for key in fp_tags_condensed_context:
                    current_list = fp_tags_condensed_context[key]
                    fp_file.write(key + "|" + current_list[0] + "|" + current_list[1]  + "|" +  current_list[2] + "|" + str(current_list[3])+"\n")

            # No context
            with open(fn_tags_nocontext, "w") as fn_file:
                fn_file.write("key" + "|" + "note_word" + "|" + "phi_tag" + "|" + "pos_tag" + "|" + "occurrences"+"\n")
                for key in fn_tags_condensed:
                    current_list = fn_tags_condensed[key]
                    fn_file.write(key + "|" + current_list[0] + "|" + current_list[1] + "|" + current_list[2] + "|" + str(current_list[3])+"\n")
            
            with open(fp_tags_nocontext, "w") as fp_file:
                fp_file.write("key" + "|" + "note_word" + "|" + "pos_tag" + "|" + "occurrences"+"\n")
                for key in fp_tags_condensed:
                    current_list = fp_tags_condensed[key]
                    fp_file.write(key + "|" + current_list[0] + "|" + current_list[1]  + "|" +  str(current_list[2])+"\n")            
            
            if self.parallel:
                # Get info on whitelist, blacklist, POS
                patterns = json.loads(open(config["filters"], "r").read())
                current_whitelist = ''
                current_blacklist = ''
                current_pos = ''
                for config_dict in patterns:
                    if config_dict['type'] == 'set' and config_dict['exclude'] == True:
                        current_blacklist = config_dict['filepath'].split('/')[-1].split('.')[0]
                        current_pos = str(config_dict['pos']).replace(" ","")
                    if config_dict['type'] == 'set' and config_dict['exclude'] == False:
                        current_whitelist = config_dict['filepath'].split('/')[-1].split('.')[0]
                
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
                "foo.txt":[
                    {
                        "phi":"1/1/2019",
                        "context":"The data was 1/1/2019 and the patient was happy",
                        "class":"numer" //number, string ... 
                    },...
                ],...
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
                    if not os.path.exists(anno_folder+f.split(".")[0]+anno_suffix):
                        print("FILE DOESNT EXIST", anno_folder+f.split(".")[0]+anno_suffix)
                        continue
                else:
                    if not os.path.exists(anno_folder+f):
                        print("FILE DOESNT EXIST", anno_folder+f)
                        continue

                orig_filename = root+f
                encoding1 = self.detect_encoding(orig_filename)
                orig = open(orig_filename,"r", encoding=encoding1['encoding']).read()

                orig_words = re.split("\s+", orig)

                anno_filename = anno_folder+f.split(".")[0]+anno_suffix
                encoding2 = self.detect_encoding(anno_filename)
                anno = open(anno_filename,"r", encoding=encoding2['encoding']).read()
                anno_words = re.split("\s+", anno)

                anno_dict = {}
                orig_dict = {}

                for w in anno_words:
                    anno_dict[w] = 1

                for i,w in enumerate(orig_words):

                    #check for edge cases that should not be "words"
                    x = w.replace("_","").strip()
                    if len(x) == 0:
                        continue

                    #add all words to our counts
                    if w not in word_counts:
                        word_counts[w] = 0
                    word_counts[w] += 1

                    #check if this word is phi
                    if w not in anno_dict:

                        left_index = i - 10
                        if left_index < 0:
                            left_index = 0

                        right_index = i + 10
                        if right_index >= len(orig_words):
                            right_index = len(orig_words) - 1
                        window = orig_words[left_index:right_index]
                        if f not in phi:
                            phi[f] = []

                        c = "string"
                        if re.search("\d+", w):
                            c = "number"

                        phi[f].append({"phi":w,"context":window,"class":c})
                    else:
                        #add all words to our counts
                        if w not in not_phi:
                            not_phi[w] = 0
                        not_phi[w] += 1

        #save our phi with context
        json.dump(phi, open("data/phi/phi_context.json", "w"), indent=4)

        #save all phi word counts
        counts = {}
        num_phi = {}
        string_phi = {}
        
        for f in phi:
            for d in phi[f]:
                if d["phi"] not in counts:
                    counts[d["phi"]] = 0
                counts[d["phi"]] += 1
                if d["class"] == "number":
                    if d["phi"] not in num_phi:
                        num_phi[d["phi"]] = 0
                    num_phi[d["phi"]] += 1
                else:
                    if d["phi"] not in string_phi:
                        string_phi[d["phi"]] = 0
                    string_phi[d["phi"]] += 1

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
                    non_phi_number[w] = 0
                non_phi_number[w] += 1
            else:
                if w not in non_phi_string:
                    non_phi_string[w] = 0
                non_phi_string[w] += 1

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
            wordlst = []
            phi_word = phi["phi"]
            for c in phi_word:
                if re.match("\d+", c):
                    wordlst.append(digit_char)
                elif re.match("[a-zA-Z]+", c):
                    wordlst.append(string_char)
                else:
                    wordlst.append(c)
            word = "".join(wordlst)
            if word not in phi_map:
                phi_map[word] = {'examples':{}}
            if phi_word not in phi_map[word]['examples']:
                phi_map[word]['examples'][phi_word] = []
            phi_map[word]['examples'][phi_word].append(phi) 

        #save the count of all representations
        for k in phi_map:
            phi_map[k]["count"] = len(phi_map[k]["examples"].keys())

        #save all representations
        json.dump(phi_map, open(out_path, "w"), indent=4)

        #save an ordered list of representations so we can prioritize regex building
        items = []
        for k in phi_map:
            items.append({"pattern":k, "examples":phi_map[k]["examples"], "count":len(phi_map[k]["examples"].keys())})

        items.sort(key=lambda x: x["count"], reverse=True)
        json.dump(items, open(sorted_path, "w"), indent=4)





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
        if "filters" in config:
            if not os.path.exists(config["filters"]):
                raise Exception("Filepath does not exist", config["filters"])
            self.patterns = json.loads(open(config["filters"], "r").read())

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
        
    def precompile(self, filepath):
        """ precompiles our regex to speed up pattern matching"""
        day_name = "(S|s)un(day)?(s)?|SUN(DAY)?(S)?|(M|m)on(day)?(s)?|MON(DAY)?(S)?|(T|t)ues(day)?(s)?|Tue|TUES(DAY)?(S)?|(W|w)ed(nesday)?(s)?|WED(NESDAY)?(S)?|(T|t)hurs(day)?(s)?|Thu|THURS(DAY)?(S)?|(F|f)ri(day)?(s)?|FRI(DAY)?(S)?|(S|s)at(urday)?(s)?|SAT(URDAY)?(S)?"
        month_name = "(J|j)an(uary)?|JAN(UARY)?|(F|f)eb(ruary)?|FEB(RUARY)?|(M|m)ar(ch)?|MAR(CH)?|(A|a)pr(il)?|APR(IL)?|(M|m)ay|MAY|(J|j)un(e)?|JUN(E)?|(J|j)ul(y)?|JUL(Y)?|(A|a)ug(ust)?|AUG(UST)?|(S|s)ep(tember)?|SEP(TEMBER)?|SEPT|(O|o)ct(ober)?|OCT(OBER)?|(N|n)ov(ember)?|NOV(EMBER)?|(D|d)ec(ember)?|DEC(EMBER)?"
        day_numbering = "1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th|11th|12th|13th|14th|15th|16th|17th|18th|19th|20th|21st|22nd|23rd|24th|25th|26th|27th|28th|29th|30th|31st"
        seasons = "(S|s)pring|SPRING|(F|f)all|FALL|(A|a)utumn|AUTUMN|(W|w)inter|WINTER|(S|s)ummer|SUMMER|(C|c)hristmas|(N|n)ew (Y|y)ear's (E|e)ve"
        
        regex = open(filepath,"r").read().strip()
        regex = regex.replace('"""+month_name+r"""', month_name).replace('"""+day_numbering+r"""', day_numbering).replace('"""+day_name+r"""', day_name).replace('"""+seasons+r"""', seasons) 
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
                    if self.debug:
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

                
    def map_regex(self, filename="", text="", pattern_index=-1):
        """ Creates a coordinate map from the pattern on this data
            generating a coordinate map of hits given (dry run doesn't transform)
        """
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))
        coord_map = self.patterns[pattern_index]["coordinate_map"]
        regex = self.patterns[pattern_index]["data"]

        
        if regex != re.compile('.'):
            matches = regex.finditer(text)
            
            for m in matches:
                # if filename == './data/i2b2_notes/312-04.txt':
                #     print(m)
                coord_map.add_extend(filename, m.start(), m.start()+len(m.group()))
        
            self.patterns[pattern_index]["coordinate_map"] = coord_map
        
        elif regex == re.compile('.'):
            start_coordinate = 0
            pre_process= re.compile(r"[^a-zA-Z0-9]")
            for w in re.split("(\s+)", text):
                stop = start_coordinate+len(w)
                if len(pre_process.sub("", w.lower().strip())) == 0:
                    #got a blank space or something without any characters or digits, move forward
                    start_coordinate = stop
                    continue
                if regex.match(w):
                    coord_map.add_extend(filename,start_coordinate, stop)
                start_coordinate = stop
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


    def map_set(self, filename="", text="", pattern_index=-1,  pre_process= r"[^a-zA-Z0-9]+"):
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

        #preserve spaces while getting POS. 
        lst = re.split("(\s+)", text)
        cleaned = []
        for item in lst:
            if len(item) > 0:
                cleaned.append(item)
        pos_list = nltk.pos_tag(cleaned)

        start_coordinate = 0
        for tup in pos_list:
            word = tup[0]
            pos  = tup[1]
            start = start_coordinate
            stop = start_coordinate + len(word)
            word_clean = re.sub(pre_process, "", word.lower().strip())
            if len(word_clean) == 0:
                #got a blank space or something without any characters or digits, move forward
                start_coordinate += len(word)
                continue

            if check_pos == False or (check_pos == True and pos in pos_set):

                if word_clean in map_set or word in map_set:
                    coord_map.add_extend(filename, start, stop)
                    #print("FOUND: ",word, "COORD: ",  text[start:stop])
                else:
                    #print("not in set: ",word, "COORD: ",  text[start:stop])
                    pass
                    
            #advance our start coordinate
            start_coordinate += len(word)

        self.patterns[pattern_index]["coordinate_map"] = coord_map

    def map_pos(self, filename="", text="", pattern_index=-1, pre_process= r"[^a-zA-Z0-9]+"):
        """ Creates a coordinate mapping of words which match this part of speech (POS)"""
        if not os.path.exists(filename):
            raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))

        if "pos" not in self.patterns[pattern_index]:
            raise Exception("Mapping POS must include parts of speech", pattern_index, "pattern length", len(patterns))
            
        coord_map = self.patterns[pattern_index]["coordinate_map"]
        pos_set = set(self.patterns[pattern_index]["pos"])
        
        #preserve spaces while getting POS. 
        lst = re.split("(\s+)", text)
        cleaned = []
        for item in lst:
            if len(item) > 0:
                cleaned.append(item)
        pos_list = nltk.pos_tag(cleaned)

        start_coordinate = 0
        for tup in pos_list:
            word = tup[0]
            pos  = tup[1]
            start = start_coordinate
            stop = start_coordinate + len(word)
            word_clean = re.sub(pre_process, "", word.lower().strip())
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

        if not os.path.exists(in_path):
            raise Exception("Filepath does not exist", in_path)
        if not os.path.exists(out_path):
            raise Exception("Filepath does not exist", out_path)

        punctuation_matcher = re.compile(r"[^a-zA-Z0-9*]")

        if self.debug:
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
            with open(out_path+f, "w") as f:
                
                #keep any matches in our include map
                
                data[filename]["text"] = txt
                
                last_marker = 0
                current_chunk = []

                #read the text by character, any non-punc non-overlaps will be replaced
                contents = []
                for i in range(0, len(txt)):

                    if i < last_marker:
                        continue

                    if include_map.does_exist(filename, i):
                        #add our preserved text
                        start,stop = include_map.get_coords(filename, i)
                        contents.append(txt[start:stop])
                        last_marker = stop
                    elif punctuation_matcher.match(txt[i]):
                        contents.append(txt[i])
                    else:
                        contents.append("*")

                f.write("".join(contents))

        #output our data for eval
        json.dump(data, open("./data/coordinates.json", "w"), indent=4)

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
            punctuation_matcher=re.compile(r"[^a-zA-Z0-9*]"), 
            text_matcher=re.compile(r"[a-zA-Z0-9]"), 
            phi_matcher=re.compile(r"\*+")):
        """ 
            Compares two sequences item by item, 
            returns generator which yields: 
            classifcation, word

            classifications can be TP, FP, FN, TN 
            corresponding to True Positive, False Positive, False Negative and True Negative
        """
        

        for note_word, anno_word in list(zip(note_lst, anno_lst)):
            
            #print(note_word, anno_word)

            if phi_matcher.search(anno_word):
                #this contains phi
                
                if note_word == anno_word:
                    #print(note_word, anno_word, "TP")
                    yield "TP", note_word
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
                            yield "FN", w
                        for w in fp_words:
                            yield "FP", w
                    else:
                        #simpler case, anno word is completely blocked out except punctuation
                        yield "FN", note_word

            else:
                #this isn't phi
                if note_word == anno_word:
                    #print(note_word, anno_word, "TN")
                    yield "TN", note_word
                else:
                    #print(note_word, anno_word, "FP")
                    yield "FP", anno_word

            


    def eval(self,
        anno_path="data/i2b2_anno/",
        anno_suffix="_phi_reduced.ano", 
        in_path="data/i2b2_results/",
        summary_output="data/phi/summary.json",
        phi_matcher=re.compile("\*+"),
        pre_process=r":|\-|\/|_|~", #characters we're going to strip from our notes to analyze against anno
        only_digits=False,
        fn_output="data/phi/fn.json",
        fp_output="data/phi/fp.json"):
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
        if self.debug:
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

        punctuation_matcher = re.compile(r"[^a-zA-Z0-9]")
        all_fn = []
        all_fp = []

        for root, dirs, files in os.walk(in_path):

            for f in files:

                #local values per file
                false_positives = [] #non-phi we think are phi
                true_positives  = [] #phi we correctly identify
                false_negatives = [] #phi we think are non-phi
                true_negatives  = [] #non-phi we correctly identify

                philtered_filename = root+f
                anno_filename = anno_path+''.join(f.split(".")[0])+anno_suffix

                # if len(anno_suffix) > 0:
                #     anno_filename = anno_folder+f.split(".")[0]+anno_suffix

                if not os.path.exists(philtered_filename):
                    raise Exception("FILE DOESNT EXIST", philtered_filename)
                
                if not os.path.exists(anno_filename):
                    print("FILE DOESNT EXIST", anno_filename)
                    continue

                encoding1 = self.detect_encoding(philtered_filename)
                philtered = open(philtered_filename,"r", encoding=encoding1['encoding']).read()
                philtered_words = re.split("\s+", philtered)
                
                encoding2 = self.detect_encoding(anno_filename)
                anno = open(anno_filename,"r", encoding=encoding2['encoding']).read()
                anno_words = re.split("\s+", anno)


                for c,w in self.seq_eval(philtered_words, anno_words):
                    
                    if c == "FP":
                        false_positives.append(w)
                    elif c == "FN":
                        #todo get context: phi = self.phi_context(philtered_filename, w, i, philtered_words)
                        #phi = {"file":philtered_filename, "word":w}
                        false_negatives.append(w)
                    elif c == "TP":
                        true_positives.append(w)
                    elif c == "TN":
                        true_negatives.append(w)

                #print("TOTAL WORDS: ",total_words,"true_positives: ", true_positives,"false_positives: ", len(false_positives),"false_negatives: ", len(false_negatives),"true_negatives: ", len(true_negatives))
                #print(false_negatives, false_positives)
                #update summary
                summary["summary_by_file"][philtered_filename] = {"false_positives":false_positives,"false_negatives":false_negatives, "num_false_negatives":len(false_negatives)}
                summary["total_true_positives"] = summary["total_true_positives"] + len(true_positives)
                summary["total_false_positives"] = summary["total_false_positives"] + len(false_positives)
                summary["total_false_negatives"] = summary["total_false_negatives"] + len(false_negatives)
                summary["total_true_negatives"] = summary["total_true_negatives"] + len(true_negatives)
                all_fp = all_fp + false_positives
                all_fn = all_fn + false_negatives

                #print(len(summary["true_positives"]), len(summary["false_positives"]), len(summary["true_negatives"]), len(summary["false_negatives"]) )

        print("true_negatives", summary["total_true_negatives"],"true_positives", summary["total_true_positives"], "false_negatives", summary["total_false_negatives"], "false_positives", summary["total_false_positives"])

        if summary["total_true_positives"]+summary["total_false_negatives"] > 0:
            print("Recall: {:.2%}".format(summary["total_true_positives"]/(summary["total_true_positives"]+summary["total_false_negatives"])))
        elif summary["total_false_negatives"] == 0:
            print("Recall: 100%")

        if summary["total_true_positives"]+summary["total_false_positives"] > 0:
            print("Precision: {:.2%}".format(summary["total_true_positives"]/(summary["total_true_positives"]+summary["total_false_positives"])))
        elif summary["total_true_positives"] == 0:
            print("Precision: 0.00%")


        if summary["total_true_negatives"]+summary["total_false_positives"] > 0:
            print("Retention: {:.2%}".format(summary["total_true_negatives"]/(summary["total_true_negatives"]+summary["total_false_positives"])))
        else:
            print("Retention: 0.00%")

        #save the phi we missed
        json.dump(summary, open(summary_output, "w"), indent=4)
        json.dump(all_fn, open(fn_output, "w"), indent=4)
        json.dump(all_fp, open(fp_output, "w"), indent=4)


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



























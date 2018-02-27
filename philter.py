
import re
import json
import os
import nltk
import chardet
from chardet.universaldetector import UniversalDetector
from nltk.stem.wordnet import WordNetLemmatizer
from coordinate_map import CoordinateMap

class Philter:
    """ 
        General text filtering class,
        can filter using whitelists, blacklists, regex's and POS
    """
    def __init__(self, config):
        if "debug" in config:
            self.debug = config["debug"]
        if "finpath" in config:
            self.finpath = config["finpath"]
        if "foutpath" in config:
            self.foutpath = config["foutpath"]
        if "anno_folder" in config:
            self.anno_folder = config["anno_folder"]
        if "patterns" in config:
            self.patterns = json.load(open(config["patterns"], "r").read())

        #All coordinate maps stored here
        self.coordinate_maps = []

        #initialize our patterns
        self.init_patterns()


    def init_patterns(self):
        """ given our input pattern config will load our sets and pre-compile our regex"""

        known_pattern_types = set(["regex", "set", "NER_tagging"])
        set_filetypes = set(["pkl", "json"])
        regex_filetypes = set(["txt"])
        reserved_list = set(["data", "coordinate_map"])

        #first check that data is formatted, can be loaded etc. 
        for pattern in self.patterns:
            if not os.path.exists(pattern["filepath"]):
                raise Exception("Filepath does not exist", pattern["filepath"])
            for k in reserved_list:
                if k in pattern:
                    raise Exception("Error, Keyword is reserved", k, pattern)
            if pattern["type"] not in known_pattern_types:
                raise Exception("Pattern type is unknown", pattern["type"])

            if pattern["type"] == "set":
                if pattern["filepath"].split(".")[-1] not in set_filetypes:
                    raise Exception("Invalid filteype", pattern["filepath"], "must be of", set_filetypes)
                self.patterns[pattern]["data"] = self.init_set(pattern["filepath"])  
            elif pattern["type"] == "regex":
                if pattern["filepath"].split(".")[-1] not in set_filetypes:
                    raise Exception("Invalid filteype", pattern["filepath"], "must be of", regex_filetypes)
                self.patterns[pattern]["data"] = self.precompile(pattern["filepath"])
        
    def precompile(self, filepath):
        """ precompiles our regex to speed up pattern matching"""
        regex = open(path+r["filepath"],"r").read().strip()
        return re.compile(regex)
               
    def init_set(self, filepath):
        """ loads a set of words, (must be a dictionary or set shape) returns result"""
        map_set = {}
        if filepath.endswith(".pkl"):
            with open(filepath, "rb") as pickle_file:
                map_set = pickle.load(pickle_file)
        elif b["filepath"].endswith(".json"):
            map_set = json.load(open(filepath, "r").read())
        else:
            raise Exception("Invalid filteype",b["filepath"])
        return map_set

    def map_coordinates(self, in_path="", allowed_filetypes=set(["txt", "ano"])):
        """ Runs the set, or regex on the input data 
            generating a coordinate map of hits given 
            (this performs a dry run on the data and doesn't transform)
        """
        
        #create coordinate maps for each pattern
        for pat in self.patterns:
            self.patterns[pat]["coordinate_map"] = CoordinateMap()

        for root, dirs, files in in_path:
            for f in files:

                filename = root+f
                if filename.split(".")[-1] not in allowed_filetypes:
                    if self.debug:
                        print("Skipping: ", filename)
                    continue

                encoding = self.detect_encoding(root+f)
                txt = open(filename,"r", encoding=encoding['encoding']).read()

                for i,pat in enumerate(self.patterns):
                    if pat["type"] == "regex":
                        self.map_regex(filename=filename, text=txt, pattern_index=i)
                    elif pat["type"] == "set":
                        self.map_set(filename=filename, text=txt, pattern_index=i)
                    elif pat["type"] == "NER_tagging":
                        self.map_ner(filename=filename, text=txt, pattern_index=i)
                    else:
                        raise Exception("Error, pattern type not supported: ", pat["type"])

                
    def map_regex(self, filename="", text="", pattern_index=-1):
        """ Creates a coordinate map from the pattern on this data
            generating a coordinate map of hits given (dry run doesn't transform)
        """
        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))
        coord_map = self.patterns[i]["coordinate_map"]
        matches = regex.finditer(txt)
        for m in matches:
           coord_map.add_extend(f, m.start(), m.start()+len(m.group()))
        self.patterns[i]["coordinate_map"] = coord_map


    def map_set(self, filename="", text="", pattern_index=-1):
        """ Creates a coordinate mapping of whitelisted words and transforms the text"""
        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(patterns))

        coord_map = self.patterns[i]["coordinate_map"]

        keep = []
        exclude = []
        start_cursor = 0
        end_cursor = 0

        words = re.split(r"(\s+)", txt)
        cursor = 0 #keeps track of the location of the start of the word in the text
        for i,w in enumerate(words):

            if w in ignore_set:
                continue

            end_cursor = start_cursor + len(w)

            #check if the basic word is in the set first,
            if inverse == False and w in map_set:
                coord_map.add_extend(filename, start_cursor, end_cursor)
                start_cursor = end_cursor
                continue

            #remove any punctuation and lowercase
            clean = re.sub(pre_process, " ", w)
            clean = clean.lower()

            # Lemmatize the word - first try assuming that the
            # word is a noun
            lemm_noun = self.lmtzr.lemmatize(clean, 'n')

            # Then try assuming that the word is a verb
            lemm_verb = self.lmtzr.lemmatize(clean, 'v')

            # Choose whichever word has the greatest change
            lemm = lemm_verb if len(lemm_verb) < len(lemm_noun) else lemm_noun

            # Double check - If the cleaned word has less than 3 characters,
            # then the rule didn't work.  Stick with the noun version
            if len(lemm) < 3:
                lemm = lemm_noun

            if lemm in ignore_set:
                continue

            if inverse == True and lemm not in map_set:
                #keep things not in set
                coord_map.add_extend(filename, start_cursor, end_cursor)
            elif inverse == False and lemm in map_set:
                coord_map.add_extend(filename, start_cursor, end_cursor)

            start_cursor = end_cursor

        return coord_map


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
            ORDER: blacklists supercede everything, whitelists are second priority
            Next are regex which support 3 default groups
            # filter regex runs as a first pass, blocks anything in group (ideally very precise)
            # extract regex runs as a second pass, keep anything in this group NOT in filter (ideally very precise)
            # filter_2 regex runs as a third pass, blocks anything in group, (generally a catch-all, general approach)
            
            **Anything not caught in these passes will be assumed to be PHI
        """

        if self.debug:
            print("transform")

        if not os.path.exists(in_path):
            raise Exception("File input path does not exist", in_path)
        
        if not os.path.exists(out_path):
            raise Exception("File output path does not exist", out_path)


        for root,filename in self.folder_walk(in_path):

            #create an intersection map of all coordinates we'll be removing
            exclude = CoordinateMap()
            exclude.add_file(filename)

            #create an interestion map of all coordinates we'll be keeping
            include = CoordinateMap()
            include.add_file(filename)

            #iterate any blacklists
            for blacklist in self.blacklists:
                for start,stop in blacklist.filecoords(filename):
                    exclude.add_extend(filename, start, stop)

            #iterate any whitelists
            for whitelist in self.whitelists:
                for start,stop in whitelist.filecoords(filename):
                    include.add_extend(filename, start, stop)

            #iterate our regex's 
            for 



            with open(foutpath+filename, "w") as f:
                #print(foutpath+filename)
                if inverse:
                    #print("transforming inverse, constraint: ", constraint)
                    #filter out anything in our constraint map NOT in our coord_map

                    contents = []
                    orig_f = self.finpath+filename
                    encoding = self.detect_encoding(orig_f)
                    txt = open(orig_f,"r", encoding=encoding['encoding']).read()

                    #create our constraint map,
                    #anything in this map, not in our coord_map will be hidden
                    #usually this is a greedy map with alot of hits
                    constraint_map = CoordinateMap()
                    matches = constraint.finditer(txt)
                    for m in matches:
                        constraint_map.add(filename, m.start(), m.group())
                    
                    last_marker = 0
                    for start,stop in constraint_map.filecoords(filename):
                        #check if this is in our coord_map
                        if coord_map.does_overlap(filename, start, stop):
                            #keep this 
                            contents.append(txt[last_marker:stop])
                        else:
                            #add up to this point
                            contents.append(txt[last_marker:start])
                            #remove this item
                            contents.append(replacement)
                        #move our marker forward
                        last_marker = stop

                    #wrap it up by adding on the remaining values if we haven't hit eof
                    if last_marker < len(txt):
                        contents.append(txt[last_marker:len(txt)])

                    f.write("".join(contents))

                else:
                    #filters out matches, leaving rest of text
                    contents = []
                    orig_f = self.finpath+filename
                    encoding = self.detect_encoding(orig_f)
                    txt = open(orig_f,"r", encoding=encoding['encoding']).read()
                    
                    last_marker = 0
                    for start,stop in coord_map.filecoords(filename):
                        contents.append(txt[last_marker:start])
                        last_marker = stop

                    #wrap it up by adding on the remaining values if we haven't hit eof
                    if last_marker < len(txt):
                        contents.append(txt[last_marker:len(txt)])

                    f.write(replacement.join(contents))



    def detect_encoding(self, fp):
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

    def eval(self,
        anno_folder="data/i2b2_anno/",
        anno_suffix=".ano", 
        philtered_folder="data/i2b2_results/",
        fp_output="data/phi/phi_fp/",
        fn_output="data/phi/phi_fn/",
        phi_matcher=re.compile("\s\*\*PHI\*\*\s"),
        pre_process=r":|\-|\/|_|~", #characters we're going to strip from our notes to analyze against anno
        only_digits=False):
        """ calculates the effectiveness of the philtering / extraction

            only_digits = <boolean> will constrain evaluation on philtering of only digit types
        """

        if self.debug:
            print("eval")

        #use config to eval
        if self.anno_folder != None:
            anno_folder = self.anno_folder

        # if self.anno_suffix != "":
        #     anno_suffix = self.anno_suffix
        
        summary = {
            "total_false_positives":0,
            "total_false_negatives":0,
            "total_true_positives": 0,
            "total_true_negatives": 0,
            "false_positives":[], #non-phi words we think are phi
            "true_positives": [], #phi words we correctly identify
            "false_negatives":[], #phi words we think are non-phi
            "true_negatives": [], #non-phi words we correctly identify
        }

        for root, dirs, files in os.walk(philtered_folder):

            for f in files:


                #local values per file
                false_positives = [] #non-phi we think are phi
                true_positives  = [] #phi we correctly identify
                false_negatives = [] #phi we think are non-phi
                true_negatives  = [] #non-phi we correctly identify

                philtered_filename = root+f
                anno_filename = anno_folder+''.join(f.split(".")[0])+anno_suffix

                # if len(anno_suffix) > 0:
                #     anno_filename = anno_folder+f.split(".")[0]+anno_suffix

                if not os.path.exists(philtered_filename):
                    raise Exception("FILE DOESNT EXIST", philtered_filename)
                
                if not os.path.exists(anno_filename):
                    print("FILE DOESNT EXIST", anno_filename)
                    continue

                
                encoding1 = self.detect_encoding(philtered_filename)
                philtered = open(philtered_filename,"r", encoding=encoding1['encoding']).read()
                #pre-process notes for comparison with anno punctuation stripped files
                if len(pre_process) > 0:
                    philtered = re.sub(pre_process, " ", philtered)
                philtered_words = re.split("\s+", philtered)

                
                encoding2 = self.detect_encoding(anno_filename)
                anno = open(anno_filename,"r", encoding=encoding2['encoding']).read()
                anno_words = re.split("\s+", anno)

                anno_dict = {}
                philtered_dict = {}

            
                for w in philtered_words:
                    philtered_dict[w] = 1                

                for w in anno_words:
                    anno_dict[w] = 1
                #print("DICTS", len(anno_dict), len(philtered_dict))

                #check what we hit
                for i,w in enumerate(philtered_words):

                    if phi_matcher.match(w):
                        continue

                    if only_digits:
                        if not re.search("\S*\d+\S*", w):
                            #skip non-digit evals
                            #assume we found a non-phi word
                            #phi = self.phi_context(philtered_filename, w, i, philtered_words)
                            #true_negatives.append(phi)
                            continue

                    #print(w, w in anno_dict, w in philtered_dict)

                    #check if this word is phi
                    if w not in anno_dict:
                        #this is phi we missed
                        phi = self.phi_context(philtered_filename, w, i, philtered_words)
                        false_negatives.append(phi)
                    else:
                        #this isn't phi, and we correctly identified it
                        phi_tn = self.phi_context(philtered_filename, w, i, philtered_words)
                        true_positives.append(phi_tn)

                #check what we missed
                for i,w in enumerate(anno_words):

                    if phi_matcher.match(w):
                        continue

                    if only_digits:
                        if not re.search("\S*\d+\S*", w):
                            #skip non-digit evals
                            #assume we got a non-phi word
                            #phi = self.phi_context(anno_filename, w, i, anno_words)
                            #true_positives.append(phi)
                            continue

                    #print(w, w in anno_dict, w in philtered_dict)

                    #check if this word is phi
                    if w not in philtered_dict:
                        #we got something that wasn't phi
                        phi_fp = self.phi_context(anno_filename, w, i, anno_words)
                        false_positives.append(phi_fp)
                    else:
                        #we correctly identified non-phi
                        #don't add twice
                        pass
                        
                
                #update summary
                summary["false_positives"] = summary["false_positives"] + false_positives
                summary["false_negatives"] = summary["false_negatives"] + false_negatives
                summary["true_positives"] = summary["true_positives"] + true_positives
                summary["true_negatives"] = summary["true_negatives"] + true_negatives

                #print(len(summary["true_positives"]), len(summary["false_positives"]), len(summary["true_negatives"]), len(summary["false_negatives"]) )

              
                #print("MISSED: ",len(false_negatives), false_negatives)
        #calc stats
        summary["total_true_negatives"] = len(summary["true_negatives"])
        summary["total_true_positives"] = len(summary["true_positives"])
        summary["total_false_negatives"] = len(summary["false_negatives"])
        summary["total_false_positives"] = len(summary["false_positives"])

        print("true_negatives", summary["total_true_negatives"],"true_positives", summary["total_true_positives"], "false_negatives", summary["total_false_negatives"], "false_positives", summary["total_false_positives"])

        if summary["total_true_positives"]+summary["total_false_negatives"] > 0:
            print("Recall: {:.2%}".format(summary["total_true_positives"]/(summary["total_true_positives"]+summary["total_false_negatives"])))
        elif summary["total_false_negatives"] == 0:
            print("Recall: 100%")

        if summary["total_true_positives"]+summary["total_false_positives"] > 0:
            print("Precision: {:.2%}".format(summary["total_true_positives"]/(summary["total_true_positives"]+summary["total_false_positives"])))

        #save the phi we missed
        json.dump(summary["false_negatives"], open(fn_output, "w"), indent=4)
        json.dump(summary["false_positives"], open(fp_output, "w"), indent=4)


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




























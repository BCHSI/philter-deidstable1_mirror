
import re
import json
import os
import chardet
from tqdm import tqdm
from chardet.universaldetector import UniversalDetector
from coordinate_map import CoordinateMap

class NPhilter:
    """ 
        General filtering class with a focus on numbers

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
        if "anno_suffix" in config:
            self.anno_suffix = config["anno_suffix"]
        #regex
        if "regex" in config:
            self.regexpatternfile = config["regex"]
            self.patterns = {"extract":[], "filter":[]} # filtration, extraction and other patterns
            self.compiled_patterns = {} #maps keyword to actual re compiled pattern object

        #default data structures
        self.coord_maps = {
            'extract':CoordinateMap(),
            'filter':CoordinateMap(),
        }

    def precompile(self, path=""):
        """ precompiles our regex to speed up pattern matching"""

        if self.debug:
            print("precompile")

        extract_patterns = []
        rpf = json.load(open(self.regexpatternfile, "r"))
        for r in rpf["patterns"]:

            regex = open(path+r["regex"],"r").read().strip()
            if r["group"] not in self.patterns:
                self.patterns[r["group"]] = [regex]
            else:
                self.patterns[r["group"]].append(regex)

        #print(self.patterns)

        #now compile these patterns
        for pat_group in self.patterns:
            if pat_group not in self.compiled_patterns:
                    self.compiled_patterns[pat_group] = []
            for regex in self.patterns[pat_group]:
                self.compiled_patterns[pat_group].append(re.compile(regex))

            #print(pat_type, self.compiled_patterns[pat_type])

    def maptransform(self, 
            filename, 
            txt,
            regex_map_name="extract", 
            replacement="**PHI**"):
        """ similar to mapcoords and transform in one,
        this can take text as input and generate a **phi** outputfile """
        
        #get our list of regex's
        regexlst = self.compiled_patterns[regex_map_name]
        coord_map = CoordinateMap()
        coord_map.add_file(filename)
        #scan our text for hits
        for regex in regexlst:
            matches = regex.finditer(txt)
            matched = 0
            for m in matches:
                matched += 1
                coord_map.add_extend(filename, m.start(), m.start()+len(m.group()))

        #now we transform
        #filters out matches, leaving rest of text
        contents = []
        last_marker = 0
        for start,stop in coord_map.filecoords(filename):
            contents.append(txt[last_marker:start])
            last_marker = stop
        #wrap it up by adding on the remaining values if we haven't hit eof
        if last_marker < len(txt):
            contents.append(txt[last_marker:len(txt)])
        return replacement.join(contents)

    def multi_maptransform(self, 
            filename, 
            txt,
            coord_maps=[
                {'title':'filter'},
                {'title':'extract'},
                {'title':'all-digits'}],
            replacement="**PHI**"):
        """ similar to mapcoords and transform in one,
        this can take text as input and generate a **phi** outputfile """
        
        #get our list of regex's
        #get coordinates for all maps
        maps = []
        for m in coord_maps:
            regexlst = self.compiled_patterns[m['title']]
            coord_map = CoordinateMap()
            #scan our text for hits
            for regex in regexlst:
                matches = regex.finditer(txt)
                matched = 0
                for m in matches:
                    matched += 1
                    coord_map.add_extend(filename, m.start(), m.start()+len(m.group()))
            maps.append(coord_map )

        if len(maps) != 3:
            raise Exception("Multi map mode only works for 3 maps, got", len(maps))

        FILTER_MAP = maps[0]
        EXTRACT_MAP = maps[1]
        BASELINE_MAP = maps[2]

        #todo: factor this out into the class methods
        FILTER_MAP.add_file(filename)
        EXTRACT_MAP.add_file(filename)
        BASELINE_MAP.add_file(filename)

        if filename.split(".")[-1] != "txt":
            raise Exception("File must be .txt file, got:", filename)
        
        #this is the map of the final coordinates we'll not be keeping
        INTERSECTION = CoordinateMap() 
        INTERSECTION.add_file(filename)

        contents = []
        #FIRST PASS
        #add all of our known phi
        for start,stop in FILTER_MAP.filecoords(filename):
            INTERSECTION.add(filename, start, stop)

        #SECOND PASS
        #use extract map to add new coordinates that don't overlap
        #anything that doesn't overlap we'll just add anyways
        for start,stop in BASELINE_MAP.filecoords(filename):

            #check if we overlap with intersection
            overlap1 = INTERSECTION.does_overlap(filename, start, stop)
            if overlap1:
                #Add and extend
                INTERSECTION.add_extend(filename, start, stop)
                continue

            overlap2 = EXTRACT_MAP.does_overlap(filename, start, stop)
            if overlap2:
                #we won't add this because it's in our extract map
                continue

            #print(overlap1, overlap2)
            #we got here, it's not in our filter or extract maps, so let's add it
            INTERSECTION.add_extend(filename, start, stop)

        #Transform step
        #filters out matches, leaving rest of text
        contents = []
        
        last_marker = 0
        for start,stop in INTERSECTION.filecoords(filename):
            contents.append(txt[last_marker:start])
            last_marker = stop

        #wrap it up by adding on the remaining values if we haven't hit eof
        if last_marker < len(txt):
            contents.append(txt[last_marker:len(txt)])

        return replacement.join(contents)


    def mapcoords(self, regex_map_name="extract", coord_map_name="extract"):
        """ Runs the set of regex on the input data 
            generating a coordinate map of hits given (dry run doesn't transform)
        """
        if self.debug:
            print("mapcoords: ", regex_map_name)

        regexlst = self.compiled_patterns[regex_map_name]

        if self.debug:
            print(regexlst)
        

        if not os.path.exists(self.foutpath):
            os.makedirs(self.foutpath)

        if coord_map_name not in self.coord_maps:
            self.coord_maps[coord_map_name] = CoordinateMap()

        for root, dirs, files in tqdm(os.walk(self.finpath)):
            for f in files:
                self.coord_maps[coord_map_name].add_file(f)

                filename = root+f
                encoding = self.detect_encoding(root+f)
                txt = open(filename,"r", encoding=encoding['encoding']).read()

                #search each word for a match
                # words = txt.split()
                # cursor = 0 #where we are in the text document
                # for i,w in enumerate(words):
                #     cursor += len(w)
                #     if regex.match(w):
                        
                #         self.coord_maps[coord_map_name].add(f, m.start(), w)
                #     cursor += 1 #add in our space offset
                
                #find iterations:
                #print(txt)
                #print(regex.finditer(txt))
                #output_txt = re.sub(regex, ".", txt)

                for regex in regexlst:
                    matches = regex.finditer(txt)
                    matched = 0
                    for m in matches:
                        matched += 1
                        self.coord_maps[coord_map_name].add_extend(f, m.start(), m.start()+len(m.group()))

    def transform(self, 
            coord_map_name="genfilter", 
            replacement=" **PHI** ",
            #replacement="**PHI{}**",
            inverse=False,
            constraint=re.compile(r"\S*\d+\S*"),
            out_path="",
            in_path=""):
        """ transform
            turns input files into output files 
            protected health information reduced to the replacement character

            replacement: the replacement string
            inverse: if true, will replace everything but the matches provided it matches the constrain param
            if false, will replace any matches

            in_path, location to read unfiltered data, if this is len == 0
            then config is used, if config is 0, raise error

            out_path, location to save transformed data, if this is len == 0
            then config is used, if config is 0, raise error
        """

        if self.debug:
            print("transform")

        #get input path
        finpath = in_path
        if len(finpath) == 0:
            finpath = self.finpath
        if len(finpath) == 0:
            raise Exception("File input path is undefined", finpath)
        if not os.path.exists(finpath):
            raise Exception("File input path does not exist", finpath)

        #get output path
        foutpath = out_path
        if len(foutpath) == 0:
            foutpath = self.foutpath
        if len(foutpath) == 0:
            raise Exception("File input path is undefined", foutpath)
        if not os.path.exists(foutpath):
            raise Exception("File input path does not exist", foutpath)

        #get coordinates
        coord_map = self.coord_maps[coord_map_name]

        for filename in tqdm(coord_map.keys()):
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

    def multi_transform(self, 
            coord_maps=[
                {'title':'filter'},
                {'title':'extract'},
                {'title':'all-digits'}], 
            replacement=" **PHI** ",
            out_path="",
            in_path=""):
        """ transforms using multiple maps as input, anything with a higher preference has priority

            turns input files into output files 
            protected health information reduced to the replacement character

            replacement: the replacement string
            keep: if true, will keep matches
            if false, will replace any matches

            in_path, location to read unfiltered data, if this is len == 0
            then config is used, if config is 0, raise error

            out_path, location to save transformed data, if this is len == 0
            then config is used, if config is 0, raise error

            perf: move this to a multi-map step, instead of doing heavy lifting ina multi-transform step
        """

        if self.debug:
            print("mutli-regex-transform")

        #get input path
        finpath = in_path
        if len(finpath) == 0:
            finpath = self.finpath
        if len(finpath) == 0:
            raise Exception("File input path is undefined", finpath)
        if not os.path.exists(finpath):
            raise Exception("File input path does not exist", finpath)

        #get output path
        foutpath = out_path
        if len(foutpath) == 0:
            foutpath = self.foutpath
        if len(foutpath) == 0:
            raise Exception("File input path is undefined", foutpath)
        if not os.path.exists(foutpath):
            raise Exception("File input path does not exist", foutpath)

        #NOTE: this has hardcoded ordering... so priority and order don't make sense here
        #sort by priority, with highest priority first
        #coord_maps.sort(key=lambda x: x["priority"], reverse=True)

        #get coordinates for all maps
        maps = []
        for m in coord_maps:
            maps.append(self.coord_maps[m['title']])

        if len(maps) != 3:
            raise Exception("Multi map mode only works for 3 maps, got", len(maps))

        FILTER_MAP = maps[0]
        EXTRACT_MAP = maps[1]
        BASELINE_MAP = maps[2]

        for root, dirs, files in tqdm(os.walk(self.finpath)):
            for filename in files:

                if filename.split(".")[-1] != "txt":
                    print("SKIPPING", filename)
                    continue

                with open(foutpath+filename, "w") as f:

                    #this is the map of the final coordinates we'll not be keeping
                    INTERSECTION = CoordinateMap() 
                    INTERSECTION.add_file(filename)

                    contents = []
                    orig_f = self.finpath+filename
                    encoding = self.detect_encoding(orig_f)
                    txt = open(orig_f,"r", encoding=encoding['encoding']).read()

                    #FIRST PASS
                    #add all of our known phi
                    for start,stop in FILTER_MAP.filecoords(filename):
                        INTERSECTION.add(filename, start, stop)

                    #SECOND PASS
                    #use extract map to add new coordinates that don't overlap
                    #anything that doesn't overlap we'll just add anyways
                    for start,stop in BASELINE_MAP.filecoords(filename):

                        #check if we overlap with intersection
                        overlap1 = INTERSECTION.does_overlap(filename, start, stop)
                        if overlap1:
                            #Add and extend
                            INTERSECTION.add_extend(filename, start, stop)
                            continue

                        overlap2 = EXTRACT_MAP.does_overlap(filename, start, stop)
                        if overlap2:
                            #we won't add this because it's in our extract map
                            continue

                        #print(overlap1, overlap2)
                        #we got here, it's not in our filter or extract maps, so let's add it
                        INTERSECTION.add_extend(filename, start, stop)

                    #Transform step
                    #filters out matches, leaving rest of text
                    contents = []
                    orig_f = self.finpath+filename
                    encoding = self.detect_encoding(orig_f)
                    txt = open(orig_f,"r", encoding=encoding['encoding']).read()
                    
                    last_marker = 0
                    for start,stop in INTERSECTION.filecoords(filename):
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
        anno_suffix="_phi_reduced.ano", 
        philtered_folder="data/i2b2_results/",
        fp_output="data/phi/phi_fp/",
        fn_output="data/phi/phi_fn/",
        phi_matcher=re.compile("\s\*\*PHI\*\*\s"),
        pre_process=r":|\-|\/|_|~", #characters we're going to strip from our notes to analyze against anno
        only_digits=True):
        """ calculates the effectiveness of the philtering / extraction

            only_digits = <boolean> will constrain evaluation on philtering of only digit types
        """

        if self.debug:
            print("eval")

        #use config to eval
        if self.anno_folder != None:
            anno_folder = self.anno_folder

        if self.anno_suffix != "":
            anno_suffix = self.anno_suffix
        
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
                anno_filename = anno_folder+f.split(".")[0]+anno_suffix

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
                if not os.path.exists(anno_folder+f.split(".")[0]+anno_suffix):
                    print("FILE DOESNT EXIST", anno_folder+f.split(".")[0]+anno_suffix)
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
            if word not in phi_map[word]['examples']:
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

    def gen_regex(self, 
            source_map="data/phi/phi_map.json", 
            regex_map_name="filter",
            output_file="data/phi/phi_regex.json",
            output_folder="data/phi/phi_regex/",
            digit_char="`", 
            string_char="?"):
        """ 
            given a map of phi general types, will create basic regex's to match these types 

            source_map = the map generated from the mapphi method, should abstract the data
            pattern = this is where the regex's generated from this operation are stored

        """

        if self.debug:
            print("gen_regex")

        d = json.load(open(source_map, "r"))
        context = "" #digit, string, any
        regex_map = {}
        

        for pattern in d:
            regexlst = []
            for c,prev_count,prev_context,context_switch in self.iterate_pattern(pattern):
                if context_switch == True:
                    if prev_context == "number":
                        regexlst.append("\d{%s}" % prev_count)
                    elif prev_context == "string":
                        regexlst.append("[a-zA-Z]{%s}" % prev_count)
                    else:
                        #print(c,prev_count,prev_context,context_switch)
                        regexlst.append("\\"+c+"{%s}" % prev_count)

                    

            regex_map[pattern] = "".join(regexlst)
            # print("#"*30)
            # print(pattern)
            # print("".join(regex))
            # print("#"*30)
        
        
        

        #save patterns locally
        regex_string = "|".join(regex_map.values())
        #print(regex_string)
        self.compiled_patterns[regex_map_name] = re.compile(regex_string)

        #save patterns to disk
        for i,pattern in enumerate(regex_map):
            with open(output_folder+str(i)+".txt", "w") as f:
                f.write(regex_map[pattern])
        
        #save the master pattern
        with open(output_folder+"001_master.txt", "w") as f:
                f.write(regex_string)


        json.dump(regex_map, open(output_file, "w"), indent=4)



    def iterate_pattern(self, pattern, 
            digit_char="`", 
            string_char="?", 
            any_char="."):
        """ 
            Helper method for gen_regex,
            generator iterates the pattern,
            telling us when a context switch has occurred 
    
            character = specific character
            prev_count = count of last context seen
            count = current count of this seen
            context = current context, can be digit, string, any
            context_switch = <boolean> tells us if the context just switched
            
        """

        prev_context = ""
        current_context = ""
        context_switch = False
        count = 0
        c = ""

        for i,char in enumerate(pattern):
            c = char

            if c == digit_char:
                current_context = "number"
                if prev_context != current_context:
                    context_switch = True
            elif c == string_char:
                current_context = "string"
                if prev_context != current_context:
                    context_switch = True
            else:
                current_context = c
                if prev_context != current_context:
                    context_switch = True
                    


            #special case on first item
            if i == 0:
                context_switch = False
                prev_context = current_context

            if context_switch == True:
                #yield our values on a context switch
                yield c, count, prev_context, context_switch
                count = 0

            #reset our context to match
            prev_context = current_context
            context_switch = False
            count += 1

        #final is always a context switch
        yield c, count, prev_context, True
            




























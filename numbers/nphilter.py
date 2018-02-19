
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
        self.debug = config["debug"]
        self.finpath = config["finpath"]
        self.foutpath = config["foutpath"]
        self.debug = config["debug"]

        #regex
        self.regexpatternfile = config["regex"]
        self.patterns = {"extract":[], "filter":[]} # filtration, extraction and other patterns
        self.compiled_patterns = {} #maps keyword to actual re compiled pattern object
        

        #data structures
        self.coord_maps = {
            'extract':CoordinateMap(),
            'filter':CoordinateMap(),
        }

    def precompile(self):
        """ precompiles our regex to speed up pattern matching"""

        if self.debug:
            print("precompile")

        extract_patterns = []
        rpf = json.load(open(self.regexpatternfile, "r"))
        for r in rpf["patterns"]:

            regex = open(r["regex"],"r").read().strip()
            if r["group"] not in self.patterns:
                self.patterns[r["group"]] = [regex]
            else:
                self.patterns[r["group"]].append(regex)

        #print(self.patterns)

        #now compile these patterns
        for pat_group in self.patterns:
            regex_string = "|".join(self.patterns[pat_group])
            
            #check if this group type exists
            self.compiled_patterns[pat_group] = re.compile(regex_string)

            #print(pat_type, self.compiled_patterns[pat_type])

    def mapcoords(self, regex_map_name="extract", coord_map_name="extract"):
        """ Runs the set of regex on the input data 
            generating a coordinate map of hits given (dry run doesn't transform)
        """
        if self.debug:
            print("mapcoords")

        regex = self.compiled_patterns[regex_map_name]

        if self.debug:
            print(regex)
        

        if not os.path.exists(self.foutpath):
            os.makedirs(self.foutpath)

        if coord_map_name not in self.coord_maps:
            self.coord_maps[coord_map_name] = CoordinateMap()

        for root, dirs, files in tqdm(os.walk(self.finpath)):
            for f in files:
                filename = root+f
                encoding = self.detect_encoding(root+f)
                txt = open(filename,"r", encoding=encoding['encoding']).read()
                
                #print(txt)
                #print(regex.finditer(txt))
                #output_txt = re.sub(regex, ".", txt)
                matches = regex.finditer(txt)
                
                matched = 0
                for m in matches:
                    matched += 1
                    self.coord_maps[coord_map_name].add(f, m.start(), m.group())




    def transform(self, 
            coord_map_name="genfilter", 
            replacement="**PHI{}**",
            inverse=False,
            out_path="",
            in_path=""):
        """ transform
            turns input files into output files 
            protected health information reduced to the replacement character

            replacement: the replacement string
            inverse: if true, will replace everything but the matches
            if false, will replace the matches

            in_path, location to read unfiltered data, if this is len == 0
            then config is used, if config is 0, raise error

            out_path, location to save transformed data, if this is len == 0
            then config is used, if config is 0, raise error
        """

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

                if inverse:
                    #saves only matches
                    contents = []
                    for coord,val in coord_map.filecoords(filename):
                        contents.append(val)
                    if len(contents) == 0:
                        f.write("**PHI**")
                    else:
                        #inverse, we save only the items within coordinates
                        f.write("**PHI**".join(contents))
                else:
                    #filters out matches, leaving rest of text
                    contents = []
                    orig_f = self.finpath+filename
                    encoding = self.detect_encoding(orig_f)
                    txt = open(orig_f,"r", encoding=encoding['encoding']).read()
                    
                    last_marker = 0
                    for coord,val in coord_map.filecoords(filename):
                        contents.append(txt[last_marker:coord])
                        last_marker = coord + len(val)

                    #wrap it up by adding on the remaining values if we haven't hit eof
                    if last_marker < len(txt):
                        contents.append(txt[last_marker:len(txt)])

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

    def eval(self,
        anno_folder="data/i2b2_anno/",
        anno_suffix="_phi_reduced.ano", 
        philtered_folder="data/i2b2_results/",
        only_digits=True):
        """ calculates the effectiveness of the philtering / extraction

            only_digits = <boolean> will constrain evaluation on philtering of only digit types
        """

        
        summary = {
            "total_false_positives":0,
            "total_false_negatives":0,
            "total_true_positives":0,
            "total_true_negatives":0,
            "false_positives":[], #non-phi words we think are phi
            "true_positives":[], #phi words we correctly identify
            "false_negatives":[], #phi words we think are non-phi
            "true_negatives":[], #non-phi words we correctly identify
        }

        for root, dirs, files in os.walk(philtered_folder):
            for f in files:

                #local values per file
                false_positives = [] #non-phi we think are phi
                true_positives  = [] #phi we correctly identify
                false_negatives = [] #phi we think are non-phi
                true_negatives  = [] #non-phi we correctly identify

                if not os.path.exists(root+f):
                    raise Exception("FILE DOESNT EXIST", root+f)
                if not os.path.exists(anno_folder+f.split(".")[0]+anno_suffix):
                    print("FILE DOESNT EXIST", anno_folder+f.split(".")[0]+anno_suffix)
                    continue

                philtered_filename = root+f
                encoding1 = self.detect_encoding(philtered_filename)
                philtered = open(philtered_filename,"r", encoding=encoding1['encoding']).read()
                philtered_words = re.split("\s+", philtered)

                anno_filename = anno_folder+f.split(".")[0]+anno_suffix
                encoding2 = self.detect_encoding(anno_filename)
                anno = open(anno_filename,"r", encoding=encoding2['encoding']).read()
                anno_words = re.split("\s+", anno)

                anno_dict = {}
                philtered_dict = {}

                
                

                for w in philtered_words:
                    philtered_dict[w] = 1                

                for w in anno_words:
                    anno_dict[w] = 1
                print("DICTS", len(anno_dict), len(philtered_dict))

                for i,w in enumerate(philtered_dict):

                    if only_digits:
                        if not re.search("\d+", w):
                            #skip non-digit evals
                            continue

                    #print(w, w in anno_dict, w in philtered_dict)

                    #check if this word is phi
                    if w not in anno_dict:
                        #this is phi we missed
                        false_negatives.append(w)
                    else:
                        #this isn't phi
                        true_negatives.append(w)

                #check what we miss / hit
                for i,w in enumerate(anno_dict):

                    if only_digits:
                        if not re.search("\d+", w):
                            #skip non-digit evals
                            continue

                    #print(w, w in anno_dict, w in philtered_dict)

                    #check if this word is phi
                    if w not in philtered_dict:
                        #we got something that wasn't phi
                        false_positives.append(w)
                    else:
                        #we correctly identified non-phi
                        true_positives.append(w)
                #update summary
                summary["false_positives"] = summary["false_positives"] + false_positives
                summary["false_negatives"] = summary["false_negatives"] + false_negatives
                summary["true_positives"] = summary["true_positives"] + true_positives
                summary["true_negatives"] = summary["true_negatives"] + true_negatives

                print(len(summary["true_positives"]), len(summary["false_positives"]), len(summary["true_negatives"]), len(summary["false_negatives"]) )

                break

                #print("MISSED: ",len(false_negatives), false_negatives)
        #calc stats
        summary["total_true_negatives"] = len(summary["true_negatives"])
        summary["total_true_positives"] = len(summary["true_positives"])
        summary["total_false_negatives"] = len(summary["false_negatives"])
        summary["total_false_positives"] = len(summary["false_positives"])

        print("true_negatives", summary["total_true_negatives"],"true_positives", summary["total_true_positives"], "false_negatives", summary["total_false_negatives"], "false_positives", summary["total_false_positives"])

        if summary["total_true_positives"]+summary["total_false_negatives"] > 0:
            print("Recall: {:.2%}".format(summary["total_true_positives"]/(summary["total_true_positives"]+summary["total_false_negatives"])))
                
        if summary["total_true_positives"]+summary["total_false_positives"] > 0:
            print("Precision: {:.2%}".format(summary["total_true_positives"]/(summary["total_true_positives"]+summary["total_false_positives"])))


    def getphi(self, 
            anno_folder="data/i2b2_anno/", 
            anno_suffix="_phi_reduced.ano", 
            data_folder="data/i2b2_notes/", 
            output_folder="i2b2_phi", 
            filter_regex=None,
            replace=["/"]):
        """ get's phi from existing data to build up a data model
            
        """

        """ data structure to hold our phi and classify phi we find
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

                #replace specific punc chars
                orig.replace("/", " ")

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
            digit_char="#", 
            string_char="*", 
            any_char="."):
        """ given all examples of the phi, creates a general representation 
            
            digit_char = this is what digits are replaced by
            string_char = this is what strings are replaced by
            any_char = this is what any random characters are replaced with
        """
        d = json.load(open(phi_path, "r"))

        phi_map = {}

        for w in d:
            wordlst = []
            for c in w:
                if re.match("\d+", c):
                    wordlst.append(digit_char)
                elif re.match("[a-zA-Z]+", c):
                    wordlst.append(string_char)
                else:
                    wordlst.append(any_char)
            word = "".join(wordlst)
            if word not in phi_map:
                phi_map[word] = 0
            phi_map[word] += 1

        #save all representations
        json.dump(phi_map, open(out_path, "w"), indent=4)


    def gen_regex(self, 
            source_map="data/phi/phi_map.json", 
            regex_map_name="filter",
            output_file="data/phi/phi_regex.json",
            output_folder="data/phi/phi_regex/",
            digit_char="#", 
            string_char="*", 
            any_char="."):
        """ 
            given a map of phi general types, will create basic regex's to match these types 

            source_map = the map generated from the mapphi method, should abstract the data
            pattern = this is where the regex's generated from this operation are stored

        """

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
                    elif prev_context == "any":
                        regexlst.append(".{%s}" % prev_count)
                    

            regex_map[pattern] = "".join(regexlst)
            # print("#"*30)
            # print(pattern)
            # print("".join(regex))
            # print("#"*30)
        for i,pattern in enumerate(regex_map):
            with open(output_folder+str(i)+".txt", "w") as f:
                f.write(regex_map[pattern])
        
        json.dump(regex_map, open(output_file, "w"), indent=4)

        #save patterns locally
        regex_string = "|".join(regex_map.values())
        self.compiled_patterns[regex_map_name] = re.compile(regex_string)



    def iterate_pattern(self, pattern, 
            digit_char="#", 
            string_char="*", 
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

        for i,c in enumerate(pattern):
            
            if c == digit_char:
                current_context = "number"
                if prev_context != current_context:
                    context_switch = True
            elif c == string_char:
                current_context = "string"
                if prev_context != current_context:
                    context_switch = True
            elif c == any_char:
                current_context = "any"
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
            




























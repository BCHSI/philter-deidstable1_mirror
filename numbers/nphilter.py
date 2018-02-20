
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
        self.debug = config***REMOVED***"debug"***REMOVED***
        self.finpath = config***REMOVED***"finpath"***REMOVED***
        self.foutpath = config***REMOVED***"foutpath"***REMOVED***
        self.debug = config***REMOVED***"debug"***REMOVED***
        self.anno_folder = config***REMOVED***"anno_folder"***REMOVED***
        self.anno_suffix = config***REMOVED***"anno_suffix"***REMOVED***

        #regex
        self.regexpatternfile = config***REMOVED***"regex"***REMOVED***
        self.patterns = {"extract":***REMOVED******REMOVED***, "filter":***REMOVED******REMOVED***} # filtration, extraction and other patterns
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

        extract_patterns = ***REMOVED******REMOVED***
        rpf = json.load(open(self.regexpatternfile, "r"))
        for r in rpf***REMOVED***"patterns"***REMOVED***:

            regex = open(r***REMOVED***"regex"***REMOVED***,"r").read().strip()
            if r***REMOVED***"group"***REMOVED*** not in self.patterns:
                self.patterns***REMOVED***r***REMOVED***"group"***REMOVED******REMOVED*** = ***REMOVED***regex***REMOVED***
            else:
                self.patterns***REMOVED***r***REMOVED***"group"***REMOVED******REMOVED***.append(regex)

        #print(self.patterns)

        #now compile these patterns
        for pat_group in self.patterns:
            regex_string = "|".join(self.patterns***REMOVED***pat_group***REMOVED***)
            
            #check if this group type exists
            self.compiled_patterns***REMOVED***pat_group***REMOVED*** = re.compile(regex_string)

            #print(pat_type, self.compiled_patterns***REMOVED***pat_type***REMOVED***)

    def mapcoords(self, regex_map_name="extract", coord_map_name="extract"):
        """ Runs the set of regex on the input data 
            generating a coordinate map of hits given (dry run doesn't transform)
        """
        if self.debug:
            print("mapcoords")

        regex = self.compiled_patterns***REMOVED***regex_map_name***REMOVED***

        if self.debug:
            print(regex)
        

        if not os.path.exists(self.foutpath):
            os.makedirs(self.foutpath)

        if coord_map_name not in self.coord_maps:
            self.coord_maps***REMOVED***coord_map_name***REMOVED*** = CoordinateMap()

        for root, dirs, files in tqdm(os.walk(self.finpath)):
            for f in files:
                filename = root+f
                encoding = self.detect_encoding(root+f)
                txt = open(filename,"r", encoding=encoding***REMOVED***'encoding'***REMOVED***).read()

                #search each word for a match
                # words = txt.split()
                # cursor = 0 #where we are in the text document
                # for i,w in enumerate(words):
                #     cursor += len(w)
                #     if regex.match(w):
                        
                #         self.coord_maps***REMOVED***coord_map_name***REMOVED***.add(f, m.start(), w)
                #     cursor += 1 #add in our space offset
                
                #find iterations:
                #print(txt)
                #print(regex.finditer(txt))
                #output_txt = re.sub(regex, ".", txt)
                
                matches = regex.finditer(txt)
                matched = 0
                for m in matches:
                    matched += 1
                    self.coord_maps***REMOVED***coord_map_name***REMOVED***.add(f, m.start(), m.group())




    def transform(self, 
            coord_map_name="genfilter", 
            replacement=" ",
            #replacement="**PHI{}**",
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
        coord_map = self.coord_maps***REMOVED***coord_map_name***REMOVED***

        for filename in tqdm(coord_map.keys()):
            with open(foutpath+filename, "w") as f:

                if inverse:
                    #saves only matches
                    contents = ***REMOVED******REMOVED***
                    for coord,val in coord_map.filecoords(filename):
                        contents.append(val)
                    if len(contents) == 0:
                        f.write(replacement)
                    else:
                        #inverse, we save only the items within coordinates
                        f.write(replacement.join(contents))
                else:
                    #filters out matches, leaving rest of text
                    contents = ***REMOVED******REMOVED***
                    orig_f = self.finpath+filename
                    encoding = self.detect_encoding(orig_f)
                    txt = open(orig_f,"r", encoding=encoding***REMOVED***'encoding'***REMOVED***).read()
                    
                    last_marker = 0
                    for coord,val in coord_map.filecoords(filename):
                        contents.append(txt***REMOVED***last_marker:coord***REMOVED***)
                        last_marker = coord + len(val)

                    #wrap it up by adding on the remaining values if we haven't hit eof
                    if last_marker < len(txt):
                        contents.append(txt***REMOVED***last_marker:len(txt)***REMOVED***)

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

    def eval(self,
        anno_folder="data/i2b2_anno/",
        anno_suffix="_phi_reduced.ano", 
        philtered_folder="data/i2b2_results/",
        fp_output="data/phi/phi_fp/",
        fn_output="data/phi/phi_fn/",
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
            "false_positives":***REMOVED******REMOVED***, #non-phi words we think are phi
            "true_positives": ***REMOVED******REMOVED***, #phi words we correctly identify
            "false_negatives":***REMOVED******REMOVED***, #phi words we think are non-phi
            "true_negatives": ***REMOVED******REMOVED***, #non-phi words we correctly identify
        }

        for root, dirs, files in os.walk(philtered_folder):
            for f in files:

                #local values per file
                false_positives = ***REMOVED******REMOVED*** #non-phi we think are phi
                true_positives  = ***REMOVED******REMOVED*** #phi we correctly identify
                false_negatives = ***REMOVED******REMOVED*** #phi we think are non-phi
                true_negatives  = ***REMOVED******REMOVED*** #non-phi we correctly identify

                if not os.path.exists(root+f):
                    raise Exception("FILE DOESNT EXIST", root+f)
                
                if not os.path.exists(anno_folder+f.split(".")***REMOVED***0***REMOVED***+anno_suffix):
                    print("FILE DOESNT EXIST", anno_folder+f.split(".")***REMOVED***0***REMOVED***+anno_suffix)
                    continue

                philtered_filename = root+f
                encoding1 = self.detect_encoding(philtered_filename)
                philtered = open(philtered_filename,"r", encoding=encoding1***REMOVED***'encoding'***REMOVED***).read()
                philtered_words = re.split("\s+", philtered)

                anno_filename = anno_folder+f.split(".")***REMOVED***0***REMOVED***+anno_suffix
                encoding2 = self.detect_encoding(anno_filename)
                anno = open(anno_filename,"r", encoding=encoding2***REMOVED***'encoding'***REMOVED***).read()
                anno_words = re.split("\s+", anno)

                anno_dict = {}
                philtered_dict = {}

            
                for w in philtered_words:
                    philtered_dict***REMOVED***w***REMOVED*** = 1                

                for w in anno_words:
                    anno_dict***REMOVED***w***REMOVED*** = 1
                #print("DICTS", len(anno_dict), len(philtered_dict))

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
                summary***REMOVED***"false_positives"***REMOVED*** = summary***REMOVED***"false_positives"***REMOVED*** + false_positives
                summary***REMOVED***"false_negatives"***REMOVED*** = summary***REMOVED***"false_negatives"***REMOVED*** + false_negatives
                summary***REMOVED***"true_positives"***REMOVED*** = summary***REMOVED***"true_positives"***REMOVED*** + true_positives
                summary***REMOVED***"true_negatives"***REMOVED*** = summary***REMOVED***"true_negatives"***REMOVED*** + true_negatives

                #print(len(summary***REMOVED***"true_positives"***REMOVED***), len(summary***REMOVED***"false_positives"***REMOVED***), len(summary***REMOVED***"true_negatives"***REMOVED***), len(summary***REMOVED***"false_negatives"***REMOVED***) )

              
                #print("MISSED: ",len(false_negatives), false_negatives)
        #calc stats
        summary***REMOVED***"total_true_negatives"***REMOVED*** = len(summary***REMOVED***"true_negatives"***REMOVED***)
        summary***REMOVED***"total_true_positives"***REMOVED*** = len(summary***REMOVED***"true_positives"***REMOVED***)
        summary***REMOVED***"total_false_negatives"***REMOVED*** = len(summary***REMOVED***"false_negatives"***REMOVED***)
        summary***REMOVED***"total_false_positives"***REMOVED*** = len(summary***REMOVED***"false_positives"***REMOVED***)

        print("true_negatives", summary***REMOVED***"total_true_negatives"***REMOVED***,"true_positives", summary***REMOVED***"total_true_positives"***REMOVED***, "false_negatives", summary***REMOVED***"total_false_negatives"***REMOVED***, "false_positives", summary***REMOVED***"total_false_positives"***REMOVED***)

        if summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_negatives"***REMOVED*** > 0:
            print("Recall: {:.2%}".format(summary***REMOVED***"total_true_positives"***REMOVED***/(summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_negatives"***REMOVED***)))
                
        if summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_positives"***REMOVED*** > 0:
            print("Precision: {:.2%}".format(summary***REMOVED***"total_true_positives"***REMOVED***/(summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_positives"***REMOVED***)))

        #save the phi we missed
        json.dump(summary***REMOVED***"false_negatives"***REMOVED***, open(fn_output, "w"), indent=4)
        json.dump(summary***REMOVED***"false_positives"***REMOVED***, open(fp_output, "w"), indent=4)


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
                if not os.path.exists(anno_folder+f.split(".")***REMOVED***0***REMOVED***+anno_suffix):
                    print("FILE DOESNT EXIST", anno_folder+f.split(".")***REMOVED***0***REMOVED***+anno_suffix)
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

        for w in d:
            wordlst = ***REMOVED******REMOVED***
            for c in w:
                if re.match("\d+", c):
                    wordlst.append(digit_char)
                elif re.match("***REMOVED***a-zA-Z***REMOVED***+", c):
                    wordlst.append(string_char)
                else:
                    wordlst.append(c)
            word = "".join(wordlst)
            if word not in phi_map:
                phi_map***REMOVED***word***REMOVED*** = {'examples':{}}
            if w not in phi_map***REMOVED***word***REMOVED******REMOVED***'examples'***REMOVED***:
                phi_map***REMOVED***word***REMOVED******REMOVED***'examples'***REMOVED******REMOVED***w***REMOVED*** = ***REMOVED******REMOVED***
            phi_map***REMOVED***word***REMOVED******REMOVED***'examples'***REMOVED******REMOVED***w***REMOVED***.append('foo.txt') 

        #save all representations
        json.dump(phi_map, open(out_path, "w"), indent=4)


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
            regexlst = ***REMOVED******REMOVED***
            for c,prev_count,prev_context,context_switch in self.iterate_pattern(pattern):
                if context_switch == True:
                    if prev_context == "number":
                        regexlst.append("\d{%s}" % prev_count)
                    elif prev_context == "string":
                        regexlst.append("***REMOVED***a-zA-Z***REMOVED***{%s}" % prev_count)
                    else:
                        #print(c,prev_count,prev_context,context_switch)
                        regexlst.append("\\"+c+"{%s}" % prev_count)

                    

            regex_map***REMOVED***pattern***REMOVED*** = "".join(regexlst)
            # print("#"*30)
            # print(pattern)
            # print("".join(regex))
            # print("#"*30)
        
        
        

        #save patterns locally
        regex_string = "|".join(regex_map.values())
        #print(regex_string)
        self.compiled_patterns***REMOVED***regex_map_name***REMOVED*** = re.compile(regex_string)

        #save patterns to disk
        for i,pattern in enumerate(regex_map):
            with open(output_folder+str(i)+".txt", "w") as f:
                f.write(regex_map***REMOVED***pattern***REMOVED***)
        
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
            




























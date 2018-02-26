import nltk
import re
import os
import json
import difflib
from difflib import SequenceMatcher
from chardet.universaldetector import UniversalDetector

#example showing the data shape
w_e = {"word":"bear", "pos":"NN", "pos_full":"Noun", "count":20}

#find all phi and non-phi words
phi = {}
non_phi = {}

anno_folder = "data/i2b2_anno/"
NOTES_folder = "data/i2b2_results/"

def detect_encoding(fp):
    detector = UniversalDetector()
    with open(fp, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done: 
                break
        detector.close()
    return detector.result


def find_diff(s1, s2, phi_matcher):
    for line in difflib.unified_diff(s1, s2):
        #if line.startswith("!") or line.startswith("*"):

        if len(line.replace("+","").strip())==0 or len(line.replace("-","").strip())==0 or len(line.strip())==0:
            continue

        if line.startswith("+"):
            #this is in our anno file, not in our notes

            w = line***REMOVED***1:***REMOVED***
            if phi_matcher.match(w):
                #ignore phi characters in anno
                continue
            yield("FP", w)
            #summary***REMOVED***"false_positives"***REMOVED***.append(w)


            pass
        elif line.startswith("-"):
            #this is in our notes file, not in our anno file
            w = line***REMOVED***1:***REMOVED***
            if phi_matcher.match(w):
                #ignore phi characters in anno
                continue
            yield("FN", w)
            #summary***REMOVED***"false_negatives"***REMOVED***.append(w)
        else:
            continue
            #print(line)


phi_matcher = re.compile(r"\s*\*\*PHI")
pre_process = re.compile(r":|\-|\/|_|~")


fn_with_pos = {}


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

for root, dirs, files in os.walk(NOTES_folder):

    for f in files:


        #local values per file
        false_positives = ***REMOVED******REMOVED*** #non-phi we think are phi
        true_positives  = ***REMOVED******REMOVED*** #phi we correctly identify
        false_negatives = ***REMOVED******REMOVED*** #phi we think are non-phi
        true_negatives  = ***REMOVED******REMOVED*** #non-phi we correctly identify

        philtered_filename = root+f
        anno_filename = anno_folder+f.split(".")***REMOVED***0***REMOVED***+"_phi_reduced.ano"
        # if len(anno_suffix) > 0:
        #     anno_filename = anno_folder+f.split(".")***REMOVED***0***REMOVED***+anno_suffix

        if not os.path.exists(philtered_filename):
            raise Exception("FILE DOESNT EXIST", philtered_filename)
        
        if not os.path.exists(anno_filename):
            print("FILE DOESNT EXIST", anno_filename)
            continue

        
        encoding1 = detect_encoding(philtered_filename)
        philtered = open(philtered_filename,"r", encoding=encoding1***REMOVED***'encoding'***REMOVED***).read()
        #pre-process notes for comparison with anno punctuation stripped files
        
        philtered = re.sub(pre_process, " ", philtered)
        philtered_words = re.split("\s+", philtered)

        #get our POS
        pos_s1 = nltk.pos_tag(nltk.word_tokenize(philtered))
        pos_dict = {}
        for pos in pos_s1:
            if pos***REMOVED***0***REMOVED*** not in pos_dict:
                pos_dict***REMOVED***pos***REMOVED***0***REMOVED******REMOVED*** = {}
            if pos***REMOVED***1***REMOVED*** not in pos_dict***REMOVED***pos***REMOVED***0***REMOVED******REMOVED***:
                pos_dict***REMOVED***pos***REMOVED***0***REMOVED******REMOVED******REMOVED***pos***REMOVED***1***REMOVED******REMOVED*** = 1
            else:
                pos_dict***REMOVED***pos***REMOVED***0***REMOVED******REMOVED******REMOVED***pos***REMOVED***1***REMOVED******REMOVED*** +=1


        encoding2 = detect_encoding(anno_filename)
        anno = open(anno_filename,"r", encoding=encoding2***REMOVED***'encoding'***REMOVED***).read()
        anno_words = re.split("\s+", anno)

        
        for tup in find_diff(philtered_words, anno_words, phi_matcher=phi_matcher):
            if tup***REMOVED***0***REMOVED*** == "FN":
                false_negatives.append(tup***REMOVED***1***REMOVED***)
            elif tup***REMOVED***0***REMOVED*** == "FP":
                false_positives.append(tup***REMOVED***1***REMOVED***)
            else:
                raise Exception("Unknown type", tup)

        for w in false_negatives:
            print("FN", w)
            if w in pos_dict:
                fn_with_pos***REMOVED***w***REMOVED*** = pos_dict***REMOVED***w***REMOVED***

        #update summary
        summary***REMOVED***"false_positives"***REMOVED*** = summary***REMOVED***"false_positives"***REMOVED*** + false_positives
        summary***REMOVED***"false_negatives"***REMOVED*** = summary***REMOVED***"false_negatives"***REMOVED*** + false_negatives
        summary***REMOVED***"true_positives"***REMOVED*** = summary***REMOVED***"true_positives"***REMOVED*** + true_positives
        summary***REMOVED***"true_negatives"***REMOVED*** = summary***REMOVED***"true_negatives"***REMOVED*** + true_negatives


#calc stats
summary***REMOVED***"total_true_negatives"***REMOVED*** = len(summary***REMOVED***"true_negatives"***REMOVED***)
summary***REMOVED***"total_true_positives"***REMOVED*** = len(summary***REMOVED***"true_positives"***REMOVED***)
summary***REMOVED***"total_false_negatives"***REMOVED*** = len(summary***REMOVED***"false_negatives"***REMOVED***)
summary***REMOVED***"total_false_positives"***REMOVED*** = len(summary***REMOVED***"false_positives"***REMOVED***)
print("true_negatives", summary***REMOVED***"total_true_negatives"***REMOVED***,"true_positives", summary***REMOVED***"total_true_positives"***REMOVED***, "false_negatives", summary***REMOVED***"total_false_negatives"***REMOVED***, "false_positives", summary***REMOVED***"total_false_positives"***REMOVED***)


pos_summary = {}

for k in fn_with_pos:
    for pos in fn_with_pos***REMOVED***k***REMOVED***:
        if pos not in pos_summary:
            pos_summary***REMOVED***pos***REMOVED*** = 0
        pos_summary***REMOVED***pos***REMOVED*** += 1

with open("pos.csv", "w") as f:
    pos_list = pos_summary.keys()
    f.write(",".join(pos_list)+"\n")

    #total results
    results = ***REMOVED******REMOVED***
    for pos in pos_list:
        results.append(pos_summary***REMOVED***pos***REMOVED***)
    results = ***REMOVED***str(x) for x in results***REMOVED***
    f.write(",".join(results))





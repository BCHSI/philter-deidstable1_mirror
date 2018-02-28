import nltk
import re
import os
import json
import difflib
from difflib import SequenceMatcher
from chardet.universaldetector import UniversalDetector


#find all phi and non-phi words
phi = {}
non_phi = {}

# anno_folder = "data/i2b2_anno/"
# NOTES_folder = "data/i2b2_results/"

# anno_folder = "data/diff_test_anno/"
# NOTES_folder = "data/diff_test_notes/"

anno_folder = "data/i2b2_anno/"
NOTES_folder = "data/2b2_notes/"

def detect_encoding(fp):
    detector = UniversalDetector()
    with open(fp, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done: 
                break
        detector.close()
    return detector.result




def find_diff(lst1, lst2, phi_matcher):
    """ iterates the two files returning the unified format, 
        This also chunks any words that match
    
        returns: class, word, start_index

        where class can be: 
        FN: False negative
        FP: False positive
        TP: True positive
        TN: True negatives

    """

    for line in difflib.unified_diff(lst1, lst2):
        #if line.startswith("!") or line.startswith("*"):

        if line.startswith("@"):
            #parse out our start coordinates from the unified diff format
            #this is the format: @@ -17,7 +17,7 @@
            # minus sign (-) denotes first file, plus sign (+) denotes second file
            # the numbers before the comma are the start coorinate
            #start_coordinate1 = int(line.split()***REMOVED***1***REMOVED***.split(",")***REMOVED***0***REMOVED***.replace("-", ""))+2
            #start_coordinate2 = int(line.split()***REMOVED***2***REMOVED***.split(",")***REMOVED***0***REMOVED***.replace("+", ""))+2

            #print("@@Diff", lst1***REMOVED***start_coordinate1***REMOVED***, lst2***REMOVED***start_coordinate2***REMOVED***)
            continue

        #print(line)
        if len(line.replace("+","").strip()) == 0 or len(line.replace("-","").strip())==0 or len(line.strip())==0:
            continue

        if line.startswith("+"):
            #this is in our anno file, not in our notes

            w = line***REMOVED***1:***REMOVED***
            if phi_matcher.match(w):
                #ignore phi characters in anno
                continue
            #print("FP", w)
            yield("FP", w)
            #summary***REMOVED***"false_positives"***REMOVED***.append(w)

            pass
        elif line.startswith("-"):
            #this is in our notes file, not in our anno file
            w = line***REMOVED***1:***REMOVED***
            if phi_matcher.match(w):
                #ignore phi characters in anno
                continue
            #print("FN", w)
            yield("FN", w)
            #summary***REMOVED***"false_negatives"***REMOVED***.append(w)
        else:
            continue
            #print(line)


phi_matcher = re.compile(r"\*\*PHI\*\*")
pre_process = re.compile(r":|\-|\/|_|~")


fn_with_pos = {}


summary = {
            "total_false_positives":0,
            "total_false_negatives":0,
            "total_true_positives": 0,
            "total_true_negatives": 0,
            "false_positives":***REMOVED******REMOVED***, #non-phi words we think are phi
            #"true_positives": ***REMOVED******REMOVED***, #phi words we correctly identify
            "false_negatives":***REMOVED******REMOVED***, #phi words we think are non-phi
            #"true_negatives": ***REMOVED******REMOVED***, #non-phi words we correctly identify
        }

summary_by_file = {}


def relu(v):
    if v > 0:
        return v
    return 0

for root, dirs, files in os.walk(NOTES_folder):

    for f in files:


        #local values per file
        false_positives = ***REMOVED******REMOVED*** #non-phi we think are phi
        true_positives  = ***REMOVED******REMOVED*** #phi we correctly identify
        false_negatives = ***REMOVED******REMOVED*** #phi we think are non-phi
        true_negatives  = ***REMOVED******REMOVED*** #non-phi we correctly identify

        philtered_filename = root+f
        anno_filename = anno_folder+f

        if not os.path.exists(philtered_filename):
            raise Exception("FILE DOESNT EXIST", philtered_filename)
        
        if not os.path.exists(anno_filename):
            print("FILE DOESNT EXIST", anno_filename)
            continue

        
        encoding1 = detect_encoding(philtered_filename)
        philtered = open(philtered_filename,"r", encoding=encoding1***REMOVED***'encoding'***REMOVED***).read()
        #pre-process notes for comparison with anno punctuation stripped files
        
        #philtered = re.sub(pre_process, " ", philtered)
        philtered_words = re.split("\s+", philtered)

        encoding2 = detect_encoding(anno_filename)
        anno = open(anno_filename,"r", encoding=encoding2***REMOVED***'encoding'***REMOVED***).read()


        anno_words = re.split("\s+", anno)

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

        
        anno_nophi = re.split("\s+",phi_matcher.sub(" ",anno))
        philtered_nophi = re.split("\s+",phi_matcher.sub(" ",philtered))

        for tup in find_diff(philtered_nophi, anno_nophi, phi_matcher=phi_matcher):
            if tup***REMOVED***0***REMOVED*** == "FN":
                false_negatives.append(tup***REMOVED***1***REMOVED***)
            elif tup***REMOVED***0***REMOVED*** == "FP":
                false_positives.append(tup***REMOVED***1***REMOVED***)
            else:
                raise Exception("Unknown type", tup)

        # Calulate number of true positives
        note_phi = phi_matcher.findall(philtered) 
        #print(len(note_phi), len(false_negatives))
        num_true_positive = relu(len(note_phi) - len(false_negatives))

        anno_phi = phi_matcher.findall(anno)
        #print(len(anno_phi), len(false_positives))

        # Calculate number of false negatives
        num_reg_anno_words = len(***REMOVED***x for x in anno_words if not phi_matcher.match(x)***REMOVED***)
        num_true_negatives = num_reg_anno_words - len(false_positives)

        for w in false_negatives:
            #print("FN", w)
            if w in pos_dict:
                fn_with_pos***REMOVED***w***REMOVED*** = pos_dict***REMOVED***w***REMOVED***

        summary_by_file***REMOVED***f***REMOVED*** = {
            "num_phi":len(anno_phi),
            "num_idents":len(note_phi),
            "false_positives":false_positives,
            "false_negatives":false_negatives,
            "total_true_positives":num_true_positive,
            "total_true_negatives":num_true_negatives,
            "total_false_negatives":len(false_positives),
            "total_false_positives":len(false_positives),
        }

        #update summary
        summary***REMOVED***"false_positives"***REMOVED*** = summary***REMOVED***"false_positives"***REMOVED*** + false_positives
        summary***REMOVED***"false_negatives"***REMOVED*** = summary***REMOVED***"false_negatives"***REMOVED*** + false_negatives
        summary***REMOVED***"total_true_positives"***REMOVED*** = summary***REMOVED***"total_true_positives"***REMOVED*** + num_true_positive
        summary***REMOVED***"total_true_negatives"***REMOVED*** = summary***REMOVED***"total_true_negatives"***REMOVED*** + num_true_negatives


#calc stats
summary***REMOVED***"total_false_negatives"***REMOVED*** = len(summary***REMOVED***"false_negatives"***REMOVED***)
summary***REMOVED***"total_false_positives"***REMOVED*** = len(summary***REMOVED***"false_positives"***REMOVED***)
print("true_negatives", summary***REMOVED***"total_true_negatives"***REMOVED***,"true_positives", summary***REMOVED***"total_true_positives"***REMOVED***, "false_negatives", summary***REMOVED***"total_false_negatives"***REMOVED***, "false_positives", summary***REMOVED***"total_false_positives"***REMOVED***)

if summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_negatives"***REMOVED*** > 0:
    print("Recall: {:.2%}".format(summary***REMOVED***"total_true_positives"***REMOVED***/(summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_negatives"***REMOVED***)))
elif summary***REMOVED***"total_false_negatives"***REMOVED*** == 0:
    print("Recall: 100%")

if summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_positives"***REMOVED*** > 0:
    print("Precision: {:.2%}".format(summary***REMOVED***"total_true_positives"***REMOVED***/(summary***REMOVED***"total_true_positives"***REMOVED***+summary***REMOVED***"total_false_positives"***REMOVED***)))
elif summary***REMOVED***"total_false_positives"***REMOVED*** == 0:
    print("Precision: 100%")


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





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
NOTES_folder = "data/i2b2_notes_sample/"

def detect_encoding(fp):
    detector = UniversalDetector()
    with open(fp, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done: 
                break
        detector.close()
    return detector.result


punctuation_matcher = re.compile(r"[^a-zA-Z0-9*]")
not_word_matcher = re.compile(r"(\W)")
phi_matcher = re.compile(r"\*+")
pre_process = re.compile(r":|\-|\/|_|~")


def find_diff(lst1, lst2):
    """ iterates the two files returning the unified format, 
        This also chunks any words that match
    
        returns: class, word, start_index

        where class can be: 
        FN: False negative
        FP: False positive
        TP: True positive
        TN: True negatives

    """

    true_positives = []
    true_negatives = []

    false_negatives = []
    false_positives = []

    print(lst1)
    print(lst2)

    d = difflib.Differ()
    for line in list(d.compare(lst1, lst2)):

        if punctuation_matcher.match(line[1:].strip()):
            #skip lines with only punctuation
            continue

        if line.startswith(" "):
            #match
            #print("match", line)
            if re.search("\*+", line[1:]):
                print("match", line)
                true_positives.append(line[1:])
            else:
                true_negatives.append(line[1:])

        elif line.startswith("-"):
            #print("neg", line)
            false_negatives.append(line[1:])
        elif line.startswith("+"):
            #print("pos", line)
            false_positives.append(line[1:])
        else:
            print(line)

        #print(line)

    print(len(true_positives))
    print(len(true_negatives))
    print(len(false_positives))
    print(len(false_negatives))
    





fn_with_pos = {}


summary = {
            "total_false_positives":0,
            "total_false_negatives":0,
            "total_true_positives": 0,
            "total_true_negatives": 0,
            "false_positives":[], #non-phi words we think are phi
            #"true_positives": [], #phi words we correctly identify
            "false_negatives":[], #phi words we think are non-phi
            #"true_negatives": [], #non-phi words we correctly identify
        }

summary_by_file = {}


def relu(v):
    if v > 0:
        return v
    return 0

print("hello")

for root, dirs, files in os.walk(NOTES_folder):
    print("hello1")
    for f in files:


        #local values per file
        false_positives = [] #non-phi we think are phi
        true_positives  = [] #phi we correctly identify
        false_negatives = [] #phi we think are non-phi
        true_negatives  = [] #non-phi we correctly identify

        philtered_filename = root+f
        anno_filename = anno_folder+f

        print(philtered_filename)

        if not os.path.exists(philtered_filename):
            raise Exception("FILE DOESNT EXIST", philtered_filename)
        
        if not os.path.exists(anno_filename):
            print("FILE DOESNT EXIST", anno_filename)
            continue

        
        encoding1 = detect_encoding(philtered_filename)
        philtered = open(philtered_filename,"r", encoding=encoding1['encoding']).read()
        #pre-process notes for comparison with anno punctuation stripped files
        
        #philtered = re.sub(pre_process, " ", philtered)
        philtered_words = re.split("\s+", philtered)

        encoding2 = detect_encoding(anno_filename)
        anno = open(anno_filename,"r", encoding=encoding2['encoding']).read()


        anno_words = re.split("\s+", anno)

     
        find_diff(philtered_words, anno_words)

#calc stats
# summary["total_false_negatives"] = len(summary["false_negatives"])
# summary["total_false_positives"] = len(summary["false_positives"])
# print("true_negatives", summary["total_true_negatives"],"true_positives", summary["total_true_positives"], "false_negatives", summary["total_false_negatives"], "false_positives", summary["total_false_positives"])

# if summary["total_true_positives"]+summary["total_false_negatives"] > 0:
#     print("Recall: {:.2%}".format(summary["total_true_positives"]/(summary["total_true_positives"]+summary["total_false_negatives"])))
# elif summary["total_false_negatives"] == 0:
#     print("Recall: 100%")

# if summary["total_true_positives"]+summary["total_false_positives"] > 0:
#     print("Precision: {:.2%}".format(summary["total_true_positives"]/(summary["total_true_positives"]+summary["total_false_positives"])))
# elif summary["total_false_positives"] == 0:
#     print("Precision: 100%")


pos_summary = {}

for k in fn_with_pos:
    for pos in fn_with_pos[k]:
        if pos not in pos_summary:
            pos_summary[pos] = 0
        pos_summary[pos] += 1

with open("pos.csv", "w") as f:
    pos_list = pos_summary.keys()
    f.write(",".join(pos_list)+"\n")

    #total results
    results = []
    for pos in pos_list:
        results.append(pos_summary[pos])
    results = [str(x) for x in results]
    f.write(",".join(results))





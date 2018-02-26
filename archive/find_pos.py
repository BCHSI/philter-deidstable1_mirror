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

anno_folder = "i2b2_anno/"
NOTES_folder = "i2b2_nochange/"

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

            w = line[1:]
            if phi_matcher.match(w):
                #ignore phi characters in anno
                continue
            yield("FP", w)
            #summary["false_positives"].append(w)


            pass
        elif line.startswith("-"):
            #this is in our notes file, not in our anno file
            w = line[1:]
            yield("FN", w)
            #summary["false_negatives"].append(w)
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
            "false_positives":[], #non-phi words we think are phi
            "true_positives": [], #phi words we correctly identify
            "false_negatives":[], #phi words we think are non-phi
            "true_negatives": [], #non-phi words we correctly identify
        }

for root, dirs, files in os.walk(NOTES_folder):

    for f in files:


        #local values per file
        false_positives = [] #non-phi we think are phi
        true_positives  = [] #phi we correctly identify
        false_negatives = [] #phi we think are non-phi
        true_negatives  = [] #non-phi we correctly identify

        philtered_filename = root+f
        anno_filename = anno_folder+f.split(".")[0]+".ano"
        # if len(anno_suffix) > 0:
        #     anno_filename = anno_folder+f.split(".")[0]+anno_suffix

        if not os.path.exists(philtered_filename):
            raise Exception("FILE DOESNT EXIST", philtered_filename)
        
        if not os.path.exists(anno_filename):
            print("FILE DOESNT EXIST", anno_filename)
            continue

        
        encoding1 = detect_encoding(philtered_filename)
        philtered = open(philtered_filename,"r", encoding=encoding1['encoding']).read()
        #pre-process notes for comparison with anno punctuation stripped files
        
        philtered = re.sub(pre_process, " ", philtered)
        philtered_words = re.split("\s+", philtered)

        #get our POS
        pos_s1 = nltk.pos_tag(nltk.word_tokenize(philtered))
        pos_dict = {}
        for pos in pos_s1:
            if pos[0] not in pos_dict:
                pos_dict[pos[0]] = {}
            if pos[1] not in pos_dict[pos[0]]:
                pos_dict[pos[0]][pos[1]] = 1
            else:
                pos_dict[pos[0]][pos[1]] +=1


        encoding2 = detect_encoding(anno_filename)
        anno = open(anno_filename,"r", encoding=encoding2['encoding']).read()
        anno_words = re.split("\s+", anno)

        
        for tup in find_diff(philtered_words, anno_words, phi_matcher=phi_matcher):
            if tup[0] == "FN":
                false_negatives.append(tup[1])
            elif tup[0] == "FP":
                false_positives.append(tup[1])
            else:
                raise Exception("Unknown type", tup)

        for w in false_negatives:
            if w in pos_dict:
                fn_with_pos[w] = pos_dict[w]



pos_summary = {}


for k in fn_with_pos:
    for pos in fn_with_pos[k]:
        if pos not in pos_summary:
            pos_summary[pos] = 0
        pos_summary[pos] += 1

with open("pos.csv", "w") as f:
    pos_list = pos_summary.keys()
    f.write(",".join(pos_list))

    #total results
    results = []
    for pos in pos_list:
        results.append(pos_summary[pos])
    results = [str(x) for x in results]
    f.write(",".join(results))


d = nltk.help.upenn_tagset()
pos_list = pos_summary.keys()
for pos in pos_list:
    if pos in d:
        print(d[pos])
    else:
        print("not available")




import json
import re
import os
from chardet.universaldetector import UniversalDetector
#makes a "fake" set of blacklists / whitelists for us to test the sets

input_anno = "../../data/i2b2_anno/"
input_notes = "../../data/i2b2_notes/"

whitelist_dict = {}
blacklist_dict = {}

def detect_encoding(fp):
    detector = UniversalDetector()
    with open(fp, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done: 
                break
        detector.close()
    return detector.result


phi_matcher = re.compile(r"\s*\*\*PHI")
pre_process = re.compile(r":***REMOVED***^a-zA-Z0-9***REMOVED***")

for root,dirs,files in os.walk(input_anno):
    for f in files:


        anno_filename = root+f

        if not os.path.exists(anno_filename):
            print("FILE DOESNT EXIST", anno_filename)
            continue

        encoding2 = detect_encoding(anno_filename)
        anno = open(anno_filename,"r", encoding=encoding2***REMOVED***'encoding'***REMOVED***).read()
        anno_words = re.split("\s+", anno)

        for w in anno_words:

            if re.search(r"\*+", w):
                continue

            temp = re.sub(pre_process, "",w.lower().strip())
            
            if re.search(r"\d+", temp):
                #skip anything with digits
                continue
            
            if len(temp) == 0:
                continue
            if temp not in whitelist_dict:
                whitelist_dict***REMOVED***temp***REMOVED*** = 0
            whitelist_dict***REMOVED***temp***REMOVED*** += 1

        note_filename = input_notes + f

        encoding = detect_encoding(note_filename)
        note = open(note_filename,"r", encoding=encoding2***REMOVED***'encoding'***REMOVED***).read()
        note_words = re.split("\s+", note)

        #get all phi words:
        for w in note_filename:

            temp = re.sub(pre_process, "",w.lower().strip())
            
            if re.search(r"\d+", temp):
                #skip anything with digits
                continue

            if len(temp) == 0:
                continue
                
            if temp not in whitelist_dict:
                if temp not in blacklist_dict:
                    blacklist_dict***REMOVED***temp***REMOVED*** = 0
                blacklist_dict***REMOVED***temp***REMOVED*** += 1

json.dump(whitelist_dict, open("whitelist.json", "w"), indent=4)
json.dump(blacklist_dict, open("blacklist.json", "w"), indent=4)
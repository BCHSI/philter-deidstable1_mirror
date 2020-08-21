

import json
import re
import os
from chardet.universaldetector import UniversalDetector
#makes a "fake" set of blacklists / whitelists for us to test the sets

input_anno = "../../data/i2b2_anno/"
input_notes = "../../data/i2b2_notes/"
phi_data = json.loads(open("../../data/phi_notes.json", "r").read())

phi_matcher = re.compile(r"\s*\*\*PHI")
pre_process = re.compile(r":[^a-zA-Z0-9]")

whitelist_dict = {}
blacklist_dict = {}

#build our blacklist
for fn in phi_data:
    for phi in phi_data[fn]["phi"]:
        for w in re.split("\s+", phi["text"]):
            temp = re.sub(pre_process, "",w.lower().strip())
            blacklist_dict[temp] = 1


def detect_encoding(fp):
    detector = UniversalDetector()
    with open(fp, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done: 
                break
        detector.close()
    return detector.result




for root,dirs,files in os.walk(input_anno):
    for f in files:


        anno_filename = root+f

        if not os.path.exists(anno_filename):
            print("FILE DOESNT EXIST", anno_filename)
            continue

        encoding2 = detect_encoding(anno_filename)
        anno = open(anno_filename,"r", encoding=encoding2['encoding']).read()
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
            if temp not in blacklist_dict:
                if temp not in whitelist_dict:
                    whitelist_dict[temp] = 0
                whitelist_dict[temp] += 1


json.dump(whitelist_dict, open("whitelist.json", "w"), indent=4)
json.dump(blacklist_dict, open("blacklist.json", "w"), indent=4)
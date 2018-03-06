"""
TODO: 
In order context, finds the window before and after a specific PHI and get's part of speech

"""


import nltk
import re
import os
import json
import difflib
from difflib import SequenceMatcher
from chardet.universaldetector import UniversalDetector


pos = {}
total_counts = {}

phi = json.loads(open("./phi_notes.json", "r").read())

for fn in phi:

    #get text and remove any initial *'s from the raw notes
    txt = phi[fn]["text"].replace("*", " ")

    lst = re.split("(\s+)", txt)
    cleaned = []
    for item in lst:
        if len(item) > 0:
            cleaned.append(item)
    pos_list = nltk.pos_tag(cleaned)

    phi_set = {}
    for p in phi[fn]["phi"]:
        phi_set[p["text"]] = 1

    pos_phi = {}
    for item in pos_list:
        if item[0] in phi_set:
            pos_phi[item[0]] = item[1]

            if item[1] not in total_counts:
                total_counts[item[1]] = 0
            total_counts[item[1]] += 1

    pos[fn] = pos_phi

json.dump(pos, open("phi_pos.json", "w"), indent=4)
json.dump(total_counts, open("phi_pos_total.json", "w"), indent=4)

#save a csv output sorted

lst = []
for k in total_counts:
    lst.append([k,total_counts[k]])

lst = sorted(lst, key=lambda x: x[1], reverse=True)
with open("phi_pos.csv", "w") as f:
    f.write(",".join([ str(x[0]) for x in lst])+"\n")
    f.write(",".join([ str(x[1]) for x in lst])+"\n")

#lst = total_counts.keys()




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
    txt = phi***REMOVED***fn***REMOVED******REMOVED***"text"***REMOVED***.replace("*", " ")

    lst = re.split("(\s+)", txt)
    cleaned = ***REMOVED******REMOVED***
    for item in lst:
        if len(item) > 0:
            cleaned.append(item)
    pos_list = nltk.pos_tag(cleaned)

    phi_set = {}
    for p in phi***REMOVED***fn***REMOVED******REMOVED***"phi"***REMOVED***:
        phi_set***REMOVED***p***REMOVED***"text"***REMOVED******REMOVED*** = 1

    pos_phi = {}
    for item in pos_list:
        if item***REMOVED***0***REMOVED*** in phi_set:
            pos_phi***REMOVED***item***REMOVED***0***REMOVED******REMOVED*** = item***REMOVED***1***REMOVED***

            if item***REMOVED***1***REMOVED*** not in total_counts:
                total_counts***REMOVED***item***REMOVED***1***REMOVED******REMOVED*** = 0
            total_counts***REMOVED***item***REMOVED***1***REMOVED******REMOVED*** += 1

    pos***REMOVED***fn***REMOVED*** = pos_phi

json.dump(pos, open("phi_pos.json", "w"), indent=4)
json.dump(total_counts, open("phi_pos_total.json", "w"), indent=4)

#save a csv output sorted

lst = ***REMOVED******REMOVED***
for k in total_counts:
    lst.append(***REMOVED***k,total_counts***REMOVED***k***REMOVED******REMOVED***)

lst = sorted(lst, key=lambda x: x***REMOVED***1***REMOVED***, reverse=True)
with open("phi_pos.csv", "w") as f:
    f.write(",".join(***REMOVED*** str(x***REMOVED***0***REMOVED***) for x in lst***REMOVED***)+"\n")
    f.write(",".join(***REMOVED*** str(x***REMOVED***1***REMOVED***) for x in lst***REMOVED***)+"\n")

#lst = total_counts.keys()




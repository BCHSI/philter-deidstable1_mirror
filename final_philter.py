import json
import os
import re

foutpath = "data/i2b2_postprocess/"

blacklist = json.load(open("false_negatives.json", "r"))

for root, dirs, files in os.walk("data/i2b2_results/"):
    for filename in files:
        orig_f = root+filename
        #encoding = self.detect_encoding(orig_f)
        txt = open(orig_f,"r").read()
        content = ***REMOVED******REMOVED***
        with open(foutpath+filename, "w") as f:

            for w in  re.split("\s+", txt):
                if w not in blacklist:
                    content.append(w)
                else:
                    content.append(" **PHI** ")

            f.write("".join(content))

import json
import os
import re
from chardet.universaldetector import UniversalDetector

foutpath = "data/i2b2_postprocess/"

blacklist = json.load(open("data/fn_blacklist.json", "r"))

with open("data/summary_text.txt", "r") as f:
    
    ignore = set(["FN","number:", "False","Negative:", ""])
    reading = False
    for line in f:
        if line.startswith("False Negative:"):
            reading = True
        elif line.startswith("FN number:"):
            reading = False

        if reading:
            words = re.split("\s+", line)
            for w in words:
                if w not in ignore:
                    w = w.lower().strip()
                    if w not in blacklist:
                        blacklist[w] = 0
                    blacklist[w] += 1

json.dump(blacklist, open("data/fn_blacklist.json", "w"), indent=4)

def detect_encoding(fp):
    detector = UniversalDetector()
    with open(fp, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done: 
                break
        detector.close()
    return detector.result

for root, dirs, files in os.walk("data/i2b2_results_002/"):
    for filename in files:
        orig_f = root+filename
        encoding = detect_encoding(orig_f)
        txt = open(orig_f,"r", encoding=encoding['encoding']).read()
        content = []
        with open(foutpath+filename, "w") as f:

            for w in  re.split("\s+", txt):
                lower_w = w.lower().strip()
                if lower_w not in blacklist:
                    content.append(w)
                else:
                    content.append("**PHI**")

            f.write(" ".join(content))

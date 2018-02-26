import json
import os
import re
from chardet.universaldetector import UniversalDetector

def detect_encoding(fp):
    detector = UniversalDetector()
    with open(fp, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done: 
                break
        detector.close()
    return detector.result


#tags all parts of speech
for root, dirs, files in os.walk("i2b2_notes/"):
    for f in files:

        #note file
        orig_f = root+f
        encoding = detect_encoding(orig_f)
        note_txt = open(orig_f,"r", encoding=encoding['encoding']).read()

        with open("i2b2_nochange/"+f.split(".")[0]+"_phi_reduced.txt", "w") as fo:
            fo.write(note_txt)
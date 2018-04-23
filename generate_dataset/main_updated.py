import nltk
import re
import os
import json
import pickle
import difflib
from difflib import SequenceMatcher
from chardet.universaldetector import UniversalDetector
from coordinate_map import CoordinateMap
import xml.etree.ElementTree as ET



xml_folder = "./testing-PHI-Gold-fixed-updated/"

phi = {} #fn --> {"text":"...", "phi":[{"type":"DATE"...}]}

def isolate_phi(xml_folder):
    #isolate all phi and data with coordinates
    #turn them into a json representation
    for root_dir, dirs, files in os.walk(xml_folder):
        for f in files:

            tree = ET.parse(root_dir+f)
            root = tree.getroot()

            text = ""
            phi_list = []

            for child in root:
                if child.tag == "TEXT":
                    text = child.text
                    #print (child.tag, child.attrib, child.text)
                if child.tag == "TAGS":
                    for t in child:
                        phi_list.append(t.attrib)
                        #print(t.tag, t.attrib, t.text)
            phi[f] = {"text":text, "phi":phi_list}

isolate_phi(xml_folder)

#save our data
json.dump(phi, open("phi_notes_updated.json", "w"), indent=4)

NOTES_FOLDER = "../data/i2b2_notes_updated/"
ANNO_FOLDER = "../data/i2b2_anno_updated/"
PHI_FOLDER  = "../data/i2b2_phi/"
PHI_CONTEXT = "../data/i2b2_phi_context_updated/"
PHI_POS     = "../data/i2b2_phi_pos_updated/"

#save our phi notes 
for fn in phi:

    #get text and remove any initial *'s from the raw notes
    txt = phi[fn]["text"].replace("*", " ")

    #save our notes file
    with open(NOTES_FOLDER+fn.split(".")[0]+".txt", "w") as note_file:
        note_file.write(txt)

    #create a coordinate mapping of all phi
    c = CoordinateMap()
    for p in phi[fn]["phi"]:
        start = int(p["start"])
        end = int(p["end"])
        c.add_extend(fn, start, end)

    contents = []
    last_marker = 0
    for start,stop in c.filecoords(fn):
        contents.append(txt[last_marker:start])
        
        #add a * for each letter preserving shape
        phi_hidden = re.sub(r"[a-zA-Z0-9]", "*", txt[start:stop])
        contents.append(phi_hidden)
        last_marker = stop

    #wrap it up by adding on the remaining values if we haven't hit eof
    if last_marker < len(txt):
        contents.append(txt[last_marker:len(txt)])

    with open(ANNO_FOLDER+fn.split(".")[0]+".txt", "w") as anno_file:
        anno_file.write("".join(contents))



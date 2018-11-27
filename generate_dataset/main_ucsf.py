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
import sys




xml_folder = sys.argv[1]


phi = {} #fn --> {"text":"...", "phi":[{"type":"DATE"...}]}

def isolate_phi(xml_folder):
    #isolate all phi and data with coordinates
    #turn them into a json representation
    for root_dir, dirs, files in os.walk(xml_folder):
        for f in files:
            with open(root_dir+f, 'r', encoding='latin1') as file:
                tree = ET.parse(file)
                root = tree.getroot()

                text = ""
                phi_list = []

                for child in root:
                    if child.tag == "TEXT":
                        text = child.text
                        # if f == '167937985.txt.xml':
                        #     print(text)
                        #print (child.tag, child.attrib, child.text)
                    if child.tag == "TAGS":
                        for t in child:
                            phi_list.append(t.attrib)
                            #print(t.tag, t.attrib, t.text)
                phi[f] = {"text":text, "phi":phi_list}

isolate_phi(xml_folder)

#save our data
json.dump(phi, open("../data/phi_notes_batch102_pass1.json", "w"), indent=4)

NOTES_FOLDER = "../data/ucsf_notes/"
ANNO_FOLDER = "../data/ucsf_anno/"
PHI_FOLDER  = "../data/ucsf_phi/"
PHI_CONTEXT = "../data/ucsf_phi_context/"
PHI_POS     = "../data/ucsf_phi_pos/"

#save our phi notes 
for fn in phi:

    #get text and remove any initial *'s from the raw notes
    txt = phi[fn]["text"].replace("*", " ")

    #save our notes file
    with open(NOTES_FOLDER+fn.split(".")[0]+".txt", "w",encoding='utf-8') as note_file:
        note_file.write(txt)

    #create a coordinate mapping of all phi
    c = CoordinateMap()
    for p in phi[fn]["phi"]:
        start = int(p["spans"].split("~")[0])
        end = int(p["spans"].split("~")[1])
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

    with open(ANNO_FOLDER+fn.split(".")[0]+".txt", "w", encoding='utf-8') as anno_file:
        anno_file.write("".join(contents))


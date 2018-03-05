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

phi_data = json.load(open("./phi_notes.json", "r").read())

for f in phi_data:

	
	
	lst = re.split("(\s+)", text)
    cleaned = []
    for item in lst:
        if len(item) > 0:
            cleaned.append(item)
    pos_list = nltk.pos_tag(cleaned)
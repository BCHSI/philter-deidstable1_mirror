#!/bin/bash

# This script runs philtervand its associated evaluation scripts on the ucsf 200-note corpus
# Note that input and output directories will vary based on your own file locations

# 1. From the de-id_stable1 directory, run downloaded and installed philter script on ucsf dataset
philter -i /media/DataHD/philter-annotations/pooneh/input_notes/ -o /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/data/ucsf_results/ -r -p 32

# 2. Run evaluation script on de-identified ucsf notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/data/ucsf_results/ -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_eval/

# 3. Run false negative script
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/getFNcategory_updated.py
# The script will ask you to input the path to the summary dictionary:
/media/DataHD/r_phi_corpus/kathleen/ucsf_eval/summary_dict.pkl
# ...and for the path to the directory containing the annotation files
/media/DataHD/philter-annotations/pooneh/pooneh-done

# Results json file is outputted to the same directory that the summary file is located in
# To visualize FN categories, enter these commands into the terminal within the resuls directory:
python3
import json
results = json.loads(open("FN_dict.json").read())
for subdict in results:
	print(subdict)
	print(len(results[subdict]))


##### Whitelist only ######
# 1. From the de-id_stable1 directory, run downloaded and installed philter script on ucsf dataset
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_whitelist.py -i /media/DataHD/philter-annotations/pooneh/input_notes/ -o /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/data/ucsf_results_whitelist/ -r -p 32

# 2. Run evaluation script on de-identified ucsf notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/data/ucsf_results_whitelist/ -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_eval_whitelist/

# 3. Run false negative script
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/getFNcategory_fred.py
# The script will ask you to input the path to the summary dictionary:
/media/DataHD/r_phi_corpus/kathleen/ucsf_eval_whitelist/summary_dict.pkl
# ...and for the path to the directory containing the annotation files
/media/DataHD/philter-annotations/pooneh/pooneh-done
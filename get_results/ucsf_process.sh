#!/bin/bash

# This script runs philtervand its associated evaluation scripts on the ucsf 200-note corpus
# Note that input and output directories will vary based on your own file locations

# 1. From the de-id_stable1 directory, run downloaded and installed philter script on ucsf dataset
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_2.0.py -i /media/DataHD/philter-annotations/pooneh/input_notes/ -o /media/DataHD/r_phi_corpus/kathleen/philter_2.0_results/ -r -p 32

# 2. Run evaluation script on de-identified ucsf notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/data/philter_2.0_results/ -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/philter_2.0_eval/

# 3. Run false negative script
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/getFNcategory_final.py /media/DataHD/r_phi_corpus/kathleen/philter_2.0_eval/summary_dict.pkl /media/DataHD/philter-annotations/pooneh/pooneh-done /media/DataHD/r_phi_corpus/kathleen/philter_2.0_eval/fn_categories_ucsf_philter2.csv

# Results json file is outputted to the same directory that the summary file is located in


##### Whitelist only ######
# 1. Run the whitelist-only scrpt on the UCSF 200
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_whitelist.py -i /media/DataHD/philter-annotations/pooneh/input_notes/ -o /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/data/ucsf_results_whitelist/ -r -p 32

# 2. Run evaluation script on de-identified ucsf notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/data/ucsf_results_whitelist/ -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_eval_whitelist/

##### Whitelist + Regex ######
# 1. Run the whitelist-only scrpt on the UCSF 200
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_whitelist.py -i /media/DataHD/philter-annotations/pooneh/input_notes/ -o /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/data/ucsf_results_whitelist/ -r -p 32

# 2. Run evaluation script on de-identified ucsf notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/data/ucsf_results_whitelist/ -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_eval_whitelist/







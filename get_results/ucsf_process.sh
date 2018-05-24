#!/bin/bash

# This script runs philtervand its associated evaluation scripts on the ucsf 200-note corpus
# Note that input and output directories will vary based on your own file locations

# 1. Run downloaded and installed philter script on ucsf dataset
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_2.0.py -i /media/DataHD/philter-annotations/pooneh/input_notes/ -o /media/DataHD/r_phi_corpus/kathleen/philter_2.0_results/ -r -p 32

# 2. Run evaluation script on de-identified ucsf notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/philter_2.0_results/ -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/philter_2.0_eval/

# Expected output:
# 191 notes have been evaulated.
# True Positive in all notes: 7963
# False Positive in all notes: 2683
# False Negative in all notes: 250
# Recall: 96.96%
# Precision: 74.80%

# 3. Run false negative script
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/getFNcategory_final.py /media/DataHD/r_phi_corpus/kathleen/philter_2.0_eval/summary_dict.pkl /media/DataHD/philter-annotations/pooneh/pooneh-done /media/DataHD/r_phi_corpus/kathleen/philter_2.0_eval/fn_categories_ucsf_philter2.csv

# Expected output:
# Not PHI: 13
# Age(>90) FNs: 0
# Date FNs: 81
# Contact FNs: 22
# ID FNs: 2
# Name FNs: 93
# Location FNs: 71


##### Whitelist only ######
# 1. Run the whitelist-only scrpt on the UCSF 200
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_whitelist.py -i /media/DataHD/philter-annotations/pooneh/input_notes/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_results_whitelist/ -r -p 32

# 2. Run evaluation script on de-identified ucsf notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/ucsf_results_whitelist/ -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_eval_whitelist/

# Expected results:
# 191 notes have been evaulated.
# True Positive in all notes: 7441
# False Positive in all notes: 12546
# False Negative in all notes: 771
# Recall: 90.61%
# Precision: 37.23%


##### Whitelist + Regex ######
# 1. Run the whitelist-only scrpt on the UCSF 200
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_whitelist_regex.py -i /media/DataHD/philter-annotations/pooneh/input_notes/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_results_whitelist_regex/ -r -p 32

# 2. Run evaluation script on de-identified ucsf notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/ucsf_results_whitelist_regex/ -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_eval_whitelist_regex/

# Expected results:
# 191 notes have been evaulated.
# True Positive in all notes: 7762
# False Positive in all notes: 10172
# False Negative in all notes: 237
# Recall: 97.04%
# Precision: 43.28%





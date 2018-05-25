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

# 2a. Run get_unlabeled_fns script to gather phi without a category label, and manually annotate category (including non-phi, if you don't agree with original annotation)
# This will not create any output files bit rather output the note word, followed by the context
# Create 2-column csv (word, category) containing all annotations, and upload to eval folder
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/get_unlabeled_fns.py /media/DataHD/r_phi_corpus/kathleen/philter_2.0_eval/summary_dict.pkl /media/DataHD/philter-annotations/pooneh/pooneh-done

# 3. Run false negative script
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/getFNcategory_final.py /media/DataHD/r_phi_corpus/kathleen/philter_2.0_eval/summary_dict.pkl /media/DataHD/philter-annotations/pooneh/pooneh-done /media/DataHD/r_phi_corpus/kathleen/philter_2.0_eval/fn_categories_ucsf_philter2.csv

# Expected output:
# Not PHI: 16
# Age(>90) FNs: 0
# Contact FNs: 18
# Date FNs: 46
# Name FNs: 94
# Location FNs: 72
# ID FNs: 2

# NOT PHI count will be subtracted from total number of FNs. The sum of all categories may also be slightly different than results from #2, due to outdated eval script
##### Whitelist only ######

# 4. Run the whitelist-only scrpt on the UCSF 200
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_whitelist.py -i /media/DataHD/philter-annotations/pooneh/input_notes/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_results_whitelist/ -r -p 32

# 5. Run evaluation script on de-identified ucsf notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/ucsf_results_whitelist/ -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_eval_whitelist/

# Expected results:
# 191 notes have been evaulated.
# True Positive in all notes: 7441
# False Positive in all notes: 12546
# False Negative in all notes: 771
# Recall: 90.61%
# Precision: 37.23%

# 5a. Run get_unlabeled_fns script to gather phi without a category label, and manually annotate category (including non-phi, if you don't agree with original annotation)
# This will not create any output files bit rather output the note word, followed by the context
# Count number of non-phi occurrences, subtract from fn total
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/get_unlabeled_fns.py /media/DataHD/r_phi_corpus/kathleen/ucsf_eval_whitelist/summary_dict.pkl /media/DataHD/philter-annotations/pooneh/pooneh-done


##### Whitelist + Regex ######
# 6. Run the whitelist-only scrpt on the UCSF 200
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_whitelist_regex.py -i /media/DataHD/philter-annotations/pooneh/input_notes/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_results_whitelist_regex/ -r -p 32

# 7. Run evaluation script on de-identified ucsf notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/ucsf_results_whitelist_regex/ -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/ucsf_eval_whitelist_regex/

# 7a. Run get_unlabeled_fns script to gather phi without a category label, and manually annotate category (including non-phi, if you don't agree with original annotation)
# This will not create any output files bit rather output the note word, followed by the context
# Count number of non-phi occurrences, subtract from fn total
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/get_unlabeled_fns.py /media/DataHD/r_phi_corpus/kathleen/ucsf_eval_whitelist_regex/summary_dict.pkl /media/DataHD/philter-annotations/pooneh/pooneh-done

# Expected results:
# 191 notes have been evaulated.
# True Positive in all notes: 7762
# False Positive in all notes: 10172
# False Negative in all notes: 237
# Recall: 97.04%
# Precision: 43.28%


######### MIT Tool ##########

# 8. Run MIT de-id tool on UCSF 200
perl /media/DataHD/r_phi_corpus/kathleen/mit_deid/deid-1.1/deid.pl id /media/DataHD/r_phi_corpus/kathleen/mit_deid/deid-1.1/deid.config

# Expected output:
# Num of true positives = 0

# Num of false positives = 4777

# Num of false negatives = 39

# Sensitivity/Recall = 0

# PPV/Specificity = 0

# 9. Run processing sript on output, so notes can be evaluated
python /media/DataHD/r_phi_corpus/kathleen/mit_deid/MIT_process2.py
'/media/DataHD/r_phi_corpus/kathleen/mit_deid/deid-1.1/id.res'
'/media/DataHD/r_phi_corpus/kathleen/mit_deid/mit_reduced'

# 10. Run eval script on phi-reduced notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/philter_eval.py -p /media/DataHD/r_phi_corpus/kathleen/mit_deid/mit_reduced -a /media/DataHD/philter-annotations/pooneh/pooneh-done/ -o /media/DataHD/r_phi_corpus/kathleen/mit_deid/mit_eval

# 10a. Run get_unlabeled_fns script to gather phi without a category label, and manually annotate category (including non-phi, if you don't agree with original annotation)
# This will not create any output files bit rather output the note word, followed by the context
# Create 2-column csv (word, category) containing all annotations, and upload to eval folder
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/get_unlabeled_fns.py /media/DataHD/r_phi_corpus/kathleen/mit_deid/mit_eval/summary_dict.pkl /media/DataHD/philter-annotations/pooneh/pooneh-done

# 11. Run FN categorization script on MIT notes
python3 /media/DataHD/r_phi_corpus/kathleen/de-id_stable1/getFNcategory_final.py /media/DataHD/r_phi_corpus/kathleen/mit_deid/mit_eval/summary_dict.pkl /media/DataHD/philter-annotations/pooneh/pooneh-done/ /media/DataHD/r_phi_corpus/kathleen/mit_deid/mit_eval/fn_categories_mit.csv

# Expected results:
# ID FNs: 203
# Not PHI: 131
# Date FNs: 326
# Age(>90) FNs: 0
# Location FNs: 263
# Contact FNs: 46
# Name FNs: 137




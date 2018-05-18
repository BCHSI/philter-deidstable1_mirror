#!/bin/bash

# This script runs philtervand its associated evaluation scripts on the ucsf 200-note corpus
# Note that input and output directories will vary based on your own file locations

# 1. Run downloaded and installed philter script on ucsf dataset
philter -i ../../../philter-annotations/pooneh/input_notes/ -o ../data/ucsf_results/ -r -p 32

# 2. Run evaluation script on de-identified ucsf notes
python3 ../philter_eval_pypi2.py -p ../data/ucsf_results/ -a ../../philter-annotations/pooneh/pooneh-done/ -o ucsf_eval/

# 3. Run whitelist-only philter on i2b2 dataset
python3 ../getFNcategory_updated.py
# The script will ask you to input the path to the summary dictionary:
summary_dict.pkl
# ...and for the path to the directory containing the annotation files
/media/DataHD/philter-annotations/pooneh/pooneh-done
# Adds variables in to regex to create complex regex

import os
import json

# Define regex variables

# Get gene symbols from json whitelist
symbols_json = json.loads(open("../../blacklists/town_tokens_black_list_fp_removed.json").read())
gene_symbols = ''
for key in symbols_json:
    gene_symbols += key + '|'
# Get rid of last "|"
gene_symbols = gene_symbols[:-1]


# Do folder walk and transform each file containing a variable to be transformed
rootdir = '.'
for root, dirs, files in os.walk(rootdir):
    for file in files:
        file_root = file.split(".")[0]

        if ".txt" in file and "_transformed.txt" not in file and "catchall" not in file:

            filepath = os.path.join(root, file)

            # Get current file name and create transformed name
            new_file_name = file_root + "_transformed.txt"
            new_filepath = os.path.join(root, new_file_name)

            # Open file
            regex = open(filepath, "r").read().strip()

            # replace variable in regex with complex list
            if '"""+town_names+r"""' in regex:
                regex = regex.replace('"""+town_names+r"""',gene_symbols)
                # Write new file
                with open(new_filepath, "w") as fout:
                    fout.write(regex)

# Adds variables in to regex to create complex regex

import os
import json

# Define regex variables

# Get gene symbols from json whitelist
symbols_json = json.loads(open("../whitelists/whitelist_genes_and_patho_terms.json").read())
gene_symbols = ''
for key in symbols_json:
	gene_symbols += key + '|'
# Get rid of first and last "|"
gene_symbols = gene_symbols[1:-1]


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
            if '"""+gene_symbols+r"""' in regex:
                regex = regex.replace('"""+gene_symbols+r"""',gene_symbols)
                # Write new file
                with open(new_filepath, "w") as fout:
                    fout.write(regex)

            # delete duplicate  "_transform" files
            # if os.path.isfile(new_filepath):
            #     og_file = open(filepath).read().strip()
            #     transformed_file = open(new_filepath).read().strip()
            #
            #     if og_file == transformed_file:
            #         os.remove(new_filepath)
            #         print("Removed %s" % (new_filepath))

# Adds variables in to regex to create complex regex

import os
import json

# Define regex variables

# Get stagings terms from json whitelist
terms_json = json.loads(open("../whitelists/whitelist_staging_terms.json").read())
staging_terms = ''
for key in terms_json:
    staging_terms += key + '|'
# Get rid of last "|"
staging_terms = staging_terms[:-1]

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
            if '"""+staging_terms+r"""' in regex:
                regex = regex.replace('"""+staging_terms+r"""',staging_terms)
                # Write new file
                with open(new_filepath, "w") as fout:
                    fout.write(regex)
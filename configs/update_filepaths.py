# Because I removed all the duplicate _transformed.txt files in the regex lists, I needed to fix any config files which called a _transformed.txt file which had been removed

import os
import re
import json

def pull_paths(inputfile):

    # get config filepaths which need to change
    with open(inputfile) as fin:
        text = fin.read()
    filepaths = re.findall('raise Exception\(\"Config filepath does not exist\"\, pattern\[\"filepath\"\]\)\s+?Exception\: \(\'Config filepath does not exist\'\, \'([\S]+?)\'\)\s+\(deidproj\) NUS11097-10-pauburk\:philter-ucsf-new pauburk\$ python3 deidpipe\.py -i \.\/data\/i2b2_notes\/', text, re.MULTILINE)

    # go through each config file
    rootdir = "."
    for root, dirs, files in os.walk(rootdir):
        for file in files:

            # check that file ends in .json
            if '.json' in file:
                print(file)
                new_file_text = []

                filepath = os.path.join(root, file)

                file_text = json.loads(open(filepath).read())

                # go through each item in the json file
                for item in file_text:

                    # if the item has a filepath key
                    if 'filepath' in item:

                        # go through each path that needs to be changed
                        for path in filepaths:

                            # check if path is the value for 'filepath'
                            if item['filepath'] == path:

                                # remove "_transformed" from filepath
                                item['filepath'] = re.findall('([\S]+)\_transformed\.txt', path)[0]+".txt"

                    # add changed item to the changed text to output
                    new_file_text.append(item)

                # write over the orginal file but with the changed filepaths
                with open(filepath, "w") as fout:
                    json.dump(new_file_text, fout, indent=4)

def main():
    pull_paths("paths_to_update.txt")

main()

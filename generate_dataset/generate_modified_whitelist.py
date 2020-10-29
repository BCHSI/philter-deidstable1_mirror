import json
import pandas as pd
import argparse
import os


def generate_whitelist(whitelist, additions, removals, outfile):

    whitelist = json.loads(open(whitelist).read())

    # Add tokens
    if additions != None:
        additions = open(additions).readlines()

        new_words = list(additions)

        for word in new_words:
            #print(word)
            word = word.strip()
            whitelist[word] = 1

    # Remove tokens
    if removals != None:
        removals = open(removals).readlines()

        words_to_remove = list(removals)

        for word in words_to_remove:
            print(word)
            whitelist.pop(word, None)



    with open(outfile,'w') as file:
        json.dump(whitelist, file)



def main():
    # get input/output/filename
    help_str = """ Philter -- PHI filter for clinical notes """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-w", "--whitelist",
                    help="Path to the base whitelist",
                    type=str)
    ap.add_argument("-a", "--additions",
                    help="Path to the txt file that contains the new words to add",
                    type=str)
    ap.add_argument("-r", "--removals",
                    help="Path to the txt file that contains the words to remove",
                    type=str)
    ap.add_argument("-o", "--outfile",
                    help="Name of the output whitelist",
                    type=str)


    args = ap.parse_args()

    base_whitelist = args.whitelist
    additions = args.additions
    removals = args.removals
    outfile = args.outfile

    generate_whitelist(base_whitelist, additions, removals, outfile)



if __name__ == "__main__":
    main()

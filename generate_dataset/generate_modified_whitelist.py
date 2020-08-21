import json
import pandas as pd
import argparse

def generate_whitelist(whitelist, additions, outfile):

    whitelist = json.loads(open(whitelist).read())

    additions = open(additions).readlines()

    new_words = list(additions)

    for word in new_words:
        word = word.strip()
        whitelist[word] = 1

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
                    help="Path to the newline txt file that contains the new words to add",
                    type=str)
    ap.add_argument("-o", "--outfile",
                    help="Name of the output whitelist",
                    type=str)


    args = ap.parse_args()

    base_whitelist = args.whitelist
    additions = args.additions
    outfile = args.outfile

    generate_whitelist(base_whitelist, additions, outfile)



if __name__ == "__main__":
    main()

import re
import argparse


def find_matches(fin):

    matches = []

    with open(fin, "r") as f:
        full_text = f.readlines()

    for i in range(len(full_text)):

        if full_text[i].startswith("<re.Match object; "):

            j = i
            while not full_text[j].startswith("map_regex(): "):
                j -= 1

            matches.append({"match" : full_text[i], "info" : full_text[j]})

    return matches



def output_matches(matches, fout):

    with open(fout, "w") as f:

        for m in matches:
            f.write(m["match"])
            f.write(m["info"])
            f.write("\n")



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--fin", type=str) # path to Philter's output .txt file
    args = ap.parse_args()

    fin = args.fin
    fout = fin[:-4]+"_matches.txt"

    matches = find_matches(fin)
    output_matches(matches, fout)


main()

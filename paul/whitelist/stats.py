import os
import shutil
import re
import argparse
import time

# set up output directories, make sure user doesn't lose files accidentally
def setup_output():

    ans = "y"
    if os.path.isdir("./stats_out"):
        print("\nThis program will replace already existing files:")
        print("  -  The directory and all contents 'stats_out' in ", os.getcwd())

        acceptable = ["y", "Y", "yes", "Yes", "YES", "ye", "n", "N", "no", "No", "NO"]
        while True:
            ans = input("Do you want to continue? (Respond y/n): ")
            if ans not in acceptable:
                print("Please provide an acceptable answer.")
                continue
            else:
                break

    if ans == ("n" or "N" or "no" or "No" or "NO"):
        return False

    try:
        shutil.rmtree("stats_out")
        print("\nReplaced previous directory: ", "'./stats_out/'")
    except:
        pass
    os.mkdir("stats_out")
    return True

# read input file, count phi_types and non-phi-filepaths to determine if whitelist was used
def stats(fin):

    phi_types = {}
    filepaths = {}

    # count phi_types
    types = re.findall('"phi_type": ("\S+?"),', fin, re.MULTILINE) # set up list
    count = 0
    for t in types: # go through each type instance
        if t in phi_types: # add one to count
            phi_types[t] += 1
        else: # start counting
            phi_types[t] = 1
        count += 1

    phi_types["total phi tags"] = count

    # count non-phi-filepaths
    sections = re.findall('"non-phi": \[[\S\s]*?\]', fin, re.MULTILINE) # get non-phi sections of the input file
    count = 0
    for sect in sections: # go through each section
        paths = re.findall('"filepath": "(\S+?)"', sect, re.MULTILINE) # find all paths in that section
        for p in paths: # go through each path in each section
            if p in filepaths: # add one to count
                filepaths[p] += 1
            else: # start counting
                filepaths[p] = 1
            count += 1

    filepaths["total non-phi tags"] = count

    return (sorted(phi_types.items(), key=lambda x: x[1], reverse=True), sorted(filepaths.items(), key=lambda x: x[1], reverse=True))

# output the statistics found in stats()
def output(types_wl, paths_wl, types_og, paths_og):

    # whitelist phi_types
    with open("./stats_out/wl_phi_types.txt", "w") as fout:
        print("\n\nPHI TYPES WITH WHITELIST:\n")
        for key, value in types_wl:
            s = key+"\t"+str(value)
            fout.write(s)
            fout.write("\n")
            print(s)

    # whitelist non-phi-filepaths
    with open("./stats_out/wl_non_phi_paths.txt", "w") as fout:
        print("\n\nNON PHI PATHS WITH WHITELIST:\n")
        for key, value in paths_wl:
            s = key+"\t"+str(value)
            fout.write(s)
            fout.write("\n")
            print(s)

    # original phi_types
    with open("./stats_out/og_phi_types.txt", "w") as fout:
        print("\n\nPHI TYPES WITHOUT WHITELIST:\n")
        for key, value in types_og:
            s = key+"\t"+str(value)
            fout.write(s)
            fout.write("\n")
            print(s)

    # original non-phi-filepaths
    with open("./stats_out/og_non_phi_paths.txt", "w") as fout:
        print("\n\nNON PHI PATHS WITHOUT WHITELIST:\n")
        for key, value in paths_og:
            s = key+"\t"+str(value)
            fout.write(s)
            fout.write("\n")
            print(s)


def main():
    help_str = """
        Reads coordinates.json files output by Philter and counts number of
        phi tags and how many times each whitelist file path appears. Outputs
        to a directory.
    """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-wl", "--coords_whitelist",
                    default="../../data/coords_whitelist.json",
                    help="""The coordinates file for the Philter run with the
                            whitelist. Default is
                            '../../data/coords_whitelist.json'.""",
                    type=str)
    ap.add_argument("-og", "--coords_original",
                    default="../../data/coords_original.json",
                    help="""The coordinates file for the Philter run without
                            the whitelist. Default is
                            '../../data/coords_original.json'.""",
                    type=str)

    args = ap.parse_args()

    coords_whitelist = args.coords_whitelist
    coords_original = args.coords_original

    cwl = open(coords_whitelist).read()
    cog = open(coords_original).read()

    # get user confirmation to create/replace directories
    if setup_output():

        start_time = time.time()

        types_wl, paths_wl = stats(cwl)
        types_og, paths_og = stats(cog)

        output(types_wl, paths_wl, types_og, paths_og)

        print("\nCompleted in", time.time() - start_time, "seconds.\n")

    else:

        print("\nTerminated.\n")

main()

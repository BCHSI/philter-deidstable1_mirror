import os
import random
import argparse
import glob
from shutil import copy2

"""Randomly select n-notes from a directory (can be nested).
Useful to generate subsets of notes to annotate, evaluate performance,
and identify institution-specific terms that might not already be
included in the whitelist.

If the file directory contains many subdirectories, parsing these directories
can take a while. Benchmark: 40million files in 10,000 directories takes approximately
5 hours (Script uses no multithreading). 
"""

def picking(finpath, pick_number, if_recursive):
    """
Does: randomly selects filepaths

Uses:


Arguments:
finpath: the path to the parent directory containing files that you would like to select from
pick_number: the number of files that you would like to randomly select
if_recursive: if True, will search through all sub-directories that exist in finpath

Returns:
A list of randomly picked files.
    """
    try:
        print("getting the directories..." )
        if if_recursive:
            filelist = glob.glob(finpath+"/**/*.txt", recursive=True)
        else:
            filelist = glob.glob(finpath+"/*.txt")
        print("Done, copy will begin.")
        return random.sample(filelist, pick_number)
    except ValueError:
        print("picking number is larger than the actual file number.")
        return []


def main():

    """
Does: collects filepaths, selects n at random, copies those files to a new directory

Uses:
glob: to collect files paths
picking(): to randomly select n files from the list of filepaths
copy2: copy the picked files into a new directory

Arguments:
("-i", "--input", help="Path to the directory that contains the notes you would like to sample from.")
("-r", "--recursive", help="Whether to search through all sub-directories that exist in finpath. ")
("-o", "--output",help="Output path to the directory that will store the randomly picked notes.")
("-n", "--number", help="How many files you want to pick?:")

Returns:
A new directory containing randomly picked files.


    """

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True,
                    help="Input path to the directory that contains the notes you would like to sample from.")
    ap.add_argument("-r", "--recursive", action = 'store_true', default=False,
                    help="Whether to search through all sub-directories that exist in input directory. Default is false.")
    ap.add_argument("-o", "--output", required=True,
                    help="Output path to the directory that will store the randomly picked notes.")
    ap.add_argument("-n", "--number", required=True, type=int,
                    help="How many files you want to pick?:")
    args = ap.parse_args()

    finpath = args.input
    foutpath = args.output
    pick_number = args.number
    if_recursive = args.recursive
    if_dir = os.path.isdir(finpath)

    # check to make sure that filepath arguments are valid
    if if_dir:
        filelist = picking(finpath, pick_number, if_recursive)
        if not os.path.exists(foutpath) and filelist != []:
            user_input = input("Output folder:{} does not exist, would you like to create it?: press y to create: ".format(foutpath))
            if user_input == 'y':
                print("Creating {}".format(foutpath))
                os.mkdir(foutpath)
            # if the directory does not exist and the user doesn't want to create one,
            # setting filelist to empty will gracefully exit. 
            else:
                print('Quiting')
                os._exit(0)
        for i in filelist:
            copy2(i, foutpath)
            print("Copied",i,"to",foutpath)
    else:
        print("Input folder does not exist.")

if __name__ == "__main__":
    main()
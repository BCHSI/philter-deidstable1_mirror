import json
import pandas as pd
import time
import re
import argparse
import os
import shutil

# notifications for when the script is ready for user confirmation
def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


# extract the names from various files based on the file type and separator/locator for the names
def get_names(files, locations):

    names = {}
    two_word_names = {}

    for i in range(len(files)): # go through each file

        file = files[i] # the file name
        loc = locations[i] # the separator (eg. 'whitespace' in a txt file), locator (eg. a column in a csv file)
        names_temp = [] # the names from the current file to be added to the big list
        extension = file.split(".")[-1]

        print("Reading '%s'..." % (file))

        if extension != "txt" and extension != "csv" and extension != "json": # if file type is not supported
            print("\nFile type '.%s' is not supported (%s)." % (extension, file))
            if i < len(files)-1: print("Trying other files...\n")
            continue


        with open(file) as fin:

            if extension == "txt": # for txt files

                if "ss_firstnames" in file: # for special case "ss_firstnames.txt"
                    lines = fin.readlines()
                    for line in lines:
                        names_temp.append(line.split(loc)[0])

                else:
                    names_temp = fin.read().split(loc) # read file and split by separator

            elif extension == "csv": # for csv files

                df = pd.read_csv(fin)

                if not loc.isnumeric(): # if the locator is not a column
                    print("\nThe column '%s' is not a number." % (loc))
                    if i < len(files)-1: print("Trying other files...\n")
                    continue

                loc = int(loc)

                if loc >= len(df.columns) or loc < 0: # if the column doesn't exist in the csv file
                    print("\nThe column '%s' does not exist in '.%s'." % (loc, file))
                else:
                    names_temp = df.iloc[:,loc]

            elif extension == "json": # for json files

                if loc != "key" and loc != "value": # if locator is not "key" or "value"
                    print("\nLocation '%s' not supported for json files." % (loc))
                    if i < len(files)-1: print("Trying other files...\n")
                    continue

                dict = json.load(fin)

                for key, value in dict.items():
                    if loc == "key":
                        names_temp.append(str(key))
                    elif loc == "value":
                        names_temp.append(str(value))


            for name in names_temp: # go through each name from the current file

                n = str(name).strip()

                if " " in n: # if name comprises of two or more words, add to dict and skip
                    if n in two_word_names.values():
                        if file not in two_word_names[n]:
                            two_word_names[n].extend([file])
                    else:
                        two_word_names[n] = [file]

                else: # if name is one word, add to dict
                    if n in names.values():
                        if file not in names[n]:
                            names[n].extend([file])
                    else:
                        names[n] = [file]

    return(names, two_word_names)


# go through each name and check whether it exists in the whitelist or not, if it does, remove it (option to ask user for confirmation on each value)
def check_wl(names, wl_in, con): # con is confirmation

    time.sleep(1)
    print("Reading existing whitelist...")

    with open(wl_in) as fin:
        wl_dict = json.load(fin)

    names_in_both = {} # values which exist in the whitelist
    removed_values = {} # values user chooses to remove
    kept_values = {} # values user chooses to keep

    time.sleep(1)
    print("Checking each value...")

    for name in names: # go through each name
        if name in wl_dict: # check if name exists in whitelist
            names_in_both[name] = names[name]

    names_exist = bool(names_in_both)

    if names_exist: # if there are names in the whitelist

        for name in names_in_both: # go through each name in the whitelist

            # ask user to keep or remove
            if con: # if user wants confirmation for each value
                notify("Script is ready!!", "remove_things_from_whitelist.py needs confirmation.")
                print("Value is %s" % (name))
                ans = ""
                while ans != "y" and ans != "n":
                    ans = input("Remove or keep value in whitelist? 'y' is remove, 'n' is keep: ")
            else: # just remove everything
                ans = "y"

            if ans == "y":
                removed_values[name] = names_in_both[name]
            elif ans == "n":
                kept_values[name] = names_in_both[name]

        time.sleep(1)

        # print chosen and not-chosen values
        if not bool(removed_values):
            print("\nYou did not choose any values to remove.")
        else:
            print("\nChosen values to remove:")
        for name in removed_values:
            print(name, removed_values[name])

        if con:
            if not bool(kept_values):
                print("\nYou did not choose any values to keep.")
            else:
                print("\nChosen values to keep:")
            for name in kept_values:
                print(name, kept_values[name])

        # get confirmation to remove all the chosen values to remove
        notify("Script is ready!!", "remove_things_from_whitelist.py needs confirmation.")
        ans = ""
        while ans != "y" and ans != "n":
            ans = input("\nDo you wish to continue and remove your chosen values? (y/n): ")

        if ans == "y":
            for name in removed_values:
                del wl_dict[name]

            new_wl = "remove_things_from_whitelist_out/"+wl_in.split("/")[-1]
            with open(new_wl, "w") as fout:
                json.dump(wl_dict, fout)

            time.sleep(1)
            print("Removed specified values.")

        elif ans == "n":
            print("\nTerminated.")

    else: # if there are no names in the whitelist

        print("No names exist in the whitelist.")

    return names_in_both


def main():

    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--files",
                    help="""The files which contain the values to check for.
                            Supported file types are txt, csv, and json.
                            Separate file paths by spaces (eg.
                            "-f file1.txt file2.csv fil3.json").""",
                    nargs="+",
                    type=str)
    ap.add_argument("-l", "--locations",
                    help="""For each file, the locations of the values. These
                            should be entered separated by spaces (if an entry
                            is whitespace, use regex "\s"), and in the same
                            order which the files were entered.
                            For .txt files, input the seperator between values
                            (eg. "-l \s" or "-l ,").
                            For .csv files, input the column index which the
                            values are in. (eg. "-l 0")
                            For .json files, input whether the values exist as
                            the key or value of the dictionary (eg. "-l key" or
                            "-l value").

                            For example look at this command:
                            "python3 script.py -f file1.txt file2.csv file3.json -l , 0 key".
                            For file1.txt, the separator between values is a comma.
                            For file2.csv, the column which the values are in is column 0.
                            For file3.json, the place where the values are is in the key of the dict.
                            """,
                    nargs="+",
                    type=str)
    ap.add_argument("-wl", "--whitelist",
                    help="""The path to the whitelist (json format) which will
                            be checked to see if it has any of the values from
                            the files.""",
                    type=str)
    ap.add_argument("-c", "--confirmation",
                    default="yes",
                    help="""Whether the user should be asked to "keep" or
                            "remove" each value which exists in the names and
                            whitelist. Options are "yes" (remove everything
                            without asking) or "no" (ask before removing each
                            value). Default is "yes".""",
                    type=str)

    args = ap.parse_args()

    start_time = time.time()

    files = args.files
    locations = args.locations
    whitelist = args.whitelist
    confirmation = args.confirmation

    # set bool based on user's confirmation choice
    if confirmation == "yes":
        con = True
    elif confirmation == "no":
        con = False
    else:
        print("""Enter "yes" or "no" for confirmation.""")
        exit()

    # set up output
    shutil.rmtree("./remove_things_from_whitelist_out/", ignore_errors=True)
    os.mkdir("remove_things_from_whitelist_out")

    names, two_word_names = get_names(files, locations)

    names_in_both = check_wl(names, whitelist, con)

    if names_in_both is not None:
        with open("remove_things_from_whitelist_out/names_in_whitelist.txt", "w") as fout: # output the names in the whitelist
            for key in names_in_both:
                s = str(key)+"    "+str(names_in_both[key])+"\n"
                fout.write(s)

    time.sleep(1)

    if bool(two_word_names): # if there are names with two words
        print("\nNames with two words:")
        for name in two_word_names:
            print("'%s'" % (name))
    else:
        print("No names with two words.")

    time.sleep(1)

    print("Completed in %s seconds.\n" % (str(time.time() - start_time)))

main()

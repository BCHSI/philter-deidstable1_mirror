"""
    ⌘F 'help_str' for details
"""

import os
import shutil
import re
import argparse
import time



# pull



# pull file paths from the grep output file
# for iterating through files and writing paths to output
def pull_paths(inputfile):
    temp = []
    with open(inputfile) as fin:
        l = re.findall('^\.([^\n]+?):', fin.read(), re.MULTILINE)
        for item in l:
            temp.append(item)
    return temp

# pull file names from the grep output file
# for iterating through files and output
def pull_names(inputfile):
    temp = []
    with open(inputfile) as fin:
        l = re.findall('^(?:.+?)//(.+?):', fin.read(), re.MULTILINE)
        for item in l:
            temp.append(item)
    return temp

# pull line numbers from the grep output file
# for iterating through each line containing a gene symbol
def pull_lines(inputfile):
    temp = []
    with open(inputfile) as fin:
        l = re.findall('^\.[^\n]+?\.txt\:([0-9]+)\:', fin.read(), re.MULTILINE)
        for item in l:
            temp.append(item)
    return temp



# setup



# create a dictionary with unique filepaths and filenames
# for iterating through each file
def setup_names(paths, names):
    return {paths[i]: names[i] for i in range(len(paths))}

# create a dictionary with file names and the lines with gene symbols
# for finding lines with gene symbols based on a file name
def setup_lines(names, lines):
    temp = {}
    for i in range(len(names)):
        name = names[i]
        line = lines[i]
        if name in temp:
            temp[name].append(line)
        else:
            temp[name] = [line]
    return temp

# create a list of symbols
# for checking for gene symbols in a line
def setup_symbols(symbolslist):
    with open(symbolslist) as fh:
        return fh.read().splitlines()
        # return re.split(',|\n', fh.read(), re.MULTILINE)

# set up output directories, make sure user doesn't lose files accidentally
def setup_output():

    ans = "y"
    if os.path.isdir("./find_rescued_symbols_out"):
        print("\nThis program will replace already existing files:")
        print("  -  The directory and all contents 'find_rescued_symbols_out' in ", os. getcwd())

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
        shutil.rmtree("find_rescued_symbols_out")
        print("\nReplaced previous directory: ", "'./find_rescued_symbols_out/'")
    except:
        pass
    os.mkdir("find_rescued_symbols_out")
    return True



# compare



# identify notes where gene symbols were protected by whitelist
# testing whitelist efficacy
def compare(ogdir, wldir, path_name, name_lines, symbols):

    rpaths = []
    rout = []
    rnames = []
    rsmbs = []
    print("\n\n==============================================================")
    print("Gene symbols recovered are:\n")


    # iterate through each file by path
    # can find file name based on path using 'path_name' dictionary
    for filepath in path_name:

        name = path_name[filepath]

        # create lists of clinical note text
        # for targeting specific lines containing gene symbols, using list
        # indices and the line numbers in dictionary
        with open(os.path.join(ogdir, name)) as fh:
            original = fh.read().splitlines()
        with open(os.path.join(wldir, name)) as fh:
            whitelist = fh.read().splitlines()

        # iterate through each line containing a gene symbol
        for line in name_lines[name]:
            og_line = original[int(line)-1]
            wl_line = whitelist[int(line)-1]

            # check lines for symbols
            for smb in symbols:
                term = "[^A-Za-z]" + re.escape(smb) + "[^A-Za-z]"
                if not re.search(term, og_line):
                    if re.search(term, wl_line):

                        # output
                        s = "'" + smb + "' was recovered in '" + path_name[filepath] + "' on line '" + line + "' : \"" + wl_line + "\""
                        rpaths.append(filepath)
                        rout.append(s)
                        rnames.append(name)
                        rsmbs.append(smb)
                        print(s)

    print("==============================================================")
    return (rpaths, rout, rnames, rsmbs)



# output



def output(rpaths, rout, rnames, rsmbs):
    count = 0
    for item in rnames: count += 1
    s = str(count)+" gene symbols were recovered."
    print(s)

    if count == 0:
        # output if there are no recovered gene symbols
        with open("find_rescued_symbols_out/out_paths.txt", "w") as fpaths:
                fpaths.write("No recovered symbols exist.")
        with open("find_rescued_symbols_out/out.txt", "w") as fout:
            fpaths.write("No recovered symbols exist.")
        with open("find_rescued_symbols_out/out_names.txt", "w") as fnames:
            fpaths.write("No recovered symbols exist.")
        with open("find_rescued_symbols_out/out_symbols.txt", "w") as fsmbs:
            fpaths.write("No recovered symbols exist.")
    else:
        # regular output
        with open("find_rescued_symbols_out/out_paths.txt", "w") as fpaths:
            for path in rpaths:
                fpaths.write(path)
                fpaths.write("\n")
        with open("find_rescued_symbols_out/out.txt", "w") as fout:
            for item in rout:
                fout.write(item)
                fout.write("\n")
        with open("find_rescued_symbols_out/out_names.txt", "w") as fnames:
            for name in rnames:
                fnames.write(name)
                fnames.write("\n")
        with open("find_rescued_symbols_out/out_symbols.txt", "w") as fsmbs:
            for smb in rsmbs:
                fsmbs.write(smb)
                fsmbs.write("\n")



# main



def main():
    help_str = """
        Compares two sets of notes, one filtered with and the other without a
        whitelist. Outputs details aboout genes symbols which were obscured in
        the 'original' set (without whitelist) and recovered
        (not obscured) in the 'new' set (with whitelist).

        For use after a grep search to find the gene symbols in the original
        set. To locate gene symbols, use
        $ grep -n -r -w -f ./items/to/search/for.txt ./dir/to/search/in/
        >> ./output/file.txt.
        The input items .txt file should contain newline seperated values.
        './dir/to/search/in/' should be the directory containing the original
        notes.
    """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-o", "--anno_original",
                    default="../data/mimic_exnotes/annotated-notes/",
                    help="""The path to the directory contianing the 'original'
                            notes, annotated without a whitelist. Default is
                            '../data/mimic_exnotes/annotated-notes/'.""",
                    type=str)
    ap.add_argument("-a", "--anno_whitelist",
                    default="../data/mimic_exnotes/annotated-notes-wl/",
                    help="""The path to the directory containing the 'new'
                            notes, annotated with a whitelist. Default is
                            '../data/mimic_exnotes/annotated-notes-wl/'.""",
                    type=str)
    ap.add_argument("-g", "--grepoutputfile",
                    default="../paul_code/mimic_data/mimic-exnotes-grep.txt",
                    help="""The file which contains the grep output. See above
                            for details on grep search. Default is
                            '../paul_code/mimic_data/mimic-exnotes-grep.txt'.
                         """,
                    type=str)
    ap.add_argument("-s", "--symbolslist", default="common_symbols.txt",
                    help="""The list of gene symbols, seperated by newlines.
                            Default is 'common_symbols.txt'.""",
                    type=str)

    args = ap.parse_args()

    anno_original = args.anno_original
    anno_whitelist = args.anno_whitelist
    grepfile = args.grepoutputfile
    symbolsfile = args.symbolslist

    # check for user confirmation
    if setup_output():
        start_time = time.time()
        print("\nRunning...")

        # pull data from the grep file
        filepaths = pull_paths(grepfile)
        filenames = pull_names(grepfile)
        linenums = pull_lines(grepfile)

        # set up lists, dictionaries
        path_name = setup_names(filepaths, filenames)
        name_lines = setup_lines(filenames, linenums)
        symbols = setup_symbols(symbolsfile)

        paths, out, names, smbs = compare(anno_original, anno_whitelist, path_name, name_lines, symbols)
        output(paths, out, names, smbs)

        print("\nCompleted in", time.time() - start_time, "seconds.\n")
    else:
        print("\nTerminated.\n")

main()

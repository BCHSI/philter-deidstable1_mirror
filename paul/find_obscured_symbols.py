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
# for iterating through files, copying files, and writing paths to output
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
def setup_output(copyans, destpath):

    ans = "y"
    if os.path.isdir("./find_obscured_symbols_out") or (copyans != "keep" and (os.path.isdir(destpath+"original-notes/") or os.path.isdir(destpath+"annotated-notes/"))):
        print("\nThis program will replace already existing files:")
        if os.path.isdir("./find_obscured_symbols_out"):
            print("    The directory and all contents 'find_obscured_symbols_out' in ", os. getcwd())
        if copyans != "keep":
            if os.path.isdir(destpath+"original-notes/"):
                print("    The directory and all contents 'original-notes' in", destpath)
            if os.path.isdir(destpath+"annotated-notes/"):
                print("    The directory and all contents 'annotated-notes' in", destpath)

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
        shutil.rmtree("find_obscured_symbols_out")
        print("\nReplaced previous directory: ", "'./find_obscured_symbols_out/'")
    except:
        pass
    os.mkdir("find_obscured_symbols_out")

    if copyans != "keep":
        try:
            shutil.rmtree(destpath+"original-notes")
            shutil.rmtree(destpath+"annotated-notes")
            print("Replaced previous directory: ", "'"+destpath+"original-notes/'")
            print("Replaced previous directory: ", "'"+destpath+"annotated-notes/'")
        except:
            pass

        os.mkdir(destpath+"original-notes")
        os.mkdir(destpath+"annotated-notes")

    return True



# copy



# copy the original and annotated files with obscured gene symbols to a new dir
# so user doesn't have to do it later to test whitelist
def copy(sources, destpath):

    print("\nCopying notes...\n")

    for s in sources:
        name = s.split("/")[-1]

        # copy original notes
        dest = destpath+"original-notes/"+name
        shutil.copy(s, dest)

        # copy annotated notes
        dest = destpath+"annotated-notes/"+name
        shutil.copy(sources[s], dest)



# compare



# identifying notes with obscured gene symbols to later test whitelist efficacy
def compare(notesdir, resultsdir, path_name, name_lines, symbols):

    copy = {}
    rpaths = []
    rout = []
    rnames = []
    rsmbs = []
    print("\n\n==============================================================")
    print("Gene symbols obscured are:\n")


    # iterate through each file by path
    # can find file name based on path using 'path_name' dictionary
    for filepath in path_name:

        fp = False # fp = false positive
        name = path_name[filepath]

        # create lists of clinical note text
        # for targeting specific lines containing gene symbols, using list
        # indices and the line numbers in dictionary
        with open(os.path.join(notesdir, name)) as fh:
            foriginal = fh.read().splitlines()
        with open(os.path.join(resultsdir, name)) as fh:
            fphilter = fh.read().splitlines()

        # iterate through each line containing a gene symbol
        for line in name_lines[name]:
            og_line = foriginal[int(line)-1]
            ph_line = fphilter[int(line)-1]

            # check lines for symbols
            for smb in symbols:
                term = "[^A-Za-z]" + re.escape(smb) + "[^A-Za-z]"
                if re.search(term, og_line):
                    if not re.search(term, ph_line):

                        # output
                        s = "'" + smb + "' was obscured in '" + path_name[filepath] + "' on line '" + line + "' : \"" + ph_line + "\""
                        rpaths.append(filepath)
                        rout.append(s)
                        rnames.append(name)
                        rsmbs.append(smb)
                        print(s)

                        # adds files to dicitionary for copying later
                        copy[notesdir+name] = resultsdir+name

                        # eliminating repitition, only need one obscured gene
                        # symbol per file to test whitelist
            #             fp = True
            #             break
            #
            # if fp: break

    print("==============================================================")
    return (rpaths, rout, rnames, rsmbs)



# output



def output(rpaths, rout, rnames, rsmbs):
    count = 0
    for item in rnames: count += 1
    s = str(count)+" gene symbols were obscured."
    print(s)

    if count == 0:
        # output if there are no recovered gene symbols
        with open("find_obscured_symbols_out/out_paths.txt", "w") as fpaths:
                fpaths.write("No obscured symbols exist.")
        with open("find_obscured_symbols_out/out.txt", "w") as fout:
            fpaths.write("No obscured symbols exist.")
        with open("find_obscured_symbols_out/out_names.txt", "w") as fnames:
            fpaths.write("No obscured symbols exist.")
        with open("find_obscured_symbols_out/out_symbols.txt", "w") as fsmbs:
            fpaths.write("No obscured symbols exist.")
    else:
        # regular output
        with open("find_obscured_symbols_out/out_paths.txt", "w") as fpaths:
            for path in rpaths:
                fpaths.write(path)
                fpaths.write("\n")
        with open("find_obscured_symbols_out/out.txt", "w") as fout:
            for item in rout:
                fout.write(item)
                fout.write("\n")
        with open("find_obscured_symbols_out/out_names.txt", "w") as fnames:
            for name in rnames:
                fnames.write(name)
                fnames.write("\n")
        with open("find_obscured_symbols_out/out_symbols.txt", "w") as fsmbs:
            for smb in rsmbs:
                fsmbs.write(smb)
                fsmbs.write("\n")



# main



def main():
    help_str = """
        Compares two sets of notes: original and de-identified, to determine
        which notes contain gene symbols obscured as phi. Outputs details
        regarding the identification to seperate .txt files. There is also an
        option to copy the files containing obscured gene symbols to a new
        directory, seperated into original and annotated groups.

        For use after the initial identification of the notes which contain
        gene symbols. To initially identify the notes, use
        $ grep -n -r -w -f ./items/to/search/for.txt ./dir/to/search/in/
        >> ./output/file.txt.
        The input items .txt file should contain newline seperated values.
    """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-o", "--original", default="../data/mimic_notes/",
                    help="""The path to the directory contianing the original
                            (not de-identified) notes. Default is
                            '../data/mimic_notes/'.""",
                    type=str)
    ap.add_argument("-a", "--annotated", default="../data/mimic_results/",
                    help="""The path to the directory containing the
                            de-identified notes. Default is
                            '../data/mimic_results/'.""",
                    type=str)
    ap.add_argument("-g", "--grepoutputfile",
                    default="../paul_code/mimic_data/mimic-full-notes-grep.txt",
                    help="""The file which contains the grep output. See above
                            for details on grep search. Default is
                            '../paul_code/mimic_data/mimic-full-notes-grep.txt'.
                         """,
                    type=str)
    ap.add_argument("-s", "--symbolslist", default="common_symbols.txt",
                    help="""The list of gene symbols, seperated by newlines.
                            Default is 'common_symbols.txt'.""",
                    type=str)
    ap.add_argument("-c", "--copy", default="copy",
                    help="""Option to copy the notes containing obscured gene
                            symbols to a seperate directory. 'copy' will copy
                            the notes, 'keep' will not. Default is 'copy'.""",
                    type=str)
    ap.add_argument("-d", "--destpath", default="../data/mimic_exnotes/",
                    help="""The destination path for the files to be copied to.
                            Default is '../data/mimic_exnotes/'.""",
                    type=str)

    args = ap.parse_args()

    original = args.original
    annotated = args.annotated
    grepfile = args.grepoutputfile
    symbolsfile = args.symbolslist
    copyans = args.copy
    destpath = args.destpath

    # check for user confirmation
    if setup_output(copyans, destpath):
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

        paths, out, names, smbs = compare(original, annotated, path_name, name_lines, symbols)
        if copyans != "keep":
            copy(sources, destpath)
        output(paths, out, names, smbs)

        print("\nCompleted in", time.time() - start_time, "seconds.\n")
    else:
        print("\nTerminated.\n")

main()

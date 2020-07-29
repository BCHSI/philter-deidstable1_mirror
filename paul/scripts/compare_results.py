import re
import os
import shutil
import json
import time
import argparse
import pandas as pd
from pandas.io.json import json_normalize

# output items in nested dict
def get_values(nested_dict):
    for key, value in nested_dict.items(): # got through dict

        if type(value) is dict: # if value is another nested dict

            with open("compare_results_out/eval_summary.txt", "a") as fout:
                fout.write("\n\n%s" % (key))

            get_values(value) # until we reach the end of nested dicts

        else: # if the value is not a nested dict, output

            with open("compare_results_out/eval_summary.txt", "a") as fout:

                if "difference" in key and float(value) > 0: # add a plus sign in front of positive differences
                    fout.write("\n%s : +%s" % (key, value))
                else:
                    fout.write("\n%s : %s" % (key, value))


# compare the two summary.json eval files
def compare_eval_summaries(dir1, dir2):

    time.sleep(1)
    print("Comparing eval/summary.json files...")

    text1 = json.loads(open(os.path.join(dir1, "eval/summary.json")).read())
    text2 = json.loads(open(os.path.join(dir2, "eval/summary.json")).read())

    summary = {} # dict to output

    for key in text1:
        summary[key] = {}
        summary[key].update({"dir1":text1[key]})
        summary[key].update({"dir2":text2[key]})
        summary[key].update({"difference (dir2 - dir1)":float(text2[key])-float(text1[key])}) # compute difference between dir2 and dir1

    get_values(summary) # output dict


# compare the tp, tn, fp, fn .eval files
def compare_eval_files(indir, dir1, dir2, options):

    # set up lists to go through
    print_statements = []
    file_names = []
    check_in = []
    check_against = []

    if "fp" in options: # if user wants to compare false positives
        fp1 = open(os.path.join(dir1, "eval/fp.eval")).read().splitlines()
        fp2 = open(os.path.join(dir2, "eval/fp.eval")).read().splitlines()
        check_in.extend([fp1, fp2])
        check_against.extend([fp2, fp1])
        print_statements.extend(["\n\n\nFalse positives in dir1 and not dir2:", "\n\n\nFalse positives in dir2 and not dir1:"])
        file_names.extend(["fp.txt", "fp.txt"]) # account for comparing both ways (1 vs 2, 2 vs 1)

    if "tp" in options: # if user wants to compare true positives
        tp1 = open(os.path.join(dir1, "eval/tp.eval")).read().splitlines()
        tp2 = open(os.path.join(dir2, "eval/tp.eval")).read().splitlines()
        check_in.extend([tp1, tp2])
        check_against.extend([tp2, tp1])
        print_statements.extend(["\n\n\nTrue positives in dir1 and not dir2:", "\n\n\nTrue positives in dir2 and not dir1:"])
        file_names.extend(["tp.txt", "tp.txt"]) # account for comparing both ways (1 vs 2, 2 vs 1)

    if "fn" in options: # if user wants to compare false negatives
        fn1 = open(os.path.join(dir1, "eval/fn.eval")).read().splitlines()
        fn2 = open(os.path.join(dir2, "eval/fn.eval")).read().splitlines()
        check_in.extend([fn1, fn2])
        check_against.extend([fn2, fn1])
        print_statements.extend(["\n\n\nFalse negatives in dir1 and not dir2:", "\n\n\nFalse negatives in dir2 and not dir1:"])
        file_names.extend(["fn.txt", "fn.txt"]) # account for comparing both ways (1 vs 2, 2 vs 1)

    if "tn" in options: # if user wants to compare true negatives
        tn1 = open(os.path.join(dir1, "eval/tn.eval")).read().splitlines()
        tn2 = open(os.path.join(dir2, "eval/tn.eval")).read().splitlines()
        check_in.extend([tn1, tn2])
        check_against.extend([tn2, tn1])
        print_statements.extend(["\n\n\nTrue negatives in dir1 and not dir2:", "\n\n\nTrue negatives in dir2 and not dir1:"])
        file_names.extend(["tn.txt", "tn.txt"]) # account for comparing both ways (1 vs 2, 2 vs 1)

    # go through each comparison, eg. (1) true positives dir1 vs dir2, (2) true postives dir2 vs dir1, (3) fase positives dir1 vs dir2, (4) false positives dir2 vs dir1
    for i in range(len(print_statements)):

        if i % 2 == 0: # account for comparing both ways for each file
            time.sleep(1)
            print("Comparing eval/%s files..." % (file_names[i]))

        exist = False # if there are no values in only one of the two dirs

        with open(os.path.join("compare_results_out/", file_names[i]), "a") as fout:
            if i % 2 == 0:
                fout.write(print_statements[i].lstrip()) # get rid of extra newlines at the beginning of the text file
            else:
                fout.write(print_statements[i])

        for line in check_in[i]: # iterate through each line in the .eval files

            if line not in check_against[i]: # if the line in the first file is not in the second

                exist = True

                # set up dictionary to make output easier

                line = line.split("\t")

                line_data = {}

                line_data["filepath"] = line[0]
                line_data["phi_type"] = line[1]
                line_data["match"] = line[2]
                line_data["start"] = line[3]
                line_data["stop"] = line[4].strip()

                filename = re.findall('[\S]+\/([\S]+?\.txt)', line_data["filepath"])[0]

                # get the "match in context" from the original txt file passed through Philter
                line_data["match in context"] = open(os.path.join(indir, filename)).read()[int(line_data["start"])-50 : int(line_data["stop"])+50].strip().replace("\n", "\\n")
                line_data["match in context"] = " ".join(line_data["match in context"].split()) # replace all whitespace with a single space

                # output
                with open(os.path.join("compare_results_out/", file_names[i]), "a") as fout:
                    fout.write("\n\n")
                    for key in line_data:
                        fout.write("%s: '%s', " % (key, line_data[key]))

        # if no differences exist
        if not exist:
            with open(os.path.join("compare_results_out/", file_names[i]), "a") as fout:
                fout.write("\n\nNo differences exist.")


# compare the log/phi_marked.json files
def compare_log_phi_marked(dir1, dir2, indir):

    time.sleep(1)
    print("Comparing log/phi_marked.json files...")

    log1 = os.path.join(dir1, "log/phi_marked.json")
    log2 = os.path.join(dir2, "log/phi_marked.json")
    in_only_1 = [] # for tags in dir1 and not dir2
    in_only_2 = [] # for tags in dir2 and not dir1

    with open(log1) as fin:
        log1_big = json.load(fin)
    with open(log2) as fin:
        log2_big = json.load(fin)

    for filepath in log1_big: # go through each file

        tags1 = log1_big[filepath]
        tags2 = log2_big[filepath]

        for tag in tags1: # go through each tag
            if tag not in tags2: # if tag is not in second dir
                filename = re.findall('[\S]+\/([\S]+?\.txt)', filepath)[0]
                context = open(os.path.join(indir, filename)).read()[int(tag["start"])-50 : int(tag["end"])+50].strip().replace("\n", "\\n")
                context = " ".join(context.split()) # replace all whitespace with a regular space
                word = tag["word"]
                in_only_1.append([word, filepath, tag, context])

        for tag in tags2: # go through each tag
            if tag not in tags1: # if tag is not in the first dir
                filename = re.findall('[\S]+\/([\S]+?\.txt)', filepath)[0]
                context = open(os.path.join(indir, filename)).read()[int(tag["start"])-50 : int(tag["end"])+50].strip().replace("\n", "\\n")
                context = " ".join(context.split()) # replace all whitespace with a regular space
                word = tag["word"]
                in_only_2.append([word, filepath, tag, context])

    # output

    if bool(in_only_1): # if there are tags in dir1 and not dir2

        with open("compare_results_out/tags_in_only_1.txt", "a") as fout:
            for item in in_only_1:
                fout.write("\n\nWord: '%s'\nFilepath: '%s'\nTag [start, stop, word, phi-type]: '%s'\nMatch in context: '%s'" % (item[0], item[1], item[2], item[3]))

    else: # if there are no tags in dir1 and not dir2

        s = "There are no tags in dir1 and not dir2."
        print(s)
        with open("compare_results_out/tags_in_only_1.txt", "a") as fout:
            fout.write(s)


    if bool(in_only_2): # if there are tags in dir1 and not dir2

        with open("compare_results_out/tags_in_only_2.txt", "a") as fout:
            for item in in_only_2:
                fout.write("\n\nWord: '%s'\nFilepath: '%s'\nTag [start, stop, word, phi-type]: '%s'\nMatch in context: '%s'" % (item[0], item[1], item[2], item[3]))

    else: # if there are no tags in dir1 and not dir2

        s = "There are no tags in dir2 and not dir1."
        print(s)
        with open("compare_results_out/tags_in_only_2.txt", "a") as fout:
            fout.write(s)


def main():
    help_str = """
        Compares two Philter runs. This script will compare any/all of the
        'eval/summary.json', 'eval/fp/tp/fn/tp.eval', or 'log/phi_marked.json'
        files.

        If the options 'fp', 'tp', 'fn', or 'tn' is included, the script will
        read in the .eval files and find values which exist in one dir but not
        the other (it will compare both dir1 vs dir2 and dir2 vs dir1).

        If the option 'summary' is included, the script will read in the
        'eval/summary.json' files and compute the differences between each file
        (dir2 - dir1).

        If the option 'phi_marked' is included, the script will read in the
        'log/phi_marked.json' files and find the tags which exist in one dir
        but not the other, and vice versa.
    """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-i", "--input_directory",
                    help="""The path to the directory which was input to
                            Philter (the text files).""",
                    type=str)
    ap.add_argument("-d1", "--directory_one",
                    help="""One of the two directories which will be compared.
                            Generally this dir should be the the control, or
                            dir which is being tested against.""",
                    type=str)
    ap.add_argument("-d2", "--directory_two",
                    help="""The other of the two directories which will be
                            compared. Generally this dir should be the test
                            dir.""",
                    type=str)
    ap.add_argument("-o", "--options",
                    help="""Which files will be compared. The options are
                            'summary', 'phi_marked', 'fp', 'tp', 'fn', or 'tn',
                            or any combination of them. For example, if 'fp'
                            and 'tp' were used, '-o fp tp', this script would
                            compare the files 'eval/fp.eval' and 'eval/tp.eval'.
                            """,
                    nargs="+",
                    type=str)

    args = ap.parse_args()

    indir = args.input_directory
    dir1 = args.directory_one
    dir2 = args.directory_two
    options = args.options

    if options is None:
        print("Please enter options.")
        exit()

    shutil.rmtree('./compare_results_out/', ignore_errors=True)
    os.mkdir('compare_results_out')

    if "summary" in options:
        compare_eval_summaries(dir1, dir2)

    compare_eval_files(indir, dir1, dir2, options)

    if "phi_marked" in options:
        compare_log_phi_marked(dir1, dir2, indir)


main()

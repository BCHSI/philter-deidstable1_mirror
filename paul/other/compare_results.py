import re
import os
import json
import argparse

# output items in nested dict
def get_values(nested_dict):
    for key, value in nested_dict.items():
        if type(value) is dict:
            print("\n"+key)
            get_values(value)
        else:
            # add a plus sign in front of positive differences
            if key=="difference (dir2 - dir1)" and value > 0:
                print("%s : +%s" % (key, value))
            else:
                print("%s : %s" % (key, value))


# compare the two summary.json eval files
def compare_summaries(dir1, dir2):

    text1 = json.loads(open(os.path.join(dir1, "eval/summary.json")).read())
    text2 = json.loads(open(os.path.join(dir2, "eval/summary.json")).read())

    summary = {}

    # create dictionary to output
    for key in text1:
        summary***REMOVED***key***REMOVED*** = {}
        summary***REMOVED***key***REMOVED***.update({"dir1":text1***REMOVED***key***REMOVED***})
        summary***REMOVED***key***REMOVED***.update({"dir2":text2***REMOVED***key***REMOVED***})
        summary***REMOVED***key***REMOVED***.update({"difference (dir2 - dir1)":float(text2***REMOVED***key***REMOVED***)-float(text1***REMOVED***key***REMOVED***)})

    get_values(summary) # output the dictionary
    print("\n")


# compare the tp, tn, fp, fn .eval files
def compare_everything_else(indir, dir1, dir2, options):

    # set up lists to go through
    print_statements = ***REMOVED******REMOVED***
    check_in = ***REMOVED******REMOVED***
    check_against = ***REMOVED******REMOVED***

    if "fp" in options: # if user wants to compare false positives
        fp1 = open(os.path.join(dir1, "eval/fp.eval")).readlines()
        fp2 = open(os.path.join(dir2, "eval/fp.eval")).readlines()

        print_statements.extend(***REMOVED***"\nFalse positives in dir1 and not dir2:\n", "\nFalse positives in dir2 and not dir1:\n"***REMOVED***)

        check_in.extend(***REMOVED***fp1, fp2***REMOVED***)
        check_against.extend(***REMOVED***fp2, fp1***REMOVED***)

    if "tp" in options: # if user wants to compare true positives
        tp1 = open(os.path.join(dir1, "eval/tp.eval")).readlines()
        tp2 = open(os.path.join(dir2, "eval/tp.eval")).readlines()

        print_statements.extend(***REMOVED***"\nTrue positives in dir1 and not dir2:\n", "\nTrue positives in dir2 and not dir1:\n"***REMOVED***)

        check_in.extend(***REMOVED***tp1, tp2***REMOVED***)
        check_against.extend(***REMOVED***tp2, tp1***REMOVED***)

    if "fn" in options: # if user wants to compare false negatives
        fn1 = open(os.path.join(dir1, "eval/fn.eval")).readlines()
        fn2 = open(os.path.join(dir2, "eval/fn.eval")).readlines()

        print_statements.extend(***REMOVED***"\nFalse negatives in dir1 and not dir2:\n", "\nFalse negatives in dir2 and not dir1:\n"***REMOVED***)

        check_in.extend(***REMOVED***fn1, fn2***REMOVED***)
        check_against.extend(***REMOVED***fn2, fn1***REMOVED***)

    if "tn" in options: # if user wants to compare true negatives
        tn1 = open(os.path.join(dir1, "eval/tn.eval")).readlines()
        tn2 = open(os.path.join(dir2, "eval/tn.eval")).readlines()

        print_statements.extend(***REMOVED***"\nTrue negatives in dir1 and not dir2:\n", "\nTrue negatives in dir2 and not dir1:\n"***REMOVED***)

        check_in.extend(***REMOVED***tn1, tn2***REMOVED***)
        check_against.extend(***REMOVED***tn2, tn1***REMOVED***)

    # go through each comparison (eg. (1) true positives dir1 vs dir2, (2) true postives dir2 vs dir1)
    for i in range(len(print_statements)):

        print(print_statements***REMOVED***i***REMOVED***)

        # iterate through each line in the .eval files
        for line in check_in***REMOVED***i***REMOVED***:

            # if the line in the first file is not in the second
            if line not in check_against***REMOVED***i***REMOVED***:

                # set up dictionary to make output easier
                line = line.split("\t")

                line_data = {}

                line_data***REMOVED***"filepath"***REMOVED*** = line***REMOVED***0***REMOVED***
                line_data***REMOVED***"phi_type"***REMOVED*** = line***REMOVED***1***REMOVED***
                line_data***REMOVED***"match"***REMOVED*** = line***REMOVED***2***REMOVED***
                line_data***REMOVED***"start"***REMOVED*** = line***REMOVED***3***REMOVED***
                line_data***REMOVED***"stop"***REMOVED*** = line***REMOVED***4***REMOVED***.strip()

                filename = re.findall('\/***REMOVED***\S***REMOVED***+\/(***REMOVED***\S***REMOVED***+?\.txt)', line_data***REMOVED***"filepath"***REMOVED***)***REMOVED***0***REMOVED***

                # get the "match in context" from the original txt file passed through Philter
                line_data***REMOVED***"match in context"***REMOVED*** = open(os.path.join(indir, filename)).read()***REMOVED***int(line_data***REMOVED***"start"***REMOVED***)-50 : int(line_data***REMOVED***"stop"***REMOVED***)+50***REMOVED***.strip().replace("\n", "\\n")
                line_data***REMOVED***"match in context"***REMOVED*** = " ".join(line_data***REMOVED***"match in context"***REMOVED***.split())

                # output
                for key in line_data:
                    print("%s: '%s'    " % (key, line_data***REMOVED***key***REMOVED***), end=' ')

                print() # newline


def main():
    help_str = """
        Compares the evals from two Philter runs. dir1 and dir2 must contain
        "eval" directories, and files "summary.json" and optionally
        "fp.eval", "tp.eval", "fn.eval", and "tn.eval" inside the "eval" dir.
        This script will read the summary file and compute and output the
        original values, and the differences between dir1 and dir2 for each
        value.

        Optionally, the script will also compare specified fp, tp, fn, and tn
        files in the "eval" directories. It will read each line and check if it
        exists in the other directory, and will output lines unique to dir1 or
        dir2. For example, this option could help determine true positives
        which got unobscured in dir2.
    """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-i", "--input_directory",
                    default="./MIMIC/faked_notes/without_tags/",
                    help="""The path to the directory which was input to
                    Philter. Default is './without_tags/'.""",
                    type=str)
    ap.add_argument("-d1", "--directory_one",
                    default="./MIMIC/faked_notes/annotated_original/",
                    help="""One of the two directories which will be compared.
                            Generally this dir should be the the control, or
                            dir which is being tested against. Default is
                            './annotated_original/'.""",
                    type=str)
    ap.add_argument("-d2", "--directory_two",
                    default="./MIMIC/faked_notes/annotated_tests/",
                    help="""The other of the two directories which will be
                            compared. Generally this dir should be the test
                            dir. Default is './annotated_tests/'.""",
                    type=str)
    ap.add_argument("-o", "--options",
                    default="",
                    help="""Which files besides summary.json will be compared.
                            The options are 'fp', 'tp', 'fn', or 'tn', or any
                            combination of them. For example, if 'fp' and 'tp'
                            were used, '-o fp tp', this script would compare
                            the false and true positive files. Default is '',
                            a blank string.""",
                    nargs="+",
                    type=str)

    args = ap.parse_args()

    indir = args.input_directory
    dir1 = args.directory_one
    dir2 = args.directory_two
    options = args.options

    compare_summaries(dir1, dir2)
    compare_everything_else(indir, dir1, dir2, options)


main()

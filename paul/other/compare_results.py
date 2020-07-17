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
        summary[key] = {}
        summary[key].update({"dir1":text1[key]})
        summary[key].update({"dir2":text2[key]})
        summary[key].update({"difference (dir2 - dir1)":float(text2[key])-float(text1[key])})

    get_values(summary) # output the dictionary
    print("\n")


# compare the tp, tn, fp, fn .eval files
def compare_everything_else(indir, dir1, dir2, options):

    # set up lists to go through
    print_statements = []
    check_in = []
    check_against = []

    if "fp" in options: # if user wants to compare false positives
        fp1 = open(os.path.join(dir1, "eval/fp.eval")).readlines()
        fp2 = open(os.path.join(dir2, "eval/fp.eval")).readlines()

        print_statements.extend(["\nFalse positives in dir1 and not dir2:\n", "\nFalse positives in dir2 and not dir1:\n"])

        check_in.extend([fp1, fp2])
        check_against.extend([fp2, fp1])

    if "tp" in options: # if user wants to compare true positives
        tp1 = open(os.path.join(dir1, "eval/tp.eval")).readlines()
        tp2 = open(os.path.join(dir2, "eval/tp.eval")).readlines()

        print_statements.extend(["\nTrue positives in dir1 and not dir2:\n", "\nTrue positives in dir2 and not dir1:\n"])

        check_in.extend([tp1, tp2])
        check_against.extend([tp2, tp1])

    if "fn" in options: # if user wants to compare false negatives
        fn1 = open(os.path.join(dir1, "eval/fn.eval")).readlines()
        fn2 = open(os.path.join(dir2, "eval/fn.eval")).readlines()

        print_statements.extend(["\nFalse negatives in dir1 and not dir2:\n", "\nFalse negatives in dir2 and not dir1:\n"])

        check_in.extend([fn1, fn2])
        check_against.extend([fn2, fn1])

    if "tn" in options: # if user wants to compare true negatives
        tn1 = open(os.path.join(dir1, "eval/tn.eval")).readlines()
        tn2 = open(os.path.join(dir2, "eval/tn.eval")).readlines()

        print_statements.extend(["\nTrue negatives in dir1 and not dir2:\n", "\nTrue negatives in dir2 and not dir1:\n"])

        check_in.extend([tn1, tn2])
        check_against.extend([tn2, tn1])

    # go through each comparison (eg. (1) true positives dir1 vs dir2, (2) true postives dir2 vs dir1)
    for i in range(len(print_statements)):

        print(print_statements[i])

        # iterate through each line in the .eval files
        for line in check_in[i]:

            # if the line in the first file is not in the second
            if line not in check_against[i]:

                # set up dictionary to make output easier
                line = line.split("\t")

                line_data = {}

                line_data["filepath"] = line[0]
                line_data["phi_type"] = line[1]
                line_data["match"] = line[2]
                line_data["start"] = line[3]
                line_data["stop"] = line[4].strip()

                filename = re.findall('\.\/[\S]+\/([\S]+?\.txt)', line_data["filepath"])[0]

                # get the "match in context" from the original txt file passed through Philter
                line_data["match in context"] = open(os.path.join(indir, filename)).read()[int(line_data["start"])-50 : int(line_data["stop"])+50].strip().replace("\n", "\\n")
                line_data["match in context"] = " ".join(line_data["match in context"].split())

                # output
                for key in line_data:
                    print("%s: '%s'    " % (key, line_data[key]), end=' ')

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

import os
import shutil
import argparse


def unbatch(inputdir, outputdir):

    for root, dirs, files in os.walk(inputdir): # get each dir

        for dir in dirs: # iterate through dirs

            files = os.listdir(root+"/"+dir) # get all files in dir

            for f in files: # iterate through files in dir

                # move file to new location
                source = root+"/"+dir+"/"+f
                dest = outputdir+"/"+f
                shutil.move(source, dest)

            # remove old dir when all files are out
            rem = root+"/"+dir
            os.rmdir(rem)


def main():
    help_str = """
        Unbatch files from multiple smaller directories to one larger one.
    """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-i", "--inputdir", default="mimic_results",
                    help="""Path to the directory containing the files to be
                            unbatched. Format 'path/to/dir', with no slashes
                            at the beginning or end. Default is
                            'mimic_results'.""",
                    type=str)
    ap.add_argument("-o", "--outputdir", default="mimic_results",
                    help="""Path to the directory to output the unbatched
                            files. Format 'path/to/dir', with no slashes at the
                            beginning or end. Default is 'mimic_results'.""",
                    type=str)


    args = ap.parse_args()

    input = args.inputdir
    output = args.outputdir

    unbatch(input, output)


main()

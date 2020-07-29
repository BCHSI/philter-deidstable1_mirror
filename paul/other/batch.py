import os
import shutil
import argparse


def batch(inputdir, outputdir, sizeofbatch):

    n = sizeofbatch
    m = 1 # file name

    for root, dirs, files in os.walk(inputdir): # get each file

        for file in files: # go through each file

            if n >= sizeofbatch: # if number of files hits max

                # create new output dir
                dir = outputdir+"/batch"+str(m)
                os.mkdir(dir)

                m += 1 # add one to file name
                n = 0 # reset number of files in batch

            # move file to new location
            source = root+"/"+file
            dest = dir+"/"+file
            shutil.move(source, dest)

            n += 1 # add one to number of files in current batch


def main():
    help_str = """
        Batch files from one larger directory into multiple smaller ones.
        Outputs directories batch1, batch2, batch3, etc, each containing a
        specified number of files.
    """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-i", "--inputdir", default="mimic_notes_full_2",
                    help="""Path to the directory containing the files to be
                            batched. Format 'path/to/dir', with no slashes at
                            the beginning or end. Default is
                            'mimic_notes_full_2'.""",
                    type=str)
    ap.add_argument("-o", "--outputdir", default="mimic_notes",
                    help="""Path to the directory to output the batched files.
                            Format 'path/to/dir', with no slashes at the
                            beginning or end. Default is 'mimic_notes'.""",
                    type=str)
    ap.add_argument("-n", "--sizeofbatch", default=1000,
                    help="""The number of files which each batch should
                            contain. Default is 1000.""",
                    type=int)


    args = ap.parse_args()

    input = args.inputdir
    output = args.outputdir
    size = args.sizeofbatch

    batch(input, output, size)


main()

import os
import argparse
from lxml import etree


# parse xml file and get the stuff between two tags
def get_text(inputfile, tag):
    doc = etree.parse(inputfile) # parse xml file
    out_text = doc.find(tag) # look for tag
    return(out_text.text) # return stuff in between tags


def main():
    help_str = """
        Parses an .xml file and outputs a .txt file containing the exact text
        between tags of your choice to a new directory. This text will not
        be modified in any way.

    """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-i", "--inputxml", default="./i2b2_anno/",
                    help="""The path to the input directory containing the xml
                            files. Default is './i2b2_anno/'.""",
                    type=str)
    ap.add_argument("-o", "--outputtxt", default="./i2b2_notes/",
                    help="""The path to the directory where the output txt
                            files will go. Default is './i2b2_notes/'.""",
                    type=str)
    ap.add_argument("-t", "--tag", default="TEXT",
                    help="""The tag you wish to search for in each xml file.
                            This script will return the text between those
                            tags. Default is 'TEXT'.""",
                    type=str)

    args = ap.parse_args()

    indir = args.inputxml
    outdir = args.outputtxt
    tag = args.tag

    for root, dirs, files in os.walk(indir): # in case of nested directories

        for file in files: # go through each file in 'indir'

            filename = file.split(".")[0] # get filename without extension

            with open(os.path.join(outdir,filename+".txt"), "w") as fout: # open output

                fout.write(get_text(os.path.join(indir,file), tag)) # write to output


main()

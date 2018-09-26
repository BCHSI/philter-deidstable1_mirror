#!/usr/local/bin/python3
import sys
import argparse

from phitexts import Phitexts


# TODO: replace this by Python's POSIX complaint versions
EXIT_SUCCESS = 0
EXIT_FAILURE = -1


def get_args():
    # gets input/output/filename
    help_str = """De-identify all text files in a folder"""
    
    ap = argparse.ArgumentParser(description=help_str)

    ap.add_argument("-i", "--input", default="./data/i2b2_notes/",
                    help="Path to the directory or the file that contains the PHI note, the default is ./data/i2b2_notes/",
                    type=str)
    ap.add_argument("-o", "--output", default="./data/i2b2_results/",
                    help="Path to the directory to save PHI-reduced notes, the default is ./data/i2b2_results/",
                    type=str)
    ap.add_argument("-f", "--filters", default="./configs/philter_alpha.json",
                    help="Path to the config file, the default is ./configs/philter_alpha.json",
                    type=str)
    ap.add_argument("-s", "--surrogate_info", default="./data/i2b2_meta/note_info_map.tsv",
                    help="Path to the tsv file that contains the surrogate info per "
                          + "note key, the default is "
                          + "./data/i2b2_meta/note_info_map.tsv",
                    type=str)
    ap.add_argument("-l", "--log", default=True,
                    help="When this is true, the pipeline prints and saves log in a subdirectory in each output directory",
                    type=lambda x:bool(distutils.util.strtobool(x)))

    return ap.parse_args()


def main():

    # assumes notes have been shredded into subdirectories such as
    # 000/000/000/000000000001.txt
    # expects path to subdirectory

    # parses commandline arguments
    args = get_args()
    if __debug__: print("read args")
 
    # initializes texts container
    phitexts = Phitexts(args.input)
    
    # detect PHI coordinates
    if __debug__: print("detecting PHI coordinates")
    phitexts.detect_phi(args.filters)

    if phitexts.coords:
        # detects PHI types
        if __debug__: print("detecting PHI types")
        phitexts.detect_phi_types()
        
        # normalizes PHI
        if __debug__: print("normalizing PHI")
        phitexts.normalize_phi()
        
        # looks-up surrogate and apply to normalized PHI
        if __debug__: print("looking up surrogates")
        phitexts.substitute_phi(args.surrogate_info)

    # transforms texts
    if __debug__: print("transforming texts")
    phitexts.transform()

    # saves output
    if __debug__: print("saving de-identified texts")
    phitexts.save(args.output)

    # print and save log 
    if args.log:
        phitexts.print_log(args.output)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())

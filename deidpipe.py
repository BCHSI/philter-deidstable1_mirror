#!/usr/local/bin/python3
import sys
import argparse
import distutils.util
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
    ap.add_argument("-l", "--log", default= True,
                    help="When this is true, the pipeline prints and saves log in a subdirectory in each output directory",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-e", "--eval", default= False,
                    help="When this is true, the pipeline computes and saves statistics in a subdirectory in each output directory",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-a", "--anno", default= './data/i2b2_xml',
                    help="When this is true, the pipeline computes and saves statistics in a subdirectory in each output directory",
                    type=str)

    return ap.parse_args()


def main():

    # assumes notes have been shredded into subdirectories such as
    # 000/000/000/000000000001.txt
    # expects path to subdirectory

    # parses commandline arguments
    args = get_args()
    
    # initializes texts container
    phitexts = Phitexts(args.input)
    
    # detect PHI coordinates
    phitexts.detect_phi(args.filters)

    if phitexts.coords:
        # detects PHI types
        phitexts.detect_phi_types()
        
        # normalizes PHI
        phitexts.normalize_phi()
        
        # looks-up surrogate and apply to normalized PHI
        phitexts.substitute_phi()

    # transforms texts
    phitexts.transform()

    # saves output
    phitexts.save(args.output)

    # print and save log 
    if args.log:
        phitexts.print_log(args.output)
    # evaluate and print stats
    if args.eval:
        phitexts.eval(args.anno, args.input, args.output)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())

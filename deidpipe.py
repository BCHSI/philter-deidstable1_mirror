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
    ap.add_argument("-s", "--surrogate_info", default="./data/i2b2_meta/note_info_map.tsv",
                    help="Path to the tsv file that contains the surrogate info per "
                          + "note key, the default is "
                          + "./data/i2b2_meta/note_info_map.tsv",
                    type=str)
    ap.add_argument("-d", "--deid_filename", default=True,
                    help="When this is true, the pipeline saves the de-identified output using de-identified note ids for the filenames",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-k", "--knownphi",
                    help="Path to the known phi file, if path to file is absent knownPHI module does not execute",
                    type=str)
    ap.add_argument("-l", "--log", default=True,
                    help="When this is true, the pipeline prints and saves log in a subdirectory in each output directory",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-e", "--eval", default=False,
                    help="When this is true, the pipeline computes and saves statistics in a subdirectory in each output directory",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-a", "--anno", default='./data/i2b2_xml',
                    help="When this is true, the pipeline computes and saves statistics in a subdirectory in each output directory",
                    type=str)
    ap.add_argument("-x", "--xml", default=False,
                    help="When this is true, the pipeline looks for xml files in the input directory and extracts the PHI information from the xml tags without running philter",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-v", "--verbose", action='store_true',
                    help="When verbose is set,"
                         + " will emit messages about script progress")

    return ap.parse_args()


def main():

    # assumes notes have been shredded into subdirectories such as
    # 000/000/000/000000000001.txt
    # expects path to subdirectory

    # parses commandline arguments
    args = get_args()
    if __debug__: print("read args")
    
    # initializes texts container
    phitexts = Phitexts(args.input,args.xml)
    
    # detect PHI coordinates
    if __debug__: print("detecting PHI coordinates")
    if args.xml:
       if __debug__: print("Generating coordinate map from xml")
       phitexts.detect_xml_phi()       
    else:
       phitexts.detect_phi(args.filters, verbose=args.verbose)

    if phitexts.coords:
        # detects PHI types
        if __debug__: print("detecting PHI types")
        if not args.xml:
           phitexts.detect_phi_types()
       
        # detect known phi
        if args.knownphi:
           if __debug__: print("Identifying known phi")
           phitexts.detect_known_phi(args.knownphi)
 
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
    phitexts.save(args.output, use_deid_note_key=args.deid_filename,
                  suf="", ext="txt")

    # print and save log 
    if args.log:
        phitexts.print_log(args.output)
    if args.eval:
        phitexts.eval(args.anno, args.input, args.output)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())

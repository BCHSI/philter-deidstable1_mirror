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
    ap.add_argument("-s", "--surrogate_info", 
                    help="Path to the tsv file that contains the surrogate info"
                          + " per note key",
                    type=str)
    ap.add_argument("-d", "--deid_filename", default=True,
                    help="When this is true, the pipeline saves the de-identified output using de-identified note ids for the filenames",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-k", "--dynamic_blacklist",
                    help="Path to the probes file, if path to file is absent dynamic blacklist does not get generated",
                    type=str)
    ap.add_argument("-l", "--log", default=True,
                    help="When this is true, the pipeline prints and saves log in a subdirectory in each output directory",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-e", "--eval", default=False,
                    help="When this is true, the pipeline computes and saves statistics in a subdirectory in each output directory (see option -a)",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-a", "--anno", default='./data/i2b2_xml',
                    help="Path to the directory or the file that contains the PHI annotation,"
                         + " the default is ./data/i2b2_xml/"
                         + " (needs option -e True)",
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
    elif args.dynamic_blacklist:
        phitexts.detect_phi(args.filters, args.dynamic_blacklist,
                            verbose=args.verbose)
    else:
        phitexts.detect_phi(args.filters, verbose=args.verbose)

    if phitexts.coords:
        if not args.xml:
            # detects PHI types
            if __debug__: print("detecting PHI types")
            phitexts.detect_phi_types()

        # normalizes PHI
        if __debug__: print("normalizing PHI")
        phitexts.normalize_phi()
        
        # looks-up surrogate and apply to normalized PHI
        if args.surrogate_info:
            if __debug__: print("looking up surrogates")
            phitexts.substitute_phi(args.surrogate_info)

    # transforms texts
    if __debug__: print("transforming texts")
    phitexts.transform()

    # saves output
    if __debug__: print("saving de-identified texts")
    if args.deid_filename and not args.surrogate_info:
        print("WARNING: no surrogate info provided, saving output with "
              + "identified note key")
        args.deid_filename=False
    phitexts.save(args.output, use_deid_note_key=args.deid_filename,
                  suf="", ext="txt")

    # print and save log 
    if args.log:
        phitexts.print_log(args.output, args.dynamic_blacklist, args.xml)
    if args.eval:
        phitexts.eval(args.anno, args.output)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())

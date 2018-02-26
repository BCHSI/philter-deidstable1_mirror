import argparse
import re 
import pickle
from nphilter import NPhilter
import gzip
import json

def main():
    # get input/output/filename
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", default="./data/i2b2_notes/",
                    help="Path to the directory or the file that contains the PHI note, the default is ./data/i2b2_notes/",
                    type=str)
    ap.add_argument("-a", "--anno", default="./data/i2b2_anno/",
                    help="Path to the directory or the file that contains the PHI note, the default is ./data/i2b2_notes/",
                    type=str)
    ap.add_argument("-o", "--output", default="./data/i2b2_results/",
                    help="Path to the directory to save the PHI-reduced notes in, the default is ./data/i2b2_results/",
                    type=str)
    ap.add_argument("-c", "--config", default="./configs/example.json",
                    help="Path to our config file",
                    type=str)
    ap.add_argument("-d", "--debug", default=False,
                    help="When debug is true, will run our eval script and emit helpful messages",
                    type=bool)

    args = ap.parse_args()

    philter_config = {
        "debug":args.debug,
        "finpath":args.input,
        "foutpath":args.output,
        "anno_folder":args.anno,
        "configpath":args.config
    }    
   
    filterer = Philter(philter_config)

    #map any regex groups we have in our config
    filterer.mapcoords_regex()
    #map any sets in our config, 
    filterer.mapcoords_sets()
    #map any POS that we are excluding
    filterer.map_pos()
    
    #transform the data 
    #ORDER: blacklists supercede everything, whitelists are second priority
    #Next are regex which support 3 default groups
    ## filter regex runs as a first pass, blocks anything in group (ideally very precise)
    ## extract regex runs as a second pass, keep anything in this group NOT in filter (ideally very precise)
    ## filter_2 regex runs as a third pass, blocks anything in group, (generally a catch-all, general approach)
    ## Anything not caught in these passes will be assumed to be PHI
    filterer.transform(in_path=args.input,
                    foutpath=args.output,
                    phi_word=" **PHI** ")

    #evaluate the effectiveness
    filterer.eval(only_digits=False, 
        fp_output="data/phi/phi_fp/phi_fp.json",
        fn_output="data/phi/phi_fn/phi_fn.json")
        
        
if __name__ == "__main__":
    main()
import argparse
import re 
import pickle
from philter import Philter
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
    ap.add_argument("-f", "--filters", default="./configs/test_set.json",
                    help="Path to our config file",
                    type=str)
    ap.add_argument("-d", "--debug", default=True,
                    help="When debug is true, will run our eval script and emit helpful messages",
                    type=bool)

    args = ap.parse_args()

    philter_config = {
        "debug":args.debug,
        "finpath":args.input,
        "foutpath":args.output,
        "anno_folder":args.anno,
        "filters":args.filters
    }    
   
    filterer = Philter(philter_config)

    #map any sets, pos and regex groups we have in our config
    filterer.map_coordinates(in_path=args.input)
    
    #transform the data 
    #Priority order is maintained in the pattern list
    filterer.transform(in_path=args.input,
                       out_path=args.output,
                       replacement="*")

    #evaluate the effectiveness
    filterer.eval(
        in_path="data/i2b2_results/",
        anno_path="data/i2b2_anno/",
        anno_suffix=".txt",
        summary_output="data/phi/summary.json",
        fn_output="data/phi/fn.json",
        fp_output="data/phi/fp.json")


    #test evals

    # filterer.eval(
    #     in_path="data/i2b2_anno/",
    #     anno_path="data/i2b2_anno/",
    #     anno_suffix=".txt",
    #     summary_output="data/phi/summary.json",
    #     fn_output="data/phi/fn.json",
    #     fp_output="data/phi/fp.json")

    # filterer.eval(
    #     in_path="data/i2b2_notes/",
    #     anno_path="data/i2b2_anno/",
    #     anno_suffix=".txt",
    #     summary_output="data/phi/summary.json",
    #     fn_output="data/phi/fn.json",
    #     fp_output="data/phi/fp.json")

    # filterer.eval(
    #     in_path="data/i2b2_results_test/",
    #     anno_path="data/i2b2_anno_test/",
    #     anno_suffix=".txt",
    #     summary_output="data/phi/summary.json",
    #     fn_output="data/phi/fn.json",
    #     fp_output="data/phi/fp.json")


        
        
if __name__ == "__main__":
    main()
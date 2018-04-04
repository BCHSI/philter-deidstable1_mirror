import argparse
import re 
import pickle
from philter import Philter
import gzip
import json


def main():
    # get input/output/filename
    help_str = """ Philter 
        python3 main.py -i 
    """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-i", "--input", default="./data/i2b2_notes/",
                    help="Path to the directory or the file that contains the PHI note, the default is ./data/i2b2_notes/",
                    type=str)
    ap.add_argument("-a", "--anno", default="./data/i2b2_anno/",
                    help="Path to the directory or the file that contains the PHI annotation, the default is ./data/i2b2_anno/",
                    type=str)
    ap.add_argument("-o", "--output", default="./data/i2b2_results/",
                    help="Path to the directory to save the PHI-reduced notes in, the default is ./data/i2b2_results/",
                    type=str)
    ap.add_argument("-f", "--filters", default="./configs/integration_1.json",
                    help="Path to our config file, the default is ./configs/integration_1.json",
                    type=str)
    ap.add_argument("-d", "--debug", default=True,
                    help="When debug is true, will run our eval script and emit helpful messages",
                    type=bool)
    ap.add_argument("--stanfordner", default="/usr/local/stanford-ner/",
                    help="Path to Stanford NER, the default is /usr/local/stanford-ner/",
                    type=str)
    ap.add_argument("--outputformat", default="asterisk",
                    help="Define format of annotation, allowed values are \"asterisk\", \"i2b2\". Default is \"asterisk\"",
                    type=str)

    args = ap.parse_args()

    if args.debug:
        print("RUNNING ", args.filters)

    philter_config = {
        "debug":args.debug,
        "finpath":args.input,
        "foutpath":args.output,
        "outformat":args.outputformat,
        "anno_folder":args.anno,
        "filters":args.filters,
        "stanford_ner_tagger": { 
            "classifier":args.stanfordner+"classifiers/english.all.3class.distsim.crf.ser.gz",
            "jar":args.stanfordner+"stanford-ner.jar",
            "download":True,
        }
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
        in_path=args.output,
        anno_path=args.anno,
        anno_suffix=".txt",
        summary_output="data/phi/summary.json",
        fn_output="data/phi/fn.json",
        fp_output="data/phi/fp.json")

        
if __name__ == "__main__":
    main()

import argparse
import distutils.util
import re 
import pickle
from philter_opt import Philter
import gzip
import json
from datetime import datetime


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
    ap.add_argument("-x", "--xml", default="./data/phi_notes.json",
                    help="Path to the json file that contains all xml data",
                    type=str)
    ap.add_argument("-c", "--coords", default="./data/coordinates.json",
                    help="Path to the json file that contains the coordinate map data",
                    type=str)
    ap.add_argument("-v", "--verbose", default=True,
                    help="When verbose is true, will emit messages about script progress",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-e", "--run_eval", default=True,
                    help="When run_eval is true, will run our eval script and emit summarized results to terminal",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("-t", "--freq_table", default=False,
                    help="When freqtable is true, will output a unigram/bigram frequency table of all note words and their PHI/non-PHI counts",
                    type=lambda x:bool(distutils.util.strtobool(x))) 
    ap.add_argument("--stanfordner", default="/usr/local/stanford-ner/",
                    help="Path to Stanford NER, the default is /usr/local/stanford-ner/",
                    type=str)
    ap.add_argument("--outputformat", default="asterisk",
                    help="Define format of annotation, allowed values are \"asterisk\", \"i2b2\". Default is \"asterisk\"",
                    type=str)
    ap.add_argument("--ucsfformat", default=False,
                    help="When ucsfformat is true, will adjust eval script for slightly different xml format",
                    type=lambda x:bool(distutils.util.strtobool(x)))
    ap.add_argument("--prod", default=False,
                    help="When prod is true, this will run the script with output in i2b2 xml format without running the eval script",
                    type=lambda x:bool(distutils.util.strtobool(x)))

    args = ap.parse_args()
    run_eval = args.run_eval
    verbose = args.verbose

    if args.prod:
        run_eval = False
        verbose = False
        outputformat = "i2b2"
        filters = "./configs/philter_alpha.json"
        philter_config = {
            "verbose":verbose,
            "run_eval":run_eval,
            "finpath":args.input,
            "foutpath":args.output,
            "outformat":outputformat,
            "filters":filters,
        }

    else:
    	philter_config = {
            "verbose":args.verbose,
            "run_eval":args.run_eval,
            "freq_table":args.freq_table,
            "finpath":args.input,
            "foutpath":args.output,
            "outformat":args.outputformat,
            "ucsfformat":args.ucsfformat,
            "anno_folder":args.anno,
            "filters":args.filters,
            "xml":args.xml,
            "coords":args.coords,
            "stanford_ner_tagger": {
                "classifier":args.stanfordner+"classifiers/english.all.3class.distsim.crf.ser.gz",
                "jar":args.stanfordner+"stanford-ner.jar",
                "download":True,
            }
        }
   
    if verbose:
        print("RUNNING ", philter_config['filters'])


    filterer = Philter(philter_config)

    #map any sets, pos and regex groups we have in our config
    filterer.map_coordinates()
    
    #transform the data 
    #Priority order is maintained in the pattern list
    filterer.transform()

    #evaluate the effectiveness
    if run_eval and args.outputformat == "asterisk":
        filterer.eval(
            philter_config,
            in_path=args.output,
            anno_path=args.anno,
            anno_suffix=".txt",
            summary_output="data/phi/summary.json",
            fn_output="data/phi/fn.json",
            fp_output="data/phi/fp.json",
            phi_matcher=re.compile("\*+"),
            pre_process=r":|\,|\-|\/|_|~", #characters we're going to strip from our notes to analyze against anno
            only_digits=False,
            pre_process2= r"[^a-zA-Z0-9]",
            punctuation_matcher=re.compile(r"[^a-zA-Z0-9\*\.]"))

# error analysis
        
if __name__ == "__main__":
    start=datetime.now()
    main()
    print(datetime.now()-start)

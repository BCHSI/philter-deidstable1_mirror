import argparse
import re 
import pickle
from philter import Philter
import gzip
import json

def main():


    philter_config = {
        "debug":True,
        "finpath":"./tests/eval01/i2b2_notes/",
        "foutpath":"./tests/eval01/i2b2_results/",
        "anno_folder":"./tests/eval01/i2b2_anno/",
        "filters":"./configs/test_set.json"
    }    
   
    filterer = Philter(philter_config)

    #evaluate the effectiveness
    filterer.eval(
        in_path="./tests/eval01/i2b2_results/",
        anno_path="./tests/eval01/i2b2_anno/",
        anno_suffix=".txt",
        summary_output="./tests/eval01/phi/summary.json",
        fn_output="./tests/eval01/phi/fn.json",
        fp_output="./tests/eval01/phi/fp.json")

    filterer.eval(
        in_path="data/i2b2_anno/",
        anno_path="data/i2b2_anno/",
        anno_suffix=".txt",
        summary_output="data/phi/summary.json",
        fn_output="data/phi/fn.json",
        fp_output="data/phi/fp.json")

    filterer.eval(
        in_path="data/i2b2_notes/",
        anno_path="data/i2b2_anno/",
        anno_suffix=".txt",
        summary_output="data/phi/summary.json",
        fn_output="data/phi/fn.json",
        fp_output="data/phi/fp.json")



        
        
if __name__ == "__main__":
    main()
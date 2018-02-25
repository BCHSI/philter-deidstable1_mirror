import argparse
import re 
import pickle
from nphilter import NPhilter

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
    ap.add_argument("-re", "--regex", default="./regex.json",
                    help="Path to the file where our regex patterns live",
                    type=str)
    ap.add_argument("-m", "--mode", default="total_recall",
                    help="Specific mode we're running, can be filter, extract, multi or generated",
                    type=str)
    ap.add_argument("-w", "--whitelist",
                    #default=os.path.join(os.path.dirname(__file__), 'whitelist.pkl'),
                    default='../whitelist.pkl',
                    help="Path to the whitelist, the default is phireducer/whitelist.pkl")

    args = ap.parse_args()

    whitelist = pickle.load(open(args.whitelist, "rb"))



    config = {
        "debug":True,
        "finpath":args.input,
        "foutpath":args.output,
        "anno_folder":args.anno,
        "regex":args.regex,
        "whitelist":whitelist,
        "anno_suffix":"_phi_reduced.ano" #_phi_reduced.ano | _all_characters_phi_reduced.ano
    }    
   
    filterer = NPhilter(config)
    filterer.precompile() #precompile any patterns we've added

    print("Running "+ args.mode)
    #different modes
    if args.mode == "filter":
        filterer.mapcoords(regex_map_name="filter", coord_map_name="filter")
        filterer.transform(coord_map_name="filter")
    elif args.mode == "extract":
        filterer.mapcoords(regex_map_name="extract", coord_map_name="extract")
        #constraint is any item with numbers in it
        filterer.transform(coord_map_name="extract", constraint=re.compile(r"\S*\d+\S*"), inverse=True)
    elif args.mode == "multi":
        #multiple transform with a priority for filter (anything we know is bad)
        filterer.mapcoords(regex_map_name="extract", coord_map_name="extract")
        filterer.mapcoords(regex_map_name="filter", coord_map_name="filter")
        filterer.mapcoords(regex_map_name="all-digits", coord_map_name="all-digits")
        filterer.mapcoords_set(whitelist=whitelist, coord_map_name="whitelist")
        filterer.multi_transform( coord_maps=***REMOVED*** 
                {'title':'filter'},
                {'title':'extract'},
                {'title':'all-digits'}***REMOVED***)

    elif args.mode == "generated":
        filterer.getphi()
        filterer.mapphi(phi_path="data/phi/phi_counts.json", out_path="data/phi/phi_map.json")
        filterer.mapphi(phi_path="data/phi/phi_number_counts.json", out_path="data/phi/phi_number_map.json")
        filterer.mapphi(phi_path="data/phi/phi_string_counts.json", out_path="data/phi/phi_string_map.json")

        filterer.gen_regex(regex_map_name="genfilter", source_map="data/phi/phi_number_map.json")
        filterer.mapcoords(regex_map_name="genfilter", coord_map_name="genfilter")
        filterer.transform(coord_map_name="genfilter")
    elif args.mode == "total_recall":
        
        filter_maps = ***REMOVED******REMOVED***
        extract_maps = ***REMOVED******REMOVED***
        baseline_maps = ***REMOVED******REMOVED***

        # for k in whitelist:
        #     print(k)

        whitelist_map = filterer.map_set(in_path=args.input,
                    map_set=whitelist, 
                    inverse=False,
                    ignore_set=set(***REMOVED******REMOVED***))
        extract_maps.append(whitelist_map)

        #block_everything 
        baseline_maps.append(filterer.map_regex(in_path=args.input,
                    regex=re.compile("\w+")))

        filterer.multi_map_transform(
            in_path=args.input,
            out_path=args.output,
            filter_pass=filter_maps,
            extract_pass=extract_maps,
            final_pass=baseline_maps,
            replacement=" **PHI** ")

    else:
         raise Exception("MODE DOESN'T EXIST",  args.mode)


    filterer.eval(only_digits=False, 
        fp_output="data/phi/phi_fp/phi_fp.json",
        fn_output="data/phi/phi_fn/phi_fn.json")
    #now map the phi we're missing
    #map false negatives and generate regex
    filterer.mapphi(phi_path="data/phi/phi_fn/phi_fn.json", 
            out_path="data/phi/phi_fn/phi_fn_map.json",  
            sorted_path="data/phi/phi_fn/phi_fn_sorted.json",  
            digit_char="#", 
            string_char="*")
    filterer.gen_regex(
        source_map="data/phi/phi_fn/phi_fn_map.json", 
        regex_map_name="gen_fn", 
        output_file="data/phi/phi_fn/phi_fn_regex.json",
        output_folder="data/phi/phi_fn/patterns/",
        digit_char="#", 
        string_char="*"
    )

    #map false positives
    filterer.mapphi(phi_path="data/phi/phi_fp/phi_fp.json", 
            out_path="data/phi/phi_fp/phi_fp_map.json",  
            sorted_path="data/phi/phi_fp/phi_fp_sorted.json",
            digit_char="#", 
            string_char="*")
    filterer.gen_regex(
        source_map="data/phi/phi_fp/phi_fp_map.json", 
        regex_map_name="gen_fp", 
        output_file="data/phi/phi_fp/phi_fp_regex.json",
        output_folder="data/phi/phi_fp/patterns/",
        digit_char="#", 
        string_char="*"
    )



if __name__ == "__main__":
    main()
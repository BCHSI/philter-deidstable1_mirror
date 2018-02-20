import argparse
from nphilter import NPhilter

def main():
    # get input/output/filename
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", default="./data/i2b2_notes/",
                    help="Path to the directory or the file that contains the PHI note, the default is ./data/i2b2_notes/",
                    type=str)
    ap.add_argument("-a", "--anno", default="./data/i2b2_annotations_with_symbols/",
                    help="Path to the directory or the file that contains the PHI note, the default is ./data/i2b2_notes/",
                    type=str)
    ap.add_argument("-o", "--output", default="./data/i2b2_results/",
                    help="Path to the directory to save the PHI-reduced notes in, the default is ./data/i2b2_results/",
                    type=str)
    ap.add_argument("-re", "--regex", default="./regex.json",
                    help="Path to the file where our regex patterns live",
                    type=str)

    args = ap.parse_args()


    config = {
        "debug":True,
        "finpath":args.input,
        "foutpath":args.output,
        "anno_folder":args.anno,
        "regex":args.regex,
        "anno_suffix":"_all_characters_phi_reduced.ano" #_phi_reduced.ano
    }

    path = "premade" #can be premade regex or generated
    #path = "generated" #needs debugging, all things are being filtered

    filterer = NPhilter(config)
    filterer.precompile() #precompile any patterns we've added

    #different modes
    if path == "premade":
        filterer.mapcoords(regex_map_name="filter", coord_map_name="filter")
        filterer.transform(coord_map_name="filter")
    elif path == "generated":
        filterer.getphi()
        filterer.mapphi(phi_path="data/phi/phi_counts.json", out_path="data/phi/phi_map.json")
        filterer.mapphi(phi_path="data/phi/phi_number_counts.json", out_path="data/phi/phi_number_map.json")
        filterer.mapphi(phi_path="data/phi/phi_string_counts.json", out_path="data/phi/phi_string_map.json")

        filterer.gen_regex(regex_map_name="genfilter", source_map="data/phi/phi_number_map.json")
        filterer.mapcoords(regex_map_name="genfilter", coord_map_name="genfilter")
        filterer.transform(coord_map_name="genfilter")


    filterer.eval(only_digits=True, 
        fp_output="data/phi/phi_fp/phi_fp.json",
        fn_output="data/phi/phi_fn/phi_fn.json")
    #now map the phi we're missing
    #map false negatives and generate regex
    filterer.mapphi(phi_path="data/phi/phi_fn/phi_fn.json", 
            out_path="data/phi/phi_fn/phi_fn_map.json",  
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
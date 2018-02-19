import argparse
from nphilter import NPhilter

def main():
    # get input/output/filename
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", default="./data/i2b2_notes/",
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
    	"regex":args.regex,
    }

    filterer = NPhilter(config)
    filterer.precompile() #precompile any patterns we've added
    filterer.mapcoords(regex_map_name="filter", coord_map_name="filter")
    filterer.transform(coord_map_name="filter")

    # filterer.getphi()
    # filterer.mapphi(phi_path="data/phi/phi_counts.json", out_path="data/phi/phi_map.json")
    # filterer.mapphi(phi_path="data/phi/phi_number_counts.json", out_path="data/phi/phi_number_map.json")
    # filterer.mapphi(phi_path="data/phi/phi_string_counts.json", out_path="data/phi/phi_string_map.json")

    # filterer.gen_regex(regex_map_name="genfilter", source_map="data/phi/phi_number_map.json")
    # filterer.mapcoords(regex_map_name="genfilter", coord_map_name="genfilter")
    # filterer.transform(coord_map_name="genfilter")
    filterer.eval(only_digits=True)


if __name__ == "__main__":
    main()
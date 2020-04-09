import argparse
import regex as re
import pandas as pd
import xml.etree.ElementTree as ET
import subprocess

def create_xml(i, pii, meta, deid_path, text_path, xml_sample_path, output_dir, note_output_dir):
	# Load sample xml file
	sample_tree = ET.parse(xml_sample_path)

	# Get deid note key from csv
	deid_key = pii.loc[i, "filename"]

	# Get full deid path
	full_deid_path = get_deid_full_path(deid_key, deid_path)

	# Get input text key
	text_key = meta[deid_key]

	# Get full text path
	full_text_path = get_text_full_path(text_key, text_path)

	# Copy text file over to input folder
	new_filepath = copy_and_normalize_note(full_text_path, text_key, note_output_dir)

	# Get search string from csv
	search_string = str(pii.loc[i, "word_found"]).replace('+','\+').replace('(','\(').replace(')','\)').replace('^','\^').replace('$','\$').replace('.','\.').replace('|','\|').replace('?','\?').replace('*','\*').replace('[','\[').replace(']','\]').replace('{','\{').replace('}','\}')

	search_pattern = re.compile(search_string)

	# Get phi tag from csv
	phi_tag = str(pii.loc[i, "original_column"])

	# Load text file
	txt = open(new_filepath, "r", encoding='utf-8', errors='surrogateescape').read()

	# Start parsing xml file
	a = sample_tree.find('TEXT')
	a.text = txt
	b = sample_tree.find('TAGS')

	# Find regex matches
	matches = search_pattern.finditer(txt)

	match_count = 0
	for m in matches:
		c = ET.SubElement(b,phi_tag)
		c.set('id','X'+str(match_count))
		c.set('spans',str(m.start()) + "~" + str(m.start()+len(m.group())))
		c.set('text',str(m.group()))
		c.set('TYPE',phi_tag)
		match_count += 1

	full_text_key = '0'*(12-len(text_key)) + text_key
	outfile = output_dir + '/' + full_text_key + '_utf8.xml'
	sample_tree.write(outfile)


def get_deid_full_path(deid_key, deid_path):
	# Directory pattern: XX/XXX/XXX/XXX/XXXXXXXXXXXXXX.txt
	l1 = deid_key[0:2]
	l2 = deid_key[2:5]
	l3 = deid_key[5:8]
	l4 = deid_key[8:11]
	full_deid_path = deid_path + '/' + l1 + '/' + l2 + '/' + l3 + '/' + l4 + '/' + deid_key + '.txt'
	return(full_deid_path)

def copy_and_normalize_note(full_text_path, text_key, note_output_dir):
	#subprocess.check_call(["cp", full_text_path, note_output_dir])

	full_text_key = '0'*(12-len(text_key)) + text_key

	new_text = ''
	with open(full_text_path, encoding='utf-8',errors='ignore') as f:
		for line in f:
			new_text = new_text + line.replace('\x00',' ').replace('\x07',' ').replace('\xf0', ' ').replace('\x15', ' ')

	new_filename = full_text_key + '_utf8.txt' 
	new_filepath = note_output_dir + '/' + new_filename
	
	with open(new_filepath, "w", encoding='utf-8') as f:
		f.write(new_text)

	return(new_filepath)

def get_text_full_path(text_key, text_path):
	# Max length is 12
	full_text_key = '0'*(12-len(text_key)) + text_key
	l1 = full_text_key[0:3]
	l2 = full_text_key[3:6]
	l3 = full_text_key[6:9]
	full_text_path = text_path + '/' + l1 + '/' + l2 + '/' + l3 + '/' + full_text_key + '.txt'
	return(full_text_path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input",
                    help="Path to the CSV file that contains PII info for this set of notes",
                    type=str)
    ap.add_argument("-o", "--output",
                    help="Path to output folder for XML files",
                    type=str)
    ap.add_argument("-d", "--deid_path",
                    help="Path to folder with deid files",
                    type=str)
    ap.add_argument("-t", "--text_path",
                    help="Path to folder with text files",
                    type=str)
    ap.add_argument("-m", "--meta_path",
                    help="Path to meta file",
                    type=str)
    ap.add_argument("-x", "--xml_sample",
                    help="Path to sample xml file",
                    type=str)
    ap.add_argument("-n", "--notes_output",
                    help="Path to output folder for original text files",
                    type=str)
    args = ap.parse_args()

    input_csv = args.input
    #input_csv = '/data/muenzenk/low_hanging_fruit_tests/corys_results_201911/node704/primarymrn.csv'
    output_dir = args.output
    #output_dir = '/data/muenzenk/low_hanging_fruit_tests/xml/primarymrn'
    deid_path = args.deid_path
    #deid_path = '/data/notes/philtered_notes_20190712_zeta'
    text_path = args.text_path
    #text_path = '/data/notes/shredded_notes_20190712'
    meta_path = args.meta_path
    #meta_path = '/data/for_cory/NOTE_INFO_MAPS.txt'
    xml_sample_path = args.xml_sample
    #xml_sample_path = '/data/muenzenk/low_hanging_fruit_tests/sample.xml'
    note_output_dir = args.notes_output
    #note_output_dir = '/data/muenzenk/low_hanging_fruit_tests/notes/primarymrn'

    meta = {}
    mfile = open(meta_path)
    for line in mfile:
    	line = line.rstrip('\n')
    	line  = line.replace('.0','')
    	key= line.split('\t')
    	meta[key[10]] = key[9]

    print("Meta loaded into hash")
    pii = pd.read_csv(input_csv)
    for i in range(len(pii)):
    	create_xml(i, pii, meta, deid_path, text_path, xml_sample_path, output_dir, note_output_dir)

        
if __name__ == "__main__":
    main()
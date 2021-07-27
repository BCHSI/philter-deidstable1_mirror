import argparse
import regex as re
import pandas as pd
import xml.etree.ElementTree as ET
import subprocess
import os
import json
from pymongo import MongoClient
import socket

def read_mongo_config(mongofile):
    if not os.path.exists(mongofile):
       raise Exception("Filepath does not exist", mongofile)
    mongo_details = json.loads(open(mongofile,"r").read())
    return mongo_details

def get_mongo_handle(mongo):
    client = MongoClient(mongo["client"],username=mongo["username"],password=mongo["password"])
    print(client)
    try:
        db = client[mongo['db']] 
    except:
        print("Mongo Server not available")
    return db


def create_xml(i, mongo, db, pii, xml_sample_path, output_dir, note_output_dir):
	# Load sample xml file
	sample_tree = ET.parse(xml_sample_path)
	
	# Get deid note key from csv
	deid_key = pii.loc[i, "filename"]

	# Get input text key
	meta_in = db[mongo['collection_meta_data']]
	meta_in_found = meta_in.find_one({"deid_note_key": deid_key})
	if meta_in_found != None:
		text_key = meta_in_found['note_key']

		# Load text file
		raw_note_text = db[mongo['collection_raw_note_text']]
		raw_note_text_found = raw_note_text.find_one({"note_key": text_key})
		if raw_note_text_found != None:
			txt = raw_note_text_found['raw_note_text']
			txt = txt.replace('\x00',' ').replace('\x07',' ').replace('\xf0', ' ').replace('\x15', ' ')


			#txt = open(new_filepath, "r", encoding='utf-8', errors='surrogateescape').read()

		    #server = socket.gethostname() + ".ucsfmedicalcenter.org" 

			# Copy text file over to input folder
			new_filepath = copy_and_normalize_note(txt, text_key, note_output_dir)
			# Get search string from csv
			search_string = str(pii.loc[i, "word_found"]).replace('+','\+').replace('(','\(').replace(')','\)').replace('^','\^').replace('$','\$').replace('.','\.').replace('|','\|').replace('?','\?').replace('*','\*').replace('[','\[').replace(']','\]').replace('{','\{').replace('}','\}')
			search_pattern = re.compile("(?i)"+search_string)
			# Get phi tag from csv
			phi_tag = str(pii.loc[i, "original_column"])

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
			outfile = output_dir + '/' + full_text_key + '.xml'
			sample_tree.write(outfile)


# def get_deid_full_path(deid_key, deid_path):
# 	# Directory pattern: XX/XXX/XXX/XXX/XXXXXXXXXXXXXX.txt
# 	l1 = deid_key[0:2]
# 	l2 = deid_key[2:5]
# 	l3 = deid_key[5:8]
# 	l4 = deid_key[8:11]
# 	full_deid_path = deid_path + '/' + l1 + '/' + l2 + '/' + l3 + '/' + l4 + '/' + deid_key + '.txt'
# 	return(full_deid_path)


# def get_deid_full_path(deid_key, deid_path):
# 	# Directory pattern: XX/XXX/XXX/XXX/XXXXXXXXXXXXXX.txt
# 	l1 = deid_key[0:2]
# 	l2 = deid_key[2:5]
# 	l3 = deid_key[5:8]
# 	l4 = deid_key[8:11]
# 	full_deid_path = deid_path + '/' + l1 + '/' + l2 + '/' + l3 + '/' + l4 + '/' + deid_key + '.txt'
# 	return(full_deid_path)


def copy_and_normalize_note(txt, text_key, note_output_dir):
	#subprocess.check_call(["cp", full_text_path, note_output_dir])
	#full_text_key = '0'*(12-len(text_key)) + text_key
	#new_text = ''
	#with open(full_text_path, encoding='utf-8',errors='ignore') as f:
	#	for line in f:
	#		new_text = new_text + line.replace('\x00',' ').replace('\x07',' ').replace('\xf0', ' ').replace('\x15', ' ')
	#new_filename = text_key + '_utf8.txt' 
	#new_filepath = note_output_dir + '/' + new_filename
	new_filepath = get_text_full_path(text_key, note_output_dir)
	with open(new_filepath, "w", encoding='utf-8') as f:
		txt = txt.replace('\x00',' ').replace('\x07',' ').replace('\xf0', ' ').replace('\x15', ' ')
		f.write(txt)
	return(new_filepath)


def get_text_full_path(text_key, text_path):
	# Max length is 12
	full_text_key = '0'*(12-len(text_key)) + text_key
	l1 = full_text_key[0:3]
	l2 = full_text_key[3:6]
	l3 = full_text_key[6:9]
	full_text_path = text_path + '/' + full_text_key + '.txt'
	return(full_text_path)

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--input",
			help="Path to the CSV file that contains PII info for this set of notes",
			type=str)
	ap.add_argument("-o", "--output",
			help="Path to output folder for XML files",
			type=str)
	ap.add_argument("-x", "--xml_sample",
			help="Path to sample xml file",
			type=str)
	ap.add_argument("-n", "--notes_output",
			help="Path to output folder for original text files",
			type=str)
	ap.add_argument("-c", "--mongo_config",
			help="Path to the Mongo config file for this database",
			type=str)
	args = ap.parse_args()

	input_csv = args.input
	#input_csv = '/data/muenzenk/low_hanging_fruit_tests/corys_results_201911/node704/primarymrn.csv'
	#input_csv = '/data/muenzenk/cory_probe_search/cory_word_check_results_073020.csv'
	#input_csv = '/data/muenzenk/gene_patho_tests/gene_patho_phi.csv'
	#input_csv = '/data/shared/pre_certification_fixes/name_2m_v2_v3.csv'
	
	output_dir = args.output
	#output_dir = '/data/muenzenk/low_hanging_fruit_tests/xml/primarymrn'
	#output_dir = '/data/muenzenk/cory_probe_search/073020_xml'
	#output_dir = '/data/muenzenk/gene_patho_tests/unit_xml'
	#output_dir = '/data/shared/pre_certification_fixes/xml/name'
	
	#deid_path = args.deid_path
	#deid_path = '/data/notes/philtered_notes_20190712_zeta'
	#deid_path = '/data/muenzenk/probetoken/probetoken_100k_output'
	#deid_path = '/data/muenzenk/gene_patho_tests/develop_gene_100k_output'
	
	#text_path = args.text_path
	#text_path = '/data/notes/shredded_notes_20190712'
	#text_path = '/data/radhakrishnanl/100k_random_20190712'
	#text_path = '/data/notes/shredded_notes_20190712'
	#text_path = '/data/notes/shredded_notes_20190712'
	
	#meta_path = args.meta_path
	#meta_path = '/data/for_cory/NOTE_INFO_MAPS.txt'
	#meta_path = '/data/for_cory/NOTE_INFO_MAPS.txt'
	#meta_path = '/data/for_cory/NOTE_INFO_MAPS.txt'
	
	xml_sample_path = args.xml_sample
	#xml_sample_path = '/data/muenzenk/low_hanging_fruit_tests/sample.xml'
	#xml_sample_path = '/data/muenzenk/low_hanging_fruit_tests/sample.xml'
	#xml_sample_path = '/data/shared/pre_certification_fixes/sample.xml'
	
	note_output_dir = args.notes_output
	#note_output_dir = '/data/muenzenk/low_hanging_fruit_tests/notes/primarymrn'
	#note_output_dir = '/data/muenzenk/cory_probe_search/073020_notes'
	#note_output_dir = '/data/muenzenk/gene_patho_tests/unit_test'
	#note_output_dir = '/data/shared/pre_certification_fixes/raw_text/name'
	
	#file_structure = args.structure
	#file_structure = 'deid'
	#file_structure = 'text'
	#file_structure = 'text'
	
	mongo_config = args.mongo_config
	#mongo_config = '/data/shared/pre_certification_fixes/mongo_2m_v2.json'

	# Read Mongo
	mongo = read_mongo_config(mongo_config)
	db = get_mongo_handle(mongo)

	#meta = {}
	#mfile = open(meta_path)
	#for line in mfile:
	#	line = line.rstrip('\n')
	#	line  = line.replace('.0','')
	#	key= line.split('\t')
	#	meta[key[10]] = key[9]

	#print("Meta loaded into hash")
	pii = pd.read_csv(input_csv)
	for i in range(len(pii)):
		create_xml(i, mongo, db, pii, xml_sample_path, output_dir, note_output_dir)


if __name__ == "__main__":
	main()



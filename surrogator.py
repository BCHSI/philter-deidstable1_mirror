#!/usr/bin/env python3

# import libraries
import sys,os
import pandas as pd
import argparse
import distutils.util
from multiprocessing import Pool

#for reading in the xml gold notes
import xml.etree.ElementTree as ET
import xmltodict

#for date shifting
import dateutil.parser
from datetime import datetime,timedelta
import random
from dateparser import parse
import re


# Extract XML
def extractXML(directory,filename,philter_or_gold,verbose):
	"""Extracts the annotated XML file from either philter or gold into text, and a dictionary of all tags """
	if verbose:
		print ("\ninput file: "+directory + '/'+ filename)
	file_to_parse = os.path.join(directory, filename)
	tree = ET.parse(file_to_parse)
	root = tree.getroot()
	xmlstr = ET.tostring(root, encoding='utf8', method='xml')
	xml_dict = xmltodict.parse(xmlstr)[philter_or_gold]
	text = xml_dict["TEXT"]
	tags_dict = xml_dict["TAGS"]
	return text,tags_dict,xmlstr

def parse_xml_files(directory,output_directory,philter_or_gold,write_surrogated_files,problem_files_log,verbose):
	"""This function
	1)  Loops through the files in the input directory, parses the XML files
    	a)  For each file, we loop through the tag dictionary and apply appropriate date shifts, & surrogations

    Outputs:
    de-identified text files written to output_directory.
    date_shift_log - a record of all of the date shifts we apply
    surrogate_log - a record of all of the surrogates we apply
    problem_files_log - a list of files we could not parse
	"""
	cols = ["Document", "PHI_element", "Text", "Type","Comment"]
	output_df = pd.DataFrame(columns = cols,index=None)
	new_dict = dict()
	filename_dates = {}
	date_shift_log = pd.DataFrame()
	surrogate_log = pd.DataFrame()
	file_list = os.listdir(directory)

	# Loop through xml_files
	for filename in os.listdir(directory):
		if filename.endswith(".xml") and "DS_Store" not in filename:

			note_text,tags_dict,xmlstr = extractXML(directory,filename,philter_or_gold,verbose)
			if not tags_dict:	
				continue

			for key, value in tags_dict.items():
				# Note:  Value can be a list of like phi elements
				# 		or a dictionary of the metadata about a phi element

				if isinstance(value, list):
					for final_value in value:
						if philter_or_gold == "PhilterUCSF":
							text_start = final_value["@spans"].split('~')[0]
							text_end = final_value["@spans"].split('~')[1]
						else:
							text_start = final_value["@start"]
							text_end = final_value["@end"]
						text = final_value["@text"]
						phi_type = final_value["@TYPE"]
						if phi_type == "DATE" or phi_type == "Date": 
							xmlstr,date_shift_log = shift_dates(filename_dates,filename,xmlstr,text,date_shift_log,note_text,text_start,text_end,verbose)
						else:
							xmlstr,surrogate_log = replace_other_surrogate(filename,xmlstr,text,phi_type,surrogate_log,verbose)								
				else:
					final_value = value
					text = final_value["@text"]
					phi_type = final_value["@TYPE"]
					if philter_or_gold == "PhilterUCSF":
						text_start = final_value["@spans"].split('~')[0]
						text_end = final_value["@spans"].split('~')[1]
					else:
						text_start = final_value["@start"]
						text_end = final_value["@end"]

					if phi_type == "DATE" or phi_type == "Date":
						xmlstr,date_shift_log = shift_dates(filename_dates,filename,xmlstr,text,date_shift_log,note_text,text_start,text_end,verbose)
					else:
						xmlstr,surrogate_log = replace_other_surrogate(filename,xmlstr,text,phi_type,surrogate_log,verbose)
			
			# here we write back out the updated XML File to a new directory
			output_dir = output_directory+filename.replace(".xml",".txt")
			try:
				xmlstr = xmlstr.decode('utf-8', 'ignore')
				output_xml_dict = xmltodict.parse(xmlstr)[philter_or_gold]
				output_text = output_xml_dict["TEXT"]
				if write_surrogated_files:
					with open(output_dir, "w") as text_file:
						text_file.write(output_text)
					if verbose:
						print ("output file: " + output_dir)

			except xmltodict.expat.ExpatError as xml_parse_error:
				if verbose:
					print ("We cannot parse this XML: " + str( xml_parse_error))
				problem_files_log = problem_files_log.append({"filename":filename,"philter_or_gold":philter_or_gold,"xml_parse_error":xml_parse_error},ignore_index=True)

	if verbose:
		date_shift_log.columns = ["Filename", "start", "end", "Input Date","Parsed Date", "Shifted Date","Time Delta","date_context"]
		surrogate_log.columns = ["filename", "text", "phi_type"]
	return date_shift_log, surrogate_log, problem_files_log

# date shift functions
def generate_random_date():
    """Generate a random date. This is used if there is no metadata associated with a date shift"""
    now = datetime.now()
    day = random.choice(range(1, 29))
    month = random.choice(range(1, 24))
    year = random.choice(range(1, 1000))
    return day,month,year,now

def lookup_date_shift(filename,filename_dates):
	"""
	This function looks up the desired date shift from the notes_metadata folder.
	Notes metadata specifies a specific date shift per patient, and has all a patients note names
	"""

	file_prefix = filename.replace(".xml","").replace(".txt","")
	note_info = pd.read_csv('data/notes_metadata/note_info.csv')
	re_id_pat = pd.read_csv('data/notes_metadata/re_id_pat.csv')

	#join together re_id_pat with NOTE_INFO on Patient_id
	notes_metadata = note_info.set_index('patient_ID').join(re_id_pat.set_index('patient_ID'))
	metadata_mapping_dict = pd.Series(notes_metadata.date_offset.values,index=notes_metadata.note_csn_id).to_dict()

	if file_prefix in metadata_mapping_dict:
		dateshift = metadata_mapping_dict[file_prefix]
		time_delta = timedelta(days=dateshift)
	else:
		print ("metadata not found. generating random date_shift")

		if filename not in filename_dates:
			day,month,year,now = generate_random_date()
			filename_dates[filename] = [day,month,year,now]

		else:
			day,month,year,now = filename_dates[filename]
		    #print (("shifting by " + str(day) + " days and by "+ str(month) + " months"))
		time_delta = timedelta(weeks=month*4,days=day)

	return time_delta

def get_context_around_date(date,text_start,text_end,note_text):
    """
    This function finds the context around a date within the note.
    It is used for logging & improving our date tagging/shifting
    """
    text_start = int(text_start)
    text_end = int(text_end)
    if text_start-16 < 0:
        text_start = 0
    else:
        text_start = text_start-16
    if text_end + 40 > len(note_text):
        text_end = len(note_text)-1
    else:
        text_end = text_end + 40

    date_context = (note_text[text_start:text_end]).replace(date, "[[" + date + "]]")

    return date_context

def precompile(filepath):
    """ precompiles our regex to speed up pattern matching"""
    regex = open(filepath,"r").read().strip()
    return re.compile(regex)

def parse_and_shift_date(date,time_delta):
    """
    We use dateparser.parse to:
    1) Parse our date into a datetime object
    2) Ensure that we maintain the same details as the original date (not inferring year or day)
    3) Applying the appropriate date shift and return the shifted date

    """
    dt = parse(date,settings={'PREFER_DAY_OF_MONTH': 'first'} )
    now = datetime.now()
    if dt !=None:
      strict_parse = parse(date,settings={'STRICT_PARSING': True})
      dt_actual = datetime(dt.year, dt.month, dt.day)
      dt_plus_arbitrary = dt_actual+ time_delta

      # we have to take into account if the input date isn't a fully specified date
      if strict_parse == None or strict_parse.year != dt.year:
          is_strict_parse = 0
          output_string = ""
          input_string = ""
          if dt.month!=now.month:
              input_string += str(dt.strftime('%B'))
              output_string += str(dt_plus_arbitrary.strftime('%B'))
          if dt.year!=now.year:
              input_string += " " +str(dt.year)
              output_string += " " +str(dt_plus_arbitrary.year)
          if dt.day!=1:
              input_string += " " +str(dt.day)
              output_string += " " +str(dt_plus_arbitrary.day)
          output_shifted_date = output_string.replace(" 00:00:00","")
          input_date = input_string.replace(" 00:00:00","")

      else:
          output_shifted_date = str(dt_plus_arbitrary).replace(" 00:00:00","")
          input_date = str(dt).replace(" 00:00:00","")

      return input_date,output_shifted_date

def parse_date_ranges(date_range,time_delta):
    """
    Philter currently has regex's that tag date ranges.
    So, we must identify these and separately shift both elements of the daterange
    """
    list_of_date_range_regex = ["filters/regex/dates/YYYY_MM-YYYY_MM_transformed.txt","filters/regex/dates/MM_DD_YY-MM_DD_YY_transformed.txt","filters/regex/dates/MM_YYYY-MM_YYYY_transformed.txt","filters/regex/dates/MM_YY-MM_YY_transformed.txt","filters/regex/dates/MM_YYYY-MM_YYYY_transformed.txt","filters/regex/dates/MM_DD-MM_DD_transformed.txt","filters/regex/dates/DD_MM-DD_MM_transformed.txt"]
    for filepath in list_of_date_range_regex:
        compiled_regex = precompile(filepath)

        matches = compiled_regex.search(date_range)
        if matches:
            match = matches.group(0)
            start_date_range = match.split("-")[0]
            end_date_range = match.split("-")[1]
            break

    input_start_date,output_start_date = parse_and_shift_date(start_date_range,time_delta)
    input_start_date,output_end_date = parse_and_shift_date(end_date_range,time_delta)

    return start_date_range,end_date_range,output_start_date,output_end_date

def shift_dates(filename_dates,filename,xmlstr,date,date_shift_log,note_text,text_start,text_end,verbose):
    """
    This function parses and shifts dates for a specified file
    output_xml: a string of the output note with shifted dates
    date_shift_log: a log of shifted dates
    """
    date_context = get_context_around_date(date,text_start,text_end,note_text)
    time_delta = lookup_date_shift(filename,filename_dates)
    time_delta_str = str(time_delta).replace(", 0:00:00","")

    dt = parse(date,settings={'PREFER_DAY_OF_MONTH': 'first'} )

    if dt !=None and dt.year > 1900:
        input_date,output_shifted_date = parse_and_shift_date(date,time_delta)
        date_shift_log = date_shift_log.append([(filename,text_start,text_end,date,input_date,output_shifted_date,time_delta_str,date_context)])
        output_xml = xmlstr.replace(date.encode(),output_shifted_date.encode()+ b" [SHIFTED DATE]")
    else:
        try:
            start_date_range,end_date_range,start_dt_plus_arbitrary,end_dt_plus_arbitrary = parse_date_ranges(date,time_delta)
            output_xml = xmlstr.replace(start_date_range.encode(),start_dt_plus_arbitrary.encode() + b" [SHIFTED DATE]")
            output_xml = xmlstr.replace(end_date_range.encode(),end_dt_plus_arbitrary.encode() + b" [SHIFTED DATE]")
            if verbose:
                date_shift_log = date_shift_log.append([(filename,text_start,text_end,date,start_date_range,start_dt_plus_arbitrary,time_delta_str,date_context)])
                date_shift_log = date_shift_log.append([(filename,text_start,text_end,date,end_date_range,end_dt_plus_arbitrary,time_delta_str,date_context)])

        except:
            output_xml = xmlstr.replace(date.encode(),b"cannot parse date")
            if verbose:
                date_shift_log = date_shift_log.append([(filename,text_start,text_end,date,"cannot parse date","cannot parse date",time_delta_str,date_context)])

    return output_xml,date_shift_log

def replace_other_surrogate(filename,xmlstr,text,phi_type,surrogate_log,verbose):
	"""
	Returns the string of a note with the tagged PHI surrogated with the PHI Type
	"""
	# replace anything else with ***PHItype***
	if phi_type == "OTHER":
		output_xml = xmlstr.replace(text.encode(),b"***PHI***")
	else:
		output_xml = xmlstr.replace(text.encode(),b"***"+phi_type.encode()+b"***")
	if verbose:
		surrogate_log = surrogate_log.append([(filename,text,phi_type)])

	return output_xml,surrogate_log

def write_logs(output_directory,date_shift_log, surrogate_log):
	"""Writing logs of date shifts and surrogates to the specified output dir"""
	print ("\n______________________________________________")

	date_shift_log.to_csv(output_directory + "/shifted_dates.csv", index=False,sep="|")
	surrogate_log.to_csv(output_directory + "/surrogated_text.csv", index=False,sep="|")

	print ("\nWrote record of shifted dates here: "+ output_directory + "shifted_dates.csv")
	print ("Wrote record of surrogated text here: "+ output_directory + "surrogated_text.csv \n\n")
	print ("\n______________________________________________")


def write_summary(date_shift_log,surrogate_log,output_directory):
	"""Writes an evaluation summary surrogator. These are summaries from the different log files"""

	total_dates_we_cannot_parse = str(date_shift_log[date_shift_log['Shifted Date'] == "cannot parse date"].count()["Shifted Date"])
	total_dates_we_can_parse = str(date_shift_log[date_shift_log['Shifted Date'] != "cannot parse date"].count()["Shifted Date"])
	print ("Summary of Date shifts \nTotal dates cannot parse: " + total_dates_we_cannot_parse)
	print ("Total dates parsed: " + total_dates_we_can_parse)

	counts_by_phi_type = surrogate_log.groupby(["phi_type"]).size()
	counts_by_phi_type.cols = ["phi_type","count"]
	counts_by_phi_type.to_csv(output_directory + "/counts_by_phi_type.csv",sep="|")
	print ("\nCounts of text surrogated by phi_type:" )
	print (counts_by_phi_type)

def date_shift_evaluation(output_directory,date_shift_log_gold,date_shift_log,problem_files_log):
	"""
	Prints( a summary of the true positives, false positives and false negatives)
    Saves a more granular file of all of these to output_directory
	"""
        s1 = pd.merge(date_shift_log_gold, date_shift_log,indicator=True, how='outer', on=['Filename','start','end','Input Date'])
	output_eval = s1[["Filename","Input Date","_merge"]]
	output_eval = output_eval.rename(index=str, columns={"_merge": "classification"})
	output_eval["classification"] = output_eval['classification'].replace({'both': 'true positive','left_only': 'false positive', 'right_only': 'false negative'})
	output_eval["description"] = output_eval['classification'].replace({'true positive':'appears in both gold and philter','false positive':'appears in gold notes only', 'false negative':'appears in philter notes only'})


	if problem_files_log.empty == False:
		problem_filenames = problem_files_log['filename'].tolist()
		output_eval = output_eval.loc[~output_eval['Filename'].isin(problem_filenames)]


	output_eval.to_csv(output_directory+"date_shift_eval.csv", index=False,sep="|")

	# count of True positives (shows in both)
	s1_true_positive = output_eval[output_eval['classification'] == "true positive"].count()["Input Date"]
	true_positives = s1_true_positive
	print ("\n______________________________________________")
	print ("\nSummary Stats: \ntrue positives: " + str(true_positives))
	
	# count of False positives (shows in actual only)
	s1_false_positive = output_eval[output_eval['classification'] == "false positive"].count()["Input Date"]
	false_positives = s1_false_positive
	print ("false positives: " + str(false_positives))

	# count of False negative (shows in predicted only)
	s1_false_negative = output_eval[output_eval['classification'] == "false negative"].count()["Input Date"]
	false_negatives = s1_false_negative
	print ("false negatives: " + str(false_negatives))
	print ("\nwriting out eval record to: " + output_directory + "date_shift_eval.csv")
	print ("\n______________________________________________\n")

def main():

	parser = argparse.ArgumentParser(description=
		"""This program will read in gold or Philter XML formatted notes \n
		Then apply date shifts to any phi tagged as a date. \n
		Next it will replace all appropriate PHI with the respective PHI Tag \n 
		Then it will output .txt files with the appropriate surrogates
		""")

	parser.add_argument("-i","--input_dir", default="data/gold_results", help="specifiy the input directory",
                    type=str)
	parser.add_argument("-o","--output_dir", default="data/surrogator/philter_results_output/", help="specifiy the output directory",
                    type=str)
	parser.add_argument("-gi","--gold_input_dir", default="data/surrogator/testing-PHI-Gold-fixed", help="specifiy the input gold directory",
		    type=str)
	parser.add_argument("-go","--gold_output_dir", default="data/surrogator/testing-PHI-Gold-fixed-output/", help="specifiy the gold output directory",
		    type=str)
	parser.add_argument("-rp","--rerun_philter", default=False, help="This will re-run the philter surrogating. It takes a while, so default is false",
                    type=lambda x:bool(distutils.util.strtobool(x)))
	parser.add_argument("-rg","--rerun_gold", default=False, help="This will re-run the gold (manually annotated) standard surrogating. It takes a while, so default is false",
		    type=lambda x:bool(distutils.util.strtobool(x)))
	parser.add_argument("-e","--evaluation", default=True, help="This will run the evaluation comparing surrogated gold with surrogated philter notes",
                    type=lambda x:bool(distutils.util.strtobool(x)))
	parser.add_argument("-t","--test", default=False, help="This will run the test, using less files",
                    type=lambda x:bool(distutils.util.strtobool(x)))
	parser.add_argument("-w","--write_surrogated_files", default=False, help="This will write the surrogated notes.",
                    type=lambda x:bool(distutils.util.strtobool(x)))
	parser.add_argument("-p","--prod", default=False, help="This will run the production mode, using only Philtered notes and not running evaluation",
                    type=lambda x:bool(distutils.util.strtobool(x)))
	parser.add_argument("-verbose","--verbose", default=True, help="This will output helpful print statements and surrogator logs, but also increase the runtime of the program",
                    type=lambda x:bool(distutils.util.strtobool(x)))
	parser.add_argument("-x","--xmldomain", default="PhilterUCSF", help="GOLD xml domain",	
	            type=str)

	parsed = parser.parse_args()
	directory = vars(parsed)["input_dir"]
	output_directory = vars(parsed)["output_dir"]
	gold_directory = vars(parsed)["gold_input_dir"]
	gold_output_directory = vars(parsed)["gold_output_dir"]
	rerun_gold = vars(parsed)["rerun_gold"]
	rerun_philter = vars(parsed)["rerun_philter"]
	evaluation = vars(parsed)["evaluation"]
	write_surrogated_files = vars(parsed)["write_surrogated_files"]
	test = vars(parsed)["test"]
	prod = vars(parsed)["prod"]
	verbose = vars(parsed)["verbose"]
	gold_xmldomain = vars(parsed)["xmldomain"]


	if test:
		directory = "data/surrogator/test/philter_results_test"
		output_directory = "data/surrogator/test/philter_results_output_test/"
		gold_directory = "data/surrogator/test/testing-PHI-Gold-fixed_test"
		gold_output_directory = "data/surrogator/test/testing-PHI-Gold-fixed-output_test/"
		write_surrogated_files = True
		verbose = True

	if prod:
		rerun_gold = False
		rerun_philter = True
		evaluation = False
		write_surrogated_files = True
		test = False
		verbose = False

	if not os.path.exists(directory):
		raise Exception("directory does not exist", directory)
	if not os.path.exists(output_directory):
		raise Exception("output_directory does not exist", output_directory)
	if not os.path.exists(gold_directory):
		raise Exception("gold_directory does not exist", gold_directory)
	if not os.path.exists(gold_output_directory):
		raise Exception("gold_output_directory does not exist", gold_output_directory)

	print ("\nRunning Surrogator...\n")

	problem_files_log = pd.DataFrame(columns = ["filename","philter_or_gold","xml_parse_error"])

	if rerun_philter or test:
		print ("Running Surrogator on philter notes...")
		date_shift_log, surrogate_log,problem_files_log = parse_xml_files(directory,output_directory,"Philter",write_surrogated_files,problem_files_log,verbose)
		if verbose:
			write_logs(output_directory,date_shift_log, surrogate_log)
	else:
		try:
			print ("Skipping re-running surrogator on philter notes. Reading from: \n    "+output_directory+"shifted_dates.csv")
			date_shift_log = pd.read_csv(output_directory+'shifted_dates.csv')
			surrogate_log = pd.read_csv(output_directory+'surrogated_text.csv')
		except:
			print ("You have not run the surrogator with --rerun_philter=True yet. Please re-run with this parameter set to true"			)

	if rerun_gold or test:
		print ("Running Surrogator on gold notes...\n")
		date_shift_log_gold, surrogate_log_gold,problem_files_log = parse_xml_files(gold_directory,gold_output_directory,gold_xmldomain,write_surrogated_files,problem_files_log,verbose)
		if verbose:
			write_logs(gold_output_directory,date_shift_log_gold, surrogate_log_gold)
	else:
		try:
			print ("Skipping re-running surrogator on gold notes. Reading from: \n    "+gold_output_directory+"shifted_dates.csv")
			surrogate_log_gold = pd.read_csv(gold_output_directory+'surrogated_text.csv')
			date_shift_log_gold = pd.read_csv(gold_output_directory+'shifted_dates.csv')
		except:
			print ("You have not run the surrogator with --rerun_gold=True yet. Please re-run with this parameter set to true"			)

	if (rerun_gold and rerun_philter) or test:
		problem_files_log.to_csv(output_directory + "/failed_to_parse.csv", index=False,sep="|")
		print ("Wrote record of files that failed to parse: "+ output_directory + "failed_to_parse.csv \n")


	if evaluation and verbose:
		print ("\nPhilter Notes:")
		write_summary(date_shift_log,surrogate_log,output_directory)
		print ("\n______________________________________________")
		print ("\nGOLD Notes")
		write_summary(date_shift_log_gold,surrogate_log_gold,gold_output_directory)
		date_shift_evaluation(output_directory,date_shift_log_gold,date_shift_log,problem_files_log)
		
if __name__ == "__main__":
	main()

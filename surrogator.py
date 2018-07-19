#!/usr/bin/python2.7


# import libraries
import sys,os
sys.path
sys.path.append('/usr/local/lib/python2.7/site-packages/')
import pandas as pd
import argparse

#for reading in the xml i2b2 notes
import xml.etree.ElementTree as ET
import xmltodict

#for date shifting
import dateutil.parser
from datetime import datetime,timedelta
import random
from dateparser import parse
import re

# Extract XML
def extractXML(directory,filename,philter_or_i2b2):
	"""Extracts the annotated XML file from either philter or i2b2 into text, and a dictionary of all tags """
	print "\ninput file: "+directory + '/'+ filename
	tree = ET.parse(directory + '/'+ filename)
	root = tree.getroot()
	xmlstr = ET.tostring(root, encoding='utf8', method='xml')
	xml_dict = xmltodict.parse(xmlstr)[philter_or_i2b2]
	text = xml_dict["TEXT"]
	tags_dict = xml_dict["TAGS"]
	return text,tags_dict,xmlstr

def parse_xml_files(directory,output_directory,philter_or_i2b2,write_surrogated_files,problem_files_log):
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
	# Loop through xml_files
	for filename in os.listdir(directory):
		if filename.endswith(".xml") and "DS_Store" not in filename:

			note_text,tags_dict,xmlstr = extractXML(directory,filename,philter_or_i2b2)

			for key, value in tags_dict.iteritems():
				# Note:  Value can be a list of like phi elements
				# 		or a dictionary of the metadata about a phi element

				if isinstance(value, list):
					for final_value in value:
						text_start = final_value["@start"]
						text_end = final_value["@end"]
						text = final_value["@text"]
						phi_type = final_value["@TYPE"]
						if phi_type == "DATE": 
							xmlstr,date_shift_log = shift_dates(filename_dates,filename,xmlstr,text,date_shift_log,note_text,text_start,text_end)
						else:
							xmlstr,surrogate_log = replace_other_surrogate(filename,xmlstr,text,phi_type,surrogate_log)								
				else:
					final_value = value
					text = final_value["@text"]
					phi_type = final_value["@TYPE"]
					text_start = final_value["@start"]
					text_end = final_value["@end"]

					if phi_type == "DATE":
						xmlstr,date_shift_log = shift_dates(filename_dates,filename,xmlstr,text,date_shift_log,note_text,text_start,text_end)
					else:
						xmlstr,surrogate_log = replace_other_surrogate(filename,xmlstr,text,phi_type,surrogate_log)
			
			# here we write back out the updated XML File to a new directory
			output_dir = output_directory+filename.replace(".xml",".txt")
			try:
				xmlstr = xmlstr.decode('utf-8', 'ignore')
				output_xml_dict = xmltodict.parse(xmlstr)[philter_or_i2b2]
				output_text = output_xml_dict["TEXT"]
				if write_surrogated_files:
					with open(output_dir, "w") as text_file:
						text_file.write(output_text)
					print "output file: " + output_dir

			except xmltodict.expat.ExpatError:
				print "We cannot parse this XML"
				problem_files_log = problem_files_log.append({"filename":filename,"philter_or_i2b2":philter_or_i2b2},ignore_index=True)


	date_shift_log.columns = ["Filename", "start", "end", "Input Date", "Shifted Date","Time Delta","date_context"]
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
		print "metadata not found. generating random date_shift"

		if filename not in filename_dates: 
			day,month,year,now = generate_random_date()
			filename_dates[filename] = [day,month,year,now]

		else:
			day,month,year,now = filename_dates[filename]
		    #print ("shifting by " + str(day) + " days and by "+ str(month) + " months")
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
          if dt.month!=now.month:
              output_string += str(dt_plus_arbitrary.strftime('%B')) 
          if dt.year!=now.year:
              output_string += " " +str(dt_plus_arbitrary.year)
          if dt.day!=1:
              output_string += " " +str(dt_plus_arbitrary.day)
          output_shifted_date = output_string.replace(" 00:00:00","")
      else:
          output_shifted_date = str(dt_plus_arbitrary).replace(" 00:00:00","")

      return output_shifted_date

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

    output_start_date = parse_and_shift_date(start_date_range,time_delta)
    output_end_date = parse_and_shift_date(end_date_range,time_delta)

    return start_date_range,end_date_range,output_start_date,output_end_date

def shift_dates(filename_dates,filename,xmlstr,date,date_shift_log,note_text,text_start,text_end):
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
        output_shifted_date = parse_and_shift_date(date,time_delta)
        date_shift_log = date_shift_log.append([(filename,text_start,text_end,date,output_shifted_date,time_delta_str,date_context)])
        output_xml = xmlstr.replace(date,output_shifted_date+ " [SHIFTED DATE]")
    else:
        try:
            start_date_range,end_date_range,start_dt_plus_arbitrary,end_dt_plus_arbitrary = parse_date_ranges(date,time_delta)
            output_xml = xmlstr.replace(str(start_date_range),start_dt_plus_arbitrary+ " [SHIFTED DATE]")
            output_xml = xmlstr.replace(str(end_date_range),end_dt_plus_arbitrary+ " [SHIFTED DATE]")
            date_shift_log = date_shift_log.append([(filename,text_start,text_end,start_date_range,start_dt_plus_arbitrary,time_delta_str,date_context)])
            date_shift_log = date_shift_log.append([(filename,text_start,text_end,end_date_range,end_dt_plus_arbitrary,time_delta_str,date_context)])

        except:
            output_xml = xmlstr.replace(date,"cannot parse date")
            date_shift_log = date_shift_log.append([(filename,text_start,text_end,date,"cannot parse date",time_delta_str,date_context)])

    return output_xml,date_shift_log

def replace_other_surrogate(filename,xmlstr,text,phi_type,surrogate_log):
	"""
	Returns the string of a note with the tagged PHI surrogated with the PHI Type
	"""
	# replace anything else with ***PHItype***
	if phi_type == "OTHER":
		output_xml = xmlstr.replace(text,"***PHI***")
	else:
		output_xml = xmlstr.replace(text,"***"+phi_type+"***")

	surrogate_log = surrogate_log.append([(filename,text,phi_type)])

	return output_xml,surrogate_log

def write_logs(output_directory,date_shift_log, surrogate_log):
	"""Writing logs of date shifts and surrogates to the specified output dir"""
	print "\n______________________________________________"

	date_shift_log.to_csv(output_directory + "/shifted_dates.csv", index=False)	
	surrogate_log.to_csv(output_directory + "/surrogated_text.csv", index=False)

	print "\nWrote record of shifted dates here: "+ output_directory + "shifted_dates.csv"
	print "Wrote record of surrogated text here: "+ output_directory + "surrogated_text.csv"


def write_summary(date_shift_log,surrogate_log,output_directory):
	"""Writes an evaluation summary surrogator. These are summaries from the different log files"""

	total_dates_we_cannot_parse = str(date_shift_log[date_shift_log['Shifted Date'] == "cannot parse date"].count()["Shifted Date"])
	total_dates_we_can_parse = str(date_shift_log[date_shift_log['Shifted Date'] != "cannot parse date"].count()["Shifted Date"])
	print "Summary of Date shifts \nTotal dates cannot parse: " + total_dates_we_cannot_parse
	print "Total dates parsed: " + total_dates_we_can_parse

	counts_by_phi_type = surrogate_log.groupby(["phi_type"]).size()
	counts_by_phi_type.cols = ["phi_type","count"]
	counts_by_phi_type.to_csv(output_directory + "/counts_by_phi_type.csv")
	print "\nCounts of text surrogated by phi_type:" 
	print counts_by_phi_type

def date_shift_evaluation(output_directory,date_shift_log_i2b2,date_shift_log,problem_files_log):
	"""
	Prints a summary of the true positives, false positives and false negatives
    Saves a more granular file of all of these to output_directory
	"""

	s1 = pd.merge(date_shift_log_i2b2, date_shift_log,indicator=True, how='outer', on=['Filename','start','end','Input Date'])
	output_eval = s1[["Filename","Input Date","_merge"]]
	output_eval = output_eval.rename(index=str, columns={"_merge": "classification"})
	output_eval["classification"] = output_eval['classification'].replace({'both': 'true positive','left_only': 'false positive', 'right_only': 'false negative'})
	output_eval["description"] = output_eval['classification'].replace({'true positive':'appears in both i2b2 and philter','false positive':'appears in i2b2 notes only', 'false negative':'appears in philter notes only'})


	if problem_files_log.empty == False:
		problem_filenames = problem_files_log['filename'].tolist()
		output_eval = output_eval.loc[~output_eval['Filename'].isin(problem_filenames)]


	output_eval.to_csv(output_directory+"date_shift_eval.csv", index=False)

	# count of True positives (shows in both)
	s1_true_positive = output_eval[output_eval['classification'] == "true positive"].count()["Input Date"]
	true_positives = s1_true_positive
	print "\n______________________________________________"
	print "\nSummary Stats: \ntrue positives: " + str(true_positives)

	# count of False positives (shows in actual only)
	s1_false_positive = output_eval[output_eval['classification'] == "false positive"].count()["Input Date"]
	false_positives = s1_false_positive
	print "false positives: " + str(false_positives)

	# count of False negative (shows in predicted only)
	s1_false_negative = output_eval[output_eval['classification'] == "false negative"].count()["Input Date"]
	false_negatives = s1_false_negative
	print "false negatives: " + str(false_negatives)
	print "\nwriting out eval record to: " + output_directory + "date_shift_eval.csv"
	print "\n______________________________________________\n"

def main():

	parser = argparse.ArgumentParser(description=
		"""This program will read in i2b2 or Philter XML formatted notes \n
		Then apply date shifts to any phi tagged as a date. \n
		Next it will replace all appropriate PHI with the respective PHI Tag \n 
		Then it will output .txt files with the appropriate surrogates
		""")

	parser.add_argument("-i","--input_dir", default="data/i2b2_results", help="specifiy the input directory",
                    type=str)
	parser.add_argument("-o","--output_dir", default="data/surrogator/philter_results_output/", help="specifiy the output directory",
                    type=str)
	parser.add_argument("-ii","--i2b2_input_dir", default="data/surrogator/testing-PHI-Gold-fixed", help="specifiy the input i2b2 directory",
                    type=str)
	parser.add_argument("-io","--i2b2_output_dir", default="data/surrogator/testing-PHI-Gold-fixed-output/", help="specifiy the i2b2 output directory",
		            type=str)
	parser.add_argument("-rp","--rerun_philter", default=False, help="This will re-run the philter surrogating. It takes a while, so default is false",
                    type=bool)
	parser.add_argument("-ri","--rerun_i2b2", default=False, help="This will re-run the i2b2 gold standard surrogating. It takes a while, so default is false",
                    type=bool)	
	parser.add_argument("-e","--evaluation", default=True, help="This will run the evaluation comparing surrogated i2b2 with surrogated philter notes",
                    type=bool)	
	parser.add_argument("-t","--test", default=False, help="This will run the test, using less files",
                    type=bool)
	parser.add_argument("-w","--write_surrogated_files", default=False, help="This will write the surrogated notes.",
                    type=bool)
	parser.add_argument("-p","--prod", default=False, help="This will run the production mode, using only Philtered notes and not running evaluation",
                    type=bool)

	parsed = parser.parse_args()
	directory = vars(parsed)["input_dir"]
	output_directory = vars(parsed)["output_dir"]
	i2b2_directory = vars(parsed)["i2b2_input_dir"]
	i2b2_output_directory = vars(parsed)["i2b2_output_dir"]
	rerun_i2b2 = vars(parsed)["rerun_i2b2"]
	rerun_philter = vars(parsed)["rerun_philter"]
	evaluation = vars(parsed)["evaluation"]
	write_surrogated_files = vars(parsed)["write_surrogated_files"]
	test = vars(parsed)["test"]
	prod = vars(parsed)["prod"]

	if test:
		directory = "data/surrogator/test/philter_results_test"
		output_directory = "data/surrogator/test/philter_results_output_test/"
		i2b2_directory = "data/surrogator/test/testing-PHI-Gold-fixed_test"
		i2b2_output_directory = "data/surrogator/test/testing-PHI-Gold-fixed-output_test/"
		write_surrogated_files = True

	if prod:
		rerun_i2b2 = False
		rerun_philter = True
		evaluation = False
		write_surrogated_files = True
		test = False

	if not os.path.exists(directory):
		raise Exception("directory does not exist", directory)
	if not os.path.exists(output_directory):
		raise Exception("output_directory does not exist", output_directory)
	if not os.path.exists(i2b2_directory):
		raise Exception("i2b2_directory does not exist", i2b2_directory)
	if not os.path.exists(i2b2_output_directory):
		raise Exception("i2b2_output_directory does not exist", i2b2_output_directory)

	print "\nRunning Surrogator...\n"

	problem_files_log = pd.DataFrame(columns = ["filename","philter_or_i2b2"])

	if rerun_philter or test:
		print "Running Surrogator on philter notes..."
		date_shift_log, surrogate_log,problem_files_log = parse_xml_files(directory,output_directory,"Philter",write_surrogated_files,problem_files_log)
		write_logs(output_directory,date_shift_log, surrogate_log)
	else:
		try:
			print "Skipping re-running surrogator on philter notes. Reading from: \n    "+output_directory+"shifted_dates.csv"
			date_shift_log = pd.read_csv(output_directory+'shifted_dates.csv')
			surrogate_log = pd.read_csv(output_directory+'surrogated_text.csv')
		except:
			print "You have not run the surrogator with --rerun_philter=True yet. Please re-run with this parameter set to true"			


	if rerun_i2b2 or test:
		print "\n\n____________________________________"
		print "Running Surrogator on i2b2 notes..."
		date_shift_log_i2b2, surrogate_log_i2b2,problem_files_log = parse_xml_files(i2b2_directory,i2b2_output_directory,"deIdi2b2",write_surrogated_files,problem_files_log)
		write_logs(i2b2_output_directory,date_shift_log_i2b2, surrogate_log_i2b2)
	else:
		try:
			print "Skipping re-running surrogator on i2b2 notes. Reading from: \n    "+i2b2_output_directory+"shifted_dates.csv"
			surrogate_log_i2b2 = pd.read_csv(i2b2_output_directory+'surrogated_text.csv')
			date_shift_log_i2b2 = pd.read_csv(i2b2_output_directory+'shifted_dates.csv')
		except:
			print "You have not run the surrogator with --rerun_i2b2=True yet. Please re-run with this parameter set to true"			

	if (rerun_i2b2 and rerun_philter) or test:
		problem_files_log.to_csv(output_directory + "/failed_to_parse.csv", index=False)
		print "Wrote record of files that failed to parse: "+ output_directory + "failed_to_parse.csv \n"


	if evaluation:
		print "\nPhilter Notes:"
		write_summary(date_shift_log,surrogate_log,output_directory)
		print "\n______________________________________________"
		print "\nI2B2 Notes"
		write_summary(date_shift_log_i2b2,surrogate_log_i2b2,i2b2_output_directory)
		date_shift_evaluation(output_directory,date_shift_log_i2b2,date_shift_log,problem_files_log)

if __name__ == "__main__":
	main()

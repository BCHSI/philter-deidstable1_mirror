# import libraries
import sys,os
sys.path
sys.path.append('/usr/local/lib/python2.7/site-packages/')
import pandas as pd

#for reading in the xml i2b2 notes
import xml.etree.ElementTree as ET
import xmltodict
#from yattag import indent

#for date shifting
import dateutil.parser
from datetime import datetime,timedelta
import random
from dateparser import parse


# Extract XML
def extractXML(directory,filename,philter_or_i2b2):
	print "\ninput filename: "+directory + '/'+ filename
	tree = ET.parse(directory + '/'+ filename)
	root = tree.getroot()
	xmlstr = ET.tostring(root, encoding='utf8', method='xml')
	xml_dict = xmltodict.parse(xmlstr)***REMOVED***philter_or_i2b2***REMOVED***
	text = xml_dict***REMOVED***"TEXT"***REMOVED***
	tags_dict = xml_dict***REMOVED***"TAGS"***REMOVED***
	return text,tags_dict,xmlstr

def parse_xml_files(directory,output_directory,philter_or_i2b2):
		# Loop through xml_files
	cols = ***REMOVED***"Document", "PHI_element", "Text", "Type","Comment"***REMOVED***
	output_df = pd.DataFrame(columns = cols,index=None)
	new_dict = dict()
	filename_dates = {}
	date_shift_log = pd.DataFrame()

	for filename in os.listdir(directory):
		if filename.endswith(".xml") and "DS_Store" not in filename:

			text,tags_dict,xmlstr = extractXML(directory,filename,philter_or_i2b2)

			for key, value in tags_dict.iteritems():
				# Note:  Value can be a list of like phi elements
				# 		or a dictionary of the metadata about a phi element

				if isinstance(value, list):
					for final_value in value:
						text = final_value***REMOVED***"@text"***REMOVED***
						phi_type = final_value***REMOVED***"@TYPE"***REMOVED***

						if phi_type == "DATE": 
							xmlstr,date_shift_log = shift_dates(filename_dates,filename,xmlstr,text,date_shift_log,verbose=0)
						else:
							xmlstr = replace_other_surrogate(xmlstr,text,phi_type)								
				else:
					final_value = value
					text = final_value***REMOVED***"@text"***REMOVED***
					phi_type = final_value***REMOVED***"@TYPE"***REMOVED***

					if phi_type == "DATE":
						xmlstr,date_shift_log = shift_dates(filename_dates,filename,xmlstr,text,date_shift_log,verbose=0)
					else:
						xmlstr = replace_other_surrogate(xmlstr,text,phi_type)
			
			# here we write back out the updated XML File to a new directory
			output_dir = output_directory+filename.replace(".xml",".txt")
			try:
				output_xml_dict = xmltodict.parse(xmlstr)***REMOVED***philter_or_i2b2***REMOVED***
				output_text = output_xml_dict***REMOVED***"TEXT"***REMOVED***

				with open(output_dir, "w") as text_file:
					text_file.write(output_text)
				print "output filename: " + output_dir

			except xmltodict.expat.ExpatError:
				print "We cannot parse this XML"

	date_shift_log.columns = ***REMOVED***"Filename", "Input Date", "Shifted Date","Time Delta"***REMOVED***
	date_shift_log.to_csv(output_directory + "/shifted_dates.csv", index=False)
	print "\nwriting record of shifted dates here: "+ output_directory + "shifted_dates.csv \n"

# date shift functions
def generate_random_date():
  now = datetime.now()
  day = random.choice(range(1, 29))
  month = random.choice(range(1, 24))
  year = random.choice(range(1, 1000))
  return day,month,year,now

def get_date_shift(filename,filename_dates):
	file_prefix = filename.replace(".xml","").replace(".txt","")
	#read in the metadata tables
	note_info = pd.read_csv('data/notes_metadata/note_info.csv')
	re_id_pat = pd.read_csv('data/notes_metadata/re_id_pat.csv')

	#join together re_id_pat with NOTE_INFO on Patient_id
	notes_metadata = note_info.set_index('patient_ID').join(re_id_pat.set_index('patient_ID'))
	# we now have columns: Patient_ID, note_csn_id, date_offset

	metadata_mapping_dict = pd.Series(notes_metadata.date_offset.values,index=notes_metadata.note_csn_id).to_dict()
	#create a dictionary_mapping***REMOVED***filename***REMOVED*** = dateshift
	#print metadata_mapping_dict

	if file_prefix in metadata_mapping_dict:
		dateshift = metadata_mapping_dict***REMOVED***file_prefix***REMOVED***
		time_delta = timedelta(days=dateshift)
	else:
		print "metadata not found. generating random date_shift"

		if filename not in filename_dates: 
			day,month,year,now = generate_random_date()
			filename_dates***REMOVED***filename***REMOVED*** = ***REMOVED***day,month,year,now***REMOVED***

		else:
			day,month,year,now = filename_dates***REMOVED***filename***REMOVED***
		    #print ("shifting by " + str(day) + " days and by "+ str(month) + " months")
		time_delta = timedelta(weeks=month*4,days=day)

	return time_delta

def shift_dates(filename_dates,filename,xmlstr,date,date_shift_log,verbose):
    now = datetime.now()
    time_delta = get_date_shift(filename,filename_dates)
    time_delta_str= str(time_delta).replace(", 0:00:00","")
    dt = parse(date.replace("O2","02"),settings={'PREFER_DAY_OF_MONTH': 'first'} ) #dateutil.parser.
    if dt !=None:
      # we know that it's incomplete if:
      # this setting returns none:  settings={'STRICT_PARSING': True}
      strict_parse = parse(date,settings={'STRICT_PARSING': True})

      # Note: we can add parameters to this parsing
      #        settings={'PREFER_DAY_OF_MONTH': 'last'} or 'first'
      #        settings={'PREFER_DATES_FROM': 'future'} or 'past'


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
          date_shift_log = date_shift_log.append(***REMOVED***(filename,date,output_shifted_date,time_delta_str)***REMOVED***)
          output_xml = xmlstr.replace(date,output_shifted_date)

      else:
        output_shifted_date = str(dt_plus_arbitrary).replace(" 00:00:00","")
    	date_shift_log = date_shift_log.append(***REMOVED***(filename,date,output_shifted_date,time_delta_str)***REMOVED***)
        output_xml = xmlstr.replace(date,output_shifted_date)
    else:
        output_xml = xmlstr.replace(date,"cannot parse date")
        date_shift_log = date_shift_log.append(***REMOVED***(filename,date,"cannot parse date",time_delta_str)***REMOVED***)

    return output_xml,date_shift_log

def replace_other_surrogate(xmlstr,text,phi_type):
	# replace anything else with ***PHItype***
	if phi_type == "OTHER":
		output_xml = xmlstr.replace(text,"***PHI***")
	else:
		output_xml = xmlstr.replace(text,"***"+phi_type+"***")
	return output_xml

def main():
	# read in i2b2 format notes
	# apply date shift to PHI Tagged as Dates	
	# replace all other PHI with ***PHItype***
	# output files

# 	I2b2 annotations
#	directory = "data/surrogator_test/testing-PHI-Gold-fixed"
#	output_directory = "data/surrogator_test/testing-PHI-Gold-fixed-output/"
#	philter_or_i2b2 = "deIdi2b2"


# 	Philter output 
	directory = "data/i2b2_results"
	output_directory = "data/surrogator_test/i2b2_results_output/"
	philter_or_i2b2 = "Philter"


	parse_xml_files(directory,output_directory,philter_or_i2b2)


if __name__ == "__main__":
	main()

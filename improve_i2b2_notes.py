import pandas 
import xml.etree.ElementTree as ET
import sys
sys.path
sys.path.append('/usr/local/lib/python2.7/site-packages/')
import xmltodict
import os
import pandas as pd
import re

### This script presumes that there is the testing-PHI-Gold-fixed 
### folder in the same directory and will output the edited annotations 
### updated_annotations_i2b2 called updated_annotations_i2b2

def extractXML(directory,filename):
	tree = ET.parse(directory + '/'+ filename)
	root = tree.getroot()
	xmlstr = ET.tostring(root, encoding='utf8', method='xml')
	#print xmlstr + "\n \n"
	xml_dict = xmltodict.parse(xmlstr)***REMOVED***"deIdi2b2"***REMOVED***
	text = xml_dict***REMOVED***"TEXT"***REMOVED***
	tags_dict = xml_dict***REMOVED***"TAGS"***REMOVED***
	return text,tags_dict,xmlstr

def delete_annotation(xml_file, phi_type, tag_to_delete):
	#print tag_to_delete
	remove_line_if = 'text="' + tag_to_delete + '"'

	for line in xml_file.split("\n"):
		#print remove_line_if
		if remove_line_if in line:
			remove_line = line + "\n"
			print remove_line
			xml_file = xml_file.replace(remove_line,"")

	return xml_file

def fix_dates(xml_file,text):
	# remove year
	PHI_type="DATE"
	date = text
	if date.isdigit():
		if len(date) == 4 and (1000<= date<=3000):
			delete_annotation(xml_file, PHI_type, text)

	# remove season
	seasons = ***REMOVED***"spring","winter","fall","summer","autumn"***REMOVED***
	if date.lower() in seasons:
		delete_annotation(xml_file, PHI_type, text)

	# remove day of week
	days=***REMOVED***"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday","Mon","Tues","Wed","Thurs","Fri","Sat","Sun"***REMOVED***
	if date in days:
		delete_annotation(xml_file, PHI_type, text)

	return xml_file

def remove_abbrevs(xml_file,text,phi_type):
	#question -- what do we do about the username field
	
	if len(text)<4 and str(text).isupper():
		delete_annotation(xml_file, phi_type, text)
	return xml_file

def remove_ids(xml_file,text):
	# three sub-categories:
	## IDNUM
	## MEDICALRECORD
	## DEVICE

	phi_type = "ID"
	if len(text)<5:
		xml_file = delete_annotation(xml_file, PHI_type, text)

	return xml_file

def remove_countries(xml_file,text,phi_type):
	if phi_type == "COUNTRY":
		xml_file = delete_annotation(xml_file, phi_type, text)
	return xml_file

def remove_age_under_90(xml_file,text,phi_type,filename):
	standardized_age = text.split("y")***REMOVED***0***REMOVED***
	non_numeric_ages =	***REMOVED***"18 month", "20's", "32y5.7m", "56y0.5m","50's","50s", "60's", "60's", "60's", "60's", "60s", "60s", "60s", "70's", "70's", "70s", "80's", "80's", "80's", "80's", "80's", "80's", "80's", "80's", "80's", "80's", "80s", "80s", "80s", "80s", "80s", "82nd", "Sevent", "sevent"***REMOVED***
	if standardized_age in non_numeric_ages:
		xml_file = delete_annotation(xml_file, phi_type, text)
	elif isinstance(standardized_age, int) and int(standardized_age) < 90:
		xml_file = delete_annotation(xml_file, phi_type, text)
	elif standardized_age not in non_numeric_ages and int(standardized_age) < 90:
		xml_file = delete_annotation(xml_file, phi_type, text)
	# else:
	# 	print filename,text
	return xml_file

	## Notes: Kept the label in the following notes of 90
		# 131-02.xml, 310-02.xml, 310-04.xml, 373-04.xml, 373-05.xml, 215-02.xml 
		# 194-02.xml, 136-05.xml 

def remove_hospitals(xml_file,text,phi_type):
	if phi_type == "HOSPITAL":
		xml_file = delete_annotation(xml_file, phi_type, text)
	return xml_file

def main():
	# Loop through xml_files
	directory = "testing-PHI-Gold-fixed"
	cols = ***REMOVED***"Document", "PHI_element", "Text", "Type","Comment"***REMOVED***
	output_df = pd.DataFrame(columns = cols,index=None)

	new_dict = dict()

	for filename in os.listdir(directory):
		print "\nfilename is: " + filename 

	# example for year
	#filename = "113-02.xml"
	
	# example for season
	#filename = "119-03.xml"

	# example for weekday 
	#filename ="110-04.xml"	
	
	#example for abbrev
	#filename = "236-01.xml"

	# re-indent
		text,tags_dict,xmlstr = extractXML(directory,filename)
	#print str(tags_dict) + '\n \n'

		for key, value in tags_dict.iteritems():
			# Note:  Value can be a list of like phi elements
			# 		or a dictionary of the metadata about a phi element

			if isinstance(value, list):
				for final_value in value:
					# do checks
					text = final_value***REMOVED***"@text"***REMOVED***
					phi_type = final_value***REMOVED***"@TYPE"***REMOVED***

					if phi_type == "DATE": 
						xmlstr = fix_dates(xmlstr,text)
					elif phi_type == "NAME" or phi_type == "DOCTOR":
						xmlstr = remove_abbrevs(xmlstr,text,phi_type)	
					elif phi_type == "ID":
						xmlstr = remove_ids(xmlstr,text)	
					elif phi_type == "COUNTRY":
						xmlstr = remove_countries(xmlstr,text,phi_type)	
					elif phi_type == "AGE":
						xmlstr = remove_age_under_90(xmlstr,text,phi_type,filename)
					elif phi_type == "HOSPITAL":
						xmlstr = remove_hospitals(xmlstr,text,phi_type)								
			else:
				final_value = value
				text = final_value***REMOVED***"@text"***REMOVED***
				phi_type = final_value***REMOVED***"@TYPE"***REMOVED***

				if phi_type == "DATE":
					xmlstr = fix_dates(xmlstr,text)
				elif phi_type == "NAME" or phi_type == "DOCTOR":
					xmlstr = remove_abbrevs(xmlstr,text,phi_type)
				elif phi_type == "ID":
						xmlstr = remove_ids(xmlstr,text)
				elif phi_type == "COUNTRY":
					xmlstr = remove_countries(xmlstr,text,phi_type)	
				elif phi_type == "AGE":
					xmlstr = remove_age_under_90(xmlstr,text,phi_type,filename)
				elif phi_type == "HOSPITAL":
					xmlstr = remove_hospitals(xmlstr,text,phi_type)	
		
		# here we write back out the updated XML File to a new directory
		output_dir = "updated_annotations_i2b2/"+filename
		with open(output_dir, "w") as text_file:
			text_file.write(xmlstr)

if __name__ == "__main__":
	main()

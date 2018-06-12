# import libraries
import sys,os
sys.path
sys.path.append('/usr/local/lib/python2.7/site-packages/')
import pandas as pd

#for reading in the xml i2b2 notes
import xml.etree.ElementTree as ET
import xmltodict

#for date shifting
import dateutil.parser
from datetime import datetime,timedelta
import random
from dateparser import parse


# Extract XML
def extractXML(directory,filename):
	print directory + '/'+ filename
	tree = ET.parse(directory + '/'+ filename)
	root = tree.getroot()
	xmlstr = ET.tostring(root, encoding='utf8', method='xml')
	xml_dict = xmltodict.parse(xmlstr)["Philter"]
	text = xml_dict["TEXT"]
	tags_dict = xml_dict["TAGS"]
	return text,tags_dict,xmlstr

def go_through_xml_files(directory,output_directory):
		# Loop through xml_files
	cols = ["Document", "PHI_element", "Text", "Type","Comment"]
	output_df = pd.DataFrame(columns = cols,index=None)
	shift_dates_together=1
	new_dict = dict()
	filename_dates = {}
	output_record_of_date_shifting = pd.DataFrame()

	for filename in os.listdir(directory):
		if filename.endswith(".xml"):
			print "\nfilename is: " + filename 

		# re-indent
			text,tags_dict,xmlstr = extractXML(directory,filename)

			for key, value in tags_dict.iteritems():
				# Note:  Value can be a list of like phi elements
				# 		or a dictionary of the metadata about a phi element

				if isinstance(value, list):
					for final_value in value:
						text = final_value["@text"]
						phi_type = final_value["@TYPE"]

						if phi_type == "DATE": 
							xmlstr,output_record_of_date_shifting = shift_dates(filename_dates,filename,shift_dates_together,xmlstr,text,output_record_of_date_shifting,verbose=0)
						else:
							xmlstr = replace_other_surrogate(xmlstr,text,phi_type)								
				else:
					final_value = value
					text = final_value["@text"]
					phi_type = final_value["@TYPE"]

					if phi_type == "DATE":
						xmlstr,output_record_of_date_shifting = shift_dates(filename_dates,filename,shift_dates_together,xmlstr,text,output_record_of_date_shifting,verbose=0)
					else:
						xmlstr = replace_other_surrogate(xmlstr,text,phi_type)
			
			# here we write back out the updated XML File to a new directory
			output_dir = output_directory+filename.replace(".xml",".txt")
			output_xml_dict = xmltodict.parse(xmlstr)["Philter"]
			output_text = output_xml_dict["TEXT"]

			with open(output_dir, "w") as text_file:
				text_file.write(output_text) 

	output_record_of_date_shifting.columns = ["Filename", "Input Date", "Shifted Date","Time Delta"]
	output_record_of_date_shifting.to_csv(output_directory + "/shifted_dates.csv", index=False)

# date shift functions
def generate_random_date():
  now = datetime.now()
  day = random.choice(range(1, 29))
  month = random.choice(range(1, 24))
  year = random.choice(range(1, 1000))
  return day,month,year,now

def shift_dates(filename_dates,filename,shift_dates_together,xmlstr,date,output_record_of_date_shifting,verbose):
    #output_shifted_dates = []
    # note this isn't working as expected
    #output_record_of_date_shifting = pd.DataFrame()
    if shift_dates_together==1 and  filename not in filename_dates: #bool(filename_dates)==False and
        day,month,year,now = generate_random_date()
        filename_dates[filename] = [day,month,year,now]
    elif shift_dates_together==1:
    	day,month,year,now = filename_dates[filename]
        #print ("shifting by " + str(day) + " days and by "+ str(month) + " months")
    #for date in dates:
    time_delta = timedelta(weeks=month*4,days=day)
    time_delta_str= str(time_delta).replace(", 0:00:00","")
    dt = parse(date,settings={'PREFER_DAY_OF_MONTH': 'first'} ) #dateutil.parser.
    if dt !=None:
      # we know that it's incomplete if:
      # this setting returns none:  settings={'STRICT_PARSING': True}
      strict_parse = parse(date,settings={'STRICT_PARSING': True})

      # Note: we can add parameters to this parsing
      #        settings={'PREFER_DAY_OF_MONTH': 'last'} or 'first'
      #        settings={'PREFER_DATES_FROM': 'future'} or 'past'

      if shift_dates_together==0 :
        day,month,year,now = generate_random_date()
      
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
    output_record_of_date_shifting = output_record_of_date_shifting.append([(filename,date,output_shifted_date,time_delta_str)])

    output_xml = xmlstr.replace(date,output_shifted_date)
    return output_xml,output_record_of_date_shifting

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
	directory = "data/surrogator_test"
	output_directory = "data/surrogator_test/output/"

	go_through_xml_files(directory,output_directory)


if __name__ == "__main__":
	main()

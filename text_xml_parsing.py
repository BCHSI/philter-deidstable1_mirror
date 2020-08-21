import xml.etree.ElementTree as ET
import xmltodict
import os
import pandas as pd

### This script extracts the tags from xml files in the folder testing-PHI-Gold-fixed
### It assumes that the mentioned folder is in the same directory as this script
### It outputs a file called phi_annotations.csv which is an organized csv of TAGS
### in the format ["Document", "PHI_element", "Text", "Type","Comment"]


def extractXML(directory,filename):
	tree = ET.parse(directory + '/'+ filename)
	root = tree.getroot()
	xmlstr = ET.tostring(root, encoding='utf8', method='xml')
	xml_dict = xmltodict.parse(xmlstr)["deIdi2b2"]
	text = xml_dict["TEXT"]
	tags_dict = xml_dict["TAGS"]
	return text,tags_dict

def createNewRow(filename,key,final_value):
	text = final_value["@text"]
	text_type = final_value["@TYPE"]
	text_comment = final_value["@comment"]
	new_row = [filename, key, text, text_type, text_comment]
	new_row_df = pd.DataFrame(columns=["Document", "PHI_element", "Text", "Type","Comment"], index=None)
	new_row_df.loc[0] = new_row
	return new_row_df


def main():
	directory = "testing-PHI-Gold-fixed"
	cols = ["Document", "PHI_element", "Text", "Type","Comment"]
	output_df = pd.DataFrame(columns = cols,index=None)


	for filename in os.listdir(directory):
		print "filename is: " + filename + '\n'
		text,tags_dict = extractXML(directory,filename)

		for key, value in tags_dict.iteritems():
			# Note:  Value can be a list of like phi elements
			# 		or a dictionary of the metadata about a phi element

			if isinstance(value, list):
				for final_value in value:
					new_row_df =createNewRow(filename,key,final_value)
					output_df = output_df.append(new_row_df)
			else:
				final_value = value
				new_row_df =createNewRow(filename,key,final_value)
				output_df = output_df.append(new_row_df)

	#print output_df.head(n=5)		
	output_df.to_csv('phi_annotations.csv',index_label = False)


if __name__ == "__main__":
	main()

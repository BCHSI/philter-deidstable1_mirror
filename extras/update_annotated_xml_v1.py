import sys
import os
import io
import re
import dask
import dask.dataframe as dd
import pandas as pd
import difflib

#for reading in the xml gold notes
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import xmltodict
from bs4 import UnicodeDammit
"""
Example:
    python update_annotated_xml.py <folder_with_annotated_xml> <folder_with_philter_xml_output> <folder_to_write_out_updated_annotated_xml>

"""


def extractXML(directory,filename,philter_or_gold,verbose):
        """Extracts the annotated XML file from either philter or gold into text, and a dictionary of all tags """
        if verbose:
                print ("\ninput file: "+directory + '/'+ filename)
        file_to_parse = os.path.join(directory, filename)
        #        tree = ET.parse(file_to_parse, etree.XMLParser(encoding='utf-8-sig'))
        #        root = tree.getroot()
        #        xmlstr = ET.tostring(root, encoding='utf-8-sig', method='xml')
        
        with open(file_to_parse, encoding='utf-8', errors='xmlcharrefreplace') as fd:
            input_xml = fd.read() 
            #print(input_xml)
            tree = ET.parse(file_to_parse)
            root = tree.getroot()
            xmlstr = ET.tostring(root, encoding='utf8', method='xml')
            text = root.find('TEXT').text
            xml_dict = xmltodict.parse(xmlstr)***REMOVED***philter_or_gold***REMOVED***
            #xml_dict = xmltodict.parse(re.sub(r'\^@',r'',input_xml,flags=re.M))
            #text = xml_dict***REMOVED***"TEXT"***REMOVED***
            #print(text)
            check_tags = root.find('TAGS')
            if check_tags is not None:
               tags_dict = xml_dict***REMOVED***"TAGS"***REMOVED***            
            else:
               tags_dict = ''
        return text,tags_dict

def check_existing_phi(filename,note_text, tag_dict,philter_start, philter_end):
    """ Checks if the Philter identified PHI already exists in the annotated XML as a PHI """
    existing_phi_value = False 
    if tags_dict is not None:
       for key, value in tags_dict.items():
              # Note:  Value can be a list of like phi elements
              #               or a dictionary of the metadata about a phi element
           if isinstance(value, list):
              for final_value in value:
                  text_start = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED*** 
                  text_end = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***
                  philter_text = final_value***REMOVED***"@text"***REMOVED***
                  phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                  if phi_type == "DATE" or phi_type == "Date":
                     #print(philter_start +'\t' + text_start + '\t' + philter_end + '\t' + text_end)
                     if int(philter_start) >= int(text_start) and int(philter_end) <= int(text_end):                      
                         existing_phi_value = True                      
                     elif int(philter_start) < int(text_start) and int(philter_end) > int(text_start) and int(philter_end) <= int(text_end):
                         #existing_phi_value = True
                         #print(philter_text)
                         print(filename + " PHI overalp" + " " + philter_start + " " + philter_end + " " + text_start + " " + text_end)
                     elif int(philter_start) > int(text_start) and int(philter_start) < int(text_end) and int(philter_end) >= int(text_end):
                         #existing_phi_value = True
                         print(filename + " PHI overalp" + " " + philter_start + " " + philter_end + " " + text_start + " " + text_end)   
           else:
               final_value = value
               text = final_value***REMOVED***"@text"***REMOVED***
               phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
               text_start = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED***
               text_end = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***
               if phi_type == "DATE" or phi_type == "Date":
                  if ((philter_start >= text_start) & (philter_start <= text_end)):       
                     existing_phi_value = True
    return existing_phi_value


def update_xml_head(note_text,tags_dict):
        """Creates a string in i2b2-XML format. This function just creates the string with the xml text. The tags string is created in another function"""
        root = "PhilterUCSF"
        contents_head = ***REMOVED******REMOVED***
        #tagdata***REMOVED***'text'***REMOVED*** = re.sub(r'\^@',' ',tagdata***REMOVED***'text'***REMOVED***)
        
        contents_head.append("<?xml version=\"1.0\" ?>\n")
        contents_head.append("<"+root+">\n")
        contents_head.append("<TEXT><!***REMOVED***CDATA***REMOVED***")
        contents_head.append(note_text)
        contents_head.append("***REMOVED******REMOVED***></TEXT>\n")
        contents_head.append("<TAGS>\n")
        return "".join(contents_head)


def update_xml_tags(tags_dict,final_value):
        """ Creates the tags string to append to the updated xml output file. Note the function merges a new PHI identified by philter to the existing annotated PHI and modifies the tag ID to be sequential while merging """
        count = 0 
        if tags_dict is not None:
          #print(philter_tags_dict)
           
           inserted = False 
           for key, value in tags_dict.items():
              # Note:  Value can be a list of like phi elements
              #               or a dictionary of the metadata about a phi element
           
                   
               if isinstance(value, list):
                  for tag_value in value:  
                      phi_type = tag_value***REMOVED***"@TYPE"***REMOVED*** 
                      tagcategory = phi_type
                      #print(tag_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED*** + '\t' + final_value***REMOVED***"@start"***REMOVED*** + '\t' + str(inserted))
                      if ((int(tag_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED***) >= int(final_value***REMOVED***"@start"***REMOVED***)) and not inserted):
                          contents.append("<")
                          contents.append("Date")
                          contents.append(" id=\"D")
                          contents.append(str(count))
                          count = count + 1
                          contents.append("\" spans=\"")
                          contents.append(str(final_value***REMOVED***"@start"***REMOVED***))
                          contents.append("~")
                          contents.append(str(final_value***REMOVED***"@end"***REMOVED***))
                          contents.append("\" text=\"")
                          contents.append(str(final_value***REMOVED***"@text"***REMOVED***))
                          contents.append("\" TYPE=\"")
                          contents.append("Date")
                          contents.append("\" comment=\"\" />\n")
                          inserted = True

                          contents.append("<")
                          contents.append(phi_type)
                          if phi_type == "DATE" or phi_type == "Date":
                             contents.append(" id=\"D")
                             contents.append(str(count))
                             count = count + 1
                          else:
                             contents.append(" id=\"")
                             contents.append(str(tag_value***REMOVED***"@id"***REMOVED***))
                          contents.append("\" spans=\"")
                          contents.append(str(tag_value***REMOVED***"@spans"***REMOVED***))
                          contents.append("\" text=\"")
                          contents.append(str(tag_value***REMOVED***"@text"***REMOVED***))
                          contents.append("\" TYPE=\"")
                          contents.append(phi_type)
                          contents.append("\" comment=\"\" />\n")                          

                      else:   
                          contents.append("<")
                          contents.append(phi_type)
                          if phi_type == "DATE" or phi_type == "Date": 
                             contents.append(" id=\"D")
                             contents.append(str(count))
                             count = count + 1
                          else:
                             contents.append(" id=\"")
                             contents.append(str(tag_value***REMOVED***"@id"***REMOVED***))
                          contents.append("\" spans=\"")
                          contents.append(str(tag_value***REMOVED***"@spans"***REMOVED***))
                          contents.append("\" text=\"")
                          contents.append(str(tag_value***REMOVED***"@text"***REMOVED***))
                          contents.append("\" TYPE=\"")
                          contents.append(phi_type)
                          contents.append("\" comment=\"\" />\n")
        
        else:
            contents.append("<")
            contents.append("Date")
            contents.append(" id=\"D")
            contents.append(str(count))
            count = count + 1
            contents.append("\" spans=\"")
            contents.append(str(final_value***REMOVED***"@start"***REMOVED***))
            contents.append("~")
            contents.append(str(final_value***REMOVED***"@end"***REMOVED***))
            contents.append("\" text=\"")
            contents.append(str(final_value***REMOVED***"@text"***REMOVED***))
            contents.append("\" TYPE=\"")
            contents.append("Date")
            contents.append("\" comment=\"\" />\n")



        return contents


def update_xml_tail():
        """ Creates a string in i2b2 xml format """
        contents_tail = ***REMOVED******REMOVED***
        root = "PhilterUCSF"
        contents_tail.append("</TAGS>\n")
        contents_tail.append("</"+root+">\n")
        
        return "".join(contents_tail)



xml_dir = sys.argv***REMOVED***1***REMOVED***
philter_dir = sys.argv***REMOVED***2***REMOVED***
out_dir = sys.argv***REMOVED***3***REMOVED***
""" For loop to traverse through each of the files in the annotated xml folders"""
for filename in os.listdir(xml_dir): 
    existing_phi = set()
    if filename.endswith('xml'):
       
       #directory = xml_dir + dirname
       philter_or_gold = 'PhilterUCSF'
       verbose = False          
       note_text,tags_dict = extractXML(xml_dir,filename,philter_or_gold,verbose)
       philter_xml = filename.split('.',1)
       philter_xml_file = philter_xml***REMOVED***0***REMOVED***+'.xml'
       #philter_dir = '/data/radhakrishnanl/philter/annotator_output'
       #philter_dir = './philter_test'
       philter_or_gold = 'Philter' 
       philter_note_text,philter_tags_dict = extractXML(philter_dir,philter_xml_file,philter_or_gold,verbose)

       if philter_tags_dict is not None:
          #print(philter_tags_dict)
          existing_phi = set() 
          for key, value in philter_tags_dict.items():
              # Note:  Value can be a list of like phi elements
              #               or a dictionary of the metadata about a phi element

              if isinstance(value, list):
                 for final_value in value:
                     text_start = final_value***REMOVED***"@start"***REMOVED***
                     text_end = final_value***REMOVED***"@end"***REMOVED***
                     philter_text = final_value***REMOVED***"@text"***REMOVED***
                     philter_phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                     if philter_phi_type == "DATE" or philter_phi_type == "Date":
                        existing_phi_new_val = check_existing_phi(filename,note_text, tags_dict, text_start, text_end)
                        if existing_phi_new_val:
                           #_type == "DATE" or phi_type == "Date":
                           #print(final_value***REMOVED***"@id"***REMOVED***)
                           existing_phi.add(final_value***REMOVED***"@id"***REMOVED***)
              else:
                  final_value = value
                  text = final_value***REMOVED***"@text"***REMOVED***
                  phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                  text_start = final_value***REMOVED***"@start"***REMOVED***
                  text_end = final_value***REMOVED***"@end"***REMOVED***
                  if phi_type == "DATE" or phi_type == "Date":
                     existing_phi_new_val = check_existing_phi(filename,note_text, tags_dict, text_start, text_end)
                     if existing_phi_new_val:
                        existing_phi.add(final_value***REMOVED***"@id"***REMOVED***)
          #print(existing_phi) 
          contents = ***REMOVED******REMOVED***
          found_new = False
          for key, value in philter_tags_dict.items():
              if isinstance(value, list):
                 for final_value in value:
                     if final_value***REMOVED***"@id"***REMOVED*** not in existing_phi:
                        found_new = True
                        #print(filename) 
                        #print(final_value***REMOVED***"@start"***REMOVED*** + '\t' + final_value***REMOVED***"@end"***REMOVED*** + '\t' + final_value***REMOVED***"@text"***REMOVED*** + "\t" + final_value***REMOVED***"@id"***REMOVED***)
                        contents = update_xml_tags(tags_dict,final_value)
              else:  
                  final_value = value        
                  if final_value***REMOVED***"@id"***REMOVED*** not in existing_phi:
                     found_new = True
                     contents = update_xml_tags(tags_dict,final_value)
          if found_new:
             with open(out_dir+'/'+filename, "w") as f:
                 contents_head = update_xml_head(note_text,tags_dict)
                 f.write(contents_head)
                 f.write("".join(contents))
                 contents_tail = update_xml_tail()
                 f.write(contents_tail)
                 #print("writing contents to: " + out_dir +'/' +  filename)
                 #print(contents)
               




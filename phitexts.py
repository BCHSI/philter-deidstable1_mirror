import os
import os.path
from chardet.universaldetector import UniversalDetector
import re
import json
from coordinate_map import CoordinateMap
from lxml import etree as ET
import xmltodict
from philter import Philter
from subs import Subs
import string
import pandas
import numpy
#from knownphi import Knownphi
from constants import *
from textmethods import get_clean, get_tokens
import time

import memory_profiler
#import sys
#sys.stdout = LogFile('memory_profile_log')

class Phitexts:
    """ container for texts, phi, attributes """

    def __init__(self, inputdir, xml=False):
        self.inputdir  = inputdir
        self.filenames = ***REMOVED******REMOVED***
        #notes text
        self.texts     = {}
        #coordinates of PHI
        self.coords    = {}
        #parts of speech
        self.pos = {}
        #list of PHI types
        self.types     = {}
        #normalized PHI
        self.norms     = {}
        #substituted PHI
        self.subs      = {}
        #de-id notes
        self.textsout  = {}
        #known phi
        #self.known_phi = {}
        if not xml:
           self._read_texts()
        self.subser = None
        self.filterer = None

    def _read_texts(self):
        if not self.inputdir:
            raise Exception("Input directory undefined: ", self.inputdir)

        for root, dirs, files in os.walk(self.inputdir):
            for filename in files:
                if (not filename.endswith("txt")) or 'meta_data' in filename:
                    continue

                filepath = os.path.join(root, filename)

                self.filenames.append(filepath)
                encoding = self._detect_encoding(filepath)
                fhandle = open(filepath, "r", encoding=encoding***REMOVED***'encoding'***REMOVED***,
                               errors='surrogateescape')
                self.texts***REMOVED***filepath***REMOVED*** = fhandle.read()
                fhandle.close()

    def _get_xml_tokens(self,string,text,start):
        tokens = {} 
        str_split = get_clean(string)
        offset = start
        for item in str_split:
            item_stripped = item.strip()
            if len(item_stripped) is 0:
                offset += len(item)
                continue
            token_start = text.find(item_stripped, offset)
            if token_start is -1:
               raise Exception("ERROR: cannot find token \"{0}\" in \"{1}\" starting at {2} in file {3}".format(item, string, offset))
            #print(item +"\t" + str(token_start) + "\t" + str(len(item_stripped)))
            token_stop = int(token_start) + int(len(item_stripped)) - 1 
            offset = token_stop + 1
            tokens.update({token_start:token_stop})
    
        return tokens

    def __read_xml_into_coordinateMap(self,inputdir):
        full_xml_map = {}
        phi_type_list = ***REMOVED***'Provider_Name','Date','DATE','Patient_Social_Security_Number','Email','Provider_Address_or_Location','Age','Name','OTHER'***REMOVED***
        phi_type_dict = {}
        for phi_type in phi_type_list:
            phi_type_dict***REMOVED***phi_type***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
        xml_texts = {}
        xml_filenames = ***REMOVED******REMOVED***

        if not inputdir:
            raise Exception("Input directory undefined: ", inputdir) 
        for filename in os.listdir(inputdir):
            xml_coordinate_map = {}
            if not filename.endswith("xml"):
               continue
            filepath = os.path.join(inputdir, filename)
            philter_or_gold = 'PhilterUCSF' 
            xml_filenames.append(filepath)
            encoding = self._detect_encoding(filepath)
            fhandle = open(filepath, "r", encoding=encoding***REMOVED***'encoding'***REMOVED***)
            input_xml = fhandle.read() 
            tree = ET.parse(filepath)
            root = tree.getroot()
            xmlstr = ET.tostring(root, encoding='utf8', method='xml')
            xml_texts***REMOVED***filepath***REMOVED*** = root.find('TEXT').text
            xml_dict = xmltodict.parse(xmlstr)***REMOVED***philter_or_gold***REMOVED***
            check_tags = root.find('TAGS')
                       
 
            if check_tags is not None:
               tags_dict = xml_dict***REMOVED***"TAGS"***REMOVED***            
            else:
               tags_dict = None
            if tags_dict is not None:
               for key, value in tags_dict.items():
              # Note:  Value can be a list of like phi elements
              #               or a dictionary of the metadata about a phi element
                   if isinstance(value, list):
                      for final_value in value:
                          text_start = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED*** 
                          text_end = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***
                          philter_text = final_value***REMOVED***"@text"***REMOVED***
                          xml_phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                          xml_coordinate_map.update(self._get_xml_tokens(philter_text, xml_texts***REMOVED***filepath***REMOVED***,int(text_start)))
                          #xml_coordinate_map***REMOVED***int(text_start)***REMOVED*** = int(text_end)  
                          if xml_phi_type not in phi_type_list:
                              phi_type_list.append(xml_phi_type)
                          for phi_type in phi_type_list:
                              if phi_type not in phi_type_dict:
                                 phi_type_dict***REMOVED***phi_type***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
                          
                          #phi_type_dict***REMOVED***xml_phi_type***REMOVED******REMOVED***0***REMOVED***.add_file(filename)
                          phi_type_dict***REMOVED***xml_phi_type***REMOVED******REMOVED***0***REMOVED***.add_extend(filepath,int(text_start),int(text_end))
                   else:
                       final_value = value
                       text = final_value***REMOVED***"@text"***REMOVED***
                       xml_phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                       text_start = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED***
                       text_end = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***
                       xml_coordinate_map.update(self._get_xml_tokens(text, xml_texts***REMOVED***filepath***REMOVED***,int(text_start)))
                       #xml_coordinate_map***REMOVED***int(text_start)***REMOVED*** = int(text_end)
                       if xml_phi_type not in phi_type_list:
                           phi_type_list.append(xml_phi_type)
                       for phi_type in phi_type_list:
                           if phi_type not in phi_type_dict:
                                 phi_type_dict***REMOVED***phi_type***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
                       #phi_type_dict***REMOVED***xml_phi_type***REMOVED******REMOVED***0***REMOVED***.add_file(filename)
                       phi_type_dict***REMOVED***xml_phi_type***REMOVED******REMOVED***0***REMOVED***.add_extend(filepath,int(text_start),int(text_end))
            full_xml_map***REMOVED***filepath***REMOVED*** = xml_coordinate_map
            fhandle.close()
        return full_xml_map, phi_type_dict, xml_texts, xml_filenames
       
    def _detect_encoding(self, fp):
        if not os.path.exists(fp):
            raise Exception("Filepath does not exist", fp)

        detector = UniversalDetector()
        with open(fp, "rb") as f:
            for line in f:
                detector.feed(line)
                if detector.done: 
                    break
            detector.close()
        return detector.result

    def detect_xml_phi(self):
        if self.coords:
           return
        self.coords, self.types, self.texts, self.filenames = self.__read_xml_into_coordinateMap(self.inputdir) 

    #@profile
    def detect_phi(self, filters="./configs/philter_alpha.json", namesprobefile=None, verbose=False):
        assert self.texts, "No texts defined"

        if self.coords:
            return
        if namesprobefile:
            philter_config = {
               "verbose":verbose,
               "run_eval":False,
               "finpath":self.inputdir,
               "filters":filters,
               "namesprobe":namesprobefile
            }

        else:
            philter_config = {
               "verbose":verbose,
               "run_eval":False,
               "finpath":self.inputdir,
               "filters":filters,
            }  

        self.filterer = Philter(philter_config)
        self.coords = self.filterer.map_coordinates()
        self.pos = self.filterer.pos_tags
    
    def detect_phi_types(self):
        assert self.texts, "No texts defined"
        assert self.coords, "No PHI coordinates defined"
        
        if self.types:
            return
        self.types = self.filterer.phi_type_dict
    

    '''    
    def detect_known_phi(self, knownphifile = "./data/knownphi_data.txt"):
        assert self.coords, "No PHI coordinates defined"
        assert self.texts, "No texts defined"
        assert self.types, "No PHI types defined"

        self.knownphi = Knownphi(knownphifile, self.coords, self.texts, self.types,self.pos)
        self.coords, self.types, self.known_phi = self.knownphi.update_coordinatemap()
    '''

    def normalize_phi(self):
        assert self.texts, "No texts defined"
        assert self.coords, "No PHI coordinates defined"
        assert self.types, "No PHI types defined"

        if self.norms:
            return

        # TODO: get normalized version for each detected phi
        # 1) get phi text given coords
        # 2) interpet/normalize phi given type

        for phi_type in self.types.keys():
            self.norms***REMOVED***phi_type***REMOVED*** = {}
        for phi_type in self.types.keys():
            if phi_type == "DATE" or phi_type == "Date":
                for filename, start, end in self.types***REMOVED***phi_type***REMOVED******REMOVED***0***REMOVED***.scan():
                    token = self.texts***REMOVED***filename***REMOVED******REMOVED***start:end***REMOVED***
                    normalized_token = Subs.parse_date(token)
                    self.norms***REMOVED***phi_type***REMOVED******REMOVED***(filename, start)***REMOVED*** = (normalized_token,
                                                               end)
            else:
                continue

        # TODO: what do we do when phi could not be interpreted?
        # e.g. change phi type to OTHER?
        # or scramble?
        # or use self.norms="unknown <type>" with <type>=self.types

        # Note: see also surrogator.shift_dates(), surrogator.parse_and_shift_date(), parse_date_ranges(), replace_other_surrogate()
        
    def substitute_phi(self, look_up_table_path = None):
        assert self.norms, "No normalized PHI defined"
        
        if self.subs:
            return

        self.subser = Subs(look_up_table_path)

        for phi_type in self.norms.keys():
            if phi_type == "DATE" or phi_type == "Date":
                if __debug__: nodateshiftlist = ***REMOVED******REMOVED***
                for filename, start in self.norms***REMOVED***phi_type***REMOVED***:
                    note_key_ucsf = os.path.splitext(os.path.basename(filename).strip('0'))***REMOVED***0***REMOVED***.replace("_utf8","").replace(".txt","").replace(".xml","")
                    if not self.subser.has_shift_amount(note_key_ucsf):
                        if __debug__:
                            if filename not in nodateshiftlist:
                                print("WARNING: no date shift found for: "
                                      + filename)
                                nodateshiftlist.append(filename)
                        continue
                    
                    normalized_token = self.norms***REMOVED***phi_type***REMOVED******REMOVED***filename, start***REMOVED******REMOVED***0***REMOVED***
                    end = self.norms***REMOVED***phi_type***REMOVED******REMOVED***filename, start***REMOVED******REMOVED***1***REMOVED***

                    # Added for eval
                    if normalized_token is None:
                        # self.eval_table***REMOVED***filename***REMOVED******REMOVED***start***REMOVED***.update({'sub':None})
                        continue
                    
                    shifted_date = self.subser.shift_date_pid(normalized_token,
                                                              note_key_ucsf)

                    if shifted_date is None:
                        if __debug__: print("WARNING: cannot shift date "
                                            + normalized_token.get_raw_string()
                                            + " in: " + filename)
                        continue
                    
                    substitute_token = self.subser.date_to_string(shifted_date)
                    # self.eval_table***REMOVED***filename***REMOVED******REMOVED***start***REMOVED***.update({'sub':substitute_token})
                    self.subs***REMOVED***(filename, start)***REMOVED*** = (substitute_token, end)
            else:
                continue


    def transform(self):
        assert self.texts, "No texts defined"

        if not self.coords:
            self.textsout = self.texts
            print("WARNING: No PHI coordinates defined: nothing to transform!")
        #Subs may be empty in the case where we do not have any date shifts to perform.
        #else:
            #assert self.subs, "No surrogated PHI defined"
                
        if self.textsout:
            return

        # TODO: apply self.subs to original text using self.coords
        for filename in self.filenames:
            
            last_marker = 0
            #current_chunk = ***REMOVED******REMOVED***
            #punctuation_matcher = re.compile(r"***REMOVED***^a-zA-Z0-9****REMOVED***")
            txt = self.texts***REMOVED***filename***REMOVED***
            exclude_dict = self.coords***REMOVED***filename***REMOVED***
            #read the text by character, any non-punc non-overlaps will be replaced
            contents = ***REMOVED******REMOVED***
            #print(filename)
            #print(exclude_dict)
            for i in range(0, len(txt)):

                if i < last_marker:
                    continue
                
                if i in exclude_dict:
                    start,stop = i, exclude_dict***REMOVED***i***REMOVED***
                    if (filename, start) in self.subs:
                        substitute_token = self.subs***REMOVED***filename, start***REMOVED******REMOVED***0***REMOVED***
                        end = self.subs***REMOVED***filename, start***REMOVED******REMOVED***1***REMOVED***
                        contents.append(substitute_token)
                        last_marker = end
                    else:
                        contents.append("*****")
                        last_marker = stop
                    
                else:
                    contents.append(txt***REMOVED***i***REMOVED***)

            self.textsout***REMOVED***filename***REMOVED*** =  "".join(contents)
    
    def _get_obscured_texts(self, symbol='*'):
        assert self.texts, "No texts defined"

        if not self.coords:
            texts_obscured = self.texts
            print("WARNING: No PHI coordinates defined: nothing to obscure!")
            return texts_obscured

        texts_obscured = {}
        for filename in self.filenames:

            txt = self.texts***REMOVED***filename***REMOVED***
            exclude_dict = self.coords***REMOVED***filename***REMOVED***

            #read the text by character, any non-punc non-overlaps will be replaced
            contents = ***REMOVED******REMOVED***
            for i in range(0, len(txt)):     
                if i in exclude_dict:
                    contents.append(symbol)    
                else:
                    contents.append(txt***REMOVED***i***REMOVED***)

            texts_obscured***REMOVED***filename***REMOVED*** =  "".join(contents)

        return texts_obscured

    def save(self, outputdir, suf="_subs", ext="txt",
             use_deid_note_key=False, create_subdirs=False):
        assert self.textsout, "Cannot save text: output not ready"
        assert outputdir, "Cannot save text: output directory undefined"

        for filename in self.filenames:
            fbase = os.path.splitext(os.path.basename(filename))***REMOVED***0***REMOVED***
            if use_deid_note_key: # name files according to deid note key
                note_key_ucsf = fbase.lstrip('0').replace("_utf8","").replace(".xml","").replace(".txt","")
                if not self.subser.has_deid_note_key(note_key_ucsf):
                    if __debug__: print("WARNING: no deid note key found for "
                                        + filename)
                    continue
                fbase = self.subser.get_deid_note_key(note_key_ucsf)
            if create_subdirs: # assume outputdir is parent and create subdirs
                               # from 14 hexadec digits long deid note keys
                duo_1 = fbase***REMOVED***:2***REMOVED***
                trio_2 = fbase***REMOVED***2:5***REMOVED***
                trio_3 = fbase***REMOVED***5:8***REMOVED***
                trio_4 = fbase***REMOVED***8:11***REMOVED***
                fbase = os.path.join(duo_1, trio_2, trio_3, trio_4, fbase)
            filepath = os.path.join(outputdir, fbase + suf + "." + ext)
            with open(filepath, "w", encoding='utf-8',
                      errors='surrogateescape') as fhandle:
                fhandle.write(self.textsout***REMOVED***filename***REMOVED***)
    
    def print_log(self, output_dir, xml):
        log_dir = os.path.join(output_dir, 'log/')

        failed_dates_file = os.path.join(log_dir, 'failed_dates.json')
        date_table_file = os.path.join(log_dir, 'parsed_dates.json')
        phi_count_file = os.path.join(log_dir, 'phi_count.log')
        phi_marked_file = os.path.join(log_dir, 'phi_marked.json')
        batch_summary_file = os.path.join(log_dir, 'batch_summary.log')
        #known_phi_file = os.path.join(log_dir,'known_phi.log')
        #Path to csv summary of all files
        csv_summary_filepath = os.path.join(log_dir,
                                            'detailed_batch_summary.csv')

        eval_table = {}
        failed_date = {}
        phi_table = {}
        parse_info = {}
        if 'DATE' in self.types:
            phi_type = 'DATE'
        elif 'Date' in self.types:
            phi_type = 'Date'

        # Per-batch logs
        if os.path.isdir(log_dir):
            pass
        else:
            os.makedirs(log_dir)
        

        # Write to file of raw dates, parsed dates and substituted dates
        num_failed = 0
        num_parsed = 0
        # with open(date_table, 'w') as f_parsed, open(failed_dates, 'w') as f_failed:
            # f_parsed.write('\t'.join(***REMOVED***'filename', 'start', 'end', 'raw', 'normalized', 'substituted'***REMOVED***))
            # f_parsed.write('\n')
            # f_failed.write('\t'.join(***REMOVED***'filename', 'start', 'end', 'raw'***REMOVED***))
            # f_failed.write('\n')
        for filename, start, end in self.types***REMOVED***phi_type***REMOVED******REMOVED***0***REMOVED***.scan():
            raw = self.texts***REMOVED***filename***REMOVED******REMOVED***start:end***REMOVED***
            normalized_date = self.norms***REMOVED***phi_type***REMOVED******REMOVED***(filename,start)***REMOVED******REMOVED***0***REMOVED***
            
            if filename not in parse_info:
                parse_info***REMOVED***filename***REMOVED*** = {'success_norm':0,'fail_norm':0,
                                        'success_sub':0,'fail_sub':0}
            if filename not in eval_table:
                eval_table***REMOVED***filename***REMOVED*** = ***REMOVED******REMOVED***

            if normalized_date is not None:
                # Add 1 to successfully normalized dates
                num_parsed += 1
                parse_info***REMOVED***filename***REMOVED******REMOVED***'success_norm'***REMOVED*** += 1
                
                normalized_token = self.subser.date_to_string(normalized_date)
                note_key_ucsf = os.path.splitext(os.path.basename(filename).strip('0'))***REMOVED***0***REMOVED***
                
                # Successfully surrogated:
                if (filename, start) in self.subs:
                    # Add 1 to successfuly surrogated dates:	
                     sub = self.subs***REMOVED***(filename,start)***REMOVED******REMOVED***0***REMOVED***
                     parse_info***REMOVED***filename***REMOVED******REMOVED***'success_sub'***REMOVED*** += 1
                # Unsuccessfully surrogated:
                else:
                    # Add 1 to unsuccessfuly surrogated dates:
                     sub = None	
                     parse_info***REMOVED***filename***REMOVED******REMOVED***'fail_sub'***REMOVED*** += 1

                eval_table***REMOVED***filename***REMOVED***.append({'start':start, 'end':end,
                                             'raw': raw,
                                             'normalized': normalized_token,
                                             'sub': sub})
                    # f_parsed.write('\t'.join(***REMOVED***filename, str(start), str(end), raw, normalized_token, sub***REMOVED***))
                    # f_parsed.write('\n')
            else:
                # Add 1 to unsuccessfuly normazlied dates:
                num_failed += 1
                parse_info***REMOVED***filename***REMOVED******REMOVED***'fail_norm'***REMOVED*** += 1
                    # f_failed.write('\t'.join(***REMOVED***filename, str(start), str(end), raw.strip('\n')***REMOVED***))
                    # f_failed.write('\n')
                if filename not in failed_date:
                        failed_date***REMOVED***filename***REMOVED*** = ***REMOVED******REMOVED***
                failed_date***REMOVED***filename***REMOVED***.append({'start':start, 'end':end,        
                                              'raw': raw})

        if __debug__:
            print ('Successfully parsed: ' + str(num_parsed) + ' dates.')
            print ('Failed to parse: ' + str(num_failed) + ' dates.')
                
        # Count by phi_type, record PHI marked
        phi_counter = {}
        marked_phi = {}
        with open(phi_count_file,'w') as f_count:
            # f_marked.write('\t'.join(***REMOVED***'filename', 'start', 'end', 'word', 'phi_type', 'category'***REMOVED***))
            # f_marked.write('\n')

            for phi_type in self.types:
                for filename, start, end in self.types***REMOVED***phi_type***REMOVED******REMOVED***0***REMOVED***.scan():
                    if filename not in phi_table:
                        phi_table***REMOVED***filename***REMOVED*** = ***REMOVED******REMOVED***
                    word = self.texts***REMOVED***filename***REMOVED******REMOVED***start:end***REMOVED***
                    phi_table***REMOVED***filename***REMOVED***.append({'start': start, 'end': end,
                                                'word': word, 'type': phi_type})

                    if phi_type not in phi_counter:
                        phi_counter***REMOVED***phi_type***REMOVED*** = 0
                    phi_counter***REMOVED***phi_type***REMOVED*** += 1

                    
                    # f_marked.write('\t'.join(***REMOVED***filename, str(start), str(end), word, phi_type***REMOVED***))
                    # f_marked.write('\n')

            for phi_type in phi_counter:
                f_count.write('\t'.join(***REMOVED***phi_type, str(phi_counter***REMOVED***phi_type***REMOVED***)***REMOVED***))
                f_count.write('\n')

        # dump to json
        with open (failed_dates_file, 'w') as f:
            json.dump(failed_date, f)
        with open(date_table_file, 'w') as f:
            json.dump(eval_table, f)
        with open(phi_marked_file, 'w') as f:
            json.dump(phi_table, f)
        '''
        if kp: 
           with open(known_phi_file,'w') as f:
                for filename in self.known_phi:
                    known_phi_dict = self.known_phi***REMOVED***filename***REMOVED***
                    for i in known_phi_dict:
                        start = i
                        stop, knownphi, context, pos = known_phi_dict***REMOVED***i***REMOVED***
                        f.write(filename+"\t"+str(start) +"\t" + str(stop) + "\t" + knownphi + "\t" + context + "\t" + pos + "\n") 
        '''
        # If the summary csv file doesn't exist yet, create it and add file headers
        # Csv summary is one directory above all input directories
        if not os.path.isfile(csv_summary_filepath):
            with open(csv_summary_filepath,'w') as f:
                file_header = 'filename'+','+'file_size'+','+'total_tokens'+','+'phi_tokens'+','+'successfully_normalized'+','+'failed_normalized'+','+'successfully_surrogated'+','+'failed_surrogated'+'\n'
                f.write(file_header)

        summary_info = {'filesize':***REMOVED******REMOVED***,'total_tokens':***REMOVED******REMOVED***,'phi_tokens':***REMOVED******REMOVED***,'successful_normalized':***REMOVED******REMOVED***,'failed_normalized':***REMOVED******REMOVED***,'successful_surrogated':***REMOVED******REMOVED***,'failed_surrogated':***REMOVED******REMOVED***}
        
        texts_obscured = self._get_obscured_texts() # needed for phi_tokens
                
        ### CSV of summary per file ####
        # 1. Filename
        for filename in self.filenames:

            # File size in bytes
            filesize = os.path.getsize(filename)
            
            if xml: 
               total_tokens = len(get_clean(self.texts***REMOVED***filename***REMOVED***)) 
               phi_tokens = len(self.coords***REMOVED***filename***REMOVED***)
            else:
               # Number of total tokens
               total_tokens = self.filterer.cleaned***REMOVED***filename***REMOVED******REMOVED***1***REMOVED***
               # Number of PHI tokens
               phi_tokens = self.filterer.get_clean_filtered(filename,
                                                             texts_obscured***REMOVED***filename***REMOVED***)***REMOVED***1***REMOVED***
            
            successful_normalized = 0
            failed_normalized = 0
            successful_surrogated = 0
            failed_surrogated = 0

            if filename in parse_info:
                # Successfully normalized dates
                successful_normalized = parse_info***REMOVED***filename***REMOVED******REMOVED***'success_norm'***REMOVED***
                # Unsuccessfully normalized dates
                failed_normalized = parse_info***REMOVED***filename***REMOVED******REMOVED***'fail_norm'***REMOVED***
                # Successfully normalized dates
                successful_surrogated = parse_info***REMOVED***filename***REMOVED******REMOVED***'success_sub'***REMOVED***
                # Unsuccessfully normalized dates
                failed_surrogated = parse_info***REMOVED***filename***REMOVED******REMOVED***'fail_sub'***REMOVED***
            
            # Add to master list for all files          
            with open(csv_summary_filepath,'a') as f:
                new_line = filename + ',' + str(filesize) + ',' + str(total_tokens) + ',' + str(phi_tokens) + ',' + str(successful_normalized) + ',' + str(failed_normalized) + ',' + str(successful_surrogated) + ',' + str(failed_surrogated) + '\n'
                f.write(new_line)
                     
            summary_info***REMOVED***'filesize'***REMOVED***.append(filesize)
            summary_info***REMOVED***'total_tokens'***REMOVED***.append(total_tokens)
            summary_info***REMOVED***'phi_tokens'***REMOVED***.append(phi_tokens)
            summary_info***REMOVED***'successful_normalized'***REMOVED***.append(successful_normalized)
            summary_info***REMOVED***'failed_normalized'***REMOVED***.append(failed_normalized)
            summary_info***REMOVED***'successful_surrogated'***REMOVED***.append(successful_surrogated)
            summary_info***REMOVED***'failed_surrogated'***REMOVED***.append(failed_surrogated)
        
        # Summarize current batch
        # Batch size (all)
        number_of_notes = len(summary_info)

        # File size
        total_kb_processed = sum(summary_info***REMOVED***'filesize'***REMOVED***)/1000
        median_file_size = numpy.median(summary_info***REMOVED***'filesize'***REMOVED***)
        q2pt5_size,q97pt5_size = numpy.percentile(summary_info***REMOVED***'filesize'***REMOVED***,***REMOVED***2.5,97.5***REMOVED***)

        # Total tokens
        total_tokens = numpy.sum(summary_info***REMOVED***'total_tokens'***REMOVED***)
        median_tokens = numpy.median(summary_info***REMOVED***'total_tokens'***REMOVED***)
        q2pt5_tokens,q97pt5_tokens = numpy.percentile(summary_info***REMOVED***'total_tokens'***REMOVED***,***REMOVED***2.5,97.5***REMOVED***)

        # Total PHI tokens
        total_phi_tokens = numpy.sum(summary_info***REMOVED***'phi_tokens'***REMOVED***)
        median_phi_tokens = numpy.median(summary_info***REMOVED***'phi_tokens'***REMOVED***)
        q2pt5_phi_tokens,q97pt5_phi_tokens = numpy.percentile(summary_info***REMOVED***'phi_tokens'***REMOVED***,***REMOVED***2.5,97.5***REMOVED***)
        # Normalization
        successful_normalization = sum(summary_info***REMOVED***'successful_normalized'***REMOVED***)
        failed_normalization = sum(summary_info***REMOVED***'failed_normalized'***REMOVED***)

        # Surrogation
        successful_surrogation = sum(summary_info***REMOVED***'successful_surrogated'***REMOVED***)
        failed_surrogation = sum(summary_info***REMOVED***'failed_surrogated'***REMOVED***)

        # Create text summary for the current batch
        with open(batch_summary_file, "w") as f:
            f.write("TOTAL NOTES PROCESSED: " + str(number_of_notes) + '\n')
            f.write("TOTAL KB PROCESSED: " + str("%.2f"%total_kb_processed)
                    + '\n')
            f.write("TOTAL TOKENS PROCESSED: " + str(total_tokens) + '\n')
            f.write("TOTAL PHI TOKENS PROCESSED: " + str(total_phi_tokens)
                    + '\n')
            f.write('\n')
            f.write("MEDIAN FILESIZE (BYTES): " + str(median_file_size)
                    + " (95% Percentile: " + str("%.2f"%q2pt5_size) + '-'
                    + str("%.2f"%q97pt5_size) + ')' + '\n')
            f.write("MEDIAN TOKENS PER NOTE: " + str(median_tokens)
                    + " (95% Percentile: " + str("%.2f"%q2pt5_tokens) + '-'
                    + str("%.2f"%q97pt5_tokens) + ')' + '\n')
            f.write("MEDIAN PHI TOKENS PER NOTE: " + str(median_phi_tokens)
                    + " (95% Percentile: " + str("%.2f"%q2pt5_phi_tokens) + '-'
                    + str("%.2f"%q97pt5_phi_tokens) + ')' + '\n')
            f.write('\n')
            f.write("DATES SUCCESSFULLY NORMALIZED: "
                    + str(successful_normalization) + '\n')
            f.write("DATES FAILED TO NORMALIZE: " + str(failed_normalization)
                    + '\n')
            f.write("DATES SUCCESSFULLY SURROGATED: "
                    + str(successful_surrogation) + '\n')
            f.write("DATES FAILED TO SURROGATE: " + str(failed_surrogation)
                    + '\n')   
        

        # Todo: add PHI type counts to summary
        # Name PHI
        # Date PHI
        # Age>=90 PHI
        # Contact PHI
        # Location PHI
        # ID PHI
        # Other PHI

    def _get_phi_type(self, filename, start, stop):
        for phi_type in self.types.keys():
            for begin,end in self.types***REMOVED***phi_type***REMOVED******REMOVED***0***REMOVED***.filecoords(filename):
                if start == begin: # TODO: extend this to an include match?
                    return phi_type
        return None

    # creates dictionary with tokens tagged by Philter
    def _tokenize_philter_phi(self, filename):
        exclude_dict = self.coords***REMOVED***filename***REMOVED***
        updated_dict = {}
        for i in exclude_dict:
            start, end = i, exclude_dict***REMOVED***i***REMOVED***
            phi_type = self._get_phi_type(filename, start, end)
            word = self.texts***REMOVED***filename***REMOVED******REMOVED***start:end***REMOVED***
            
            try:
                tokens = get_tokens(word)
            except Exception as err:
                raise Exception("ERROR: cannot get tokens in \"{0}\" starting at {1} in file {2}: {3}".format(word, start, filename, err))
            
            for tstart in tokens:
                token_start = tstart + start
                token_stop = tokens***REMOVED***tstart***REMOVED******REMOVED***0***REMOVED*** + start
                token = tokens***REMOVED***tstart***REMOVED******REMOVED***1***REMOVED***
                updated_dict.update({token_start:***REMOVED***token_stop, phi_type, token***REMOVED***})
        return updated_dict

    # returns the left, middle and right parts of possible overlaps
    def _get_sub_tokens(self, token1, token2):
        
        if (token1***REMOVED***'stop'***REMOVED*** < token2***REMOVED***'start'***REMOVED***
            or token1***REMOVED***'start'***REMOVED*** > token2***REMOVED***'stop'***REMOVED***): # tokens do not overlap
            return None

        subtokens1 = {}
        subtokens2 = {}
        left = {}
        middle = {}
        right = {}

        tk1_has_type = True if 'phitype' in token1 else False
        tk2_has_type = True if 'phitype' in token2 else False

        # looks for dangling beginning
        if token1***REMOVED***'start'***REMOVED*** < token2***REMOVED***'start'***REMOVED***: # token1 has dangling beginning
            left***REMOVED***'start'***REMOVED*** = token1***REMOVED***'start'***REMOVED***
            left***REMOVED***'length'***REMOVED*** = token2***REMOVED***'start'***REMOVED*** - token1***REMOVED***'start'***REMOVED***
            left***REMOVED***'stop'***REMOVED*** = token2***REMOVED***'start'***REMOVED*** - 1
            left***REMOVED***'token'***REMOVED*** = token1***REMOVED***'token'***REMOVED******REMOVED***0:left***REMOVED***'length'***REMOVED******REMOVED***
            if tk1_has_type:
                left***REMOVED***'phitype'***REMOVED*** = token1***REMOVED***'phitype'***REMOVED***
                subtokens1.update({left***REMOVED***'start'***REMOVED***:***REMOVED***left***REMOVED***'stop'***REMOVED***, left***REMOVED***'phitype'***REMOVED***,
                                                  left***REMOVED***'token'***REMOVED******REMOVED***})
            else:
                subtokens1.update({left***REMOVED***'start'***REMOVED***:***REMOVED***left***REMOVED***'stop'***REMOVED***, left***REMOVED***'token'***REMOVED******REMOVED***})
        elif token1***REMOVED***'start'***REMOVED*** > token2***REMOVED***'start'***REMOVED***: # token2 has dangling beginning
            left***REMOVED***'start'***REMOVED*** = token2***REMOVED***'start'***REMOVED***
            left***REMOVED***'length'***REMOVED*** = token1***REMOVED***'start'***REMOVED*** - token2***REMOVED***'start'***REMOVED***
            left***REMOVED***'stop'***REMOVED*** = token1***REMOVED***'start'***REMOVED*** - 1
            left***REMOVED***'token'***REMOVED*** = token2***REMOVED***'token'***REMOVED******REMOVED***0:left***REMOVED***'length'***REMOVED******REMOVED***
            if tk2_has_type:
                left***REMOVED***'phitype'***REMOVED*** = token2***REMOVED***'phitype'***REMOVED***
                subtokens2.update({left***REMOVED***'start'***REMOVED***:***REMOVED***left***REMOVED***'stop'***REMOVED***, left***REMOVED***'phitype'***REMOVED***,
                                                  left***REMOVED***'token'***REMOVED******REMOVED***})
            else:
                subtokens2.update({left***REMOVED***'start'***REMOVED***:***REMOVED***left***REMOVED***'stop'***REMOVED***, left***REMOVED***'token'***REMOVED******REMOVED***})
        else: # tokens have the same start
            left***REMOVED***'start'***REMOVED*** = token1***REMOVED***'start'***REMOVED***
            left***REMOVED***'length'***REMOVED*** = 0
            left***REMOVED***'stop'***REMOVED*** = token1***REMOVED***'start'***REMOVED*** - 1
            left***REMOVED***'phitype'***REMOVED*** = None
            left***REMOVED***'token'***REMOVED*** = ""

        # looks for dangling end
        if token1***REMOVED***'stop'***REMOVED*** < token2***REMOVED***'stop'***REMOVED***: # token2 has dangling end
            right***REMOVED***'start'***REMOVED*** = token1***REMOVED***'stop'***REMOVED*** + 1
            right***REMOVED***'length'***REMOVED*** = token2***REMOVED***'stop'***REMOVED*** - token1***REMOVED***'stop'***REMOVED***
            right***REMOVED***'stop'***REMOVED*** = token2***REMOVED***'stop'***REMOVED***
            right***REMOVED***'token'***REMOVED*** = token2***REMOVED***'token'***REMOVED******REMOVED***-right***REMOVED***'length'***REMOVED***:***REMOVED***
            if tk2_has_type:
                right***REMOVED***'phitype'***REMOVED*** = token2***REMOVED***'phitype'***REMOVED***
                subtokens2.update({right***REMOVED***'start'***REMOVED***:***REMOVED***right***REMOVED***'stop'***REMOVED***,
                                                   right***REMOVED***'phitype'***REMOVED***,
                                                   right***REMOVED***'token'***REMOVED******REMOVED***})
            else:
                subtokens2.update({right***REMOVED***'start'***REMOVED***:***REMOVED***right***REMOVED***'stop'***REMOVED***,
                                                   right***REMOVED***'token'***REMOVED******REMOVED***})
        elif token2***REMOVED***'stop'***REMOVED*** < token1***REMOVED***'stop'***REMOVED***: # token1 has dangling end
            right***REMOVED***'start'***REMOVED*** = token2***REMOVED***'stop'***REMOVED*** + 1
            right***REMOVED***'length'***REMOVED*** = token1***REMOVED***'stop'***REMOVED*** - token2***REMOVED***'stop'***REMOVED***
            right***REMOVED***'stop'***REMOVED*** = token1***REMOVED***'stop'***REMOVED***
            right***REMOVED***'token'***REMOVED*** = token1***REMOVED***'token'***REMOVED******REMOVED***-right***REMOVED***'length'***REMOVED***:***REMOVED***
            if tk1_has_type:
                right***REMOVED***'phitype'***REMOVED*** = token1***REMOVED***'phitype'***REMOVED***
                subtokens1.update({right***REMOVED***'start'***REMOVED***:***REMOVED***right***REMOVED***'stop'***REMOVED***,
                                                   right***REMOVED***'phitype'***REMOVED***,
                                                   right***REMOVED***'token'***REMOVED******REMOVED***})
            else:
                subtokens1.update({right***REMOVED***'start'***REMOVED***:***REMOVED***right***REMOVED***'stop'***REMOVED***,
                                                   right***REMOVED***'token'***REMOVED******REMOVED***})
        else: # tokens have the same end
            right***REMOVED***'start'***REMOVED*** = token1***REMOVED***'stop'***REMOVED*** + 1
            right***REMOVED***'length'***REMOVED*** = 0
            right***REMOVED***'stop'***REMOVED*** = token1***REMOVED***'stop'***REMOVED***
            right***REMOVED***'phitype'***REMOVED*** = None
            right***REMOVED***'token'***REMOVED*** = ""

        # looks for middle portion
        middle***REMOVED***'start'***REMOVED*** = left***REMOVED***'stop'***REMOVED*** + 1
        middle***REMOVED***'stop'***REMOVED*** = right***REMOVED***'start'***REMOVED*** - 1
        middle***REMOVED***'length'***REMOVED*** = middle***REMOVED***'stop'***REMOVED*** - middle***REMOVED***'start'***REMOVED*** + 1
        if left***REMOVED***'start'***REMOVED*** == token1***REMOVED***'start'***REMOVED***:
            middle***REMOVED***'token'***REMOVED*** = token1***REMOVED***'token'***REMOVED******REMOVED***left***REMOVED***'length'***REMOVED***:left***REMOVED***'length'***REMOVED***+middle***REMOVED***'length'***REMOVED******REMOVED***
            othertoken = token2
        else:
            middle***REMOVED***'token'***REMOVED*** = token2***REMOVED***'token'***REMOVED******REMOVED***left***REMOVED***'length'***REMOVED***:left***REMOVED***'length'***REMOVED***+middle***REMOVED***'length'***REMOVED******REMOVED***
            othertoken = token1
        if not middle***REMOVED***'token'***REMOVED*** == othertoken***REMOVED***'token'***REMOVED******REMOVED***0:middle***REMOVED***'length'***REMOVED******REMOVED***:
            if __debug__: print(str(left),str(middle),str(right))
            raise Exception("ERROR: string mismatch: \"" + middle***REMOVED***'token'***REMOVED***
                            + "\" != \""
                            +  othertoken***REMOVED***'token'***REMOVED******REMOVED***0:middle***REMOVED***'length'***REMOVED******REMOVED***
                            + "\" in tokens: \""
                            + token1***REMOVED***'token'***REMOVED*** + "\" (" + str(token1***REMOVED***'start'***REMOVED***)
                            + "-" + str(token1***REMOVED***'stop'***REMOVED***) + ") and \""
                            + token2***REMOVED***'token'***REMOVED*** + "\" (" + str(token2***REMOVED***'start'***REMOVED***)
                            + "-" + str(token2***REMOVED***'stop'***REMOVED***) + ")")

        if tk1_has_type:
            middle***REMOVED***'phitype'***REMOVED*** = token1***REMOVED***'phitype'***REMOVED***
            subtokens1.update({middle***REMOVED***'start'***REMOVED***:***REMOVED***middle***REMOVED***'stop'***REMOVED***,
                                                middle***REMOVED***'phitype'***REMOVED***,
                                                middle***REMOVED***'token'***REMOVED******REMOVED***})
        else:
            subtokens1.update({middle***REMOVED***'start'***REMOVED***:***REMOVED***middle***REMOVED***'stop'***REMOVED***,
                                                middle***REMOVED***'token'***REMOVED******REMOVED***})
        if tk2_has_type:
            middle***REMOVED***'phitype'***REMOVED*** = token2***REMOVED***'phitype'***REMOVED***
            subtokens2.update({middle***REMOVED***'start'***REMOVED***:***REMOVED***middle***REMOVED***'stop'***REMOVED***,
                                                middle***REMOVED***'phitype'***REMOVED***,
                                                middle***REMOVED***'token'***REMOVED******REMOVED***})
        else:
            subtokens2.update({middle***REMOVED***'start'***REMOVED***:***REMOVED***middle***REMOVED***'stop'***REMOVED***,
                                                middle***REMOVED***'token'***REMOVED******REMOVED***})

        return subtokens1, subtokens2
    
    # creates a dictionary of tokens found in XML files
    def _get_gold_phi(self, anno_dir):
        gold_phi = {}
        for root, dirs, files in os.walk(anno_dir):
            for filename in files:
                if not filename.endswith("xml"):
                    continue
                #print("root: " + str(root) + " filename: " + str(filename))
                filepath = os.path.join(root, filename)
                # change here: what will the input format be?
                file_id = self.inputdir + filename.split('.')***REMOVED***0***REMOVED*** + '.txt'
                tree = ET.parse(filepath)
                rt = tree.getroot()
                xmlstr = ET.tostring(rt, encoding='utf8', method='xml')
                xml_dict = xmltodict.parse(xmlstr)***REMOVED***'PhilterUCSF'***REMOVED***
                check_tags = rt.find('TAGS')
                full_text = xml_dict***REMOVED***"TEXT"***REMOVED***
                if check_tags is not None:
                   tags_dict = xml_dict***REMOVED***"TAGS"***REMOVED***
                else:
                   tags_dict = None

                if file_id  not in gold_phi:
                   gold_phi***REMOVED***file_id***REMOVED*** = {}
                # the existence of puncs in text makes the end index inaccurate - only use start index as the key
                if tags_dict is not None: 

                    for key, value in tags_dict.items():
                        if not isinstance(value, list):
                            value = ***REMOVED***value***REMOVED***
                        for final_value in value:
                            start = int(final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED***)
                            end = int(final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***)
                            text = final_value***REMOVED***"@text"***REMOVED***
                            phi_type = final_value***REMOVED***"@TYPE"***REMOVED***

                            try:
                                tokens = get_tokens(text)
                            except Exception as err:
                                raise Exception("EROOR: cannot get tokens in \"{0}\" starting at {1} in file {2}: {3}".format(text, start, filename, err))
            
                            for tstart in tokens:
                                token_start = tstart + start
                                token_stop = tokens***REMOVED***tstart***REMOVED******REMOVED***0***REMOVED*** + start
                                token = tokens***REMOVED***tstart***REMOVED******REMOVED***1***REMOVED***
                                gold_phi***REMOVED***file_id***REMOVED***.update({token_start:***REMOVED***token_stop,
                                                                       phi_type,
                                                                       token***REMOVED***})
        return gold_phi

    # creates a dictionary of tokens found in Philter
    def _get_philter_phi(self, filenames):
        philter_phi = {}
        for filename in filenames:
            philter_phi***REMOVED***filename***REMOVED*** = self._tokenize_philter_phi(filename)
        return philter_phi

    # subtokenizes gold and philter tokens with the respective other coords 
    def _update_with_sub_tokens(self, gold_phi, philter_phi):
        gold = {}
        philter = {}
        for filename in gold_phi:
            gphi = gold_phi***REMOVED***filename***REMOVED***.copy()
            pphi = philter_phi***REMOVED***filename***REMOVED***.copy()
            for gstart in gphi:
                gold***REMOVED***'start'***REMOVED*** = gstart
                gold***REMOVED***'stop'***REMOVED*** = gphi***REMOVED***gstart***REMOVED******REMOVED***0***REMOVED***
                gold***REMOVED***'phitype'***REMOVED*** = gphi***REMOVED***gstart***REMOVED******REMOVED***1***REMOVED***
                gold***REMOVED***'token'***REMOVED*** = gphi***REMOVED***gstart***REMOVED******REMOVED***2***REMOVED***
                for pstart in pphi:
                    philter***REMOVED***'start'***REMOVED*** = pstart
                    philter***REMOVED***'stop'***REMOVED*** = pphi***REMOVED***pstart***REMOVED******REMOVED***0***REMOVED***
                    philter***REMOVED***'phitype'***REMOVED*** = pphi***REMOVED***pstart***REMOVED******REMOVED***1***REMOVED***
                    philter***REMOVED***'token'***REMOVED*** = pphi***REMOVED***pstart***REMOVED******REMOVED***2***REMOVED***
                    subtokens = self._get_sub_tokens(gold, philter)
                    if subtokens is None:
                        continue
                    for st in subtokens***REMOVED***0***REMOVED***:
                        start = st
                        stop = subtokens***REMOVED***0***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                        phitype = subtokens***REMOVED***0***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                        token = subtokens***REMOVED***0***REMOVED******REMOVED***st***REMOVED******REMOVED***2***REMOVED***
                        gold_phi***REMOVED***filename***REMOVED***.update({start:***REMOVED***stop, phitype,
                                                          token***REMOVED***})
                    for st in subtokens***REMOVED***1***REMOVED***:
                        start = st
                        stop = subtokens***REMOVED***1***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                        phitype = subtokens***REMOVED***1***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                        token = subtokens***REMOVED***1***REMOVED******REMOVED***st***REMOVED******REMOVED***2***REMOVED***
                        philter_phi***REMOVED***filename***REMOVED***.update({start:***REMOVED***stop, phitype,
                                                             token***REMOVED***})

    # true positives (tokens in gold and philter)
    def _get_tp_dicts(self, gold_dicts, philter_dicts):
        tp_dicts = {}
        for filename in gold_dicts:
            tp_dicts***REMOVED***filename***REMOVED*** = {}
            keys = gold_dicts***REMOVED***filename***REMOVED***.keys() & philter_dicts***REMOVED***filename***REMOVED***.keys()
            for k in keys:
                tp_dicts***REMOVED***filename***REMOVED***.update({k:gold_dicts***REMOVED***filename***REMOVED******REMOVED***k***REMOVED***})
        return tp_dicts

    # false positives (tokens in philter but not in gold)
    def _get_fp_dicts(self, gold_dicts, philter_dicts):
        fp_dicts = {}
        for filename in gold_dicts:
            fp_dicts***REMOVED***filename***REMOVED*** = {}
            keys = philter_dicts***REMOVED***filename***REMOVED***.keys() - gold_dicts***REMOVED***filename***REMOVED***.keys()
            for k in keys:
                fp_dicts***REMOVED***filename***REMOVED***.update({k:philter_dicts***REMOVED***filename***REMOVED******REMOVED***k***REMOVED***})
        return fp_dicts

    # true negatives (tokens not tagged)
    def _get_tn_dicts(self, full_dicts, gold_dicts, philter_dicts):
        tn_dicts = {}
        for filename in gold_dicts:
            tn_dicts***REMOVED***filename***REMOVED*** = {}
            keys = (full_dicts***REMOVED***filename***REMOVED***.keys() - gold_dicts***REMOVED***filename***REMOVED***.keys()
                    - philter_dicts***REMOVED***filename***REMOVED***.keys())
            for k in keys:
                tn_dicts***REMOVED***filename***REMOVED***.update({k:full_dicts***REMOVED***filename***REMOVED******REMOVED***k***REMOVED***})
        return tn_dicts

    # false negatives (tokens in gold but not in philter)
    def _get_fn_dicts(self, gold_dicts, philter_dicts):
        fn_dicts = {}
        for filename in gold_dicts:
            fn_dicts***REMOVED***filename***REMOVED*** = {}
            keys = gold_dicts***REMOVED***filename***REMOVED***.keys() - philter_dicts***REMOVED***filename***REMOVED***.keys()
            for k in keys:
                fn_dicts***REMOVED***filename***REMOVED***.update({k:gold_dicts***REMOVED***filename***REMOVED******REMOVED***k***REMOVED***})
        return fn_dicts

    # subtokenizes full texts tokens with phi coordinates
    def _sub_tokenize(self, fulltext_dicts, phi_dicts):
        ftoken = {}
        phi = {}
        for filename in fulltext_dicts:
            ftdict = fulltext_dicts***REMOVED***filename***REMOVED***.copy()
            pdict = phi_dicts***REMOVED***filename***REMOVED***.copy()
            for fstart in ftdict:
                ftoken***REMOVED***'start'***REMOVED*** = fstart
                ftoken***REMOVED***'stop'***REMOVED*** = ftdict***REMOVED***fstart***REMOVED******REMOVED***0***REMOVED***
                ftoken***REMOVED***'token'***REMOVED*** = ftdict***REMOVED***fstart***REMOVED******REMOVED***1***REMOVED***
                for pstart in pdict:
                    phi***REMOVED***'start'***REMOVED*** = pstart
                    phi***REMOVED***'stop'***REMOVED*** = pdict***REMOVED***pstart***REMOVED******REMOVED***0***REMOVED***
                    phi***REMOVED***'token'***REMOVED*** = pdict***REMOVED***pstart***REMOVED******REMOVED***2***REMOVED***
                    subtokens = self._get_sub_tokens(ftoken, phi)
                    if subtokens is None:
                        continue
                    for st in subtokens***REMOVED***0***REMOVED***:
                        start = st
                        stop = subtokens***REMOVED***0***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                        token = subtokens***REMOVED***0***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                        fulltext_dicts***REMOVED***filename***REMOVED***.update({start:***REMOVED***stop, token***REMOVED***})

    # returns the tokenized full texts with subtokenization 
    def _get_fulltext_dicts(self, gold_dicts, philter_dicts):
        fulltext_dicts = {}
        for filename in gold_dicts:
            fulltext_dicts***REMOVED***filename***REMOVED*** = get_tokens(self.texts***REMOVED***filename***REMOVED***)
                
        self._sub_tokenize(fulltext_dicts, gold_dicts)
        self._sub_tokenize(fulltext_dicts, philter_dicts)
        
        return fulltext_dicts
                                          
    def eval(self, anno_dir, output_dir):
        print("Running eval") 
        eval_dir = os.path.join(output_dir, 'eval/')
        summary_file = os.path.join(eval_dir, 'summary.json')
        json_summary_by_file = os.path.join(eval_dir, 'summary_by_file.json')
        json_summary_by_category = os.path.join(eval_dir,
                                                'summary_by_category.json')
        if not os.path.isdir(eval_dir):
            os.makedirs(eval_dir)       


        text_fp_file = open(os.path.join(eval_dir,'fp.eval'),"w+")
        text_tp_file = open(os.path.join(eval_dir,'tp.eval'),"w+")
        text_fn_file = open(os.path.join(eval_dir,'fn.eval'),"w+")
        text_tn_file = open(os.path.join(eval_dir,'tn.eval'),"w+")

        # gathers full text tokens, gold and philter tokens
        gold_dicts = self._get_gold_phi(anno_dir)
        philter_dicts = self._get_philter_phi(gold_dicts.keys())
        self._update_with_sub_tokens(gold_dicts, philter_dicts)
        fulltext_dicts = self._get_fulltext_dicts(gold_dicts, philter_dicts)

        # our core eval metrics
        truepositives_dicts = self._get_tp_dicts(gold_dicts, philter_dicts)
        falsepositives_dicts = self._get_fp_dicts(gold_dicts, philter_dicts)
        truenegatives_dicts = self._get_tn_dicts(fulltext_dicts,
                                                 gold_dicts, philter_dicts)
        falsenegatives_dicts = self._get_fn_dicts(gold_dicts, philter_dicts)

        summary_by_category = {}
        summary_by_file = {}
        total_tp = 0
        total_fp = 0
        total_tn = 0
        total_fn = 0
        total_ctp = 0
        total_cfp = 0
        total_ctn = 0
        total_cfn = 0
        for filename in self.filenames:
            if filename not in summary_by_file:
                summary_by_file***REMOVED***filename***REMOVED*** = {}
                
            # file-level counters
            tp = (len(truepositives_dicts***REMOVED***filename***REMOVED***) if filename in
                  truepositives_dicts else 0)
            fp = (len(falsepositives_dicts***REMOVED***filename***REMOVED***) if filename in
                  falsepositives_dicts else 0)
            tn = (len(truenegatives_dicts***REMOVED***filename***REMOVED***) if filename in
                  truenegatives_dicts else 0)
            fn = (len(falsenegatives_dicts***REMOVED***filename***REMOVED***) if filename in
                  falsenegatives_dicts else 0)

            # counts corrected for included phitype
            ctp = 0
            cfp = 0
            ctn = 0
            cfn = 0
            
            for st in truepositives_dicts***REMOVED***filename***REMOVED***:
                start = st
                stop = truepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                phi_type = truepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                token = truepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***2***REMOVED***
                text_tp_file.write('\n' + filename + '\t' + str(phi_type)
                                   + '\t' + token
                                   + '\t' + str(start) + '\t' + str(stop))
                
                if phi_type not in summary_by_category:
                    summary_by_category***REMOVED***phi_type***REMOVED*** = {}
                if 'tp' not in summary_by_category***REMOVED***phi_type***REMOVED***:
                    summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'tp'***REMOVED*** = ***REMOVED******REMOVED***
                summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'tp'***REMOVED***.append(token)
                
                if phi_type in ucsf_include_tags:
                    ctp += 1
                else:
                    cfp += 1
                    
            for st in falsepositives_dicts***REMOVED***filename***REMOVED***:
                start = st
                stop = falsepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                phi_type = falsepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                token = falsepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***2***REMOVED***
                text_fp_file.write('\n' + filename + '\t' + str(phi_type)
                                   + '\t' + token
                                   + '\t' + str(start) + '\t' + str(stop))
                
                if phi_type not in summary_by_category:
                    summary_by_category***REMOVED***phi_type***REMOVED*** = {}
                if 'fp' not in summary_by_category***REMOVED***phi_type***REMOVED***:
                    summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fp'***REMOVED*** = ***REMOVED******REMOVED***
                summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fp'***REMOVED***.append(token)

                cfp += 1
                
            for st in truenegatives_dicts***REMOVED***filename***REMOVED***:
                start = st
                stop = truenegatives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                phi_type = None
                token = truenegatives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                text_tn_file.write('\n' + filename + '\t' + str(phi_type)
                                   + '\t' + token
                                   + '\t' + str(start) + '\t' + str(stop))
                # this is not phi and produces too much output
                # uncomment for debugging
                # if phi_type not in summary_by_category:
                #     summary_by_category***REMOVED***phi_type***REMOVED*** = {}
                # if 'tn' not in summary_by_category***REMOVED***phi_type***REMOVED***:
                #     summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'tn'***REMOVED*** = ***REMOVED******REMOVED***
                # summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'tn'***REMOVED***.append(token)

                ctn += 1
                
            for st in falsenegatives_dicts***REMOVED***filename***REMOVED***:
                start = st
                stop = falsenegatives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                phi_type = falsenegatives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                token = falsenegatives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***2***REMOVED***
                text_fn_file.write('\n' + filename + '\t' + str(phi_type)
                                   + '\t' + token
                                   + '\t' + str(start) + '\t' + str(stop))
                
                if phi_type not in summary_by_category:
                    summary_by_category***REMOVED***phi_type***REMOVED*** = {}
                if 'fn' not in summary_by_category***REMOVED***phi_type***REMOVED***:
                    summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fn'***REMOVED*** = ***REMOVED******REMOVED***
                summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fn'***REMOVED***.append(token)
                
                if phi_type in ucsf_include_tags:
                    if phi_type == 'Age':
                        if token.isdigit():
                            if int(token) >= 90:
                                cfn += 1
                            else:
                                ctn += 1
                        else:
                            if 'ninety' in token:
                                cfn +=1
                            else:
                                ctn += 1
                    else:
                        cfn += 1
                else:
                    ctn += 1
            
            total_tp += tp
            total_fp += fp
            total_tn += tn
            total_fn += fn
            
            total_ctp += ctp
            total_cfp += cfp
            total_ctn += ctn
            total_cfn += cfn
            
            try:
               precision = tp / (tp + fp)
            except ZeroDivisionError:
               precision = 0
            try:
               recall = tp / (tp + fn)
            except ZeroDivisionError:
               recall = 0
            try:
               retention = tn / (tn + fp)
            except ZeroDivisionError:
               retention = 0
            
            try:
               cprecision = ctp / (ctp + cfp)
            except ZeroDivisionError:
               cprecision = 0
            try:
               crecall = ctp / (ctp + cfn)
            except ZeroDivisionError:
               crecall = 0
            try:
               cretention = ctn / (ctn + cfp)
            except ZeroDivisionError:
               cretention = 0
            
            summary_by_file***REMOVED***filename***REMOVED***.update({'tp':tp, 'fp':fp,
                                              'tn':tn, 'fn':fn,
                                              'recall':recall,
                                              'precision':precision,
                                              'retention':retention})
            summary_by_file***REMOVED***filename***REMOVED***.update({'ctp':ctp, 'cfp':cfp,
                                              'ctn':ctn, 'cfn':cfn,
                                              'crecall':crecall,
                                              'cprecision':cprecision,
                                              'cretention':cretention})
        
        try:
           total_precision = total_tp / (total_tp + total_fp)
        except ZeroDivisionError:
           total_precision = 0
        try:
           total_recall = total_tp / (total_tp + total_fn)
        except ZeroDivisionError:
           total_recall = 0
        try:
           total_retention = total_tn / (total_tn + total_fp)
        except ZeroDivisionError:
           total_retention = 0
        try:
           total_cprecision = total_ctp / (total_ctp + total_cfp)
        except ZeroDivisionError:
           total_cprecision = 0
        try:
           total_crecall = total_ctp / (total_ctp + total_cfn)
        except ZeroDivisionError:
           total_crecall = 0
        try:
           total_cretention = total_ctn / (total_ctn + total_cfp)
        except ZeroDivisionError:
           total_cretention = 0
        total_summary = {'tp':total_tp, 'fp':total_fp,
                         'tn':total_tn, 'fn':total_fn,
                         'precision':total_precision, 'recall':total_recall,
                         'retention':total_retention,
                         'ctp':total_ctp, 'cfp':total_cfp,
                         'ctn':total_ctn, 'cfn':total_cfn,
                         'cprecision':total_cprecision, 'crecall':total_crecall,
                         'cretention':total_cretention}

        json.dump(total_summary, open(summary_file, "w"), indent=4)
        json.dump(summary_by_file, open(json_summary_by_file, "w"), indent=4)
        json.dump(summary_by_category, open(json_summary_by_category, "w"),
                  indent=4)

        text_tp_file.close()
        text_fp_file.close()
        text_tn_file.close()
        text_fn_file.close()

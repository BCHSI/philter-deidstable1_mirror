import os
import os.path
from chardet.universaldetector import UniversalDetector
import re
import json
from subs import Subs
from coordinate_map import CoordinateMap
from lxml import etree as ET
import xmltodict
from philter import Philter
import json
from subs import Subs
import string
import pandas
import numpy

class Phitexts:
    """ container for texts, phi, attributes """

    def __init__(self, inputdir):
        self.inputdir  = inputdir
        self.filenames = []
        #notes text
        self.texts     = {}
        #coordinates of PHI
        self.coords    = {}
        #list of PHI types
        self.types     = {}
        #normalized PHI
        self.norms     = {}
        #substituted PHI
        self.subs      = {}
        #de-id notes
        self.textsout  = {}
        #no subs de-id notes
        self.textsout_nosubs  = {}
        #total_phi_counts
        self.total_phi_counts  = {}
        #parse info
        self.parse_info = {}
        #parse info
        self.summary_info = {'filesize':[],'total_tokens':[],'phi_tokens':[],'successful_normalized':[],'failed_normalized':[],'successful_surrogated':[],'failed_surrogated':[]}
        #All coordinate maps stored here
        self.coordinate_maps = []
        #create a memory for exclude coordinate map
        self.xml_map = CoordinateMap()
        self.full_xml_map = {}
        self._read_texts()
        self.subser = None
        self.filterer = None
        #create a memory for the list of known PHI types
        self.phi_type_list = ['DATE','ID','NAME','CONTACT','AGE>=90','NAME','OTHER','LOCATION']
        self.phi_type_dict = {}
        for phi_type in self.phi_type_list:
            self.phi_type_dict[phi_type] = [CoordinateMap()]        
        self._read_xml()

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
                fhandle = open(filepath, "r", encoding=encoding['encoding'], errors='surrogateescape')
                self.texts[filepath] = fhandle.read()
                fhandle.close()

        #self.note_keys = [os.path.splitext(os.path.basename(f).strip('0'))[0] for f in self.filenames]


    def _read_xml(self):
        
        if not self.inputdir:
            raise Exception("Input directory undefined: ", self.inputdir) 
        for filename in os.listdir(self.inputdir):
            xml_coordinate_map = {}
            if not filename.endswith("xml"):
               continue
               
            philter_or_gold = 'PhilterUCSF' 
            filepath = os.path.join(self.inputdir, filename)
            #print(filepath)           
            self.filenames.append(filepath)
            encoding = self._detect_encoding(filepath)
            fhandle = open(filepath, "r", encoding=encoding['encoding'])
            input_xml = fhandle.read() 
            #print(input_xml)
            tree = ET.parse(filepath)
            root = tree.getroot()
            xmlstr = ET.tostring(root, encoding='utf8', method='xml')
            self.texts[filepath] = root.find('TEXT').text
            xml_dict = xmltodict.parse(xmlstr)[philter_or_gold]
            check_tags = root.find('TAGS')
                       
 
            self.xml_map.add_file(filepath)
            if check_tags is not None:
               tags_dict = xml_dict["TAGS"]            
            else:
               tags_dict = None
               print(filename)
            if tags_dict is not None:
               for key, value in tags_dict.items():
              # Note:  Value can be a list of like phi elements
              #               or a dictionary of the metadata about a phi element
                   if isinstance(value, list):
                      for final_value in value:
                          text_start = final_value["@spans"].split('~')[0] 
                          text_end = final_value["@spans"].split('~')[1]
                          philter_text = final_value["@text"]
                          xml_phi_type = final_value["@TYPE"]
                          xml_coordinate_map[int(text_start)] = int(text_end)  
                          if xml_phi_type not in self.phi_type_list:
                              #print(xml_phi_type)
                              self.phi_type_list.append(xml_phi_type)
                          for phi_type in self.phi_type_list:
                              if phi_type not in self.phi_type_dict:
                                 self.phi_type_dict[phi_type] = [CoordinateMap()]
                              self.phi_type_dict[phi_type][0].add_file(filepath)
                   else:
                       final_value = value
                       text = final_value["@text"]
                       xml_phi_type = final_value["@TYPE"]
                       text_start = final_value["@spans"].split('~')[0]
                       text_end = final_value["@spans"].split('~')[1]
                       xml_coordinate_map[int(text_start)] = int(text_end)
                       if xml_phi_type not in self.phi_type_list:
                             self.phi_type_list.append(xml_phi_type)
                       for phi_type in self.phi_type_list:
                           if phi_type not in self.phi_type_dict:
                                 self.phi_type_dict[phi_type] = [CoordinateMap()]
                           self.phi_type_dict[phi_type][0].add_file(filepath)
                      
            self.full_xml_map[filepath] = xml_coordinate_map
            self.coords = self.full_xml_map
            fhandle.close()
        #print(self.full_xml_map) 
        return self.full_xml_map
 

    '''
    def _extract_coordinates(self,filename,tags_dict):
        if tags_dict is not None:
           for key, value in tags_dict.items():
              # Note:  Value can be a list of like phi elements
              #               or a dictionary of the metadata about a phi element
               if isinstance(value, list):
                  for final_value in value:
                      text_start = final_value["@spans"].split('~')[0] 
                      text_end = final_value["@spans"].split('~')[1]
                      philter_text = final_value["@text"]
                      phi_type = final_value["@TYPE"]
                      self.xml_map.add(filename,text_start,text_end)
               else:
                   final_value = value
                   text = final_value["@text"]
                   phi_type = final_value["@TYPE"]
                   text_start = final_value["@spans"].split('~')[0]
                   text_end = final_value["@spans"].split('~')[1]
                   self.xml_map.add(filename,text_start,text_end)
        return self.xml_map[filename]
    ''' 
       
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


    def _get_clean(self, text, punctuation_matcher=re.compile(r"[^a-zA-Z0-9\*\/]")):

            # Use pre-process to split sentence by spaces AND symbols, while preserving spaces in the split list
        # print (text)
        lst = re.split("(\s+)", text)
        cleaned = []
        for item in lst:
            if len(item) > 0:
                if item.isspace() == False:
                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, "", item))
                    for elem in split_item:
                        if len(elem) > 0:
                                cleaned.append(elem)
                                # print (elem)
                # else:
                #     cleaned.append(item)
        return cleaned




    def detect_phi(self, filters="./configs/philter_alpha.json"):
        assert self.texts, "No texts defined"
        
        if self.coords:
            return
        
        philter_config = {
            "verbose":False,
            "run_eval":False,
            "finpath":self.inputdir,
            "filters":filters,
            "outformat":"asterisk"
        }

        self.filterer = Philter(philter_config)
        self.coords = self.filterer.map_coordinates()

    def detect_phi_types(self):
        assert self.texts, "No texts defined"
        assert self.coords, "No PHI coordinates defined"
        
        if self.types:
            return

        self.types = self.filterer.phi_type_dict

    def detect_xml_phi_types(self):
        assert self.texts, "No texts defined"
        assert self.coords, "No PHI coordinates defined"

        if self.types:
            return
        #print(self.phi_type_dict) 
        self.types = self.phi_type_dict

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
            self.norms[phi_type] = {}
        for phi_type in self.types.keys():
            if phi_type == "DATE" or phi_type == "Date":
                for filename, start, end in self.types[phi_type][0].scan():
                    token = self.texts[filename][start:end]
                    normalized_token = Subs.parse_date(token)                 
                    self.norms[phi_type] [(filename, start)] = (normalized_token, end)
                
            else:
                continue

        # TODO: what do we do when phi could not be interpreted?
        # e.g. change phi type to OTHER?
        # or scramble?
        # or use self.norms="unknown <type>" with <type>=self.types

        # Note: this is currently done in surrogator.shift_dates(), surrogator.parse_and_shift_date(), parse_date_ranges(), replace_other_surrogate()
        
    def substitute_phi(self, look_up_table_path = None):
        assert self.norms, "No normalized PHI defined"
        
        if self.subs:
            return

        self.subser = Subs(look_up_table_path)

        for phi_type in self.norms.keys():
            if phi_type == "DATE" or phi_type == "Date":
                for filename, start in self.norms[phi_type]:
                    note_key_ucsf = os.path.splitext(os.path.basename(filename).strip('0'))[0]
                    if not self.subser.has_shift_amount(note_key_ucsf):
                        if __debug__: print("WARNING: no date shift found for: " + filename)
                        continue
                    normalized_token = self.norms[phi_type][filename, start][0]
                    end = self.norms[phi_type][filename, start][1]

                    # Added for eval
                    if normalized_token is None:
                        # self.eval_table[filename][start].update({'sub':None})
                        continue

                    shifted_date = self.subser.shift_date_pid(normalized_token,
                                                              note_key_ucsf)
                    if shifted_date is None:
                        if __debug__: print("WARNING: cannot shift date in: "
                                            + filename)
                        continue
                    substitute_token = self.subser.date_to_string(shifted_date)
                    # self.eval_table[filename][start].update({'sub':substitute_token})
                    self.subs[(filename, start)] = (substitute_token, end)
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
            #current_chunk = []
            #punctuation_matcher = re.compile(r"[^a-zA-Z0-9*]")
            txt = self.texts[filename]
            exclude_dict = self.coords[filename]

            #read the text by character, any non-punc non-overlaps will be replaced
            contents = []
            for i in range(0, len(txt)):

                if i < last_marker:
                    continue
                
                if i in exclude_dict:
                    start,stop = i, exclude_dict[i]
                    if (filename, start) in self.subs:
                        substitute_token = self.subs[filename, start][0]
                        end = self.subs[filename, start][1]
                        contents.append(substitute_token)
                        last_marker = end
                    else:
                        contents.append("*****")
                        last_marker = stop
                    
                else:
                    contents.append(txt[i])

            self.textsout[filename] =  "".join(contents)
    
    def simple_transform(self):
        assert self.texts, "No texts defined"

        if not self.coords:
            self.textsout_nosubs = self.texts
            print("WARNING: No PHI coordinates defined: nothing to transform!")
                
        if self.textsout_nosubs:
            return
        
        for filename in self.filenames:
            
            last_marker = 0

            txt = self.texts[filename]
            exclude_dict = self.coords[filename]

            #read the text by character, any non-punc non-overlaps will be replaced
            contents = []
            for i in range(0, len(txt)):     
                if i in exclude_dict:
                    contents.append("*")    
                else:
                    contents.append(txt[i])

            self.textsout_nosubs[filename] =  "".join(contents)     

    def _transform_text(self, txt, infilename,
                        include_map, exclude_map, subs):       
        last_marker = 0
        current_chunk = []
        punctuation_matcher = re.compile(r"[^a-zA-Z0-9*]")

        #read the text by character, any non-punc non-overlaps will be replaced
        contents = []
        for i in range(0, len(txt)):

            if i < last_marker:
                continue
            
            if include_map.does_exist(infilename, i):
                #add our preserved text
                start,stop = include_map.get_coords(infilename, i)
                contents.append(txt[start:stop])
                last_marker = stop
            elif exclude_map.does_exist(infilename, i):
                #print(infilename)
                #print(i)
                start,stop = exclude_map.get_coords(infilename, i)
                if (infilename, start, stop) in subs:
                    contents.append(subs[(infilename, start, stop)])
                else:
                    contents.append("*")
            elif punctuation_matcher.match(txt[i]):
                contents.append(txt[i])
            else:
                contents.append("*")

        return "".join(contents)


    def save(self, outputdir):
        assert self.textsout, "Cannot save text: output not ready"
        if not outputdir:
            raise Exception("Output directory undefined: ", outputdir)

        for filename in self.filenames:
            fbase, fext = os.path.splitext(filename)
            fbase = fbase.split('/')[-1]
            filepath = outputdir + fbase + "_subs.txt"
            with open(filepath, "w", encoding='utf-8', errors='surrogateescape') as fhandle:
                fhandle.write(self.textsout[filename])
    
    def print_log(self, output_dir):
        log_dir = os.path.join(output_dir, 'log/')
        #master_log_dir = '/'.join(output_dir.split('/')[:-2])+'/log/'

        failed_dates_file = os.path.join(log_dir, 'failed_dates.json')
        date_table_file = os.path.join(log_dir, 'parsed_dates.json')
        phi_count_file = os.path.join(log_dir, 'phi_count.txt')
        phi_marked_file = os.path.join(log_dir, 'phi_marked.json')
        batch_summary_file = os.path.join(log_dir, 'batch_summary.txt')

        #Path to csv summary of all files
        csv_summary_filepath = log_dir+'detailed_batch_summary.csv'



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
            # f_parsed.write('\t'.join(['filename', 'start', 'end', 'raw', 'normalized', 'substituted']))
            # f_parsed.write('\n')
            # f_failed.write('\t'.join(['filename', 'start', 'end', 'raw']))
            # f_failed.write('\n')
        for filename, start, end in self.types[phi_type][0].scan():
            raw = self.texts[filename][start:end]
            normalized_date = self.norms[phi_type][(filename,start)][0]
            
            if filename not in parse_info:
                parse_info[filename] = {'success_norm':0,'fail_norm':0,'success_sub':0,'fail_sub':0}
            if filename not in eval_table:
                eval_table[filename] = []

            if normalized_date is not None:
                # Add 1 to successfully normalized dates
                num_parsed += 1
                parse_info[filename]['success_norm'] += 1
                
                normalized_token = self.subser.date_to_string(normalized_date)
                note_key_ucsf = os.path.splitext(os.path.basename(filename).strip('0'))[0]
                
                # Successfully surrogated:
                if not self.subser.has_shift_amount(note_key_ucsf):
                    # Add 1 to unsuccessfuly surrogated dates:
                     sub = None	
                     parse_info[filename]['fail_sub'] += 1
                # Unsuccessfully surrogated:
                else:
                    # Add 1 to successfuly surrogated dates:	
                     sub = self.subs[(filename,start)][0]
                     parse_info[filename]['success_sub'] += 1

                eval_table[filename].append({'start':start, 'end':end, 'raw': raw, 'normalized': normalized_token, 'sub': sub})
                    # f_parsed.write('\t'.join([filename, str(start), str(end), raw, normalized_token, sub]))
                    # f_parsed.write('\n')
            else:
                # Add 1 to unsuccessfuly normazlied dates:
                num_failed += 1
                parse_info[filename]['fail_norm'] += 1
                    # f_failed.write('\t'.join([filename, str(start), str(end), raw.strip('\n')]))
                    # f_failed.write('\n')
                if filename not in failed_date:
                        failed_date[filename] = []
                failed_date[filename].append({'start':start, 'end':end, 'raw': raw})

        print ('Successfully parsed: ' + str(num_parsed) + ' dates.')
        print ('Failed to parse: ' + str(num_failed) + ' dates.')
                
        # Count by phi_type, record PHI marked
        phi_counter = {}
        marked_phi = {}
        with open(phi_count_file,'w') as f_count:
            # f_marked.write('\t'.join(['filename', 'start', 'end', 'word', 'phi_type', 'category']))
            # f_marked.write('\n')

            for phi_type in self.types:
                for filename, start, end in self.types[phi_type][0].scan():
                    if filename not in phi_table:
                        phi_table[filename] = []
                    word = self.texts[filename][start:end]
                    phi_table[filename].append({'start': start, 'end': end, 'word': word, 'type': phi_type})

                    if phi_type not in phi_counter:
                        phi_counter[phi_type] = 0
                    phi_counter[phi_type] += 1

                    
                    # f_marked.write('\t'.join([filename, str(start), str(end), word, phi_type]))
                    # f_marked.write('\n')

            for phi_type in phi_counter:
                f_count.write('\t'.join([phi_type, str(phi_counter[phi_type])]))
                f_count.write('\n')

        # dump to json
        with open (failed_dates_file, 'w') as f:
            json.dump(failed_date, f)
        with open(date_table_file, 'w') as f:
            json.dump(eval_table, f)
        with open(phi_marked_file, 'w') as f:
            json.dump(phi_table, f)


        # If the summary csv file doesn't exist yet, create it and add file headers
        # Csv summary is one directory above all input directories
        if not os.path.isfile(csv_summary_filepath):
            with open(csv_summary_filepath,'w') as f:
                file_header = 'filename'+','+'file_size'+','+'total_tokens'+','+'phi_tokens'+','+'successfully_normalized'+','+'failed_normalized'+','+'successfully_surrogated'+','+'failed_surrogated'+'\n'
                f.write(file_header)
        
        ### CSV of summary per file ####
        # 1. Filename
        for filename in self.filenames:

            # File size in bytes
            filesize = os.path.getsize(filename)
            
            # Number of total tokens
            total_tokens = self.filterer.cleaned[filename][1]
            
            # Number of PHI tokens
            phi_tokens = self.filterer.get_clean_filtered(filename,self.textsout_nosubs[filename])[1]
            
            successful_normalized = 0
            failed_normalized = 0
            successful_surrogated = 0
            failed_surrogated = 0

            if filename in parse_info:
                # Successfully normalized dates
                successful_normalized = parse_info[filename]['success_norm']
                # Unsuccessfully normalized dates
                failed_normalized = parse_info[filename]['fail_norm']
                # Successfully normalized dates
                successful_surrogated = parse_info[filename]['success_sub']
                # Unsuccessfully normalized dates
                failed_surrogated = parse_info[filename]['fail_sub']
            
            # Add to master list for all files          
            with open(csv_summary_filepath,'a') as f:
                new_line = filename + ',' + str(filesize) + ',' + str(total_tokens) + ',' + str(phi_tokens) + ',' + str(successful_normalized) + ',' + str(failed_normalized) + ',' + str(successful_surrogated) + ',' + str(failed_surrogated) + '\n'
                f.write(new_line)
                     
            self.summary_info['filesize'].append(filesize)
            self.summary_info['total_tokens'].append(total_tokens)
            self.summary_info['phi_tokens'].append(phi_tokens)
            self.summary_info['successful_normalized'].append(successful_normalized)
            self.summary_info['failed_normalized'].append(failed_normalized)
            self.summary_info['successful_surrogated'].append(successful_surrogated)
            self.summary_info['failed_surrogated'].append(failed_surrogated)
        
        # Summarize current batch
        # Batch size (all)
        number_of_notes = len(self.summary_info)

        # File size
        total_kb_processed = sum(self.summary_info['filesize'])/1000
        median_file_size = numpy.median(self.summary_info['filesize'])
        q2pt5_size,q97pt5_size = numpy.percentile(self.summary_info['filesize'],[2.5,97.5])

        # Total tokens
        total_tokens = numpy.sum(self.summary_info['total_tokens'])
        median_tokens = numpy.median(self.summary_info['total_tokens'])
        q2pt5_tokens,q97pt5_tokens = numpy.percentile(self.summary_info['total_tokens'],[2.5,97.5])

        # Total PHI tokens
        total_phi_tokens = numpy.sum(self.summary_info['phi_tokens'])
        median_phi_tokens = numpy.median(self.summary_info['phi_tokens'])
        q2pt5_phi_tokens,q97pt5_phi_tokens = numpy.percentile(self.summary_info['phi_tokens'],[2.5,97.5])

        # Normalization
        successful_normalization = sum(self.summary_info['successful_normalized'])
        failed_normalization = sum(self.summary_info['failed_normalized'])

        # Surrogation
        successful_surrogation = sum(self.summary_info['successful_surrogated'])
        failed_surrogation = sum(self.summary_info['failed_surrogated'])

        # Create text summary for the current batch
        with open(batch_summary_file, "w") as f:
            f.write("TOTAL NOTES PROCESSED: "+str(number_of_notes)+'\n')
            f.write("TOTAL KB PROCESSED: "+str("%.2f"%total_kb_processed)+'\n')
            f.write("TOTAL TOKENS PROCESSED: "+str(total_tokens)+'\n')
            f.write("TOTAL PHI TOKENS PROCESSED: "+str(total_phi_tokens)+'\n')
            f.write('\n')
            f.write("MEDIAN FILESIZE (BYTES): "+str(median_file_size)+" (95% Percentile: "+str("%.2f"%q2pt5_size)+'-'+str("%.2f"%q97pt5_size)+')'+'\n')
            f.write("MEDIAN TOKENS PER NOTE: "+str(median_tokens)+" (95% Percentile: "+str("%.2f"%q2pt5_tokens)+'-'+str("%.2f"%q97pt5_tokens)+')'+'\n')
            f.write("MEDIAN PHI TOKENS PER NOTE: "+str(median_phi_tokens)+" (95% Percentile: "+str("%.2f"%q2pt5_phi_tokens)+'-'+str("%.2f"%q97pt5_phi_tokens)+')'+'\n')
            f.write('\n')
            f.write("DATES SUCCESSFULLY NORMALIZED: "+str(successful_normalization)+'\n')
            f.write("DATES FAILED TO NORMALIZE: "+str(failed_normalization)+'\n')
            f.write("DATES SUCCESSFULLY SURROGATED: "+str(successful_surrogation)+'\n')
            f.write("DATES FAILED TO SURROGATE: "+str(failed_surrogation)+'\n')   
        
        
        # Create detailed csv for the current batch


        # Todo: add PHI type counts to summary
        # Name PHI
        # Date PHI
        # Age>=90 PHI
        # Contact PHI
        # Location PHI
        # ID PHI
        # Other PHI


    def eval(self, anno_dir, in_dir, output_dir):
        # preserve these two puncs so that dates are complete
        s = string.punctuation.replace('/','')
        s = s.replace('-', '')
        translator = str.maketrans('', '', s)

        gold_phi = {}
        eval_dir = os.path.join(output_dir, 'eval/')
        summary_file = os.path.join(eval_dir, 'summary.json')
        json_summary_by_file = os.path.join(eval_dir, 'summary_by_file.json')
        json_summary_by_category = os.path.join(eval_dir, 'summary_by_category.json')

        if os.path.isdir(eval_dir):
            pass
        else:
            os.makedirs(eval_dir)

        for root, dirs, files in os.walk(anno_dir):
            for filename in files:
                #print(root)
                if not filename.endswith("xml"):
                    continue                
                #filepath = os.path.join(root, filename)
                filepath = os.path.join(anno_dir, filename)
                # change here: what will the input format be?
                file_id = in_dir + filename.split('.')[0] + '.txt'
                tree = ET.parse(filepath)
                root = tree.getroot()
                xmlstr = ET.tostring(root, encoding='utf8', method='xml')
                xml_dict = xmltodict.parse(xmlstr)['PhilterUCSF']
                check_tags = root.find('TAGS')
                text = xml_dict["TEXT"]
                if check_tags is not None:
                   tags_dict = xml_dict["TAGS"]
                else:
                   tags_dict = None

                if file_id  not in gold_phi:
                   gold_phi[file_id] = {}
                # the existence of puncs in text makes the end index inaccurate - only use start index as the key
                if tags_dict is not None: 

                   for key, value in tags_dict.items():
                       if isinstance(value, list):
                          for final_value in value:
                              #start = int(final_value["@start"])
                              #end = int(final_value["@end"])
                              start = int(final_value["@spans"].split('~')[0])
                              end = int(final_value["@spans"].split('~')[1])
                              text = final_value["@text"].translate(translator)
                              phi_type = final_value["@TYPE"]
                              gold_phi[file_id].update({start:[end,phi_type,text]})

                       else:
                          final_value = value
                          #start = int(final_value["@start"])
                          start = int(final_value["@spans"].split('~')[0])
                          #end = int(final_value["@end"])
                          end = int(final_value["@spans"].split('~')[1])
                          text = final_value["@text"].translate(translator)
                          phi_type = final_value["@TYPE"]
                          gold_phi[file_id].update({start:[end, phi_type, text]})
       
        # converting self.types to an easier accessible data structure
        eval_table = {}
        phi_table = {}
        non_phi = {}
        for phi_type in self.types:
            for filename, start, end in self.types[phi_type][0].scan():
                word = self.texts[filename][start:end].translate(translator)
                #print(filename + "\t" + str(start) + "\t" + str(end) +"\t" + word)
                if filename not in phi_table:
                    phi_table[filename] = {}
                phi_table[filename].update({start:[end, phi_type, word]})
        for filename in gold_phi:
            if filename not in eval_table:
                eval_table[filename] = {'fp':{},'tp':{},'fn':{},'tn':{}}
            # each ele contains an annotated phi
            # token_set = self._get_clean(self.texts[filename])
            text = self.texts[filename]
            for start in gold_phi[filename]:
                gold_start = start
                gold_end = gold_phi[filename][start][0]
                gold_type = gold_phi[filename][start][1]
                gold_word = gold_phi[filename][start][2]
                #print(filename + "\t" + gold_start + "\t" + gold_end +"\t" + gold_word)
                # remove phi from text to form the non_phi_set
                text = text.replace(gold_word, '')
                
                if filename in phi_table:
                    # is phi and is caught -> TP
                    if gold_start in phi_table[filename]:
                        word = phi_table[filename][gold_start][2]
                        if word == gold_word:
                            if gold_type not in eval_table[filename]['tp']:
                                eval_table[filename]['tp'][gold_type] = []
                            eval_table[filename]['tp'][gold_type].append(word)
                    # is phi but not caught -> FN
                    else:
                        #print("fn" + filename + "\t" + gold_start + "\t" + gold_end +"\t" + gold_word)
                        # word = phi_table[filename][gold_start][2]
                        if gold_type not in eval_table[filename]['fn']:
                            eval_table[filename]['fn'][gold_type] = []
                        eval_table[filename]['fn'][gold_type].append(gold_word)
                else:
                    print (filename + ' not processed by philter or check filename!')
                    continue
            non_phi[filename] = self._get_clean(text)
        for filename in phi_table:
            if filename in gold_phi:
                if filename not in eval_table:
                    eval_table[filename] = {'fp':{},'tp':{},'fn':{},'tn':[]}
                for start in phi_table[filename]:
                    end = phi_table[filename][start][0]
                    phi_type = phi_table[filename][start][1]
                    word = phi_table[filename][start][2]
                    #print (""+"\t"+word + "\t" + str(start))
                    # word caught but is not phi -> FP
                    if start not in gold_phi[filename]:
                        #print ("fp" + "\t" + filename + "\t" + word + "\t" + str(start))
                        if phi_type not in eval_table[filename]['fp']:
                            eval_table[filename]['fp'][phi_type] = []
                            eval_table[filename]['fp'][phi_type].append(word)
                            if word in non_phi[filename]:
                                non_phi[filename].remove(word)
            else:
                print (filename + ' not found!')
        # the rest is all TN
        for filename in non_phi:
            if filename not in eval_table:
                eval_table[filename] = {'fp':{},'tp':{},'fn':{},'tn':{}}
            eval_table[filename]['tn'] = non_phi[filename]

        summary_by_category = {}
        summary_by_file = {}

        total_tp = 0
        total_fn = 0
        total_tn = 0
        total_fp = 0
        for filename in eval_table:
            # file-level counters
            tp = 0
            fn = 0
            tn = 0
            fp = 0
            if filename not in summary_by_file:
                summary_by_file[filename] = {}
            for phi_type in eval_table[filename]['tp']:
                tp += len(eval_table[filename]['tp'][phi_type])
                total_tp += tp
                if phi_type not in summary_by_category:
                    summary_by_category[phi_type] = {}
                if 'tp' not in summary_by_category[phi_type]:
                    summary_by_category[phi_type]['tp'] = []
                summary_by_category[phi_type]['tp'].append(eval_table[filename]['tp'][phi_type])
            for phi_type in eval_table[filename]['fp']:
                fp += len(eval_table[filename]['fp'][phi_type])
                total_fp += fp
                if phi_type not in summary_by_category:
                    summary_by_category[phi_type] = {}
                if 'fp' not in summary_by_category[phi_type]:
                    summary_by_category[phi_type]['fp'] = []
                summary_by_category[phi_type]['fp'].append(eval_table[filename]['fp'][phi_type])
            for phi_type in eval_table[filename]['fn']:
                tp += len(eval_table[filename]['fn'][phi_type])
                total_tp += tp
                if phi_type not in summary_by_category:
                    summary_by_category[phi_type] = {}
                if 'fn' not in summary_by_category[phi_type]:
                    summary_by_category[phi_type]['fn'] = []
                summary_by_category[phi_type]['fn'].append(eval_table[filename]['fn'][phi_type])
            tn = len(eval_table[filename]['tn'])
            total_tn += tn
            try:  
               precision = tp / (tp + fp)
            except ZeroDivisionError:
               precision = 0
            try:  
               recall = tp / (tp + fn)
            except ZeroDivisionError:
               recall = 0
            summary_by_file[filename].update({'tp':tp, 'fp': fp, 'fn':fn, 'tn':tn, 'recall':recall,'precision':precision})
            # summary_by_category[filename].update({'tp':tp, 'fp': fp, 'fn':fn, 'tn':tn, 'recall':recall,'precision':precision})
        
        try:
           total_precision = total_tp / (total_tp + total_fp)
        except ZeroDivisionError:
           total_precision = 0     

        try:
           total_recall = total_tp / (total_tp + total_fn)
        except ZeroDivisionError:
           total_recall = 0
        total_summary = {'tp':total_tp, 'tn':total_tn, 'fp':total_fp, 'fn':total_fn, 'precision':total_precision, 'recall':total_recall}
        json.dump(total_summary, open(summary_file, "w"), indent=4)
        json.dump(summary_by_file, open(json_summary_by_file, "w"), indent=4)
        json.dump(summary_by_category, open(json_summary_by_category, "w"), indent=4)



            

                    





        


                

        

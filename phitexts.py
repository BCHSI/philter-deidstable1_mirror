import os
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

class Phitexts:
    """ container for texts, phi, attributes """

    def __init__(self, inputdir):
        self.inputdir  = inputdir
        self.filenames = ***REMOVED******REMOVED***
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
        #All coordinate maps stored here
        self.coordinate_maps = ***REMOVED******REMOVED***
        #create a memory for exclude coordinate map
        self.xml_map = CoordinateMap()
        self.full_xml_map = {}
        self._read_texts()
        self.subser = None
        self.filterer = None
        #create a memory for the list of known PHI types
        self.phi_type_list = ***REMOVED***'Date'***REMOVED***
        self.phi_type_dict = {}
        for phi_type in self.phi_type_list:
            self.phi_type_dict***REMOVED***phi_type***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***        
        self._read_xml()

    def _read_texts(self):
        if not self.inputdir:
            raise Exception("Input directory undefined: ", self.inputdir)

        for root, dirs, files in os.walk(self.inputdir):
            for filename in files:
                if not filename.endswith("txt"):
                    continue

                filepath = os.path.join(root, filename)

                self.filenames.append(filepath)
                encoding = self._detect_encoding(filepath)
                fhandle = open(filepath, "r", encoding=encoding***REMOVED***'encoding'***REMOVED***, errors='surrogateescape')
                self.texts***REMOVED***filepath***REMOVED*** = fhandle.read()
                fhandle.close()

        #self.note_keys = ***REMOVED***os.path.splitext(os.path.basename(f).strip('0'))***REMOVED***0***REMOVED*** for f in self.filenames***REMOVED***


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
            fhandle = open(filepath, "r", encoding=encoding***REMOVED***'encoding'***REMOVED***)
            input_xml = fhandle.read() 
            #print(input_xml)
            tree = ET.parse(filepath)
            root = tree.getroot()
            xmlstr = ET.tostring(root, encoding='utf8', method='xml')
            self.texts***REMOVED***filepath***REMOVED*** = root.find('TEXT').text
            xml_dict = xmltodict.parse(xmlstr)***REMOVED***philter_or_gold***REMOVED***
            check_tags = root.find('TAGS')
                       
 
            self.xml_map.add_file(filepath)
            if check_tags is not None:
               tags_dict = xml_dict***REMOVED***"TAGS"***REMOVED***            
            else:
               tags_dict = None
               print(filename)
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
                          xml_coordinate_map***REMOVED***int(text_start)***REMOVED*** = int(text_end)  
                          if xml_phi_type not in self.phi_type_list:
                              #print(xml_phi_type)
                              self.phi_type_list.append(xml_phi_type)
                          for phi_type in self.phi_type_list:
                              if phi_type not in self.phi_type_dict:
                                 self.phi_type_dict***REMOVED***phi_type***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
                              self.phi_type_dict***REMOVED***phi_type***REMOVED******REMOVED***0***REMOVED***.add_file(filepath)
                   else:
                       final_value = value
                       text = final_value***REMOVED***"@text"***REMOVED***
                       xml_phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                       text_start = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED***
                       text_end = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***
                       xml_coordinate_map***REMOVED***int(text_start)***REMOVED*** = int(text_end)
                       if xml_phi_type not in self.phi_type_list:
                             self.phi_type_list.append(xml_phi_type)
                       for phi_type in self.phi_type_list:
                           if phi_type not in self.phi_type_dict:
                                 self.phi_type_dict***REMOVED***phi_type***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
                           self.phi_type_dict***REMOVED***phi_type***REMOVED******REMOVED***0***REMOVED***.add_file(filepath)
                      
            self.full_xml_map***REMOVED***filepath***REMOVED*** = xml_coordinate_map
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
                      text_start = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED*** 
                      text_end = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***
                      philter_text = final_value***REMOVED***"@text"***REMOVED***
                      phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                      self.xml_map.add(filename,text_start,text_end)
               else:
                   final_value = value
                   text = final_value***REMOVED***"@text"***REMOVED***
                   phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                   text_start = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED***
                   text_end = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***
                   self.xml_map.add(filename,text_start,text_end)
        return self.xml_map***REMOVED***filename***REMOVED***
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


    def _get_clean(self, text, punctuation_matcher=re.compile(r"***REMOVED***^a-zA-Z0-9\*\/***REMOVED***")):

            # Use pre-process to split sentence by spaces AND symbols, while preserving spaces in the split list
        # print (text)
        lst = re.split("(\s+)", text)
        cleaned = ***REMOVED******REMOVED***
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
            self.norms***REMOVED***phi_type***REMOVED*** = {}
        for phi_type in self.types.keys():
            if phi_type == "DATE" or phi_type == "Date":
                for filename, start, end in self.types***REMOVED***phi_type***REMOVED******REMOVED***0***REMOVED***.scan():
                    token = self.texts***REMOVED***filename***REMOVED******REMOVED***start:end***REMOVED***
                    normalized_token = Subs.parse_date(token)                 
                    self.norms***REMOVED***phi_type***REMOVED*** ***REMOVED***(filename, start)***REMOVED*** = (normalized_token, end)
                
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
                for filename, start in self.norms***REMOVED***phi_type***REMOVED***:
                    note_key_ucsf = os.path.splitext(os.path.basename(filename).strip('0'))***REMOVED***0***REMOVED***
                    if not self.subser.has_shift_amount(note_key_ucsf):
                        if __debug__: print("WARNING: no date shift found for: " + filename)
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
                        if __debug__: print("WARNING: cannot shift date in: "
                                            + filename)
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

    def _transform_text(self, txt, infilename,
                        include_map, exclude_map, subs):       
        last_marker = 0
        current_chunk = ***REMOVED******REMOVED***
        punctuation_matcher = re.compile(r"***REMOVED***^a-zA-Z0-9****REMOVED***")

        #read the text by character, any non-punc non-overlaps will be replaced
        contents = ***REMOVED******REMOVED***
        for i in range(0, len(txt)):

            if i < last_marker:
                continue
            
            if include_map.does_exist(infilename, i):
                #add our preserved text
                start,stop = include_map.get_coords(infilename, i)
                contents.append(txt***REMOVED***start:stop***REMOVED***)
                last_marker = stop
            elif exclude_map.does_exist(infilename, i):
                #print(infilename)
                #print(i)
                start,stop = exclude_map.get_coords(infilename, i)
                if (infilename, start, stop) in subs:
                    contents.append(subs***REMOVED***(infilename, start, stop)***REMOVED***)
                else:
                    contents.append("*")
            elif punctuation_matcher.match(txt***REMOVED***i***REMOVED***):
                contents.append(txt***REMOVED***i***REMOVED***)
            else:
                contents.append("*")

        return "".join(contents)


    def save(self, outputdir, suf="_subs", ext="txt",
             use_deid_note_key=False):
        assert self.textsout, "Cannot save text: output not ready"
        assert outputdir, "Cannot save text: output directory undefined"

        for filename in self.filenames:
            fbase = os.path.splitext(os.path.basename(filename))***REMOVED***0***REMOVED***
            if use_deid_note_key:
                note_key_ucsf = fbase.lstrip('0')
                if not self.subser.has_deid_note_key(note_key_ucsf):
                    if __debug__: print("WARNING: no deid note key found for "
                                        + filename)
                    continue
                fbase = self.subser.get_deid_note_key(note_key_ucsf)
            filepath = os.path.join(outputdir, fbase + suf + "." + ext)
            with open(filepath, "w", encoding='utf-8',
                      errors='surrogateescape') as fhandle:
                fhandle.write(self.textsout***REMOVED***filename***REMOVED***)
    
    def print_log(self, output_dir):
        log_dir = os.path.join(output_dir, 'log/')
        failed_dates_file = os.path.join(log_dir, 'failed_dates.json')
        date_table_file = os.path.join(log_dir, 'parsed_dates.json')
        phi_count_file = os.path.join(log_dir, 'phi_count.txt')
        phi_marked_file = os.path.join(log_dir, 'phi_marked.json')

        eval_table = {}
        failed_date = {}
        phi_table = {}
        if 'DATE' in self.types:
            phi_type = 'DATE'
        elif 'Date' in self.types:
            phi_type = 'Date'

        if os.path.isdir(log_dir ):
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
            if normalized_date is not None:
                normalized_token = self.subser.date_to_string(normalized_date)
                note_key_ucsf = os.path.splitext(os.path.basename(filename).strip('0'))***REMOVED***0***REMOVED***
                if not self.subser.has_shift_amount(note_key_ucsf):	
                     sub = None	
                else:	
                     sub = self.subs***REMOVED***(filename,start)***REMOVED******REMOVED***0***REMOVED***
                num_parsed += 1
                if filename not in eval_table:
                    eval_table***REMOVED***filename***REMOVED*** = ***REMOVED******REMOVED***
                eval_table***REMOVED***filename***REMOVED***.append({'start':start, 'end':end, 'raw': raw, 'normalized': normalized_token, 'sub': sub})
                    # f_parsed.write('\t'.join(***REMOVED***filename, str(start), str(end), raw, normalized_token, sub***REMOVED***))
                    # f_parsed.write('\n')
            else:
                num_failed += 1
                    # f_failed.write('\t'.join(***REMOVED***filename, str(start), str(end), raw.strip('\n')***REMOVED***))
                    # f_failed.write('\n')
                if filename not in failed_date:
                        failed_date***REMOVED***filename***REMOVED*** = ***REMOVED******REMOVED***
                failed_date***REMOVED***filename***REMOVED***.append({'start':start, 'end':end, 'raw': raw})

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
                    phi_table***REMOVED***filename***REMOVED***.append({'start': start, 'end': end, 'word': word, 'type': phi_type})

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
                file_id = in_dir + filename.split('.')***REMOVED***0***REMOVED*** + '.txt'
                tree = ET.parse(filepath)
                root = tree.getroot()
                xmlstr = ET.tostring(root, encoding='utf8', method='xml')
                xml_dict = xmltodict.parse(xmlstr)***REMOVED***'PhilterUCSF'***REMOVED***
                check_tags = root.find('TAGS')
                text = xml_dict***REMOVED***"TEXT"***REMOVED***
                if check_tags is not None:
                   tags_dict = xml_dict***REMOVED***"TAGS"***REMOVED***
                else:
                   tags_dict = None

                if file_id  not in gold_phi:
                   gold_phi***REMOVED***file_id***REMOVED*** = {}
                # the existence of puncs in text makes the end index inaccurate - only use start index as the key
                if tags_dict is not None: 

                   for key, value in tags_dict.items():
                       if isinstance(value, list):
                          for final_value in value:
                              #start = int(final_value***REMOVED***"@start"***REMOVED***)
                              #end = int(final_value***REMOVED***"@end"***REMOVED***)
                              start = int(final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED***)
                              end = int(final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***)
                              text = final_value***REMOVED***"@text"***REMOVED***.translate(translator)
                              phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                              gold_phi***REMOVED***file_id***REMOVED***.update({start:***REMOVED***end,phi_type,text***REMOVED***})

                       else:
                          final_value = value
                          #start = int(final_value***REMOVED***"@start"***REMOVED***)
                          start = int(final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED***)
                          #end = int(final_value***REMOVED***"@end"***REMOVED***)
                          end = int(final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***)
                          text = final_value***REMOVED***"@text"***REMOVED***.translate(translator)
                          phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                          gold_phi***REMOVED***file_id***REMOVED***.update({start:***REMOVED***end, phi_type, text***REMOVED***})
       
        # converting self.types to an easier accessible data structure
        eval_table = {}
        phi_table = {}
        non_phi = {}
        for phi_type in self.types:
            for filename, start, end in self.types***REMOVED***phi_type***REMOVED******REMOVED***0***REMOVED***.scan():
                word = self.texts***REMOVED***filename***REMOVED******REMOVED***start:end***REMOVED***.translate(translator)
                #print(filename + "\t" + str(start) + "\t" + str(end) +"\t" + word)
                if filename not in phi_table:
                    phi_table***REMOVED***filename***REMOVED*** = {}
                phi_table***REMOVED***filename***REMOVED***.update({start:***REMOVED***end, phi_type, word***REMOVED***})
        for filename in gold_phi:
            if filename not in eval_table:
                eval_table***REMOVED***filename***REMOVED*** = {'fp':{},'tp':{},'fn':{},'tn':{}}
            # each ele contains an annotated phi
            # token_set = self._get_clean(self.texts***REMOVED***filename***REMOVED***)
            text = self.texts***REMOVED***filename***REMOVED***
            for start in gold_phi***REMOVED***filename***REMOVED***:
                gold_start = start
                gold_end = gold_phi***REMOVED***filename***REMOVED******REMOVED***start***REMOVED******REMOVED***0***REMOVED***
                gold_type = gold_phi***REMOVED***filename***REMOVED******REMOVED***start***REMOVED******REMOVED***1***REMOVED***
                gold_word = gold_phi***REMOVED***filename***REMOVED******REMOVED***start***REMOVED******REMOVED***2***REMOVED***
                #print(filename + "\t" + gold_start + "\t" + gold_end +"\t" + gold_word)
                # remove phi from text to form the non_phi_set
                text = text.replace(gold_word, '')
                
                if filename in phi_table:
                    # is phi and is caught -> TP
                    if gold_start in phi_table***REMOVED***filename***REMOVED***:
                        word = phi_table***REMOVED***filename***REMOVED******REMOVED***gold_start***REMOVED******REMOVED***2***REMOVED***
                        if word == gold_word:
                            if gold_type not in eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED***:
                                eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED******REMOVED***gold_type***REMOVED*** = ***REMOVED******REMOVED***
                            eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED******REMOVED***gold_type***REMOVED***.append(word)
                    # is phi but not caught -> FN
                    else:
                        #print("fn" + filename + "\t" + gold_start + "\t" + gold_end +"\t" + gold_word)
                        # word = phi_table***REMOVED***filename***REMOVED******REMOVED***gold_start***REMOVED******REMOVED***2***REMOVED***
                        if gold_type not in eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED***:
                            eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED******REMOVED***gold_type***REMOVED*** = ***REMOVED******REMOVED***
                        eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED******REMOVED***gold_type***REMOVED***.append(gold_word)
                else:
                    print (filename + ' not processed by philter or check filename!')
                    continue
            non_phi***REMOVED***filename***REMOVED*** = self._get_clean(text)
        for filename in phi_table:
            if filename in gold_phi:
                if filename not in eval_table:
                    eval_table***REMOVED***filename***REMOVED*** = {'fp':{},'tp':{},'fn':{},'tn':***REMOVED******REMOVED***}
                for start in phi_table***REMOVED***filename***REMOVED***:
                    end = phi_table***REMOVED***filename***REMOVED******REMOVED***start***REMOVED******REMOVED***0***REMOVED***
                    phi_type = phi_table***REMOVED***filename***REMOVED******REMOVED***start***REMOVED******REMOVED***1***REMOVED***
                    word = phi_table***REMOVED***filename***REMOVED******REMOVED***start***REMOVED******REMOVED***2***REMOVED***
                    #print (""+"\t"+word + "\t" + str(start))
                    # word caught but is not phi -> FP
                    if start not in gold_phi***REMOVED***filename***REMOVED***:
                        #print ("fp" + "\t" + filename + "\t" + word + "\t" + str(start))
                        if phi_type not in eval_table***REMOVED***filename***REMOVED******REMOVED***'fp'***REMOVED***:
                            eval_table***REMOVED***filename***REMOVED******REMOVED***'fp'***REMOVED******REMOVED***phi_type***REMOVED*** = ***REMOVED******REMOVED***
                            eval_table***REMOVED***filename***REMOVED******REMOVED***'fp'***REMOVED******REMOVED***phi_type***REMOVED***.append(word)
                            if word in non_phi***REMOVED***filename***REMOVED***:
                                non_phi***REMOVED***filename***REMOVED***.remove(word)
            else:
                print (filename + ' not found!')
        # the rest is all TN
        for filename in non_phi:
            if filename not in eval_table:
                eval_table***REMOVED***filename***REMOVED*** = {'fp':{},'tp':{},'fn':{},'tn':{}}
            eval_table***REMOVED***filename***REMOVED******REMOVED***'tn'***REMOVED*** = non_phi***REMOVED***filename***REMOVED***

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
                summary_by_file***REMOVED***filename***REMOVED*** = {}
            for phi_type in eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED***:
                tp += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED******REMOVED***phi_type***REMOVED***)
                total_tp += tp
                if phi_type not in summary_by_category:
                    summary_by_category***REMOVED***phi_type***REMOVED*** = {}
                if 'tp' not in summary_by_category***REMOVED***phi_type***REMOVED***:
                    summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'tp'***REMOVED*** = ***REMOVED******REMOVED***
                summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'tp'***REMOVED***.append(eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED******REMOVED***phi_type***REMOVED***)
            for phi_type in eval_table***REMOVED***filename***REMOVED******REMOVED***'fp'***REMOVED***:
                fp += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'fp'***REMOVED******REMOVED***phi_type***REMOVED***)
                total_fp += fp
                if phi_type not in summary_by_category:
                    summary_by_category***REMOVED***phi_type***REMOVED*** = {}
                if 'fp' not in summary_by_category***REMOVED***phi_type***REMOVED***:
                    summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fp'***REMOVED*** = ***REMOVED******REMOVED***
                summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fp'***REMOVED***.append(eval_table***REMOVED***filename***REMOVED******REMOVED***'fp'***REMOVED******REMOVED***phi_type***REMOVED***)
            for phi_type in eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED***:
                tp += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED******REMOVED***phi_type***REMOVED***)
                total_tp += tp
                if phi_type not in summary_by_category:
                    summary_by_category***REMOVED***phi_type***REMOVED*** = {}
                if 'fn' not in summary_by_category***REMOVED***phi_type***REMOVED***:
                    summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fn'***REMOVED*** = ***REMOVED******REMOVED***
                summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fn'***REMOVED***.append(eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED******REMOVED***phi_type***REMOVED***)
            tn = len(eval_table***REMOVED***filename***REMOVED******REMOVED***'tn'***REMOVED***)
            total_tn += tn
            try:  
               precision = tp / (tp + fp)
            except ZeroDivisionError:
               precision = 0
            try:  
               recall = tp / (tp + fn)
            except ZeroDivisionError:
               recall = 0
            summary_by_file***REMOVED***filename***REMOVED***.update({'tp':tp, 'fp': fp, 'fn':fn, 'tn':tn, 'recall':recall,'precision':precision})
            # summary_by_category***REMOVED***filename***REMOVED***.update({'tp':tp, 'fp': fp, 'fn':fn, 'tn':tn, 'recall':recall,'precision':precision})
        
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



            

                    





        


                

        

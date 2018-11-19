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
        self.sub = Subs(note_info_path = None, re_id_pat_path = None)
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
                fhandle = open(filepath, "r", encoding=encoding***REMOVED***'encoding'***REMOVED***)
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
                    normalized_token = self.sub.parse_date(token)                  
                    self.norms***REMOVED***phi_type***REMOVED*** ***REMOVED***(filename, start)***REMOVED*** = (normalized_token, end)
                
            else:
                continue

        # TODO: what do we do when phi could not be interpreted?
        # e.g. change phi type to OTHER?
        # or scramble?
        # or use self.norms="unknown <type>" with <type>=self.types

        # Note: this is currently done in surrogator.shift_dates(), surrogator.parse_and_shift_date(), parse_date_ranges(), replace_other_surrogate()
        
    def substitute_phi(self):
        assert self.norms, "No normalized PHI defined"
        
        if self.subs:
            return

        self.subser = Subs(look_up_table_path)

        for phi_type in self.norms.keys():
            if phi_type == "DATE" or phi_type == "Date":
                for filename, start in self.norms***REMOVED***phi_type***REMOVED***:
                    normalized_token = self.norms***REMOVED***phi_type***REMOVED******REMOVED***filename, start***REMOVED******REMOVED***0***REMOVED***
                    end = self.norms***REMOVED***phi_type***REMOVED******REMOVED***filename, start***REMOVED******REMOVED***1***REMOVED***

                    # Added for eval
                    if normalized_token is None:
                        # self.eval_table***REMOVED***filename***REMOVED******REMOVED***start***REMOVED***.update({'sub':None})
                        continue
                    #TODO: why don't we make the lookup by the filename instead of patient_id
                    substitute_token = self.sub.date_to_string(self.sub.shift_date_pid(normalized_token, filename))
                    # self.eval_table***REMOVED***filename***REMOVED******REMOVED***start***REMOVED***.update({'sub':substitute_token})
                    self.subs***REMOVED***(filename, start)***REMOVED*** = (substitute_token, end)
            else:
                continue


    def transform(self):
        assert self.texts, "No texts defined"

        if not self.coords:
            self.textsout = self.texts
            print("WARNING: No PHI coordinates defined: nothing to transform!")
        else:
            assert self.subs, "No surrogated PHI defined"
                
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


    def save(self, outputdir):
        assert self.textsout, "Cannot save text: output not ready"
        if not outputdir:
            raise Exception("Output directory undefined: ", outputdir)

        for filename in self.filenames:
            fbase, fext = os.path.splitext(filename)
            fbase = fbase.split('/')***REMOVED***-1***REMOVED***
            filepath = outputdir + fbase + "_subs.txt"
            with open(filepath, "w", encoding='utf-8') as fhandle:
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
                normalized_token = self.sub.date_to_string(normalized_date)
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
    



            

                    





        


                

        

import os
from chardet.universaldetector import UniversalDetector
import re
import json
from subs import Subs
from coordinate_map import CoordinateMap
from lxml import etree as ET
import xmltodict
from philter import Philter
from subs import Subs
import string
from knownphi import Knownphi

class Phitexts:
    """ container for texts, phi, attributes """

    def __init__(self, inputdir, xml=False):
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
        if not xml:
           self._read_texts()
        self.subser = None
        self.filterer = None

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
            filename = (filename.replace('_utf8','')).replace('.txt','')   
            philter_or_gold = 'PhilterUCSF' 
            xml_filenames.append(filename)
            encoding = self._detect_encoding(filepath)
            fhandle = open(filepath, "r", encoding=encoding***REMOVED***'encoding'***REMOVED***)
            input_xml = fhandle.read() 
            tree = ET.parse(filepath)
            root = tree.getroot()
            xmlstr = ET.tostring(root, encoding='utf8', method='xml')
            xml_texts***REMOVED***filename***REMOVED*** = root.find('TEXT').text
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
                          xml_coordinate_map***REMOVED***int(text_start)***REMOVED*** = int(text_end)  
                          if xml_phi_type not in phi_type_list:
                              phi_type_list.append(xml_phi_type)
                          for phi_type in phi_type_list:
                              if phi_type not in phi_type_dict:
                                 phi_type_dict***REMOVED***phi_type***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
                          
                          #phi_type_dict***REMOVED***xml_phi_type***REMOVED******REMOVED***0***REMOVED***.add_file(filename)
                          phi_type_dict***REMOVED***xml_phi_type***REMOVED******REMOVED***0***REMOVED***.add_extend(filename,int(text_start),int(text_end))
                   else:
                       final_value = value
                       text = final_value***REMOVED***"@text"***REMOVED***
                       xml_phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                       text_start = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***0***REMOVED***
                       text_end = final_value***REMOVED***"@spans"***REMOVED***.split('~')***REMOVED***1***REMOVED***
                       xml_coordinate_map***REMOVED***int(text_start)***REMOVED*** = int(text_end)
                       if xml_phi_type not in phi_type_list:
                           phi_type_list.append(xml_phi_type)
                       for phi_type in phi_type_list:
                           if phi_type not in phi_type_dict:
                                 phi_type_dict***REMOVED***phi_type***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
                       #phi_type_dict***REMOVED***xml_phi_type***REMOVED******REMOVED***0***REMOVED***.add_file(filename)
                       phi_type_dict***REMOVED***xml_phi_type***REMOVED******REMOVED***0***REMOVED***.add_extend(filename,int(text_start),int(text_end))
            full_xml_map***REMOVED***filename***REMOVED*** = xml_coordinate_map
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


    def _get_clean(self, text, punctuation_matcher=re.compile(r"***REMOVED***^a-zA-Z0-9***REMOVED***")):

            # Use pre-process to split sentence by spaces AND symbols, while preserving spaces in the split list
        #lst = re.split("***REMOVED***(\s+)/-***REMOVED***", text)
        lst = re.findall(r"***REMOVED***\w'***REMOVED***+",text)
        cleaned = ***REMOVED******REMOVED***
        for item in lst:
            if len(item) > 0:
                if item.isspace() == False:
                    split_item = re.split("(\s+)", re.sub(punctuation_matcher, " ", item))
                    for elem in split_item:
                        if len(elem) > 0:
                           cleaned.append(elem)
                #else:
                #     cleaned.append(item)
        return cleaned

    def detect_xml_phi(self):
        if self.coords:
           return
        self.coords, self.types, self.texts, self.filenames = self.__read_xml_into_coordinateMap(self.inputdir) 


    def detect_phi(self, filters="./configs/philter_alpha.json"):
        assert self.texts, "No texts defined"
        
        if self.coords:
            return
        
        philter_config = {
            "verbose":False,
            "run_eval":False,
            "finpath":self.inputdir,
            "filters":filters#,
            #"outformat":"asterisk"
        }

        self.filterer = Philter(philter_config)
        self.coords = self.filterer.map_coordinates()


    def detect_phi_types(self):
        assert self.texts, "No texts defined"
        assert self.coords, "No PHI coordinates defined"
        
        if self.types:
            return
        self.types = self.filterer.phi_type_dict
        
    def detect_known_phi(self, knownphifile = "./data/knownphi.txt"):
        assert self.coords, "No PHI coordinates defined"
        assert self.texts, "No texts defined"
        assert self.types, "No PHI types defined"

        self.knownphi = Knownphi(knownphifile, self.coords, self.texts, self.types)
        self.coords, self.types = self.knownphi.update_coordinatemap()


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

        # Note: this is currently done in surrogator.shift_dates(), surrogator.parse_and_shift_date(), parse_date_ranges(), replace_other_surrogate()
        
    def substitute_phi(self, look_up_table_path = None):
        assert self.norms, "No normalized PHI defined"
        
        if self.subs:
            return

        self.subser = Subs(look_up_table_path)

        for phi_type in self.norms.keys():
            if phi_type == "DATE" or phi_type == "Date":
                if __debug__: nodateshiftlist = ***REMOVED******REMOVED***
                for filename, start in self.norms***REMOVED***phi_type***REMOVED***:
                    note_key_ucsf = os.path.splitext(os.path.basename(filename).strip('0'))***REMOVED***0***REMOVED***
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
            with open(filepath, "w", encoding='utf-8', errors='surrogateescape') as fhandle:
                fhandle.write(self.textsout***REMOVED***filename***REMOVED***)
    
    def print_log(self, output_dir):
        log_dir = os.path.join(output_dir, 'log/')
        failed_dates_file = os.path.join(log_dir, 'failed_dates.json')
        date_table_file = os.path.join(log_dir, 'parsed_dates.json')
        phi_count_file = os.path.join(log_dir, 'phi_count.log')
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
                eval_table***REMOVED***filename***REMOVED***.append({'start':start, 'end':end,
                                             'raw': raw,
                                             'normalized': normalized_token,
                                             'sub': sub})
                    # f_parsed.write('\t'.join(***REMOVED***filename, str(start), str(end), raw, normalized_token, sub***REMOVED***))
                    # f_parsed.write('\n')
            else:
                num_failed += 1
                    # f_failed.write('\t'.join(***REMOVED***filename, str(start), str(end), raw.strip('\n')***REMOVED***))
                    # f_failed.write('\n')
                if filename not in failed_date:
                        failed_date***REMOVED***filename***REMOVED*** = ***REMOVED******REMOVED***
                failed_date***REMOVED***filename***REMOVED***.append({'start':start, 'end':end,
                                              'raw': raw})

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

    def _get_tokens(self, string):
        tokens = {}
        str_split = self._get_clean(string)
                
        offset = 0
        for item in str_split:
            item_stripped = item.strip()
            if len(item_stripped) is 0:
                offset += len(item)
                continue
            token_start = string.find(item_stripped, offset)
            if token_start is -1:
                raise Exception("ERROR: cannot find token \"{0}\" in \"{1}\" starting at {2} in file {3}".format(item, string, offset))
            token_stop = token_start + len(item_stripped) - 1
            offset = token_stop + 1
            tokens.update({token_start:***REMOVED***token_stop,item_stripped***REMOVED***})
    
        return tokens

    def _get_phi_type(self, filename, start, stop):
        for phi_type in self.types.keys():
            for begin,end in self.types***REMOVED***phi_type***REMOVED******REMOVED***0***REMOVED***.filecoords(filename):
                if start == begin:
                    return phi_type
        return None
    
    def _tokenize_philter_phi(self, filename):
        exclude_dict = self.coords***REMOVED***filename***REMOVED***
        updated_dict = {}
        for i in exclude_dict:
            start, end = i, exclude_dict***REMOVED***i***REMOVED***
            phi_type = self._get_phi_type(filename, start, end)
            word = self.texts***REMOVED***filename***REMOVED******REMOVED***start:end***REMOVED***
            
            try:
                tokens = self._get_tokens(word)
            except Exception as err:
                raise Exception("ERROR: cannot get tokens in \"{0}\" starting at {1} in file {2}: {3}".format(word, start, filename, err))
            
            for tstart in tokens:
                token_start = tstart + start
                token_stop = tokens***REMOVED***tstart***REMOVED******REMOVED***0***REMOVED*** + start
                token = tokens***REMOVED***tstart***REMOVED******REMOVED***1***REMOVED***
                updated_dict.update({token_start:***REMOVED***token_stop, phi_type, token***REMOVED***})
        return updated_dict
    


    def eval_start_match(self, start, input_dict):
          
        if start in input_dict:
           return True
        else:
           return False 
 
    def eval_overlap_match(self, start, end, input_dict, dict_type):
        for input_dict_start in input_dict:
            if dict_type == "gold":
               input_dict_end = input_dict***REMOVED***input_dict_start***REMOVED******REMOVED***0***REMOVED***
            else:
               input_dict_end = input_dict***REMOVED***input_dict_start***REMOVED***
            if input_dict_end >= end and start >= input_dict_start:
               return True
        return False       
            
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
    
    def _get_gold_phi(self, anno_dir):
        gold_phi = {}
        for root, dirs, files in os.walk(anno_dir):
            for filename in files:
                if not filename.endswith("xml"):
                    continue
                print("root: " + str(root) + " filename: " + str(filename))
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
                                tokens = self._get_tokens(text)
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

    def _get_philter_phi(self, filenames):
        philter_phi = {}
        for filename in filenames:
            philter_phi***REMOVED***filename***REMOVED*** = self._tokenize_philter_phi(filename)
        return philter_phi
    
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
    
    def _get_tp_dicts(self, gold_dicts, philter_dicts):
        tp_dicts = {}
        for filename in gold_dicts:
            tp_dicts***REMOVED***filename***REMOVED*** = {}
            keys = gold_dicts***REMOVED***filename***REMOVED***.keys() & philter_dicts***REMOVED***filename***REMOVED***.keys()
            for k in keys:
                tp_dicts***REMOVED***filename***REMOVED***.update({k:gold_dicts***REMOVED***filename***REMOVED******REMOVED***k***REMOVED***})
        return tp_dicts
    
    def _get_fp_dicts(self, gold_dicts, philter_dicts):
        fp_dicts = {}
        for filename in gold_dicts:
            fp_dicts***REMOVED***filename***REMOVED*** = {}
            keys = philter_dicts***REMOVED***filename***REMOVED***.keys() - gold_dicts***REMOVED***filename***REMOVED***.keys()
            for k in keys:
                fp_dicts***REMOVED***filename***REMOVED***.update({k:philter_dicts***REMOVED***filename***REMOVED******REMOVED***k***REMOVED***})
        return fp_dicts
    
    def _get_tn_dicts(self, full_dicts, gold_dicts, philter_dicts):
        tn_dicts = {}
        for filename in gold_dicts:
            tn_dicts***REMOVED***filename***REMOVED*** = {}
            keys = (full_dicts***REMOVED***filename***REMOVED***.keys() - gold_dicts***REMOVED***filename***REMOVED***.keys()
                    - philter_dicts***REMOVED***filename***REMOVED***.keys())
            for k in keys:
                tn_dicts***REMOVED***filename***REMOVED***.update({k:full_dicts***REMOVED***filename***REMOVED******REMOVED***k***REMOVED***})
        return tn_dicts
    
    def _get_fn_dicts(self, gold_dicts, philter_dicts):
        fn_dicts = {}
        for filename in gold_dicts:
            fn_dicts***REMOVED***filename***REMOVED*** = {}
            keys = gold_dicts***REMOVED***filename***REMOVED***.keys() - philter_dicts***REMOVED***filename***REMOVED***.keys()
            for k in keys:
                fn_dicts***REMOVED***filename***REMOVED***.update({k:gold_dicts***REMOVED***filename***REMOVED******REMOVED***k***REMOVED***})
        return fn_dicts

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
    
    def _get_fulltext_dicts(self, gold_dicts, philter_dicts):
        fulltext_dicts = {}
        for filename in gold_dicts:
            fulltext_dicts***REMOVED***filename***REMOVED*** = self._get_tokens(self.texts***REMOVED***filename***REMOVED***)
                
        self._sub_tokenize(fulltext_dicts, gold_dicts)
        self._sub_tokenize(fulltext_dicts, philter_dicts)
        
        return fulltext_dicts
                                          
    def eval(self, anno_dir, output_dir):
        # preserve these two puncs so that dates are complete

        ### TO DO: eval should be using read_xml_into_coordinateMap for reading the xml
        ######### Create a get function to get Lu's data structure given the coordinate maps
        
        include_tags = {'Age','Diagnosis_Code_ICD_or_International','Medical4_Department_Name','Patient_Language_Spoken','Patient_Place_Of_Work_or_Occupation','Medical_Research_Study_Name_or_Number','Teaching_Institution_Name','Non_UCSF_Medical_Institution_Name','Medical_Institution_Abbreviation', 'Unclear'}
        eval_dir = os.path.join(output_dir, 'eval/')
        summary_file = os.path.join(eval_dir, 'summary.json')
        json_summary_by_file = os.path.join(eval_dir, 'summary_by_file.json')
        json_summary_by_category = os.path.join(eval_dir, 'summary_by_category.json')
        if not os.path.isdir(eval_dir):
            os.makedirs(eval_dir)       


        text_fp_file = open(os.path.join(eval_dir,'fp.eval'),"w+")
        text_tp_file = open(os.path.join(eval_dir,'tp.eval'),"w+")
        text_fn_file = open(os.path.join(eval_dir,'fn.eval'),"w+")
        text_tn_file = open(os.path.join(eval_dir,'tn.eval'),"w+")


        gold_dicts = self._get_gold_phi(anno_dir)
        philter_dicts = self._get_philter_phi(gold_dicts.keys())
        self._update_with_sub_tokens(gold_dicts, philter_dicts)
        fulltext_dicts = self._get_fulltext_dicts(gold_dicts, philter_dicts)

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
            
            total_tp += tp
            total_fp += fp
            total_tn += tn
            total_fn += fn
              
            try:  
               precision = tp / (tp + fp)
            except ZeroDivisionError:
               precision = 0
            try:  
               recall = tp / (tp + fn)
            except ZeroDivisionError:
               recall = 0
            summary_by_file***REMOVED***filename***REMOVED***.update({'tp':tp, 'fp': fp,
                                              'tn':tn, 'fn':fn,
                                              'recall':recall,
                                              'precision':precision})

            
            for st in truepositives_dicts***REMOVED***filename***REMOVED***:
                start = st
                stop = truepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                phi_type = truepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                token = truepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***2***REMOVED***
                text_tp_file.write('\n' + filename + '\t' + str(phi_type)
                                   + '\t' + token
                                   + '\t' + str(start) + '\t' + str(stop))
            for st in falsepositives_dicts***REMOVED***filename***REMOVED***:
                start = st
                stop = falsepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                phi_type = falsepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                token = falsepositives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***2***REMOVED***
                text_fp_file.write('\n' + filename + '\t' + str(phi_type)
                                   + '\t' + token
                                   + '\t' + str(start) + '\t' + str(stop))
            for st in truenegatives_dicts***REMOVED***filename***REMOVED***:
                start = st
                stop = truenegatives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                phi_type = None
                token = truenegatives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                text_tn_file.write('\n' + filename + '\t' + str(phi_type)
                                   + '\t' + token
                                   + '\t' + str(start) + '\t' + str(stop))
            for st in falsenegatives_dicts***REMOVED***filename***REMOVED***:
                start = st
                stop = falsenegatives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***0***REMOVED***
                phi_type = falsenegatives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***1***REMOVED***
                token = falsenegatives_dicts***REMOVED***filename***REMOVED******REMOVED***st***REMOVED******REMOVED***2***REMOVED***
                text_fn_file.write('\n' + filename + '\t' + str(phi_type)
                                   + '\t' + token
                                   + '\t' + str(start) + '\t' + str(stop))
            
            
        
        try:
           total_precision = total_tp / (total_tp + total_fp)
        except ZeroDivisionError:
           total_precision = 0     
        try:
           total_recall = total_tp / (total_tp + total_fn)
        except ZeroDivisionError:
           total_recall = 0
        total_summary = {'tp':total_tp, 'fp':total_fp,
                         'tn':total_tn, 'fn':total_fn,
                         'precision':total_precision, 'recall':total_recall}
        json.dump(total_summary, open(summary_file, "w"), indent=4)
        json.dump(summary_by_file, open(json_summary_by_file, "w"), indent=4)

        text_tp_file.close()
        text_fp_file.close()
        text_tn_file.close()
        text_fn_file.close()
        

        
        # summary_by_category = {}
        # summary_by_file = {}
        # total_tp = 0
        # total_fn = 0
        # total_tn = 0
        # total_fp = 0
        # for filename in eval_table:
        #     # file-level counters
        #     tp = 0
        #     fn = 0
        #     tn = 0
        #     fp = 0
        #     if filename not in summary_by_file:
        #         summary_by_file***REMOVED***filename***REMOVED*** = {}
        #     for phi_type in eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED***:
        #         if phi_type not in include_tags:
        #            tp += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED******REMOVED***phi_type***REMOVED***)
        #            total_tp += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED******REMOVED***phi_type***REMOVED***)
        #            if phi_type not in summary_by_category:
        #               summary_by_category***REMOVED***phi_type***REMOVED*** = {}
        #            if 'tp' not in summary_by_category***REMOVED***phi_type***REMOVED***:
        #               summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'tp'***REMOVED*** = ***REMOVED******REMOVED***
        #            summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'tp'***REMOVED***.append(eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED******REMOVED***phi_type***REMOVED***)
        #            text_tp_file.write('\n'+filename+'\t' + phi_type + '\t')
        #            tp_to_file = ('\n' + filename +'\t'+ phi_type + '\t').join(eval_table***REMOVED***filename***REMOVED******REMOVED***"tp"***REMOVED******REMOVED***phi_type***REMOVED***)
        #            text_tp_file.write(tp_to_file)
        #         else:
        #            fp += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED******REMOVED***phi_type***REMOVED***)
        #            total_fp += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED******REMOVED***phi_type***REMOVED***)
        #            if phi_type not in summary_by_category:
        #               summary_by_category***REMOVED***phi_type***REMOVED*** = {}
        #            if 'fp' not in summary_by_category***REMOVED***phi_type***REMOVED***:
        #               summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fp'***REMOVED*** = ***REMOVED******REMOVED***
        #            summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fp'***REMOVED***.append(eval_table***REMOVED***filename***REMOVED******REMOVED***'tp'***REMOVED******REMOVED***phi_type***REMOVED***) 
        #            text_fp_file.write('\n'+filename+ '\t'+ phi_type + '\t')
        #            fp_to_file = ('\n'+ filename + '\t'+ phi_type + '\t').join(eval_table***REMOVED***filename***REMOVED******REMOVED***"tp"***REMOVED******REMOVED***phi_type***REMOVED***) 
        #            text_fp_file.write(fp_to_file)
        #     for phi_type in eval_table***REMOVED***filename***REMOVED******REMOVED***'fp'***REMOVED***:
        #         fp += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'fp'***REMOVED******REMOVED***phi_type***REMOVED***)
        #         total_fp += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'fp'***REMOVED******REMOVED***phi_type***REMOVED***)
        #         if phi_type not in summary_by_category:
        #             summary_by_category***REMOVED***phi_type***REMOVED*** = {}
        #         if 'fp' not in summary_by_category***REMOVED***phi_type***REMOVED***:
        #             summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fp'***REMOVED*** = ***REMOVED******REMOVED***
        #         summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fp'***REMOVED***.append(eval_table***REMOVED***filename***REMOVED******REMOVED***'fp'***REMOVED******REMOVED***phi_type***REMOVED***)
        #         text_fp_file.write('\n'+ filename + '\t'+ phi_type + '\t')
        #         fp_to_file = ('\n' + filename + '\t'+ phi_type + '\t').join(eval_table***REMOVED***filename***REMOVED******REMOVED***"fp"***REMOVED******REMOVED***phi_type***REMOVED***)
        #         text_fp_file.write(fp_to_file)
        #     for phi_type in eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED***:
        #         if phi_type not in include_tags:
        #            fn += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED******REMOVED***phi_type***REMOVED***)
        #            total_fn += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED******REMOVED***phi_type***REMOVED***)
        #            if phi_type not in summary_by_category:
        #               summary_by_category***REMOVED***phi_type***REMOVED*** = {}
        #            if 'fn' not in summary_by_category***REMOVED***phi_type***REMOVED***:
        #               summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fn'***REMOVED*** = ***REMOVED******REMOVED***
        #            summary_by_category***REMOVED***phi_type***REMOVED******REMOVED***'fn'***REMOVED***.append(eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED******REMOVED***phi_type***REMOVED***)
        #            text_fn_file.write('\n'+ filename + '\t'+ phi_type + '\t')
        #            fn_to_file = ('\n'+ filename + '\t'+ phi_type + '\t').join(eval_table***REMOVED***filename***REMOVED******REMOVED***"fn"***REMOVED******REMOVED***phi_type***REMOVED***)
        #            text_fn_file.write(fn_to_file)
        #         else:
        #            tn += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED******REMOVED***phi_type***REMOVED***)
        #            total_tn += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'fn'***REMOVED******REMOVED***phi_type***REMOVED***)
        #            text_tn_file.write('\n'+ filename + '\t'+ phi_type + '\t')
        #            tn_to_file = ('\n' + filename + '\t'+ phi_type + '\t').join(eval_table***REMOVED***filename***REMOVED******REMOVED***"fn"***REMOVED******REMOVED***phi_type***REMOVED***)
        #            text_tn_file.write(tn_to_file)
        #     tn += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'tn'***REMOVED***)
        #     total_tn += len(eval_table***REMOVED***filename***REMOVED******REMOVED***'tn'***REMOVED***)
        #     text_tn_file.write('\n'+ filename + '\t'+ phi_type + '\t') 
        #     tn_to_file = ('\n' + filename + '\t'+ phi_type + '\t').join(eval_table***REMOVED***filename***REMOVED******REMOVED***"tn"***REMOVED***)
        #     text_tn_file.write(tn_to_file) 
             
        #     try:  
        #        precision = tp / (tp + fp)
        #     except ZeroDivisionError:
        #        precision = 0
        #     try:  
        #        recall = tp / (tp + fn)
        #     except ZeroDivisionError:
        #        recall = 0
        #     summary_by_file***REMOVED***filename***REMOVED***.update({'tp':tp, 'fp': fp, 'fn':fn, 'tn':tn, 'recall':recall,'precision':precision})
        #     # summary_by_category***REMOVED***filename***REMOVED***.update({'tp':tp, 'fp': fp, 'fn':fn, 'tn':tn, 'recall':recall,'precision':precision})
        
        # try:
        #    total_precision = total_tp / (total_tp + total_fp)
        # except ZeroDivisionError:
        #    total_precision = 0     

        # try:
        #    total_recall = total_tp / (total_tp + total_fn)
        # except ZeroDivisionError:
        #    total_recall = 0
        # total_summary = {'tp':total_tp, 'tn':total_tn, 'fp':total_fp, 'fn':total_fn, 'precision':total_precision, 'recall':total_recall}
        # json.dump(total_summary, open(summary_file, "w"), indent=4)
        # json.dump(summary_by_file, open(json_summary_by_file, "w"), indent=4)
        # json.dump(summary_by_category, open(json_summary_by_category, "w"), indent=4)
        


            

                    





        


                

        

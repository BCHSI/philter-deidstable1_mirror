import os
from chardet.universaldetector import UniversalDetector
import re
from philter import Philter
import json
from subs import Subs

class Phitexts:
    """ container for texts, phi, attributes """

    def __init__(self, inputdir):
        self.inputdir  = inputdir
        self.filenames = []
        #self.note_keys = []
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
                fhandle = open(filepath, "r", encoding=encoding['encoding'], errors='surrogateescape')
                self.texts[filepath] = fhandle.read()
                fhandle.close()
        #self.note_keys = [os.path.splitext(os.path.basename(f).strip('0'))[0] for f in self.filenames]
            
                
    def _detect_encoding(self, fp):
        if not os.path.exists(fp):
            raise Exception("Filepath does not exist", fp)

        detector = UniversalDetector()
        #detector.MINIMUM_THRESHOLD = 0.2
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
            if phi_type == "DATE":
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
            if phi_type == "DATE":
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
        #    assert self.subs, "No surrogated PHI defined"
                
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
        failed_dates_file = os.path.join(log_dir, 'failed_dates.json')
        date_table_file = os.path.join(log_dir, 'parsed_dates.json')
        phi_count_file = os.path.join(log_dir, 'phi_count.txt')
        phi_marked_file = os.path.join(log_dir, 'phi_marked.json')

        eval_table = {}
        failed_date = {}
        phi_table = {}


        if os.path.isdir(log_dir ):
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
        for filename, start, end in self.types['DATE'][0].scan():
            raw = self.texts[filename][start:end]
            normalized_date = self.norms['DATE'][(filename,start)][0]
            if normalized_date is not None:
                normalized_token = self.subser.date_to_string(normalized_date)
                note_key_ucsf = os.path.splitext(os.path.basename(filename).strip('0'))[0]
                if not self.subser.has_shift_amount(note_key_ucsf):
                     sub = None
                else:
                     sub = self.subs[(filename,start)][0]
                num_parsed += 1
                if filename not in eval_table:
                    eval_table[filename] = []
                eval_table[filename].append({'start':start, 'end':end, 'raw': raw, 'normalized': normalized_token, 'sub': sub})
                    # f_parsed.write('\t'.join([filename, str(start), str(end), raw, normalized_token, sub]))
                    # f_parsed.write('\n')
            else:
                num_failed += 1
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
    



            

                    





        


                

        

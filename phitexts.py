import os
from chardet.universaldetector import UniversalDetector
import re
from philter import Philter
import json
from subs import Subs
import xml.etree.ElementTree as ET
import xmltodict
import string


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


        self._read_texts()
        self.sub = Subs(note_info_path = None, re_id_pat_path = None)
        self.filterer = None

    def _read_texts(self):
        if not self.inputdir:
            raise Exception("Input directory undefined: ", self.inputdir)

        for root, dirs, files in os.walk(self.inputdir):
            for filename in files:
                if not filename.endswith("txt"):
                    continue
                filepath = root +  filename
                self.filenames.append(filepath)
                encoding = self._detect_encoding(filepath)
                fhandle = open(filepath, "r", encoding=encoding['encoding'])
                self.texts[filepath] = fhandle.read()
                fhandle.close()
            
                
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
                    normalized_token = self.sub.parse_date(token)                  
                    self.norms[phi_type] [(filename, start)] = (normalized_token, end)
                
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

        for phi_type in self.norms.keys():
            if phi_type == "DATE":
                for filename, start in self.norms[phi_type]:
                    normalized_token = self.norms[phi_type][filename, start][0]
                    end = self.norms[phi_type][filename, start][1]

                    # Added for eval
                    if normalized_token is None:
                        # self.eval_table[filename][start].update({'sub':None})
                        continue
                    #TODO: why don't we make the lookup by the filename instead of patient_id
                    substitute_token = self.sub.date_to_string(self.sub.shift_date_pid(normalized_token, filename))
                    # self.eval_table[filename][start].update({'sub':substitute_token})
                    self.subs[(filename, start)] = (substitute_token, end)
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
            with open(filepath, "w", encoding='utf-8') as fhandle:
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
        for filename, start, end in self.types['DATE'][0].scan():
            raw = self.texts[filename][start:end]
            normalized_date = self.norms['DATE'][(filename,start)][0]
            if normalized_date is not None:
                normalized_token = self.sub.date_to_string(normalized_date)
                sub = self.subs[(filename,start)][0]
                num_parsed += 1
                if filename not in eval_table:
                    eval_table[filename] = []
                eval_table[filename].append({'start':start, 'end':end, 'raw': raw, 'normalized': normalized_token, 'sub': sub})
            else:
                num_failed += 1
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
            json.dump(failed_date, f, indent=4)
        with open(date_table_file, 'w') as f:
            json.dump(eval_table, f, indent=4)
        with open(phi_marked_file, 'w') as f:
            json.dump(phi_table, f, indent=4)
    
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
                if not filename.endswith("xml"):
                    continue                
                filepath = os.path.join(root, filename)
                # change here: what will the input format be?
                file_id = in_dir + filename.split('.')[0] + '.txt'
                tree = ET.parse(filepath)
                root = tree.getroot()
                xmlstr = ET.tostring(root, encoding='utf8', method='xml')
                xml_dict = xmltodict.parse(xmlstr)['deIdi2b2']
                text = xml_dict["TEXT"]
                tags_dict = xml_dict["TAGS"]
                if file_id  not in gold_phi:
                   gold_phi[file_id] = {}
                # the existence of puncs in text makes the end index inaccurate - only use start index as the key
                for key, value in tags_dict.items():
                    if isinstance(value, list):
                        for final_value in value:
                            start = int(final_value["@start"])
                            end = int(final_value["@end"])
                            text = final_value["@text"].translate(translator)
                            phi_type = final_value["@TYPE"]
                            gold_phi[file_id].update({start:[end,phi_type,text]})

                    else:
                        final_value = value
                        start = int(final_value["@start"])
                        end = int(final_value["@end"])
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
                    # print (word)
                    # word caught but is not phi -> FP
                    if start not in gold_phi:
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
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            summary_by_file[filename].update({'tp':tp, 'fp': fp, 'fn':fn, 'tn':tn, 'recall':recall,'precision':precision})
            # summary_by_category[filename].update({'tp':tp, 'fp': fp, 'fn':fn, 'tn':tn, 'recall':recall,'precision':precision})
        
       
        total_precision = total_tp / (total_tp + total_fp)
        total_recall = total_tp / (total_tp + total_fn)
        total_summary = {'tp':total_tp, 'tn':total_tn, 'fp':total_fp, 'fn':total_fn, 'precision':total_precision, 'recall':total_recall}
        json.dump(total_summary, open(summary_file, "w"), indent=4)
        json.dump(summary_by_file, open(json_summary_by_file, "w"), indent=4)
        json.dump(summary_by_category, open(json_summary_by_category, "w"), indent=4)


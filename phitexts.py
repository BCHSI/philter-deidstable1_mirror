import os
from chardet.universaldetector import UniversalDetector
import re
from philter import Philter
from subs import Subs

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
        self.sub = Subs()
        self.filterer = None



    def _read_texts(self):
        if not self.inputdir:
            raise Exception("Input directory undefined: ", self.inputdir)

        for root, dirs, files in os.walk(self.inputdir):
            for filename in files:
                if not filename.endswith("txt"):
                    continue
                filepath = root+filename
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
        #self.norms = 

        for phi_type in self.types.keys():
            self.norms[phi_type] = {}
        for phi_type in self.types.keys():
            if phi_type == "DATE":
                for filename, start, end in self.types[phi_type][0].scan():
                    token = self.texts[filename][start:end]
                    normalized_token = self.sub.parse_date(token)
                    self.norms[phi_type] [(filename, start)] = normalized_token 
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

        # TODO: look up surrogate for normalized phi
        # 1) look up surrogate map for current note key (TODO: where to get key from?)
        # 2) use map to swap out normalized phi by map value
        #    if no map value, use placeholder based on phi type, e.g. [[NAME]]
        #self.subs
        
        # Note: this is currently done in surrogator.shift_dates(), surrogator.parse_and_shift_date(), parse_date_ranges(), replace_other_surrogate()

        for phi_type in self.norms.keys():
            if phi_type == "DATE":
                for filename, start in self.norms[phi_type]:
                    normalized_token = self.norms[phi_type][filename, start]
                    if normalized_token is None:
                        continue
                    substitute_token = self.sub.date_to_string(self.sub.shift_date(normalized_token, 35))
                    self.subs[(filename, start)] = substitute_token

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
                        substitute_token = self.subs[filename, start]
                        contents.append(substitute_token)
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
            filepath = outputdir + fbase + "_subs.txt"
            with open(filepath, "w", encoding='utf-8') as fhandle:
                fhandle.write(self.textsout[filename])
                

        

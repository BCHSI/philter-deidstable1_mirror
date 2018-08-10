import os
from chardet.universaldetector import UniversalDetector

from philter import Philter


class Phitexts:
    """ container for texts, phi, attributes """

    def __init__(self, inputdir):
        self.inputdir  = inputdir
        self.filenames = []
        self.texts     = {}
        self.coords    = []
        self.types     = []
        self.norms     = []
        self.subs      = []
        self.textsout  = {}

        self._read_texts()

    def _read_texts(self):
        if not self.inputdir:
            raise Exception("Input directory undefined: ", self.inputdir)

        for root, dirs, files in os.walk(self.inputdir):
            for filename in files:
                self.filenames.append(filename)
                filepath = root+filename
                encoding = self._detect_encoding(filepath)
                fhandle = open(filepath, "r", encoding=encoding['encoding'])
                self.texts[filename] = fhandle.read()
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
            "filters":filters
        }
        filterer = Philter(philter_config)
        filterer.map_coordinates()

        
        # TODO: extract exclude map, see Philter.transform()
        #self.coords = filterer.get_combined_coord_maps()

    def detect_phi_types(self):
        assert self.texts, "No texts defined"
        assert self.coords, "No PHI coordinates defined"
        
        if self.types:
            return

        # TODO: extract or detect phi types
        # EITHER self.types = filterer.get_phitypes()
        # OR     self.types = detect_type(self.texts, self.phicoords)

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
        #self.textsout = 

    def save(self, outputdir):
        assert self.textsout, "Cannot save text: output not ready"
        if not outputdir:
            raise Exception("Output directory undefined: ", outputdir)

        for filename in self.filenames:
            fbase, fext = os.path.splitext(filename)
            filepath = outputdir + fbase + "_subs.txt"
            with open(filepath, "w", encoding='utf-8') as fhandle:
                fhandle.write(self.textsout[filename])
                

        

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
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import bson
import sys
import pandas as pd
from datetime import datetime
import socket
import datetime
#import memory_profiler
#import sys
#sys.stdout = LogFile('memory_profile_log')

class Phitexts:
    """ container for texts, phi, attributes """

    def __init__(self, inputdir = None, xml = False, batch = None, db = None, mongo = None):
        self.inputdir  = inputdir
        self.db = db
        self.mongo = mongo
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
        self.batch = batch
        #known phi
        self.known_phi = {}
        if not xml and not mongo:
           self._read_texts()
        if mongo is not None:
           if batch is not None:
              self._read_mongo(mongo,batch)
        self.subser = None
        self.filterer = None

    def get_mongo_handle(self, mongo):
        client = MongoClient(mongo***REMOVED***"client"***REMOVED***,username=mongo***REMOVED***"username"***REMOVED***,password=mongo***REMOVED***"password"***REMOVED***)
        try:
          db = client***REMOVED***mongo***REMOVED***'db'***REMOVED******REMOVED***
        except:
          print("Mongo Server not available")
        return db

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

    def _read_mongo(self, mongo, batch):
        db = self.db
        chunk_collection = db***REMOVED***mongo***REMOVED***'collection_chunk'***REMOVED******REMOVED***
        meta_status = db***REMOVED***mongo***REMOVED***'collection_status'***REMOVED******REMOVED***
        raw_note_text = db***REMOVED***mongo***REMOVED***'collection_raw_note_text'***REMOVED******REMOVED***
        meta_in = db***REMOVED***mongo***REMOVED***'collection_meta_data'***REMOVED******REMOVED*** 
        server = socket.gethostname() + ".ucsfmedicalcenter.org" 
        # list_of_mongo_ids = meta_status.find({"note_key_status": {"$in": ***REMOVED***'Add','Update'***REMOVED***}})
        #list_of_mongo_ids = chunk_collection.find({"batch": batch, "url":server.lower()},{"_id": 1})
        try:
          
           to_philter = chunk_collection.aggregate(***REMOVED***{"$match":{"$and":***REMOVED***{"url": server.lower()},{"batch": batch}***REMOVED***}},
                                                    {"$lookup": {"from": 'raw_note_text', "localField": "_id", "foreignField": "_id", "as": "get_text"}},
                                                    {"$unwind": {"path": "$get_text"}},
                                                    {"$project": {"_id": 1, "patient_ID": 1, "raw_note_text": "$get_text.raw_note_text"}}***REMOVED***)
           probes_name = chunk_collection.aggregate(***REMOVED***{"$match":{"$and":***REMOVED***{"url": server.lower()},{"batch": batch}***REMOVED***}},
                                                    {"$lookup": {"from": 'probes', "localField": "patient_ID", "foreignField": "person_id", "as": "prb"}},
                                                    {"$unwind":"$prb"},
                                                    {"$project": {"_id": 1, "patient_ID": 1, "probes_lname": "$prb.lname", "probes_fname": "$prb.fname"}}***REMOVED***)
        except pymongo.errors.OperationFailure as e:
           print(e.code)
           print(e.details)
        probes_list = list(probes_name)
        for philter in list(to_philter):
           self.filenames.append(philter***REMOVED***'_id'***REMOVED***)
           self.texts***REMOVED***philter***REMOVED***'_id'***REMOVED******REMOVED*** = philter***REMOVED***'raw_note_text'***REMOVED***
           if mongo***REMOVED***'known_phi'***REMOVED*** == True:
              probes = ***REMOVED******REMOVED***
              for prb in probes_list:
                  if philter***REMOVED***'_id'***REMOVED*** == prb***REMOVED***'_id'***REMOVED***:
                     if 'probes_lname' in prb and 'probes_fname' in prb: 
                        probes = prb***REMOVED***'probes_lname'***REMOVED*** + prb***REMOVED***'probes_fname'***REMOVED***
                     elif 'probes_lname' in prb and 'probes_fname' not in prb:
                        probes = prb***REMOVED***'probes_lname'***REMOVED***
                     elif 'probes_lname' not in prb and 'probes_fname' in prb:
                        probes = prb***REMOVED***'probes_fname'***REMOVED***
                     break;
              self.known_phi***REMOVED***philter***REMOVED***'_id'***REMOVED******REMOVED*** = probes

       

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

    def _get_tag_start_stop(self, tag_line):
        if "@spans" in tag_line.keys():
            start, stop = final_value***REMOVED***"@spans"***REMOVED***.split('~')
        elif "@start" and  "@end" in tag_line.keys():
            start = tag_line***REMOVED***"@start"***REMOVED***
            stop  = tag_line***REMOVED***"@end"***REMOVED***
        else:
            raise Exception("ERROR: cannot read tag_line: {0}".format(tag_line))
        return int(start), int(stop)
    
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
            xml_filenames.append(filepath)
            encoding = self._detect_encoding(filepath)
            fhandle = open(filepath, "r", encoding=encoding***REMOVED***'encoding'***REMOVED***)
            input_xml = fhandle.read() 
            tree = ET.parse(filepath)
            root = tree.getroot()
            xmlstr = ET.tostring(root, encoding='utf8', method='xml')
            xml_texts***REMOVED***filepath***REMOVED*** = root.find('TEXT').text
            xml_dict = xmltodict.parse(xmlstr)
            xml_dict = next(iter(xml_dict.values()))
            check_tags = root.find('TAGS')
                       
 
            if check_tags is not None:
                tags_dict = xml_dict***REMOVED***"TAGS"***REMOVED***            
            else:
                tags_dict = None
            if tags_dict is not None:
                for key, value in tags_dict.items():
                # Note:  Value can be a list of like phi elements
                #        or a dictionary of the metadata about a phi element
                    if not isinstance(value, list):
                        value = ***REMOVED***value***REMOVED***
                    for final_value in value:
                        text_start, text_end = self._get_tag_start_stop(final_value)
                        philter_text = final_value***REMOVED***"@text"***REMOVED***
                        xml_phi_type = final_value***REMOVED***"@TYPE"***REMOVED***
                        xml_coordinate_map.update(self._get_xml_tokens(philter_text, xml_texts***REMOVED***filepath***REMOVED***,int(text_start))) 
                        if xml_phi_type not in phi_type_list:
                            phi_type_list.append(xml_phi_type)
                        for phi_type in phi_type_list:
                            if phi_type not in phi_type_dict:
                                phi_type_dict***REMOVED***phi_type***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
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

        philter_config = {}
        philter_config***REMOVED***"verbose"***REMOVED*** = verbose
        philter_config***REMOVED***"run_eval"***REMOVED*** = False
        philter_config***REMOVED***"filters"***REMOVED*** = filters 
        if namesprobefile:     
           philter_config***REMOVED***"namesprobe"***REMOVED*** = namesprobefile
        if self.known_phi:
           philter_config***REMOVED***"known_phi"***REMOVED*** = self.known_phi
        philter_config***REMOVED***"phi_text"***REMOVED*** = self.texts
        philter_config***REMOVED***"filenames"***REMOVED*** = self.filenames
        
        self.filterer = Philter(philter_config)
        self.coords = self.filterer.map_coordinates()
        print("Coordinates Identified")
        self.pos = self.filterer.pos_tags
        print("Pos_tags identified") 
    def detect_phi_types(self):
        assert self.texts, "No texts defined"
        assert self.coords, "No PHI coordinates defined"
        
        if self.types:
            return
        self.types = self.filterer.phi_type_dict
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
                xml_dict = xmltodict.parse(xmlstr)
                xml_dict = next(iter(xml_dict.values()))
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
#                            print("final_value: " + )
                            start, end = self._get_tag_start_stop(final_value)
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

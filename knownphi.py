import os
import pandas as pd
from coordinate_map import CoordinateMap
import re
from philter import Philter
import nltk 
class Knownphi:

   def __init__(self, knownphifile, coordinates, note_text, phi_type,pos_tags):
       self.postags = pos_tags
       #print(self.postags)
       self.knownphifile = knownphifile
       #coordinates of PHI
       self.coords = coordinates
       self.knownphitable = self._read_knownphi()
       self.texts = note_text       
       self.phi_types = phi_type
       self.known_phi = {}
   '''
   def get_pos(filename, cleaned):
       if filename not in self.pos_tags:
          self.pos_tags = {}
       self.pos_tags[filename] = nltk.pos_tag(cleaned)
       return self.pos_tags[filename]
   '''
   def _read_knownphi(self):
       if not self.knownphifile:
            raise Exception("Input known phi file is undefined: ", self.knownphifile)
       knownphi_table = pd.read_csv(self.knownphifile, sep='\t', index_col=False, usecols=['patient_ID', 'phi_type', 'clean_value', 'note_key'], dtype=str)
       return knownphi_table  
   @staticmethod 
   def _get_clean(text, punctuation_matcher=re.compile(r"[^a-zA-Z0-9]")):

            # Use pre-process to split sentence by spaces AND symbols, while preserving spaces in the split list
        #lst = re.split("[(\s+)/-]", text)
        lst = re.findall(r"[\w']+",text)
        cleaned = []
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
   
   # tokenizes a string
   @staticmethod
   def _get_tokens(string):
       tokens = {}
       str_split = Knownphi._get_clean(string)
               
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
           tokens.update({token_start:[token_stop,item_stripped]})
   
       return tokens
   
   def get_postag(self, kp_start, kp):
        for item in self.postags:
           start_coordinate = 0           
           for i in self.postags[item]:
              word = i[0]
              pos = i[1]
              start = start_coordinate
              stop = start_coordinate + len(word)

              # This converts spaces into empty strings, so we know to skip forward to the next real word
              word_clean = re.sub(r"[^a-zA-Z0-9]+", "", word.lower().strip())
              if len(word_clean) == 0:
                 #got a blank space or something without any characters or digits, move forward
                 start_coordinate += len(word)
                 continue
              if word.lower() == kp.lower():
                 if start == kp_start:
                    return pos
            
            #advance our start coordinate
              start_coordinate += len(word) 
        return "No pos"     

   def  update_coordinatemap(self):
       ''' Updates self.coords with known phi identified data'''
       
       file_note_key = ""
       note_key2knownphi_dict = pd.Series(self.knownphitable.note_key.values, index=self.knownphitable.clean_value).to_dict()
       for key in self.texts:
           tokenize = Knownphi._get_tokens(self.texts[key])
           for elem in key.split('/'):
               if (elem.find('.txt') != -1) or (elem.find('.xml') != -1):
                   elem = elem.replace('\n','')
                   elem = elem.replace('.txt','')
                   elem = elem.lstrip('0')
                   elem = elem.replace('.xml','')
                   elem = elem.replace('_utf8','')
                   file_note_key = elem  
           for knownphi in note_key2knownphi_dict:
               if note_key2knownphi_dict[knownphi] == file_note_key:
                  #for start in tokenize:
                  #     if knownphi.lower() == tokenize[start][1].lower():
                        #stop = tokenize[start][0]
                        #print("Found a Known PHI!" + str(knownphi) + ":" +file_note_key)
                  self.add_knownphi(key, file_note_key, tokenize, knownphi)
       return self.coords, self.phi_types, self.known_phi

   def update_phi_type(self,filename, file_note_key, start, stop):
       ''' Update the phi_type with new phi_types from known phi '''
       knownphitype_dict = pd.Series(self.knownphitable.phi_type.values, index=self.knownphitable.clean_value).to_dict()
       for types in knownphitype_dict:
           if types not in self.phi_types:
              self.phi_types[types] = [CoordinateMap()]
           print("types updated:" + types)
           self.phi_types[types][0].add_extend(filename,int(start),int(end))
   

   def add_knownphi(self, filename, file_note_key, tokenize, knownphi):
       ''' adds a new coordinate to the self.coords dict
                 This always rejects any overlapping hits '''
       if isinstance(knownphi,str):
          for start in tokenize:
              if knownphi.lower() == tokenize[start][1].lower():
                 stop = tokenize[start][0]
                 types = self.knownphitable.loc[self.knownphitable['clean_value'] == knownphi, 'phi_type'].iloc[0]
                 if types == 'lname' or types == 'fname':
                    if filename in self.coords: 
                       if start in self.coords[filename]:          
                          ''' check overlap '''
                          if stop > self.coords[filename][start]:
                             print("KnownPHI: Extending the philter PHI coordinates!")
                             self.coords[filename][start] = stop
                             #self.update_phi_type(filename, file_note_key, start, stop)
                             #types = self.knownphitable.loc[self.knownphitable['clean_value'] == knownphi, 'phi_type'].iloc[0]
                             #if types == 'lname' or types == 'fname':
                             if types not in self.phi_types:
                                self.phi_types[types] = [CoordinateMap()]
                             if filename not in self.known_phi:
                                self.known_phi[filename] = {}
                             
                             flank_start = int(start) - 10
                             flank_end = int(stop) + 10
                             if(flank_start < 0):
                               flank_start = 1
                             if len(self.texts[filename])<flank_end:
                               flank_end = len(self.texts[filename])
                             context = self.texts[filename][flank_start:flank_end]
                             pos = self.get_postag(int(start),knownphi)
                             #print(str(start) + "\t" + str(stop) + "\t" + str(self.coords[filename][start]) + "\t" + knownphi + "\t" + context + "\t" + pos) 
                             self.known_phi[filename].update({int(start):[int(stop),knownphi,context,pos]})                   
                             #print("types updated:" + types)
                             self.phi_types[types][0].add_extend(filename,int(start),int(stop))

                       else:
                           ''' Add the coordinates as a newly identified PHI'''
                           self.coords[filename][start] = stop
                           types = self.knownphitable.loc[self.knownphitable['clean_value'] == knownphi, 'phi_type'].iloc[0]
                           #if types == 'lname' or types == 'fname':          
                           print("Updating coords with new known PHI" + filename)
                           print(filename + "\t" + str(start) + "\t" + str(stop) + "\t" + knownphi) 
                           if types not in self.phi_types:
                              self.phi_types[types] = [CoordinateMap()]
                           if filename not in self.known_phi:
                              self.known_phi[filename] = {}
                           flank_start = int(start) - 10
                           flank_end = int(stop) + 10
                           if(flank_start < 0):
                             flank_start = 1
                           if len(self.texts[filename])<flank_end:
                              flank_end = len(self.texts[filename])
                           context = self.texts[filename][flank_start:flank_end]
                           pos = self.get_postag(int(start),knownphi)
                           self.known_phi[filename].update({int(start):[int(stop),knownphi,context,pos]})
                           self.phi_types[types][0].add_extend(filename,int(start),int(stop))               
   


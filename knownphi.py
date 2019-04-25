import os
import pandas as pd
from coordinate_map import CoordinateMap
import re
from philter import Philter
from textmethods import get_tokens
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
       self.pos_tags***REMOVED***filename***REMOVED*** = nltk.pos_tag(cleaned)
       return self.pos_tags***REMOVED***filename***REMOVED***
   '''
   def _read_knownphi(self):
       if not self.knownphifile:
            raise Exception("Input known phi file is undefined: ", self.knownphifile)
       knownphi_table = pd.read_csv(self.knownphifile, sep='\t', index_col=False, usecols=***REMOVED***'patient_ID', 'phi_type', 'clean_value', 'note_key'***REMOVED***, dtype=str)
       return knownphi_table  

   def get_postag(self, kp_start, kp):
        for item in self.postags:
           start_coordinate = 0           
           for i in self.postags***REMOVED***item***REMOVED***:
              word = i***REMOVED***0***REMOVED***
              pos = i***REMOVED***1***REMOVED***
              start = start_coordinate
              stop = start_coordinate + len(word)

              # This converts spaces into empty strings, so we know to skip forward to the next real word
              word_clean = re.sub(r"***REMOVED***^a-zA-Z0-9***REMOVED***+", "", word.lower().strip())
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
           tokenize = get_tokens(self.texts***REMOVED***key***REMOVED***)
           for elem in key.split('/'):
               if (elem.find('.txt') != -1) or (elem.find('.xml') != -1):
                   elem = elem.replace('\n','')
                   elem = elem.replace('.txt','')
                   elem = elem.lstrip('0')
                   elem = elem.replace('.xml','')
                   elem = elem.replace('_utf8','')
                   file_note_key = elem  
           for knownphi in note_key2knownphi_dict:
               if note_key2knownphi_dict***REMOVED***knownphi***REMOVED*** == file_note_key:
                  #for start in tokenize:
                  #     if knownphi.lower() == tokenize***REMOVED***start***REMOVED******REMOVED***1***REMOVED***.lower():
                        #stop = tokenize***REMOVED***start***REMOVED******REMOVED***0***REMOVED***
                        #print("Found a Known PHI!" + str(knownphi) + ":" +file_note_key)
                  self.add_knownphi(key, file_note_key, tokenize, knownphi)
       return self.coords, self.phi_types, self.known_phi

   def update_phi_type(self,filename, file_note_key, start, stop):
       ''' Update the phi_type with new phi_types from known phi '''
       knownphitype_dict = pd.Series(self.knownphitable.phi_type.values, index=self.knownphitable.clean_value).to_dict()
       for types in knownphitype_dict:
           if types not in self.phi_types:
              self.phi_types***REMOVED***types***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
           print("types updated:" + types)
           self.phi_types***REMOVED***types***REMOVED******REMOVED***0***REMOVED***.add_extend(filename,int(start),int(end))
   

   def add_knownphi(self, filename, file_note_key, tokenize, knownphi):
       ''' adds a new coordinate to the self.coords dict
                 This always rejects any overlapping hits '''
       if isinstance(knownphi,str):
          for start in tokenize:
              if knownphi.lower() == tokenize***REMOVED***start***REMOVED******REMOVED***1***REMOVED***.lower():
                 stop = tokenize***REMOVED***start***REMOVED******REMOVED***0***REMOVED***
                 types = self.knownphitable.loc***REMOVED***self.knownphitable***REMOVED***'clean_value'***REMOVED*** == knownphi, 'phi_type'***REMOVED***.iloc***REMOVED***0***REMOVED***
                 if types == 'lname' or types == 'fname':
                    if filename in self.coords: 
                       if start in self.coords***REMOVED***filename***REMOVED***:          
                          ''' check overlap '''
                          if stop > self.coords***REMOVED***filename***REMOVED******REMOVED***start***REMOVED***:
                             print("KnownPHI: Extending the philter PHI coordinates!")
                             self.coords***REMOVED***filename***REMOVED******REMOVED***start***REMOVED*** = stop
                             #self.update_phi_type(filename, file_note_key, start, stop)
                             #types = self.knownphitable.loc***REMOVED***self.knownphitable***REMOVED***'clean_value'***REMOVED*** == knownphi, 'phi_type'***REMOVED***.iloc***REMOVED***0***REMOVED***
                             #if types == 'lname' or types == 'fname':
                             if types not in self.phi_types:
                                self.phi_types***REMOVED***types***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
                             if filename not in self.known_phi:
                                self.known_phi***REMOVED***filename***REMOVED*** = {}
                             
                             flank_start = int(start) - 10
                             flank_end = int(stop) + 10
                             if(flank_start < 0):
                               flank_start = 1
                             if len(self.texts***REMOVED***filename***REMOVED***)<flank_end:
                               flank_end = len(self.texts***REMOVED***filename***REMOVED***)
                             context = self.texts***REMOVED***filename***REMOVED******REMOVED***flank_start:flank_end***REMOVED***
                             pos = self.get_postag(int(start),knownphi)
                             #print(str(start) + "\t" + str(stop) + "\t" + str(self.coords***REMOVED***filename***REMOVED******REMOVED***start***REMOVED***) + "\t" + knownphi + "\t" + context + "\t" + pos) 
                             self.known_phi***REMOVED***filename***REMOVED***.update({int(start):***REMOVED***int(stop),knownphi,context,pos***REMOVED***})                   
                             #print("types updated:" + types)
                             self.phi_types***REMOVED***types***REMOVED******REMOVED***0***REMOVED***.add_extend(filename,int(start),int(stop))

                       else:
                           ''' Add the coordinates as a newly identified PHI'''
                           self.coords***REMOVED***filename***REMOVED******REMOVED***start***REMOVED*** = stop
                           types = self.knownphitable.loc***REMOVED***self.knownphitable***REMOVED***'clean_value'***REMOVED*** == knownphi, 'phi_type'***REMOVED***.iloc***REMOVED***0***REMOVED***
                           #if types == 'lname' or types == 'fname':          
                           print("Updating coords with new known PHI" + filename)
                           print(filename + "\t" + str(start) + "\t" + str(stop) + "\t" + knownphi) 
                           if types not in self.phi_types:
                              self.phi_types***REMOVED***types***REMOVED*** = ***REMOVED***CoordinateMap()***REMOVED***
                           if filename not in self.known_phi:
                              self.known_phi***REMOVED***filename***REMOVED*** = {}
                           flank_start = int(start) - 10
                           flank_end = int(stop) + 10
                           if(flank_start < 0):
                             flank_start = 1
                           if len(self.texts***REMOVED***filename***REMOVED***)<flank_end:
                              flank_end = len(self.texts***REMOVED***filename***REMOVED***)
                           context = self.texts***REMOVED***filename***REMOVED******REMOVED***flank_start:flank_end***REMOVED***
                           pos = self.get_postag(int(start),knownphi)
                           self.known_phi***REMOVED***filename***REMOVED***.update({int(start):***REMOVED***int(stop),knownphi,context,pos***REMOVED***})
                           self.phi_types***REMOVED***types***REMOVED******REMOVED***0***REMOVED***.add_extend(filename,int(start),int(stop))               
   


import os
import pandas as pd
from coordinate_map import CoordinateMap

class Knownphi:

   def __init__(self, knownphifile, coordinates, note_text, phi_type):
       self.knownphifile = knownphifile
       #coordinates of PHI
       self.coords = coordinates
       self.knownphitable = self._read_knownphi()
       self.texts = note_text       
       self.phi_types = phi_type


   def _read_knownphi(self):
       if not self.knownphifile:
            raise Exception("Input known phi file is undefined: ", self.knownphifile)
       knownphi_table = pd.read_csv(self.knownphifile, sep='\t', index_col=False, usecols=['person_id', 'phi_type', 'clean_value', 'note_key'], dtype=str)
       return knownphi_table  

   def update_coordinatemap(self):
       ''' Updates self.coords with known phi identified data'''

       file_note_key = ""
       note_key2knownphi_dict = pd.Series(self.knownphitable.note_key.values, index=self.knownphitable.clean_value).to_dict()
       for key in self.texts:
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
                  
                  start = self.texts[key].find(str(knownphi))
                  stop = len(str(knownphi))
                  if start != -1:
                     print("Found a Known PHI!" + str(knownphi) + ":" +file_note_key)
                     self.add_knownphi(key, file_note_key, start, stop)
       return self.coords, self.phi_types


   def add_knownphi(self, filename, file_note_key, start, stop):
       ''' adds a new coordinate to the self.coords dict
                 This always rejects any overlapping hits '''

       if filename in self.coords: 
          if start in self.coords[filename]:          
             ''' check overlap '''
             if stop > self.coords[filename][start]:
                print("KnownPHI: Extending the philter PHI coordinates!")
                self.coords[filename][start] = stop
                self.update_phi_type(filename, file_note_key, start, stop)
          else:
             ''' Add the coordinates as a newly identified PHI'''
             print("Updating coords with new known PHI" + filename)
             self.coords[filename][start] = stop
             self.update_phi_type(filename, file_note_key, start, stop)
   
   def update_phi_type(self,filename, file_note_key, start, stop):
       ''' Update the phi_type with new phi_types from known phi '''
       knownphitype_dict = pd.Series(self.knownphitable.phi_type.values, index=self.knownphitable.clean_value).to_dict()
       for types in knownphitype_dict:
           if knownphitype_dict[types] == file_note_key:       
              if types not in self.phi_types:
                 self.phi_types[types] = [CoordinateMap()]
       
              self.phi_types[types][0].add_extend(filename,int(start),int(end))       


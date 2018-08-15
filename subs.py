import dateutil.parser
from datetime import datetime,timedelta
import random
from dateparser import parse
import re
import pandas as pd

class Subs:
    def __init__(self):
        #load shift table to a dictionary
        self.shift_table  = self.lookup_date_shift()
    
    def get_shift_amount(self,patient_id):
        return self.shift_table***REMOVED***patient_id***REMOVED***

    def shift_date(self, date, shift_amount):
        return date + shift_amount
    
    def shift_date_pid(self, date, patient_id):
        return date + self.get_shift_amount(patient_id)

    def parse_date(self, date_string):
        date = parse(date_string, settings={'PREFER_DAY_OF_MONTH': 'first'} )
        return date
    

    def lookup_date_shift(self,
     note_info_path='data/notes_metadata/note_info.csv',
     re_id_pat_path='data/notes_metadata/re_id_pat.csv'):

        note_info = pd.read_csv(note_info_path)
        re_id_pat = pd.read_csv(re_id_pat_path)

        #join together re_id_pat with NOTE_INFO on Patient_id
        joined_table = note_info.set_index('patient_ID').join(re_id_pat.set_index('patient_ID'))
        id2offset = pd.Series(joined_table.date_offset.values,index=joined_table.index).to_dict()

        return id2offset
import random
import re
import pandas as pd
from collections import defaultdict
import dask.dataframe as dd
from datetime2 import datetime2

DEFAULT_SHIFT_VALUE = 32

class Subs:
    def __init__(self,note_info_path = None, re_id_pat_path = None, note_keys = None):
        #load shift table to a dictionary
        self.shift_table  = self._load_look_up_table(note_info_path, re_id_pat_path, note_keys)
    
    def get_shift_amount(self,note_id):
        shift_amount = self.shift_table[note_id]

        #if the shift amount is an int or can be converted to an int then return it.
        try:
            shift_amount = int(shift_amount)
            return shift_amount
        #if the shift amount is not int then print the data_offset and note_id values and return the DEFAULT_SHIFT_VALUE
        except ValueError:
            print("Error: date_offset is not an integer. date_offset=" + str(shift_amount)
                 + ", note_id=" + str(note_id))
        return DEFAULT_SHIFT_VALUE

    def shift_date(self, date, shift_amount):
        return date + shift_amount
    
    def shift_date_pid(self, date, note_id):
        return self.shift_date(date, self.get_shift_amount(note_id))

    @staticmethod
    def parse_date(date_string):
        date = datetime2.parse(date_string, settings={'PREFER_DAY_OF_MONTH': 'first'} )
        return date

    def date_to_string(self, date):
        return date.to_string()

    def _load_look_up_table(self,note_info_path, re_id_pat_path, note_keys):

        # note_info_path='data/notes_metadata/note_info.csv'
        # re_id_pat_path='data/notes_metadata/re_id_pat.csv'

        if note_info_path is None or re_id_pat_path is None:
            return defaultdict(lambda:DEFAULT_SHIFT_VALUE)


        note_info = dd.read_csv(note_info_path, sep='\t', usecols=['patient_ID', 'note_key'])
        re_id_pat = dd.read_csv(re_id_pat_path, sep='\t', usecols=['PatientId', 'date_offset'])

        

        #join together re_id_pat with NOTE_INFO on Patient_id
        joined_table = note_info.set_index('patient_ID').join(re_id_pat.set_index('PatientId'))
        joined_table = joined_table[joined_table["note_key"].isin(note_keys)].compute()

        id2offset = pd.Series(joined_table.date_offset.values,index=joined_table.note_key).to_dict()

        return id2offset

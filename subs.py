import dateutil.parser
from datetime import datetime,timedelta
import random
from dateparser import parse
import re
import pandas as pd
from collections import defaultdict
import dask.dataframe as dd

DEFAULT_SHIFT_VALUE = 32
class Subs:
    def __init__(self, look_up_table_path = None):
        #load shift table to a dictionary
        self.shift_table  = self._load_look_up_table(look_up_table_path)
    
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
        return date + timedelta(days=shift_amount) 
    
    def shift_date_pid(self, date, note_id):
        return self.shift_date(date, self.get_shift_amount(note_id))

    @staticmethod
    def parse_date(date_string):
        date = parse(date_string, settings={'PREFER_DAY_OF_MONTH': 'first'} )
        return date
    
    def date_to_string(self, date):
        return date.strftime("%m/%d/%Y")

    def _load_look_up_table(self, look_up_table_path):

        # note_info_path='data/notes_metadata/note_info.csv'
        # re_id_pat_path='data/notes_metadata/re_id_pat.csv'
        # "note_key | date_offset | deid_note_key | patient_ID"

        if look_up_table_path is None:
            return defaultdict(lambda:DEFAULT_SHIFT_VALUE)


        look_up_table = pd.read_csv(look_up_table_path, sep='\t', usecols=['note_key', 'date_offset'])

        

        #join together re_id_pat with NOTE_INFO on Patient_id
        #joined_table = note_info.set_index('patient_ID').join(re_id_pat.set_index('PatientId'))
        #joined_table = joined_table[joined_table["note_key"].isin(note_keys)].compute()

        id2offset = pd.Series(look_up_table.date_offset.values,index=look_up_table.note_key).to_dict()

        return id2offset

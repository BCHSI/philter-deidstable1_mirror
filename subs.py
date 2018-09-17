import random
import re
import pandas as pd
from collections import defaultdict
import dask.dataframe as dd
from datetime2 import datetime2

DEFAULT_SHIFT_VALUE = 32
class Subs:
    def __init__(self, look_up_table_path = None):
        #load shift table to a dictionary
        self.shift_table  = self._load_look_up_table(look_up_table_path)
    

    def has_shift_amount(self, note_id):
        return note_id in self.shift_table
    def get_shift_amount(self,note_id):
        try:
            shift_amount = int(self.shift_table***REMOVED***note_id***REMOVED***)
            if shift_amount == 0:
                print("WARNING: shift amount for note_id: {0} is zero.".format(note_id))
        except KeyError as err:
            print("Key Error in shift_table {0}".format(err))
            return None
            #return DEFAULT_SHIFT_VALUE #TODO: return None or negative or NAN to indicate missing shift to upstream
        except ValueError as err:
            print("Value Error: {0}".format(err))
            print("Error: date_offset is not an integer. date_offset=" + str(shift_amount)
                  + ", note_id=" + str(note_id))
            return None
            #return DEFAULT_SHIFT_VALUE
        return shift_amount

    def shift_date(self, date, shift_amount):
        return date - shift_amount
    
    def shift_date_pid(self, date, note_id):
        return self.shift_date(date, self.get_shift_amount(note_id)) # TODO: check return value before shift

    @staticmethod
    def parse_date(date_string):
        date = datetime2.parse(date_string, settings={'PREFER_DAY_OF_MONTH': 'first'} )
        return date
    
    def date_to_string(self, date):
        return date.to_string()

    def _load_look_up_table(self, look_up_table_path):

        # note_info_path='data/notes_metadata/note_info.csv'
        # re_id_pat_path='data/notes_metadata/re_id_pat.csv'
        # "note_key | date_offset | deid_note_key | patient_ID"

        if look_up_table_path is None:
            return {} #defaultdict(lambda:DEFAULT_SHIFT_VALUE)


        look_up_table = pd.read_csv(look_up_table_path, sep='\t', usecols=***REMOVED***'note_key', 'date_offset'***REMOVED***)

        

        #join together re_id_pat with NOTE_INFO on Patient_id
        #joined_table = note_info.set_index('patient_ID').join(re_id_pat.set_index('PatientId'))
        #joined_table = joined_table***REMOVED***joined_table***REMOVED***"note_key"***REMOVED***.isin(note_keys)***REMOVED***.compute()

        id2offset = pd.Series(look_up_table.date_offset.values,index=look_up_table.note_key).to_dict()


        return id2offset

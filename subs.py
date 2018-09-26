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
    

    def has_shift_amount(self, note_id):
        return note_id in self.shift_table
    def get_shift_amount(self,note_id):
        try:
            shift_amount = int(self.shift_table[note_id])
            if shift_amount == 0:
                print("WARNING: shift amount for note_id: {0} is zero.".format(note_id))
        except KeyError as err:
            print("Key Error in shift_table {0}".format(err))
            shift_amount = None
        except ValueError as err:
            print("Value Error: date_offset is not an integer for note_id=" + str(note_id) + "{0}".format(err))
            shift_amount = None
        return shift_amount

    def shift_date(self, date, shift_amount):
        return date - timedelta(days=shift_amount) 
    
    def shift_date_pid(self, date, note_id):
        return self.shift_date(date, self.get_shift_amount(note_id)) # TODO: check return value before shift

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
            return {} #defaultdict(lambda:DEFAULT_SHIFT_VALUE)


        look_up_table = dd.read_csv(look_up_table_path, sep='\t', usecols=['note_key', 'date_offset'], dtype=str)
        look_up_table = look_up_table[~look_up_table["date_offset"].isnull()].compute()
        

        #join together re_id_pat with NOTE_INFO on Patient_id
        #joined_table = note_info.set_index('patient_ID').join(re_id_pat.set_index('PatientId'))
        #joined_table = joined_table[joined_table["note_key"].isin(note_keys)].compute()

        id2offset = pd.Series(look_up_table.date_offset.values,index=look_up_table.note_key).to_dict()


        return id2offset

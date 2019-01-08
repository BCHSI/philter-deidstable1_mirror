import random
import re
import pandas as pd
from collections import defaultdict
import datetime as dt
from datetime2 import datetime2

DEFAULT_SHIFT_VALUE = 32
DATE_REF = dt.datetime(2000, 2, 29)

class Subs:
    def __init__(self, look_up_table_path = None):
        #load shift table to a dictionary
        self.shift_table, self.deid_note_key_table = self._load_look_up_table(look_up_table_path)
    
    def has_shift_amount(self, note_id):
        return note_id in self.shift_table
    
    def has_deid_note_key(self, note_id):
        return note_id in self.deid_note_key_table
    
    def get_deid_note_key(self, note_id):
        try:
            deid_note_key = self.deid_note_key_table[note_id]
        except KeyError as err:
            print("Key Error in deid_note_key_table for note " + str(note_id)
                  + ": {0}".format(err))
            deid_note_key = None
        return deid_note_key
    
    def get_shift_amount(self, note_id):
        try:
            shift_amount = int(self.shift_table[note_id])
            if shift_amount == 0:
                print("WARNING: shift amount for note " + str(note_id)
                      + " is zero.")
        except KeyError as err:
            print("Key Error in shift_table for note " + str(note_id)
                  + ": {0}".format(err))
            shift_amount = None
        except ValueError as err:
            print("Value Error: date_offset is not an integer for note "
                  + str(note_id) + ": {0}".format(err))
            shift_amount = None
        return shift_amount
    
    def shift_date(self, date, shift_amount):
        return date.subtract_days(shift_amount)
    
    def shift_date_pid(self, date, note_id):
        shifted_date = None
        shift = self.get_shift_amount(note_id)
        if shift is None:
            return None
        try:
            shifted_date = self.shift_date(date, shift)
        except OverflowError as err:
            if __debug__: print("WARNING: cannot shift date \""
                                + date.to_string(debug=True)
                                + " pretty: " + date.to_string()
                                + "\" with shift " + str(shift)
                                + " in note " + str(note_id)
                                + " Overflow Error: {0}".format(err))
        return shifted_date
      
    @staticmethod
    def parse_date(date_string):
        date = datetime2.parse(date_string,
                               settings={'RELATIVE_BASE': DATE_REF,
                                         'PREFER_DAY_OF_MONTH': 'first'})
        return date
    
    def date_to_string(self, date):
        return date.to_string()

    def _load_look_up_table(self, look_up_table_path):
        if look_up_table_path is None:
            return {} #defaultdict(lambda:DEFAULT_SHIFT_VALUE)

        try:
            look_up_table = pd.read_csv(look_up_table_path, sep='\t',
                                        index_col=False,
                                        usecols=['note_key', 'date_offset',
                                                 'deid_note_key'],
                                        dtype=str)
        except pd.errors.EmptyDataError as err:
            print("Pandas Empty Data Error: " + look_up_table_path
                  + " is empty {0}".format(err))
            return {}, {}
        except ValueError as err:
            print("Value Error: " + look_up_table_path
                  + " is invalid {0}".format(err))
            return {}, {}
        
        offset_table = look_up_table[~look_up_table["date_offset"].isnull()]
        deid_table = look_up_table[~look_up_table["deid_note_key"].isnull()]
        id2offset = pd.Series(offset_table.date_offset.values,
                              index=offset_table.note_key).to_dict()
        id2deid = pd.Series(deid_table.deid_note_key.values,
                            index=deid_table.note_key).to_dict()
        
        return id2offset, id2deid

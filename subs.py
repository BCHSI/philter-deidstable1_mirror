import random
import re
import pandas as pd
from collections import defaultdict
import dask.dataframe as dd
import datetime as dt
from datetime2 import datetime2

DEFAULT_SHIFT_VALUE = 32
DATE_REF = dt.datetime(2000, 2, 29)

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
            shift_amount = None
        except ValueError as err:
            print("Value Error: date_offset is not an integer for note_id="
                  + str(note_id) + "{0}".format(err))
            shift_amount = None
        return shift_amount

    def shift_date(self, date, shift_amount):
        return date.subtract_days(shift_amount)
    
    def shift_date_pid(self, date, note_id):
        return self.shift_date(date, self.get_shift_amount(note_id)) # TODO: check return value before shift

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
            look_up_table = pd.read_csv(look_up_table_path, sep='\t', index_col=False, usecols=***REMOVED***'note_key', 'date_offset'***REMOVED***, dtype=str)
        except pd.errors.EmptyDataError as err:
            print("Pandas Empty Data Error: " + look_up_table_path
                  + " is empty {0}".format(err))
            return {}
        
        look_up_table = look_up_table***REMOVED***~look_up_table***REMOVED***"date_offset"***REMOVED***.isnull()***REMOVED*** #.compute()

        id2offset = pd.Series(look_up_table.date_offset.values, index=look_up_table.note_key).to_dict()

        return id2offset

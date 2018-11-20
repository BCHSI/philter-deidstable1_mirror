import dateutil.parser
from datetime import datetime,timedelta
import random
from dateparser import parse
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
            shift_amount = None
        except ValueError as err:
            print("Value Error: date_offset is not an integer for note_id=" + str(note_id) + "{0}".format(err))
            shift_amount = None
        return shift_amount
    
    def shift_date(self, date, shift_amount):
        return date.subtract_days(shift_amount)
    
    def shift_date_pid(self, date, note_id):
        return self.shift_date(date, self.get_shift_amount(note_id)) # TODO: check return value before shift
    
    @staticmethod
    def parse_date(date_string):
        date = datetime2.parse(date_string, settings={'PREFER_DAY_OF_MONTH': 'first'} )
        return date
    
    def date_to_string(self, date):
        return date.to_string()

    """
    def parse_date_2(self, date_string):
        date = parse(date_string, settings={'PREFER_DAY_OF_MONTH': 'first'} )
        today = datetime.now()
        if parsed_date is not None:
            date_strict = parse(parsed_date,settings={'STRICT_PARSING': True})

            # we have to take into account if the input date isn't a fully specified date
            #date parse implementation returns current month if month is not found
            # and sets day to equal 1 if day is not found
            if strict_parsed_date is None or strict_parsed_date.year != date.year:
                if date.month != today.month:
                    input_string += str(dt.strftime('%B')) 
                    output_string += str(dt_plus_arbitrary.strftime('%B')) 
                if dt.year!=now.year:
                    input_string += " " +str(dt.year)
                    output_string += " " +str(dt_plus_arbitrary.year)
                if dt.day!=1:
                    input_string += " " +str(dt.day)
                    output_string += " " +str(dt_plus_arbitrary.day)
                output_shifted_date = output_string.replace(" 00:00:00","")
                input_date = input_string.replace(" 00:00:00","")

            else:
                output_shifted_date = str(dt_plus_arbitrary).replace(" 00:00:00","")
                input_date = str(dt).replace(" 00:00:00","")
    """

    def _load_look_up_table(self, look_up_table_path):
        # note_info_path='data/notes_metadata/note_info.csv'
        # re_id_pat_path='data/notes_metadata/re_id_pat.csv'
        if look_up_table_path is None:
            return {} #defaultdict(lambda:DEFAULT_SHIFT_VALUE)
        look_up_table = pd.read_csv(look_up_table_path, sep='\t', index_col=False, usecols=***REMOVED***'note_key', 'date_offset'***REMOVED***, dtype=str)
        look_up_table = look_up_table***REMOVED***~look_up_table***REMOVED***"date_offset"***REMOVED***.isnull()***REMOVED***
        #.compute()
        id2offset = pd.Series(look_up_table.date_offset.values, index=look_up_table.note_key).to_dict()
        
        return id2offset
        
        

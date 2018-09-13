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
    def __init__(self,note_info_path = None, re_id_pat_path = None, note_keys = None):
        #load shift table to a dictionary
        self.shift_table  = self._load_look_up_table(note_info_path, re_id_pat_path, note_keys)
    
    def get_shift_amount(self,note_id):
        try:
            shift_amount = int(self.shift_table[note_id])
        except KeyError as err:
            print("Key Error in shift_table {0}".format(err))
            return DEFAULT_SHIFT_VALUE #TODO: return None or negative or NAN to indicate missing shift to upstream
        except ValueError as err:
            print("Value Error: {0}".format(err))
            print("Error: date_offset is not an integer. date_offset=" + str(shift_amount)
                  + ", note_id=" + str(note_id))
            return DEFAULT_SHIFT_VALUE
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

    def _load_look_up_table(self,note_info_path, re_id_pat_path, note_keys):

        # note_info_path='data/notes_metadata/note_info.csv'
        # re_id_pat_path='data/notes_metadata/re_id_pat.csv'

        if note_info_path is None or re_id_pat_path is None:
            return defaultdict(lambda:DEFAULT_SHIFT_VALUE)


        note_info = dd.read_csv(note_info_path, sep='\t', usecols=['patient_ID', 'note_key'])
        re_id_pat = dd.read_csv(re_id_pat_path, sep='\t', usecols=['PatientId', 'date_offset'])

        

        #join together re_id_pat with NOTE_INFO on Patient_id
        joined_table = re_id_pat.set_index('PatientId').join(note_info.set_index('patient_ID'))
        joined_table = joined_table[joined_table["note_key"].isin(note_keys)].compute()
        id2offset = pd.Series(joined_table.date_offset.values,index=joined_table.note_key).to_dict()
        
        return id2offset

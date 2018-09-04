import dateutil.parser
from datetime import datetime,timedelta
import random
from dateparser import parse
import re
import pandas as pd
from collections import defaultdict

class Subs:
    def __init__(self,note_info_path = None, re_id_pat_path = None):
        #load shift table to a dictionary
        self.shift_table  = self._load_look_up_table(note_info_path,re_id_pat_path)
    
    def get_shift_amount(self,patient_id):
        return self.shift_table[patient_id]

    def shift_date(self, date, shift_amount):
        return date + timedelta(days=shift_amount) 
    
    def shift_date_pid(self, date, patient_id):
        return self.shift_date(date, self.get_shift_amount(patient_id))

    def parse_date(self, date_string):
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

    def _load_look_up_table(self,note_info_path,re_id_pat_path):

        # note_info_path='data/notes_metadata/note_info.csv'
        # re_id_pat_path='data/notes_metadata/re_id_pat.csv'

        if note_info_path is None or re_id_pat_path is None:
            return defaultdict(lambda:32)


        note_info = pd.read_csv(note_info_path)
        re_id_pat = pd.read_csv(re_id_pat_path)

        #join together re_id_pat with NOTE_INFO on Patient_id
        joined_table = note_info.set_index('patient_ID').join(re_id_pat.set_index('patient_ID'))
        id2offset = pd.Series(joined_table.date_offset.values,index=joined_table.index).to_dict()

        return id2offset
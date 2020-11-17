import random
import re
import pandas as pd
from collections import defaultdict
import datetime as dt
import types
from datetime2 import datetime2
import calendar as cal
import pymongo
from pymongo.errors import ConnectionFailure
import os
import pprint
import json
from pymongo import MongoClient
from word2number import w2n

DEFAULT_SHIFT_VALUE = 32
DATE_REF = dt.datetime(2000, 2, 29) # do not change this!!!!

class Subs:
    def __init__(self, filenames, look_up_table_path = None, db = None,
                 ref_date = None):
        #load shift/surrogate table to dictionaries
        if type(look_up_table_path) is dict:
           if db is None:
              raise ValueError("Expecting a mongo handle. None provided.")
           else:
              self.db = db
           self.xwalk = self._load_look_up_mongo(filenames, look_up_table_path)
        else:   
           self.xwalk = self._load_look_up_table(look_up_table_path)

        self.ref_date = self.parse_date(ref_date)
        if not self.ref_date.is_complete():
            raise ValueError("reference date is incomplete, use YYYY-MM-DD")

    def has_shift_amount(self, note_id):
        return note_id in self.xwalk["offset"]
    
    def has_deid_note_key(self, note_id):
        return note_id in self.xwalk["deidnotekey"]
    
    def get_deid_note_key(self, note_id):
        try:
            deid_note_key = self.xwalk["deidnotekey"][note_id]
        except KeyError as err:
            if __debug__:
                print("Missing Deid note key for note " + str(note_id)
                      + ": {0}".format(err))
            deid_note_key = None
        return deid_note_key

    def get_dob(self, note_id):
        try:
            dob = self.parse_date(self.xwalk["dob"][note_id])
        except KeyError as err:
            if __debug__:
                print("Missing DOB for note " + str(note_id)
                      + ": {0}".format(err))
            dob = None
        return dob

    def get_deid_dob(self, note_id):
        try:
            deid_dob = self.parse_date(self.xwalk["deiddob"][note_id])
        except KeyError as err:
            if __debug__:
                print("Missing Deid DOB in metadata for note " + str(note_id)
                      + ": {0}".format(err))
            deid_dob = None
        return deid_dob

    def get_deid_91_bdate(self, note_id):
        try:
            deid_91_bdate = self.parse_date(self.xwalk["deid91bdate"][note_id])
        except KeyError as err:
            if __debug__:
                print("Missing Deid 91st birthday for note " + str(note_id)
                      + ": {0}".format(err))
            deid_91_bdate = None
        return deid_91_bdate

    def get_ref_date(self):
        return self.ref_date
    
    def get_shift_amount(self, note_id):
        try:
            shift_amount = (None if self.xwalk["offset"][note_id] is None
                            else int(self.xwalk["offset"][note_id]))
            if shift_amount == 0:
                print("WARNING: shift amount for note " + str(note_id)
                      + " is zero.")
                shift_amount = None
        except KeyError as err:
            if __debug__:
                print("Missing date shift for note " + str(note_id)
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
        if not date: return None
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
      
    def shift_date_wrt_dob(self, date, note_id):
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
                                + "\" with shift -" + str(shift)
                                + " in note " + str(note_id)
                                + " Overflow Error: {0}".format(err))

        dob = self.get_dob(note_id)
        if not date.missing_year and dob and date == dob:
            shifted_date = self.shift_dob_pid(dob, note_id)
            shifted_date = datetime2(shifted_date.year, shifted_date.month,
                                     shifted_date.day,
                                     date_string = date.date_string,
                                     missing_year = date.missing_year,
                                     missing_month = date.missing_month,
                                     missing_day = date.missing_day,
                                     missing_century = date.missing_century)
            
        # not yet implemented in Deid CDW
        # shifted_date = max(shifted_date, shifted_dob)
        
        return shifted_date

    def _days_from_bday(self, ref, dob):
        days_from_bday = (dt.datetime(year = ref.year,
                                      month = ref.month,
                                      day = ref.day)
                          - dt.datetime(year = ref.year,
                                        month =  dob.month,
                                        day = (dob.day - 1
                                               if (dob.day == 29
                                                   and dob.month == 2
                                                   and not cal.isleap(ref.year))
                                               else dob.day))).days
        return days_from_bday

    def shift_dob_pid(self, dob, note_id):
        #
        shift = self.get_shift_amount(note_id)
        deid_bday91 = self.get_deid_91_bdate(note_id)

        if shift is None or dob is None or deid_bday91 is None:
            if __debug__: print("WARNING: cannot find birth date info"
                                + " for note " + str(note_id))
            return None
        try:
            shifted_dob = self.shift_date(dob, shift)
        except OverflowError as err:
            if __debug__: print("WARNING: cannot shift date of birth \""
                                + dob.to_string(debug=True)
                                + " pretty: " + dob.to_string()
                                + "\" with shift -" + str(shift)
                                + " for note " + str(note_id)
                                + " Overflow Error: {0}".format(err))

        ref = self.ref_date # today or the date of Notes extraction

        shifted_age = self._age(shifted_dob)
        if shifted_age >= 91: # the patient is older than 90:
            days_from_bday = self._days_from_bday(ref, shifted_dob)
            if days_from_bday < 0:
                shifted_byear = ref.year - 91
            else:
                shifted_byear = ref.year - 90
            ninety_shift = (dt.datetime(year = shifted_byear,
                                        month = shifted_dob.month,
                                        day = (shifted_dob.day - 1
                                               if (shifted_dob.day == 29
                                                   and shifted_dob.month == 2
                                                   and not cal.isleap(shifted_byear))
                                               else shifted_dob.day))
                            - dt.datetime(year = shifted_dob.year,
                                          month =  shifted_dob.month,
                                          day = shifted_dob.day))
            shifted_dob = shifted_dob + ninety_shift

            # general goal is to transform all ages >=91 --> 90
            # for now, just use reference date and not death date
            # Things to look out for:
                # leap years (before, on, after)
                # 2000, maybe 2020?
                # check around 91st bdays
                # what if ref date is before date of birth
                # try some extreme values

        deid_age = self._age(shifted_dob)

        # Throw warning if birthdate is not shifted as expected
        if shifted_age >= 91 and deid_age != 90:
            print("WARNING: Birthdate for age > 90 not shifted correctly for note ID", note_id)
        if shifted_age < 91 and deid_age >= 91:
            print("WARNING: Birthdate for age < 90 not shifted correctly for note ID", note_id)

        # perhaps good to implement some consistency checks with metadata
        if __debug__:
            deid_bdate = self.get_deid_dob(note_id)
            if deid_bdate is not None and shifted_dob != deid_bdate:
                print("WARNING: shifted date of birth "
                      + shifted_dob.to_string()
                      + " with shift -" + str(shift) + " days"
                      + " for note " + str(note_id)
                      + " not equal to deid_BirthDate in meta data "
                      + deid_bdate.to_string() + ".")
                if (shifted_dob.day == deid_bdate.day
                    and shifted_dob.month == deid_bdate.month):
                    print("WARNING: Reference date " + str(ref)
                          + " not equal to date of ETL?")

        return shifted_dob

    def _age(self, dob, dob_century=None): # integer age on reference date
        if not dob or dob.missing_year: return None
        if not dob.missing_century:
            age = self.ref_date.year - dob.year
        elif dob_century:
            age = self.ref_date.year - dob.year % 100 - dob_century
        else:
            return None
        days_from_bday = self._days_from_bday(self.ref_date, dob)
        if days_from_bday < 0:
            age -= 1
        return age

    def shifted_age_pid(self, note_id):
        shifted_dob = self.shift_date_pid(self.get_dob(note_id), note_id)
        return self._age(shifted_dob)
    
    @staticmethod
    def parse_age(age_string):
        try:
            if age_string.isdigit():
                age = int(age_string)
            else:
                age = w2n.word_to_num(age_string)
        except ValueError as err:
            print("ValueError: \"" + age_string
                  + "\" is invalid age: {0}".format(err))
            return None
        return age
    
    @staticmethod
    def parse_date(date_string):
        date = datetime2.parse(date_string,
                               settings={'RELATIVE_BASE': DATE_REF,
                                         'PREFER_DAY_OF_MONTH': 'first'})
        return date

    @staticmethod
    def date_to_string(date):
        return date.to_string()

    def _load_look_up_table(self, look_up_table_path):
        notekey2id = {}
        id2offset = {}
        id2deidnotekey = {}
        id2dob = {}
        id2deiddob = {}
        id2deid91bdate = {}
        if look_up_table_path is None:
            return {}  #defaultdict(lambda:DEFAULT_SHIFT_VALUE)

        try:
            look_up_table = pd.read_csv(look_up_table_path, sep='\t',
                                        index_col=False,
                                        usecols=(lambda x:
                                                 x in ['note_key',
                                                       'report_id',
                                                       'date_offset',
                                                       'deid_date_offset_cdw',
                                                       'deid_note_key',
                                                       'deid_report_id',
                                                       'BirthDate',
                                                       'Birthdate',
                                                       'Deid_BirthDate',
                                                       'deid_birthdate',
                                                       'deid_turns_91_date']),
                                        dtype=str)
        except pd.errors.EmptyDataError as err:
            print("Pandas Empty Data Error: " + look_up_table_path
                  + " is empty {0}".format(err))
            return {}
        except ValueError as err:
            print("Value Error: " + look_up_table_path
                  + " is invalid {0}".format(err))
            return {}

        nkey = ("note_key" if "note_key" in look_up_table.keys()
                else ("report_id"
                      if "report_id" in look_up_table.keys()
                      else "") )
        deid_nkey = ("deid_note_key" if "note_key" in look_up_table.keys()
                     else ("deid_report_id"
                           if "deid_report_id" in look_up_table.keys()
                           else "") )
        dateoffset = ("date_offset" if "date_offset" in look_up_table.keys()
                      else ("deid_date_offset_cdw"
                            if "deid_date_offset_cdw" in look_up_table.keys()
                            else "") )
        birthdate = ("BirthDate" if "BirthDate" in look_up_table.keys()
                     else ("Birthdate"
                           if "Birthdate" in look_up_table.keys()
                           else "") )
        deid_birthdate = ("Deid_BirthDate" if "Deid_BirthDate" in look_up_table.keys()
                          else ("deid_birthdate"
                                if "deid_birthdate" in look_up_table.keys()
                                else "") )
        if dateoffset:
            offset_table = look_up_table[~look_up_table[dateoffset].isnull()]
            notekey2id["offset"] = pd.Series(offset_table[dateoffset].values,
                                             index=offset_table[nkey]).to_dict()
        if deid_nkey:
            deid_table = look_up_table[~look_up_table[deid_nkey].isnull()]
            notekey2id["deidnotekey"] = pd.Series(deid_table[deid_nkey].values,
                                                  index=deid_table[nkey]).to_dict()
        if birthdate:
            dob_table = look_up_table[~look_up_table[birthdate].isnull()]
            notekey2id["dob"] = pd.Series(dob_table[birthdate].values,
                                          index=dob_table[nkey]).to_dict()
        if deid_birthdate:
            deid_dob_table = look_up_table[~look_up_table[deid_birthdate].isnull()]
            notekey2id["deiddob"] = pd.Series(deid_dob_table[deid_birthdate].values,
                                              index=deid_dob_table[nkey]).to_dict()
        if "deid_turns_91_date" in look_up_table.keys():
            deid_91_bdate_table = look_up_table[~look_up_table["deid_turns_91_date"].isnull()]
            notekey2id["deid91bdate"] = pd.Series(deid_91_bdate_table.deid_turns_91_date.values,
                                                  index=deid_91_bdate_table[nkey]).to_dict()
 
        return notekey2id

    def _load_look_up_mongo(self, filenames, mongo):
        try:
           db = self.db
           collection = db[mongo['collection_meta_data']]
        except:
           print("Cannot connect to Mongo Database note_info_map")
        notekey2id = {}
        id2offset = {}
        id2deidnotekey = {}
        id2dob = {}
        id2deiddob = {}
        id2deid91bdate = {}
        #print(collection.find_one({"note_key":note_key},{"_id":0,"note_key":1, "deid_date_offset_cdw":1,"patient_ID":1,"deid_note_key":1}))
        surrogate_info = collection.find({"_id": {"$in": filenames}},
                                         {"_id":1, "deid_date_offset_cdw":1,
                                          "deid_note_key":1, "BirthDate":1,
                                          "Deid_BirthDate":1,
                                          "deid_turns_91_date":1})

        for filename in list(surrogate_info):
           if "deid_date_offset_cdw" in filename:
              id2offset[filename['_id']]  = filename["deid_date_offset_cdw"]
           if "deid_note_key" in filename:
              id2deidnotekey[filename['_id']] = filename["deid_note_key"]        
           if "BirthDate" in filename:
              id2dob[filename['_id']] = filename["BirthDate"]
           if "Deid_BirthDate" in filename:
              id2deiddob[filename['_id']] = filename["Deid_BirthDate"]
           if "deid_turns_91_date" in filename:
              id2deid91bdate[filename['_id']] = filename["deid_turns_91_date"]
        notekey2id = {"offset":id2offset, "deidnotekey":id2deidnotekey,
                      "dob":id2dob, "deiddob":id2deiddob,
                      "deid91bdate":id2deid91bdate}
        return notekey2id

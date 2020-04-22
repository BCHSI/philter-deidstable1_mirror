import random
import re
import pandas as pd
from collections import defaultdict
import datetime as dt
import types
from datetime2 import datetime2
import pymongo
from pymongo.errors import ConnectionFailure
import os
import pprint
import json
from pymongo import MongoClient

DEFAULT_SHIFT_VALUE = 32
DATE_REF = dt.datetime(2000, 2, 29)

class Subs:
    def __init__(self, filenames, look_up_table_path = None, db = None):
        #load shift table to a dictionary
        if type(look_up_table_path) is dict:
           if db is None:
              print("In Subs. Expecting a mongo handel. None provided.")
              quit()
           else:
              self.db = db
           self.shift_table, self.deid_note_key_table = self._load_look_up_mongo(filenames,look_up_table_path)
        else:   
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

    @staticmethod
    def date_to_string(date):
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

    def _load_look_up_mongo(self, filenames, mongo):
        try:
           db = self.db
           collection = db[mongo['collection_meta_data']]
        except:
           print("Cannot connect to Mongo Database note_info_map")
        id2offset = {}
        id2deid = {}
        #print(collection.find_one({"note_key":note_key},{"_id":0,"note_key":1, "deid_date_offset_cdw":1,"patient_ID":1,"deid_note_key":1}))
        surrogate_info = collection.find({"_id": {"$in": filenames}},{"_id":1,"deid_date_offset_cdw":1,"deid_note_key":1})
                
        for filename in list(surrogate_info):
           id2offset[filename['_id']]  = filename["deid_date_offset_cdw"]
           id2deid[filename['_id']] = filename["deid_note_key"]        

        return id2offset, id2deid
       

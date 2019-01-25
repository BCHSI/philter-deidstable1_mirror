import re
import dateparser
import datetime
DATE_1 = datetime.datetime(3008, 12, 12)
DATE_2 = datetime.datetime(1004, 5, 5)

"""
datetime2 is an extension to python's standard datetime. It can be used anywhere
datetime.datetime is used since it inherits from datetime.datetime. The additional
features that datetime2 provides that are:

1. Creating an date from a string representation.
    datetime2.parse("13th of June") #will return a datetime2 object with day set to 13 and month set to 6.

2. Detecting missing parts of the date (year, month, and/or day).
    >> datetime2.parse("13th of June").missing_year
    >> True
    ------------
    >> datetime2.parse("13th of June").missing_day
    >> False

3. Providing a more flexible string output. The default datetime2 string representation will change depending on missing parts in the object.
    >> datetime2.parse("13th of June").to_string()
    >> 'June 13'
    ------------
    >> datetime2.parse("13th of June, 2017").to_string()
    >> '06/13/2017'
    ------------
    >> datetime2.parse("August 98").to_string()
    >> 'August 1998'
    ------------
    >> datetime2.parse("Sep").to_string()
    >> 'September'
"""
class datetime2(datetime.datetime):
    def __new__(cls, year, month, day, date_string = None,
                missing_year = None, missing_month = None,
                missing_day = None, missing_century = None):
        self = datetime.datetime.__new__(cls,year,month,day)
        self.missing_year = missing_year
        self.missing_month = missing_month
        self.missing_day = missing_day
        self.missing_century = missing_century
        
        self.date_string = date_string
        return self
    
    
    @staticmethod
    def parse(date_string, *args, **kwargs):
        try:
            temp_date = dateparser.parse(date_string, *args, **kwargs)
            if temp_date is None:
                raise ValueError("parser returned None")
            missing_year, missing_month, missing_day, missing_century = datetime2.missing_date_parts(date_string)
        except ValueError as err:
            if __debug__: print("WARNING: cannot parse date \"" + date_string
                                + "\" Value Error: {0}".format(err))
            return None
        except OverflowError as err:
            if __debug__: print("WARNING: cannot parse date \"" + date_string
                                + "\" Overflow Error: {0}".format(err))
            return None
        except TypeError as err:
            if __debug__: print("WARNING: cannot parse date \"" + date_string
                                + "\" Type Error: {0}".format(err))
            return None
        year = temp_date.year
        month = temp_date.month
        day = temp_date.day
        return datetime2(year, month, day, date_string = date_string, 
                         missing_year = missing_year,
                         missing_month = missing_month,
                         missing_day = missing_day,
                         missing_century = missing_century)
    
    @staticmethod
    def missing_date_parts(date_string):
        missing_day = False
        missing_month = False
        missing_year = False
        missing_century = False
        try:
            parsed_date_1 = dateparser.parse(date_string,
                                             settings={'RELATIVE_BASE':DATE_1,
                                                       'PREFER_DATES_FROM':"past"})
            if parsed_date_1 is None:
                raise ValueError("parser returned None")
            parsed_date_2 = dateparser.parse(date_string,
                                             settings={'RELATIVE_BASE':DATE_2,
                                                       'PREFER_DATES_FROM':"past"})
        except ValueError as err:
            raise ValueError("cannot parse date \"" + date_string
                             + "\" {0}".format(err))
        if parsed_date_2 is None: # handles dates like "02-29-00"
            if parsed_date_1 != datetime.datetime(2000, 2, 29):
                print("WARNING: unknown date encountered \""
                      + date_string + "\"")
            missing_century = True
            parsed_date_2 = dateparser.parse(date_string,
                                             settings={'RELATIVE_BASE':DATE_2,
                                                       'PREFER_DATES_FROM':"future"})
        
        missing_day = parsed_date_1.day != parsed_date_2.day
        missing_month = parsed_date_1.month != parsed_date_2.month
        missing_year = parsed_date_1.year % 100 != parsed_date_2.year % 100
        missing_century = missing_century or (~missing_year
                                              and (parsed_date_1.year
                                                   != parsed_date_2.year))
        return missing_year, missing_month, missing_day, missing_century
            
    def add_days(self, number_of_days):
        return self + number_of_days

    def subtract_days(self, number_of_days):
        return self - number_of_days

    def __add__(self, other):
        #if other is int then create a timedelta object with days=other
        if isinstance(other, int):
            other = datetime.timedelta(days=other)
        tmp = datetime.datetime.__add__(self, other)
        return datetime2(tmp.year, tmp.month, tmp.day,
                         date_string = self.date_string,
                         missing_year = self.missing_year,
                         missing_month = self.missing_month,
                         missing_day = self.missing_day,
                         missing_century = self.missing_century)

    def __sub__(self, other):
        #if other is int then create a timedelta object with days=other
        if isinstance(other, int):
            other = datetime.timedelta(days=other)
        tmp = datetime.datetime.__sub__(self, other)
        return datetime2(tmp.year, tmp.month, tmp.day,
                         date_string = self.date_string,
                         missing_year = self.missing_year,
                         missing_month = self.missing_month,
                         missing_day = self.missing_day,
                         missing_century = self.missing_century)

    def get_raw_string(self):
        return self.date_string
    
    def to_string(self, debug=False):
        if debug: date_string = (self.date_string + " (internal: "
                                 + self.strftime("%m/%d/%Y") + " missing ")
        
        #month; month dd; month yyyy; mm/dd/yyyy;
        if self.missing_year and self.missing_day:
            #only month
            if debug: date_string += "year, day)"
            else: date_string = self.strftime("%B")
        elif self.missing_year:
            #month dd
            if debug: date_string += "year)"
            else: date_string = self.strftime("%B %d")
        elif self.missing_day and self.missing_month:
            #year
            if self.missing_century:
                #yy
                if debug: date_string += "century, month, day)"
                else: date_string = self.strftime("%y")
            else:
                #yyyy
                if debug: date_string += "month, day)"
                else: date_string = self.strftime("%Y")
        elif self.missing_day:
            #month year
            if self.missing_century:
                #month yy
                if debug: date_string += "century, day)"
                else: date_string = self.strftime("%B %y")
            else:
                #month yyyy
                if debug: date_string += "day)"
                else: date_string = self.strftime("%B %Y")
        elif self.missing_century:
            #mm/dd/yy
            if debug: date_string += "century)"
            else: date_string = self.strftime("%m/%d/%y")
        else:
            #mm/dd/yyyy
            if debug: date_string += "nothing)"
            else: date_string = self.strftime("%m/%d/%Y")

        return date_string

import dateparser
import datetime
DATE_1 = datetime.datetime(3000, 12, 12)
DATE_2 = datetime.datetime(1000, 5, 5)

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
                missing_year = None,missing_month = None, missing_day = None):
        self = datetime.datetime.__new__(cls,year,month,day)
        self.missing_year = missing_year
        self.missing_month = missing_month
        self.missing_day = missing_day
        
        self.date_string = date_string
        return self
    
    
    @staticmethod
    def parse(date_string, *args, **kwargs):
        temp_date = dateparser.parse(date_string, *args, **kwargs)
        if temp_date is None:
            return None
        year = temp_date.year
        month = temp_date.month
        day = temp_date.day
        missing_year, missing_month, missing_day = datetime2.missing_date_parts(date_string)
        return datetime2(year, month, day, date_string = date_string, 
                         missing_year = missing_year, missing_month = missing_month, missing_day = missing_day)
    
    @staticmethod
    def missing_date_parts(date_string):
        parsed_date_1 = dateparser.parse(date_string, settings={'RELATIVE_BASE':DATE_1})
        parsed_date_2 = dateparser.parse(date_string, settings={'RELATIVE_BASE':DATE_2})

        missing_day = parsed_date_1.day != parsed_date_2.day
        missing_month = parsed_date_1.month != parsed_date_2.month
        missing_year = parsed_date_1.year != parsed_date_2.year

        return missing_year, missing_month, missing_day
            
    def add_days(self, number_of_days):
        return self + number_of_days

    def subtract_days(self, number_of_days):
        return self - number_of_days

    def __add__(self, other):
        #if other is int then create a timedelta object with days=other
        if isinstance(other, int):
            other = datetime.timedelta(days=other)
        tmp = datetime.datetime.__add__(self, other)
        return datetime2(tmp.year, tmp.month, tmp.day, date_string = self.date_string,
                missing_year = self.missing_year, missing_month = self.missing_month,
                missing_day = self.missing_day)

    def __sub__(self, other):
        #if other is int then create a timedelta object with days=other
        if isinstance(other, int):
            other = datetime.timedelta(days=other)
        tmp = datetime.datetime.__sub__(self, other)
        return datetime2(tmp.year, tmp.month, tmp.day, date_string = self.date_string,
                missing_year = self.missing_year, missing_month = self.missing_month,
                missing_day = self.missing_day)



    def to_string(self):
        #month; month dd; month yyyy; mm/dd/yyyy;
        if self.missing_year and self.missing_day:
            #only month
            return self.strftime("%B")
        elif self.missing_year:
            #month dd
            return self.strftime("%B %d")
        elif self.missing_day:
            #month yyyy
            return self.strftime("%B %Y")
        else:
            #mm/dd/yyyy;
            return self.strftime("%m/%d/%Y")
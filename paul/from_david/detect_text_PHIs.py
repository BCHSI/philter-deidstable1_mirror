# general comments

'''
    for readability, I would change all "[0-9]" to "\d"
    all changed stuff I put at the beginning of the line "changed!!" (with the quotation marks)

'''


def detect_text_PHIs(text):
    #here, text is the text of a single clinical note (already de-identified)

    #list to track all of the PHIs within a single clinical note
    text_PHIs = []

    #PHI_list: general format
    '''
    [
        {
            "location": match.span() (tuple containing the start and end locations of the PHI)
            "type": "name", "date", "patient number", etc.
            "subtype": varies depending on broad type, but this should help with making synthetic generation more realistic later on
            "modifiers": this is a dictionary that can be filled anything, in case there is a desire to implement more features
            "text": physical texts of the PHI (not including "[**" and "**]") - in case it is needed later on
        }
    ]
    '''

    #for detecting all instances where "[** ... **]" exists - these are where PHIs are located (also has to detect trouble characters)
    "changed!!" pattern = re.compile("\[\*\*.*?\*\*\]|&|<|>|\"|\'")

    #variable to ensure that entries in the PHI dictionary have unique keys (because of the way python's dict.update() function works)
    number = 0

    #list of unrecognized PHIs (for debugging)
    unrecognized = []

    "changed!!" #dates
    new_date_pattern = re.compile('(\d+\-\d+(\-\d+)?)|(\d+/\d+(/\d+)?)|(\d{4})') # this could be a mushed together version of date_pattern, second_date_pattern, and fourth_date_pattern
    new_date_pattern_1 = re.compile('(\d+(\-|/)){1,2}(\d+)?|(\d{4})') # this is an alternative to new_date_pattern, could match 12/14-2004 (not sure if you want that)
    new_third_date_pattern = re.compile('date|month|mth|year|yr|january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|october|oct|november|nov|december|dec', re.IGNORECASE) # added abbreviations

    date_pattern = re.compile('\d+\-\d+\-\d+|\d+/\d+/\d+') #for dates, which seem to come in the format YYYY-MM-DD, but I made it more flexible just in case
    second_date_pattern = re.compile('\d+\-\d+|\d+/\d+')#this is an alternate date type, which seems to be MM-DD (variants with / instead of - are also accounted for)
    third_date_pattern = re.compile('date|month|year|january|february|march|april|may|june|july|august|september|october|november|december', re.IGNORECASE) #for date ranges and dates that just say "month (only)", "year (only)", and month names
    fourth_date_pattern = re.compile('[0-9][0-9][0-9][0-9]') #this is for another alternate date type, which seems to be YYYY
    date_range_pattern = re.compile('range', re.IGNORECASE) #this is so that date ranges will actually be converted to date ranges and not just a single date

    #names
    name_pattern = re.compile('name', re.IGNORECASE) #searches for the word "name" (i.e. doctor and patient names), regardless of case
    gender_name_patterns = [re.compile('male', re.IGNORECASE), re.compile('female', re.IGNORECASE)]  #these regular expressions could technically be made different variables, but I think this is a bit clearer in terms of the grouping
    format_name_patterns = [re.compile('first', re.IGNORECASE), re.compile('last', re.IGNORECASE)] #these regular expressions aim to capture instances where the tag is only for a first or last name

    #holidays
    holiday_pattern = re.compile('holiday', re.IGNORECASE) #searches for the word "holiday", regardless of case

    #contact information
    email_pattern = re.compile('email', re.IGNORECASE) #searches for the word "email" (not just address, as this would catch street addresses as well)
    contact_pattern = re.compile('info', re.IGNORECASE) #searches for the word "info" (there are many variations of this extremely vague tag, and it will be replaced by a phone number or email address at random)
    phone_pattern = re.compile('phone', re.IGNORECASE) #searches for the word "phone", which should usually catch both phone and fax numbers
    pager_pattern = re.compile('pager', re.IGNORECASE) #searches for the word "pager", regardless of case
    url_pattern = re.compile('url', re.IGNORECASE) #searches for the word "url", regardless of case

    #IDs (generally numbers)

    '''

        something to think about is abbreviations, eg. "ss num" for "social security", although idk if MIMIC would have abbreviations in tags

        there are also different ways to represent the regex
                re.compile('(social.*?security)|(scl.*?security)|(ss)', re.IGNORECASE)

        for example
                re.compile('(social|scl|s).*?(security|s)', re.IGNORECASE)
        would also work because its 0+ number of chars

        i don't know which version is best (don't think it matters)

    '''

    "changed!!" # alternatives (see comment above)
    numeric_identifier_pattern = re.compile('numeric.*?identifier', re.IGNORECASE) #searches for "numeric identifier" with any number of characters in between (in case there are spaces or something)
    social_security_pattern = re.compile('(social.*?security)|(scl.*?security)|(ss)', re.IGNORECASE) #searches for "social security" with any number of characters in between
    provider_pattern = re.compile('provider', re.IGNORECASE) #searches for the word "provider", regardless of case
    medical_record_pattern = re.compile('(medical|mdcl|med|md).*?(record|rcrd|rcd)', re.IGNORECASE) #searches for "medical record" with any number of characters in between
    md_number_pattern = re.compile('md.*?(number|num|nm)', re.IGNORECASE) #searches for "md number" with any number of characters in between
    job_number_pattern = re.compile('job.*?(number|num|nm)', re.IGNORECASE) #searches for "job number" with any number of characters in between
    clip_number_pattern = re.compile('clip.*?(number|num|nm)', re.IGNORECASE) #searches for "clip number" with any number of characters in between

    # originals
    numeric_identifier_pattern = re.compile('numeric.*?identifier', re.IGNORECASE) #searches for "numeric identifier" with any number of characters in between (in case there are spaces or something)
    social_security_pattern = re.compile('social.*?security', re.IGNORECASE) #searches for "social security" with any number of characters in between
    provider_pattern = re.compile('provider', re.IGNORECASE) #searches for the word "provider", regardless of case
    medical_record_pattern = re.compile('medical.*?record', re.IGNORECASE) #searches for "medical record" with any number of characters in between
    md_number_pattern = re.compile('md.*?number', re.IGNORECASE) #searches for "md number" with any number of characters in between
    job_number_pattern = re.compile('job.*?number', re.IGNORECASE) #searches for "job number" with any number of characters in between
    clip_number_pattern = re.compile('clip.*?number', re.IGNORECASE) #searches for "clip number" with any number of characters in between

    #ages (over 90 only)
    age_pattern = re.compile('age', re.IGNORECASE) #this only needs to detect "age" since all obscured ages are those of patients over 90 years old

    #locations (more abbreviations)
    "changed!!" # also don't forget about hospital suites, not just wards and units
    "changed!!" new_hospital_pattern = re.compile('hospital|hosp|ward|wrd|unit', re.IGNORECASE) #searches for the various terms associated with hospital locations

    hospital_pattern = re.compile('hospital|ward|unit', re.IGNORECASE) #searches for the various terms associated with hospital locations
    "changed!!" # you would need suite in the next one if you're gonna add it
    hospital_modifier_patterns = [re.compile('ward', re.IGNORECASE), re.compile('unit', re.IGNORECASE)] #searches for the modifiers associated with hospital locations
    home_pattern = re.compile('home|address|zip.*?code|state|country', re.IGNORECASE) #searches for the various terms associated with home locations
    work_pattern = re.compile('work|university', re.IGNORECASE) #searches for the various terms associated with work locations
    "changed!!!" po_box_pattern = re.compile('p.*?o.*?box', re.IGNORECASE) #searches for "po box" with any number of characters in between
    address_pattern = re.compile('address', re.IGNORECASE) #searches for the word "address", regardless of case
    "changed!!!" number_pattern = re.compile('number|num|nm', re.IGNORECASE) #searches for the word "number", regardless of case
    location_pattern = re.compile('location', re.IGNORECASE) #searches for the word "location", regardless of case

    #create a variable and a dictionary so that subtypes and modifiers can be added (for extra detail about a given PHI)
    subtype = None #setting this to None initially; will be modified by the code below if necessary
    modifiers = {} #setting this to an empty dictionary - the reason it isn't initially set to None is so that the dictionary can be updated with something like modifiers["key"]:value in the code
    unrecognized = [] #to make sure no

    #searching through all PHIs for their location, type, and subtype
    for match in pattern.finditer(text):

        #figure out whether the match is a PHI or a trouble character and define test_text accordingly
        if re.compile('\[\*\*.*?\*\*\]').search(match.group()) != None:
            test_text = match.group()[3:-3].lower() #since the starting and ending sequences for PHI's are 3 characters long, doing this isolates just the text in the middle of the indicators
        else:
            test_text = match.group()

        #use the text of the PHI to determine its broad type (date, name, phone number, other number, etc.)

        #dates (subtypes: range)
        if date_pattern.search(test_text) != None or second_date_pattern.search(test_text) != None or third_date_pattern.search(test_text) != None or fourth_date_pattern.match(test_text) != None:
            TYPE = "date"

            #seeing whether the date given is in the form of a date range (since ranges will have to be treated differently)
            if date_range_pattern.search(test_text) != None:
                subtype = "range"

        #names (subtypes: patient, doctor; modifiers: gender (male, female, unknown))
        elif (name_pattern.search(test_text) != None) and hospital_pattern.search(test_text) == None:
            TYPE = "name"

            #checking gender of the person (if one is not detected, then leave as None)
            if gender_name_patterns[0].search(test_text) != None:
                modifiers["gender"] = "male"
            elif gender_name_patterns[1].search(test_text)!= None:
                modifiers["gender"] = "female"
            else:
                modifiers["gender"] = None

            #checking whether the name tag is only for a first or last name
            if format_name_patterns[0].search(test_text) != None:
                modifiers["format"] = "first"
            elif format_name_patterns[1].search(test_text) != None:
                modifiers["format"] = "last"
            else:
                modifiers["format"] = None

        #holidays (no subtypes)
        elif holiday_pattern.search(test_text) != None:
            TYPE = "holiday"

        #contact information (subtypes: email, contact (a bit vague in my opinion as well), phone, pager, url)
        elif email_pattern.search(test_text) != None or contact_pattern.search(test_text) != None or phone_pattern.search(test_text) != None or pager_pattern.search(test_text) != None or url_pattern.search(test_text) != None:
            TYPE = "contact"

            #checking contact category subtypes
            if email_pattern.search(test_text) != None:
                subtype = "email"
            elif contact_pattern.search(test_text) != None:
                subtype = "contact"
            elif phone_pattern.search(test_text) != None:
                subtype = "phone"
            elif pager_pattern.search(test_text) != None:
                subtype = "pager"
            else:
                subtype = "url"

        #identification (subtypes: numeric_identifier, social_security_number, provider_number, medical_record_number)
        elif numeric_identifier_pattern.search(test_text) != None or social_security_pattern.search(test_text) != None or provider_pattern.search(test_text) != None or medical_record_pattern.search(test_text) != None or md_number_pattern.search(test_text) != None or job_number_pattern.search(test_text) != None or clip_number_pattern.search(test_text) != None:
            TYPE = "ID"

            #checking identifier category subtypes
            if numeric_identifier_pattern.search(test_text) != None:
                subtype = "numeric_identifier"
            elif social_security_pattern.search(test_text) != None:
                subtype = "social_security_number"
            elif provider_pattern.search(test_text) != None:
                subtype = "provider_number"
            elif medical_record_pattern.search(test_text) != None:
                subtype = "medical_record_number"
            elif md_number_pattern.search(test_text) != None:
                subtype = "md_number"
            elif job_number_pattern.search(test_text) != None:
                subtype = "job_number"
            else:
                subtype = "clip_number"

        #age (no subtypes)
        elif age_pattern.search(test_text) != None:
            TYPE = "age"

        #locations (subtypes: hospital, home, work, other; modifiers: ward, unit, name, number, address) - a bit oversimplified but plenty satisfactory for Philter (not to mention those more complex versions will be randomly generated anyway)
        elif hospital_pattern.search(test_text) != None or home_pattern.search(test_text) != None or work_pattern.search(test_text) != None or po_box_pattern.search(test_text) != None or location_pattern.search(test_text) != None:
            TYPE = "location"

            #checking location category subtypes
            if hospital_pattern.search(test_text) != None:
                subtype = "hospital"
                #checking if the hospital location is a unit or ward
                if hospital_modifier_patterns[0].search(test_text) != None:
                    modifiers["hospital_subtype"] = "ward"
                else:
                    modifiers["hospital_subtype"] = "unit"
            elif home_pattern.search(test_text) != None:
                subtype = "home"
            elif work_pattern.search(test_text) != None:
                subtype = "work"
            elif location_pattern.search(test_text) != None:
                subtype = "unknown"
            else:
                subtype = "other"

            #checking location category modifiers
            if name_pattern.search(test_text) != None:
                modifiers["location_type"] = "name"
            elif address_pattern.search(test_text) != None:
                modifiers["location_type"] = "address"
            elif number_pattern.search(test_text) != None:
                modifiers["location_type"] = "number"

        "changed!!" elif test_text in ["&", "<", ">", '"', "'"]:
            TYPE = "trouble_character"

        #unrecognized (in addition to being added to the list of the given text's PHI, so that they can be removed, it will be added to a JSON as a sanity check to see that PHIs are being properly detected)
        else:
            TYPE = "unrecognized"
            unrecognized.append(test_text)

        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #if there is a desire to add functionality to make synthetic PHI's consistent accross multiple notes as well as occurances within the text, the code for that should probably be added here
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        #add the PHI to the dictionary for this text's PHIs (needs to be done no matter what, as the text needs to have PHIs subsituted - this will help do that)
        text_PHIs.append({
            "location": match.span(),
            "type": TYPE,
            "subtype": subtype,
            "modifiers": modifiers,
            "text": test_text,
        })

        number += 1

    return text_PHIs, unrecognized

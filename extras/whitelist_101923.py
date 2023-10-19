# Original whitelist and references was recieved from Kathleen. These references are mostly from 2017.
# Goal is to update umls_set | des_mesh_set | mesh_heir_term_set | mesh_set | abbrevs_and_definitions_set | mp_set_normalized | snomed_set | drug_set | icd9_diagnoses_set.
# In each section, the old code is also used to obtain the original set and make a comparison for the documentation, but 
# since is commented out at the end.

import pandas as pd
import json
import csv
import xml.etree.ElementTree as ET
import re
import string
import unicodedata
import csv
import random
import sys
from bs4 import BeautifulSoup

# Functions

# function to get all the existing tags
def get_tags (inp):
    import xml.etree.ElementTree as ET
    xmlTree = ET.parse(inp)
    tags = {elem.tag for elem in xmlTree.iter()}
    #print(tags)
    return tags

# function to extract all the child elements corresponding to the given tags
def get_terms (sp, ls):
    umls_xml = []
    for item in ls:
        Text = sp.find_all(item)
        for text in Text:
            umls_xml.append(text.text)
    return(umls_xml)

# function to clean and remove unwanted characters
def clean_set(ls):
    series = pd.Series(ls)
    # Remove blanks
    series = series[series.notnull()]
    # Remove numbers
    series = series.str.replace('\d+', '')
    # Remove apostrophes, underscores, backslashes
    series = series.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') # Edit 1/22/18
    # Remove single character words
    series = series.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ')
    # The pattern \b\w\b will replace any single word character with a word boundary
    series = series.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
    # Remove rows where length of descriptor is less than 3
    series = list(series[series.str.len() > 2])

    list_ = [term.split() for term in series] # convert each string into a list of the words in the string
    list_ = [item for sublist in list_ for item in sublist] # flatten the list of lists into a single list
    list_ = [i.lower() for i in list_] # make all lower case
    list_ = [i.replace(' ','') for i in list_] # last check for spaces
    return(set(list_))




#1- umls
# Read in the NLM Lexicon containing common English words and medical terms
# Old: https://lexsrv3.nlm.nih.gov/LexSysGroup/Projects/lexicon/2017/release/LEX/LEXICON


# New: https://lhncbc.nlm.nih.gov/LSG/Projects/lexicon/current/web/release/ --> 2023 Lexicon Release
# (How to navigate) https://lhncbc.nlm.nih.gov/LHC-downloads/downloads.html --> Downloads --> Specialist Lexicon --> Download the SPECIALIST Lexicon
## There are several formats available
# f = open('LEXICON.ascii','r')
# lines = f.read()
# lines[0:100]

# For the whitelis regeneration the xml file was selected and downloaded on August 2023 
filename = 'LEXICON2023.xml'

# parse xml
from bs4 import BeautifulSoup

with open(filename, 'r') as f:
    file = f.read()

soup = BeautifulSoup(file, 'xml')

# get the tags in the existing file
tags = get_tags (filename)

# extract all the child elements corresponding to the given tags
umls_xml_list = get_terms(soup, list(tags))

# clean and remove unwanted characters and conver to set
umls2023 = clean_set(umls_xml_list)



#2- descriptor_mesh
from bs4 import BeautifulSoup
filename = 'desc2023.xml'

with open(filename, 'r') as f:
    file = f.read()

soup = BeautifulSoup(file, 'xml')

# # get the tags in the existing file
tags = get_tags (filename)

# # extract all the child elements corresponding to the given tags
mesh_xml_list = get_terms(soup, list(tags))

# clean and remove unwanted characters and convet to set
mesh2023 = clean_set(mesh_xml_list)

des_mesh_set = mesh2023



#3- med_abbreviations
#The original source is UPDATED ON MAY 22, 2018 (https://nurseslabs.com/nursing-abbreviations/).
#We did not find more recent versions of Nursing abbreviation so we used original file and code for this section.

################################## list_of_med_abbreviations.csv ###############################
# Read in list of common medical abbreviations
abbreviations = pd.read_csv('list_of_med_abbreviations.csv', delimiter = ',')
#print("list_of_med_abbreviations.csv loaded")

# Create list from df
abbrev_list = list(abbreviations.abbreviation)
abbrev_list = [i for i in abbrev_list if type(i) is str]
abbrev_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|','').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in abbrev_list]
abbrev_list = [i.lower() for i in abbrev_list]
abbrev_list = [term.split() for term in abbrev_list if type(term) is str]
abbrev_list = [item for sublist in abbrev_list for item in sublist] # flatten
abbrev_set = set(abbrev_list)


### Medical abbreviations
more_abbreviations = pd.read_csv('medical_abbreviations.csv', delimiter = ',',encoding="latin-1")

abbreviations_list = list(more_abbreviations['abbreviation'])
abbreviations_list = [str(i) for i in abbreviations_list]
abbreviations_list = [i.lower() for i in abbreviations_list]

definitions_list = list(more_abbreviations['definition'])
definitions_list = [term.split(" ") for term in definitions_list]
definitions_list = [item for sublist in definitions_list for item in sublist]
definitions_list = [i.replace("(",'').replace(")",'').replace(" ",'').replace("/",'')  for i in definitions_list]
definitions_list = [i.lower() for i in definitions_list]

abbrevs_and_definitions_set = set(abbreviations_list + definitions_list) | abbrev_set
# len(abbrevs_and_definitions_set)



# 4- mplus.xml
"""
Helper function is_unicode determines whether a string is unicode or not. Outputs
a boolean
"""
def is_unicode(s):
    if isinstance(s, str):
        return False
    elif isinstance(s, bytes):
    #elif isinstance(s, unicode):
        return True
    else:
        print("not a string")
        
### mplus.xml
mp_set = set()
tree = ET.ElementTree(file='mplus_topics_2023-08-24.xml')
#print("mplus.xml loaded")

# also-called
for elem in tree.iter(tag='also-called'):
    mp_set = mp_set | set(elem.text.lower().split(' '))

# health-topic
for elem in tree.iterfind('health-topic'):
    mp_set = mp_set | set(elem.attrib['title'].lower().split(' '))


# Create a new set for mp that contains ascii characters only
# Edit 1/22/18:
mp_set_normalized = set()
for item in mp_set:
    if is_unicode(item):
        new_item = unicodedata.normalize('NFD', item).encode('ascii', 'ignore')
        mp_set_normalized.add(new_item)
    else:
        mp_set_normalized.add(item)


mp_set_normalized = set([i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in mp_set_normalized])  # Edit 1/22/18
mp_set_normalized = [term.split() for term in mp_set_normalized if type(term) is str]
mp_set_normalized = set([item for sublist in mp_set_normalized for item in sublist]) # flatten

#len(mp_set_normalized)
#len(mp_set_normalized - mp_set_normalized0) #132 # e.g., 19, 2019, cov, covid, boost, positive, lacrimation, ...
# len(mp_set_normalized0 - mp_set_normalized) # 75 # e.g., 12, 7, adopción,narcotics, .. 

# I used the files generated on August 24, 2023 - 
# I was not able to find 2017 on the website because only the six most recent files and their corresponding DTDs are available on https://medlineplus.gov/xml.html.
# I used the file I recieved from Kathleen to compare with 2023 version that I used. 
# There are 132 words in new set that did not exist in old set. (Out of 3676)



# 5- SNOMED CT
# Was not able to download the files first, requested UMLS liscence. I recieved an email indicating that my licence was approved and the email also included links to SNOMED CT, ...I had to use login.gov with user/pass and message to download the files.

# I downloaded two seperate folders from different links, sct2_Description_Full-en_US1000124_20230901 and sct2_TextDefinition_Full-en_US1000124_20230901 were in https://www.nlm.nih.gov/healthit/snomedct/us_edition.html
# and tls_Icd10cmHumanReadableMap_US1000124_20230901 in {Download SNOMED CT to ICD-10-CM Mapping Resources} and used tls_Icd10cmHumanReadableMap_US1000124_20230901.tsz.

import csv
filename = './SNOMED/sct2_Description_Full-en_US1000124_20230901.txt'
sno_Des = pd.read_csv(filename, sep="\t", error_bad_lines=False)
# Get form column
form_df = sno_Des['term']
# Remove blanks
form_df = form_df[form_df.notnull()]
# Remove characters
form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
# Makes list 
form_list = list(form_df)
form_list = [term.split(" ") for term in form_list]
form_list = [item for sublist in form_list for item in sublist] 
form_list = [i.lower() for i in form_list]
sno_Des_set = set(form_list)

filename = './SNOMED/sct2_TextDefinition_Full-en_US1000124_20230901.txt'
sno_Txt = pd.read_csv(filename, sep="\t", error_bad_lines=False)
# Get form column
form_df = sno_Txt['term']
# Remove blanks
form_df = form_df[form_df.notnull()]
# Remove characters
form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
# Makes list 
form_list = list(form_df)
form_list = [term.split(" ") for term in form_list]
form_list = [item for sublist in form_list for item in sublist] 
form_list = [i.lower() for i in form_list]
sno_Txt_set = set(form_list)

filename = './SNOMED/tls_Icd10cmHumanReadableMap_US1000124_20230901.tsv'
tls = pd.read_csv(filename, sep="\t", error_bad_lines=False)
# Get form column
form_df = tls['referencedComponentName']
# Remove blanks
form_df = form_df[form_df.notnull()]
# Remove characters
form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
# Makes list 
form_list = list(form_df)
form_list = [term.split(" ") for term in form_list]
form_list = [item for sublist in form_list for item in sublist] 
form_list = [i.lower() for i in form_list]
tls_set_1 = set(form_list)

form_df = tls['mapTargetName']
# Remove blanks
form_df = form_df[form_df.notnull()]
# Remove characters
form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
# Makes list 
form_list = list(form_df)
form_list = [term.split(" ") for term in form_list]
form_list = [item for sublist in form_list for item in sublist] 
form_list = [i.lower() for i in form_list]
tls_set_2 = set(form_list)

tls_set = tls_set_1 | tls_set_2

## SNOMED CT COVID-19 Related Content
# https://confluence.ihtsdotools.org/display/snomed/SNOMED%20CT%20COVID-19%20Related%20Content

from bs4 import BeautifulSoup
filename = './SNOMED/SNOMED CT COVID-19 Related Content - Announcements - SNOMED Confluence.html'

with open(filename, 'r') as f:
    file = f.read()

soup = BeautifulSoup(file, "html.parser")

#soup.find_all('table')[0]
soup = BeautifulSoup(file, "lxml") #Parse the HTML as a string
table = soup.find_all('table')[0] # Grab the first table


snomed_covid = []
for row in table.find_all('tr'):
    if 'tr role' in str(row):
        #print(row)
        row.find_all('td')
        s1 = str(row.find_all('td')[2])
        s2 = str(row.find_all('td')[3])
        #print(s1)
        #print(s2)
        #print(s1.count('>'), s2.count('>'))
        if (s1.count('>') == 2) & (s2.count('>') ==2):
            #print(s1.split(">")[1].split("<")[0])
            #print(s2.split(">")[1].split("<")[0])
            #print('first if')
            snomed_covid.append(s1.split(">")[1].split("<")[0])
            snomed_covid.append(s2.split(">")[1].split("<")[0])
        if (s1.count('>') == 4) & (s2.count('>') ==2):
            #print(s1.split(">")[2].split("<")[0])
            #print(s2.split(">")[1].split("<")[0])
            #print('second if')
            snomed_covid.append(s1.split(">")[2].split("<")[0])
            snomed_covid.append(s2.split(">")[1].split("<")[0])
        if (s1.count('>') == 2) & (s2.count('>') ==4):
            #print(s1.split(">")[1].split("<")[0])
            #print(s2.split(">")[2].split("<")[0])
            #print('3rd if')
            snomed_covid.append(s1.split(">")[1].split("<")[0])
            snomed_covid.append(s2.split(">")[2].split("<")[0])
        if (s1.count('>') == 4) & (s2.count('>') ==4):
            #print(s1.split(">")[2].split("<")[0])
            #print(s2.split(">")[2].split("<")[0])
            snomed_covid.append(s1.split(">")[2].split("<")[0])
            snomed_covid.append(s2.split(">")[2].split("<")[0])
            #print('4th if')
            
# SNOMED CT to ICD-10 Map -> The content of this table is already included

### Existing Relevant SNOMED CT Content Added to the GPS

table = soup.find_all('table')[2]
for row in table.find_all('tr'):
    if 'tr role' in str(row):
        #print(row)
        row.find_all('td')
        s1 = str(row.find_all('td')[2])
        s2 = str(row.find_all('td')[3])
        if (s1.count('>') == 2) & (s2.count('>') ==2):
            #print(s1.split(">")[1].split("<")[0])
            #print(s2.split(">")[1].split("<")[0])
            #print('first if')
            snomed_covid.append(s1.split(">")[1].split("<")[0])
            snomed_covid.append(s2.split(">")[1].split("<")[0])
        if (s1.count('>') == 4) & (s2.count('>') ==2):
            #print(s1.split(">")[2].split("<")[0])
            #print(s2.split(">")[1].split("<")[0])
            #print('second if')
            snomed_covid.append(s1.split(">")[2].split("<")[0])
            snomed_covid.append(s2.split(">")[1].split("<")[0])
        if (s1.count('>') == 2) & (s2.count('>') ==4):
            #print(s1.split(">")[1].split("<")[0])
            #print(s2.split(">")[2].split("<")[0])
            #print('3rd if')
            snomed_covid.append(s1.split(">")[1].split("<")[0])
            snomed_covid.append(s2.split(">")[2].split("<")[0])
        if (s1.count('>') == 4) & (s2.count('>') ==4):
            #print(s1.split(">")[2].split("<")[0])
            #print(s2.split(">")[2].split("<")[0])
            snomed_covid.append(s1.split(">")[2].split("<")[0])
            snomed_covid.append(s2.split(">")[2].split("<")[0])
            #print('4th if')
        
#len(snomed_covid)
series = pd.Series(snomed_covid)
series = series.str.replace('\d+', '').str.replace('\xa0','').str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
form_list = [term.split(" ") for term in list(series)]
form_list = [item for sublist in form_list for item in sublist] 
form_list = [i.lower() for i in form_list]
snomed_covid_set = set(form_list)
#len(snomed_covid_set)

snomed2023_set = tls_set | sno_Txt_set | sno_Des_set | snomed_covid_set
series = pd.Series(list(snomed2023_set))
series = series.str.replace('\d+', '')
form_list = [term.split(" ") for term in list(series)]
form_list = [item for sublist in form_list for item in sublist] 
snomed2023_set = set(form_list)
# len(snomed2023_set) -> 107734

#seems like snomed_covid_set is already included in sno_Des_set



# 6- FDA: list of approved drugs, active ingredients, strengths
### Not sure about strength - maybe remove? maybe use regex - keep in mind when you are doing the test

################################# FDA: list of approved drugs, active ingredients, strengths, form ##################
# go to https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files and download the zip file
# copy "Products.txt"

filename = 'Products_drugs_fda_2023.txt'
# fda_drugs_df2023 = pd.read_fwf(filename) # Edit August 2023
import csv
fda_drugs_df2023 = pd.read_csv(filename, sep="\t", error_bad_lines=False)

####### Form
# Get form column
form_df = fda_drugs_df2023['Form']
# Remove blanks
form_df = form_df[form_df.notnull()]
# Remove characters
form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
# Makes list 
form_list = list(form_df)
form_list = [term.split(" ") for term in form_list]
form_list = [item for sublist in form_list for item in sublist] 
form_list = [i.lower() for i in form_list]


######## Strengths
# Get strength column
strength_df = fda_drugs_df2023['Strength']
# Remove blanks
strength_df = strength_df[strength_df.notnull()]
# Remove characters
strength_df = strength_df.str.replace("*",'').str.replace(';',' ').str.replace('(','').str.replace(')','')
# Makes list 
strength_list = list(strength_df)
strength_list = [term.split(" ") for term in strength_list]
strength_list = [item for sublist in strength_list for item in sublist] 
strength_list = [i.lower() for i in strength_list]


###### Drug names
# Get drug names column 
drug_df = fda_drugs_df2023['DrugName']
# Remove blanks
drug_df = drug_df[drug_df.notnull()]
# Remove characters
drug_df = drug_df.str.replace("*",'').str.replace(';',' ').str.replace('(','').str.replace(')','')
# Makes list 
drug_list = list(drug_df)
drug_list = [term.split(" ") for term in drug_list]
drug_list = [item for sublist in drug_list for item in sublist] 
drug_list = [i.lower() for i in drug_list]


######## Actice ingredients
# Get drug names column 
ingredient_df = fda_drugs_df2023['ActiveIngredient']
# Remove blanks
ingredient_df = ingredient_df[ingredient_df.notnull()]
# Remove characters
ingredient_df = ingredient_df.str.replace("*",'').str.replace(';',' ').str.replace('(','').str.replace(')','')
# Makes list 
ingredient_list = list(ingredient_df)
ingredient_list = [term.split(" ") for term in ingredient_list]
ingredient_list = [item for sublist in ingredient_list for item in sublist] 
ingredient_list = [i.lower() for i in ingredient_list]


# Combine lists into set
drug_set2023 = set(form_list + strength_list + ingredient_list + drug_list)

# len(drug_set2023 - drug_set) # 6236 # e.g., '17.7mg', 'solu-medrol', 'hyaluronidase-fihj', '50mg/300mg/300mg'
# len(drug_set - drug_set2023) # 148 # e.g., '0.00%', '0.035%', '0.090mg', '0.25gm/packet', '3.75mg/vial,7.5mg/vial'
# drug_set2023 why / and - still there? Also clean up at the end, investigate the effect of strength



# 7- ICD9 diagnoses
############################### ICD9 diagnoses ###############################
# List of icd9 diagnoses, already separated by word
# Go to https://www.cms.gov/Medicare/Coding/ICD9ProviderDiagnosticCodes/codes.html and download the Version 32 Full and Abbreviated Code Titles Effective October 1, 2014 [ZIP, 1MB]
# upload the two .xlsx files

#converters={'DIAGNOSIS CODE': str} to keep leading zeros in a column when reading CSV with Pandas?
icd9dx = pd.read_excel('icd9-CMS32_DESC_LONG_SHORT_DX.xlsx', converters={'DIAGNOSIS CODE': str})
icd9sg = pd.read_excel('icd9-CMS32_DESC_LONG_SHORT_SG.xlsx', converters={'PROCEDURE CODE': str})

###### 
# dx
icd9_dx_dic = {}
for item in ['DIAGNOSIS CODE', 'LONG DESCRIPTION', 'SHORT DESCRIPTION']:
    icd9_dx = icd9dx[item]
    # Remove blanks
    icd9_dx = icd9_dx[icd9_dx.notnull()]
    # Makes list 
    icd9_dx_list = list(icd9_dx)
    icd9_dx_dic[item] = icd9_dx_list

icd9_dx_list = icd9_dx_dic['DIAGNOSIS CODE'] + icd9_dx_dic['LONG DESCRIPTION'] + icd9_dx_dic['SHORT DESCRIPTION']

###### 
# sg
icd9_sg_dic = {}
for item in ['PROCEDURE CODE', 'LONG DESCRIPTION', 'SHORT DESCRIPTION']:
    icd9_sg = icd9sg[item]
    # Remove blanks
    icd9_sg = icd9_sg[icd9_sg.notnull()]
    # Makes list 
    icd9_sg_list = list(icd9_sg)
    icd9_sg_dic[item] = icd9_sg_list

icd9_sg_list = icd9_sg_dic['PROCEDURE CODE'] + icd9_sg_dic['LONG DESCRIPTION'] + icd9_sg_dic['SHORT DESCRIPTION']

icd9_list = icd9_dx_list + icd9_sg_list
icd9_list = [str(i).replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','').replace('"','') for i in icd9_list]
icd9_list = [term.split(" ") for term in icd9_list]
icd9_list = [item for sublist in icd9_list for item in sublist] 
icd9_list = [i.lower() for i in icd9_list]
icd9_set = set(icd9_list)
#len(icd9_set) #27985
# len(icd9_diagnoses_set - icd9_set) #623
# len(icd9_set - icd9_diagnoses_set) #1276

# Remove numbers
series = pd.Series(list(icd9_set))
series = series.str.replace('\d+', '')
form_list = [term.split(" ") for term in list(series)]
form_list = [item for sublist in form_list for item in sublist] 
icd9_set = set(form_list)
# len(icd9_set) #10991



# 8 - ICD10 diagnoses
# go to https://www.cms.gov/medicare/coding-billing/icd-10-codes/2023-icd-10-cm and 
# download "2023 Code Tables, Tabular and Index - updated 01/11/2023 (ZIP)", use the .xml files as input
# also add exemption and addendum and ...

#### 2023 Code Tables, Tabular and Index - updated 01/11/2023 (ZIP)
filename = './icd10-files/icd10cm_drug_2023.xml'

# parse xml
from bs4 import BeautifulSoup

with open(filename, 'r') as f:
    file = f.read()

soup = BeautifulSoup(file, 'xml')

# get the tags in the existing file
tags = get_tags (filename)
#tags
# don't get the root tags because it will contain the leave nodes as well as all type of wierd characters, containers, etc
tags = ['cell','title','head','nemod','see', 'seeAlso']
# extract all the child elements corresponding to the given tags
icd10_list_drug = get_terms(soup, list(tags))

# clean and remove unwanted characters and convert to set, but instead of clean set function use the icd-9 cleaning, because for example
# Kathleem did not remove numbers for icd 9 at this step, etc.
#umls2023 = clean_set(umls_xml_list)

icd10_list_drug = [str(i).replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','').replace('"','').replace('.','').replace('\n',' ') for i in icd10_list_drug] #.replace('.','')
icd10_list_drug = [term.split(" ") for term in icd10_list_drug]
icd10_list_drug = [item for sublist in icd10_list_drug for item in sublist] 
icd10_list_drug = [i.lower() for i in icd10_list_drug]
# I added the following part
icd10_list_drug = [i for i in icd10_list_drug if len(i) > 1]
# len(set(icd10_list_drug))


filename = './icd10-files/icd10cm_eindex_2023.xml'
# parse xml
from bs4 import BeautifulSoup

with open(filename, 'r') as f:
    file = f.read()

soup = BeautifulSoup(file, 'xml')

# get the tags in the existing file
# don't get the root tags
tags = get_tags (filename)
#tags
#don't get the root tags because it will contain the leave nodes as well as all type of wierd characters, containers, etc
tags = ['code', 'nemod', 'see', 'seeAlso', 'seecat', 'subcat', 'title', ]
# extract all the child elements corresponding to the given tags
icd10_list_eindex = get_terms(soup, list(tags))

# clean and remove unwanted characters and convert to set, but instead of clean set function use the icd-9 cleaning, because for example
# Kathleem did not remove numbers for icd 9 at this step, etc.
#umls2023 = clean_set(umls_xml_list)

icd10_list_eindex = [str(i).replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','').replace('"','').replace('.','').replace('\n',' ') for i in icd10_list_eindex] #.replace('.','')
icd10_list_eindex = [term.split(" ") for term in icd10_list_eindex]
icd10_list_eindex = [item for sublist in icd10_list_eindex for item in sublist] 
icd10_list_eindex = [i.lower() for i in icd10_list_eindex]
# I added the following part
icd10_list_eindex = [i for i in icd10_list_eindex if len(i) > 1]
#len(set(icd10_list_eindex))
# Remove the "nemod" tag itsels


filename = './icd10-files/icd10cm_index_2023.xml'

# parse xml
from bs4 import BeautifulSoup

with open(filename, 'r') as f:
    file = f.read()

soup = BeautifulSoup(file, 'xml')

# get the tags in the existing file
tags = get_tags (filename)
#tags
#don't get the root tags because it will contain the leave nodes as well as all type of wierd characters, containers, etc
tags = ['code','manif', 'nemod', 'see', 'seeAlso', 'seecat', 'subcat', 'title']
# extract all the child elements corresponding to the given tags
icd10_list_index = get_terms(soup, list(tags))

# clean and remove unwanted characters and convert to set, but instead of clean set function use the icd-9 cleaning, because for example
# Kathleem did not remove numbers for icd 9 at this step, etc.
#umls2023 = clean_set(umls_xml_list)

icd10_list_index = [str(i).replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','').replace('"','').replace('.','').replace('\n',' ') for i in icd10_list_index] #.replace('.','')
icd10_list_index = [term.split(" ") for term in icd10_list_index]
icd10_list_index = [item for sublist in icd10_list_index for item in sublist] 
icd10_list_index = [i.lower() for i in icd10_list_index]
# I added the following part
icd10_list_index = [i for i in icd10_list_index if len(i) > 1]
len(set(icd10_list_index))


filename = './icd10-files/icd10cm_neoplasm_2023.xml'

# parse xml
from bs4 import BeautifulSoup

with open(filename, 'r') as f:
    file = f.read()

soup = BeautifulSoup(file, 'xml')

# get the tags in the existing file
# Be careful, don't get the root tags because it will contain the leave nodes as well as all type of wierd characters, containers, etc
tags = get_tags (filename)
#tags
#don't get the root tags because it will contain the leave nodes as well as all type of wierd characters, containers, etc
tags = ['cell','head', 'manif', 'nemod', 'see', 'seeAlso', 'title' ]
# extract all the child elements corresponding to the given tags
icd10_list_neoplasm = get_terms(soup, list(tags))

# clean and remove unwanted characters and convert to set, but instead of clean set function use the icd-9 cleaning, because for example
# Kathleem did not remove numbers for icd 9 at this step, etc.
#umls2023 = clean_set(umls_xml_list)

icd10_list_neoplasm = [str(i).replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','').replace('"','').replace('.','').replace('\n',' ') for i in icd10_list_neoplasm] #.replace('.','')
icd10_list_neoplasm = [term.split(" ") for term in icd10_list_neoplasm]
icd10_list_neoplasm = [item for sublist in icd10_list_neoplasm for item in sublist] 
icd10_list_neoplasm = [i.lower() for i in icd10_list_neoplasm]
# added the following part
icd10_list_neoplasm = [i for i in icd10_list_neoplasm if len(i) > 1]
len(set(icd10_list_neoplasm))


filename = './icd10-files/icd10cm_tabular_2023.xml'

# parse xml
from bs4 import BeautifulSoup

with open(filename, 'r') as f:
    file = f.read()

soup = BeautifulSoup(file, 'xml')

# get the tags in the existing file
# Be careful, don't get the root tags because it will contain the leave nodes as well as all type of wierd characters, containers, etc
tags = get_tags (filename)
#tags
#don't get the root tags because it will contain the leave nodes as well as all type of wierd characters, containers, etc
tags = ['codeAlso', 'desc','note','name', 'extension', 'heading', 'sectionRef' ,'title','value','visMax', 'visMin' ]
# extract all the child elements corresponding to the given tags
icd10_list_tabular = get_terms(soup, list(tags))

# clean and remove unwanted characters and convert to set, but instead of clean set function use the icd-9 cleaning, because for example
# Kathleem did not remove numbers for icd 9 at this step, etc.
#umls2023 = clean_set(umls_xml_list)

icd10_list_tabular = [str(i).replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','').replace('"','').replace('.','').replace('\n',' ') for i in icd10_list_tabular] #.replace('.','')
icd10_list_tabular = [term.split(" ") for term in icd10_list_tabular]
icd10_list_tabular = [item for sublist in icd10_list_tabular for item in sublist] 
icd10_list_tabular = [i.lower() for i in icd10_list_tabular]
# I added the following part
icd10_list_tabular = [i for i in icd10_list_tabular if len(i) > 1]
len(set(icd10_list_tabular))


all_xml = list(set(icd10_list_drug + icd10_list_eindex + icd10_list_index + icd10_list_neoplasm + icd10_list_tabular))
series = pd.Series(all_xml)
# Remove numbers
series = series.str.replace('\d+', '')
form_list = [term.split(" ") for term in list(series)]
form_list = [item for sublist in form_list for item in sublist] 
all_xml_set = set(form_list)
#len(all_xml_set)


#### 2023 Code Descriptions in Tabular Order - updated 01/11/2023 (ZIP)
import csv
filename = './icd10-files/icd10cm_codes_2023.txt'
icd10cm_codes_2023 = pd.read_csv(filename, sep="\t", error_bad_lines=False, header=None, names = ['col1'])
# Get form column
form_df = icd10cm_codes_2023['col1']
#Remove blanks
form_df = form_df[form_df.notnull()]
# Remove characters
form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
# Makes list 
form_list = list(form_df)
form_list = [i.lower() for i in form_list]
series = pd.Series(form_list)
# Remove numbers
series = series.str.replace('\d+', '')
form_list = [term.split(" ") for term in list(series)]
form_list = [item for sublist in form_list for item in sublist] 
icd10cm_codes_2023_set = set(form_list)

filename = './icd10-files/icd10cm_codes_addenda_2023.txt'
icd10cm_codesa_2023 = pd.read_csv(filename, sep="\t", error_bad_lines=False, header=None, names = ['col1'])
# Get form column
form_df = icd10cm_codesa_2023['col1']
#Remove blanks
form_df = form_df[form_df.notnull()]
# Remove characters
form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
# Makes list 
form_list = list(form_df)
form_list = [i.lower() for i in form_list]
series = pd.Series(form_list)
# Remove numbers
series = series.str.replace('\d+', '')
form_list = [term.split(" ") for term in list(series)]
form_list = [item for sublist in form_list for item in sublist] 
icd10cm_codesa_2023_set = set(form_list)

filename = './icd10-files/icd10cm_order_2023.txt'
icd10cm_order_2023 = pd.read_csv(filename, sep="\t", error_bad_lines=False, header=None, names = ['col1'])
# Get form column
form_df = icd10cm_order_2023['col1']
#Remove blanks
form_df = form_df[form_df.notnull()]
# Remove characters
form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
# Makes list 
form_list = list(form_df)
form_list = [i.lower() for i in form_list]
series = pd.Series(form_list)
# Remove numbers
series = series.str.replace('\d+', '')
form_list = [term.split(" ") for term in list(series)]
form_list = [item for sublist in form_list for item in sublist] 
icd10cm_order_2023_set = set(form_list)
#len(icd10cm_order_2023_set)

filename = './icd10-files/icd10cm_order_addenda_2023.txt'
icd10cm_ordera_2023 = pd.read_csv(filename, sep="\t", error_bad_lines=False, header=None, names = ['col1'])
# Get form column
form_df = icd10cm_ordera_2023['col1']
#Remove blanks
form_df = form_df[form_df.notnull()]
# Remove characters
form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
# Makes list 
form_list = list(form_df)
form_list = [i.lower() for i in form_list]
series = pd.Series(form_list)
# Remove numbers
series = series.str.replace('\d+', '')
form_list = [term.split(" ") for term in list(series)]
form_list = [item for sublist in form_list for item in sublist] 
icd10cm_ordera_2023_set = set(form_list)
len(icd10cm_ordera_2023_set)

all_code_set = set(icd10cm_codes_2023_set | icd10cm_codesa_2023_set | icd10cm_order_2023_set | icd10cm_ordera_2023_set)
# len(all_code_set) 8837

#### 2023 POA Exempt Codes - Updated 03/01/2023 (ZIP)
filename = './icd10-files/POAexemptAddCodesApr23.txt'
POAexemptAddCodesApr23 = pd.read_csv(filename, sep="\t", error_bad_lines=False)
# Get form column
POAexemptAddCodesApr23_set = set()
for column in POAexemptAddCodesApr23.columns.values:
    form_df = POAexemptAddCodesApr23[column]
    form_df = form_df.astype(str)
    #Remove blanks
    form_df = form_df[form_df.notnull()]
    # Remove characters
    form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
    # Makes list 
    form_list = list(form_df)
    form_list = [i.lower() for i in form_list]
    series = pd.Series(form_list)
    # Remove numbers
    series = series.str.replace('\d+', '')
    form_list = [term.split(" ") for term in list(series)]
    form_list = [item for sublist in form_list for item in sublist] 
    POAexemptAddCodesApr23_set = set(form_list) | POAexemptAddCodesApr23_set
    
filename = './icd10-files/POAexemptCodesApr23.txt'
POAexemptCodesApr23 = pd.read_csv(filename, sep="\t", error_bad_lines=False)
# Get form column
POAexemptCodesApr23_set = set()
for column in POAexemptCodesApr23.columns.values:
    form_df = POAexemptCodesApr23[column]
    form_df = form_df.astype(str)
    #Remove blanks
    form_df = form_df[form_df.notnull()]
    # Remove characters
    form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
    # Makes list 
    form_list = list(form_df)
    form_list = [i.lower() for i in form_list]
    series = pd.Series(form_list)
    # Remove numbers
    series = series.str.replace('\d+', '')
    form_list = [term.split(" ") for term in list(series)]
    form_list = [item for sublist in form_list for item in sublist] 
    POAexemptCodesApr23_set = set(form_list) | POAexemptCodesApr23_set
    
filename = './icd10-files/POAexemptDeleteCodesApr23.txt'
POAexemptDeleteCodesApr23 = pd.read_csv(filename, sep="\t", error_bad_lines=False)
# Get form column
POAexemptDeleteCodesApr23_set = set()
for column in POAexemptDeleteCodesApr23.columns.values:
    form_df = POAexemptDeleteCodesApr23[column]
    form_df = form_df.astype(str)
    #Remove blanks
    form_df = form_df[form_df.notnull()]
    # Remove characters
    form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
    # Makes list 
    form_list = list(form_df)
    form_list = [i.lower() for i in form_list]
    series = pd.Series(form_list)
    # Remove numbers
    series = series.str.replace('\d+', '')
    form_list = [term.split(" ") for term in list(series)]
    form_list = [item for sublist in form_list for item in sublist] 
    POAexemptDeleteCodesApr23_set = set(form_list) | POAexemptDeleteCodesApr23_set
    
filename = './icd10-files/POAexemptReviseCodesApr23.txt'
POAexemptReviseCodesApr23 = pd.read_csv(filename, sep="\t", error_bad_lines=False)
# Get form column
POAexemptReviseCodesApr23_set = set()
for column in POAexemptReviseCodesApr23.columns.values:
    form_df = POAexemptReviseCodesApr23[column]
    form_df = form_df.astype(str)
    #Remove blanks
    form_df = form_df[form_df.notnull()]
    # Remove characters
    form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') 
    # Makes list 
    form_list = list(form_df)
    form_list = [i.lower() for i in form_list]
    series = pd.Series(form_list)
    # Remove numbers
    series = series.str.replace('\d+', '')
    form_list = [term.split(" ") for term in list(series)]
    form_list = [item for sublist in form_list for item in sublist] 
    POAexemptReviseCodesApr23_set = set(form_list) | POAexemptReviseCodesApr23_set
    
POAexempt = POAexemptAddCodesApr23_set | POAexemptCodesApr23_set | POAexemptDeleteCodesApr23_set | POAexemptReviseCodesApr23_set
# len(POAexempt) #3561

icd10_set = set(all_xml_set| all_code_set | POAexempt)

# len(icd10_set) #33409
#len(icd9_set - icd10_set ) #4300



# 9 - 20k English words
############ First user input ################
########### My 20k English words ###########
# https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt


#english_words_all = pd.read_csv('20k_english_words.csv',delimiter = ',', encoding="latin-1")
english_words_all = pd.read_csv('20k_english_words.csv',delimiter = ',')

# Get length of word list to add
add_words_length = len(english_words_all)
#add_words_length = int(add_20k_words_amt/100 * len(english_words_all))


# Get word list
english_words = list(english_words_all['word'])
english_words = english_words[:add_words_length]
english_words = [str(i) for i in english_words]
english_20k_set = set([i.lower() for i in english_words])
print("20k words added:",len(english_20k_set))

########################## More common words #####################



# 10 - 1k_verbs
### Verbs
# Go to https://www.worldclasslearning.com/english/five-verb-forms.html
# Copy all contents to csv and name "1k_verbs.csv"

thousand_verbs_df = pd.read_csv('1k_verbs.csv', delimiter = ',', encoding="latin-1")
thousand_verbs = list(thousand_verbs_df['base']) + list(thousand_verbs_df['past']) + list(thousand_verbs_df['past_participle']) + list(thousand_verbs_df['present']) + list(thousand_verbs_df['present_participle'])

# Get length of word list to add
add_verbs_length = int(len(thousand_verbs))

verbs_set = thousand_verbs[:add_verbs_length]
verbs_set = set([i.lower() for i in verbs_set])
print("1k verbs added:",len(verbs_set))



# 11- Adding SNODENT
# https://terminology.hl7.org/downloads.html
#V3 Source Files
#The HL7 Version 3 coremif file for this release
# HL7 V3 MIF --> DEFN=UV=VO=5.3.0.coremif

# filename = './SNODENT/DEFN=UV=VO=5.3.0.coremif'
# # parse xml
# from bs4 import BeautifulSoup

# with open(filename, 'r') as f:
#     file = f.read()

# soup = BeautifulSoup(file, 'xml')

# tags = ['concept']
# # extract all the child elements corresponding to the given tags
# coremif_parse = soup.find_all(list(tags))

#Found a pdf file that is 2018 but has a more complete list of the SNODENT terminologies, opened the pdf with word and copied the
#files to a txt file 

filename = './SNODENT/snodent_from_pdf_2018-modified.txt'
Snodent_codes_2018 = pd.read_csv(filename, sep="\t", error_bad_lines=False)
# Get form column
snodent_ls = list(Snodent_codes_2018['SNODENT TERM'])
snodent_set = clean_set(snodent_ls)
# len(snodent_set) # 4016
# len(snodent_set - whitelist_new = 15)



# 12- ICD-O
#https://www.naaccr.org/icdo3/
filename = './ICD_O/Copy-of-ICD-O-3.2_MFin_17042019_web.csv'
ICD_O_codes = pd.read_csv(filename, sep=",", error_bad_lines=False)
ICD_O_codes = ICD_O_codes.rename(columns=ICD_O_codes.iloc[0])
ICD_O_ls = list(ICD_O_codes['Term'])
ICD_O_set = clean_set(ICD_O_ls)
# len(ICD_O_set - whitelist_new) #22


# Generate whitelist
whitelist_new = umls2023 | mesh2023 | abbrevs_and_definitions_set | mp_set_normalized | snomed2023_set | drug_set2023 | icd9_set | icd10_set | english_20k_set | verbs_set
#len(whitelist_medical_terms): 233528
len(whitelist_new)

# Remove numbers
series = pd.Series(list(whitelist_new))
series = series.str.replace('\d+', '')
form_list = [term.split(" ") for term in list(series)]
form_list = [item for sublist in form_list for item in sublist] 
whitelist_new = set(form_list)

#Remove punct
whitelist_new = [re.split("\s",re.sub(r"[^a-z]", " ", item)) for item in whitelist_new]
whitelist_new = set([item for sublist in whitelist_new for item in sublist])

whitelist_new_dict = {}
for k in whitelist_new:
    whitelist_new_dict[k] = 1
    
with open("whitelist_101923.json",'w') as outfile:
    json.dump(whitelist_new_dict, outfile)
    
# # new whitelist
# whitelist_new = json.loads(open("whitelist_new_Habibeh.json").read())
# # Get keys
# whitelist_new = set(whitelist_new.keys())
#len(whitelist_new) -> 472325
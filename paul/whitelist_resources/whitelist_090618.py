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

# Get inputs for whitelist subsets
add_20k_words_amt = int(sys.argv***REMOVED***1***REMOVED***)
print("20k words %: ", add_20k_words_amt)

# subtract_streets_amt = int(sys.argv***REMOVED***4***REMOVED***)
# print("Street names %: ", subtract_streets_amt)
# subtract_cities_amt = int(sys.argv***REMOVED***5***REMOVED***)
# print("Cities and counties %: ", subtract_cities_amt)

# Get output filename, based on input values
outfile_name = "../whitelist_addback_100_unigram_ucsf2.json" + str(add_20k_words_amt) + ".json" # + "_S" + str(subtract_streets_amt) + "_C" + str(subtract_cities_amt) + ".json"

# Read in updated blacklist
# names_blacklist = json.loads(open('../names_blacklist_batch102_110_unigram2.json').read(), encoding="latin-1")
# names_blacklist_set = set(list(names_blacklist.keys()))

"""
Helper function is_unicode determines whether a string is unicode or not. Outputs
a boolean
"""
def is_unicode(s):
    if isinstance(s, str):
        return False
    elif isinstance(s, unicode):
        return True
    else:
        print("not a string")

############################### umls_LEXICON.csv ###############################
# Read in the NLM Lexicon containing common English words and medical terms
umls_df = pd.read_csv('umls_LEXICON.csv', delimiter = ',', encoding="latin-1") # Edit 1/22/18
#print("umls_LEXICON.csv loaded")
# Get column of df that contains "base" and "entry" specifications
umls_df_crap = umls_df***REMOVED***'crap'***REMOVED***
# Remove blanks
umls_df_crap = umls_df_crap***REMOVED***umls_df_crap.notnull()***REMOVED***
# Remove numbers
umls_df_crap = umls_df_crap.str.replace('\d+', '')
# Remove apostrophes, underscores, backslashes
umls_df_crap = umls_df_crap.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('***REMOVED***','').str.replace('***REMOVED***','').str.replace('?','') # Edit 1/22/18
# Remove single character words
umls_df_crap = umls_df_crap.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ')
# The pattern \b\w\b will replace any single word character with a word boundary
umls_df_crap = umls_df_crap.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# Remove rows where length of descriptor is less than 3
umls_df_crap = list(umls_df_crap***REMOVED***umls_df_crap.str.len() > 2***REMOVED***)


# Get column of df that contains term stem and other crap
umls_df_label = umls_df***REMOVED***'label'***REMOVED***
# Remove blanks
umls_df_label = umls_df_label***REMOVED***umls_df_label.notnull()***REMOVED***
# Remove numbers
umls_df_label = umls_df_label.str.replace('\d+', '')
# Remove apostrophes, underscores, commas, colons, semicolons, backslashes
umls_df_label = umls_df_label.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('***REMOVED***','').str.replace('***REMOVED***','').str.replace('?','') # Edit 1/22/18
# Remove single character words
umls_df_label = umls_df_label.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ')
# The pattern \b\w\b will replace any single word character with a word boundary
umls_df_label = umls_df_label.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# Remove rows where length of descriptor is less than 3
umls_df_label = list(umls_df_label***REMOVED***umls_df_label.str.len() > 2***REMOVED***)


# Order Edit 1/18/17
# Get column of df that contains variations on the stem
umls_df_useful = umls_df***REMOVED***'useful'***REMOVED***
# Remove blanks
umls_df_useful = umls_df_useful***REMOVED***umls_df_useful.notnull()***REMOVED***
# Remove numbers
umls_df_useful = umls_df_useful.str.replace('\d+', '')
# Remove apostrophes, underscores, commas, colons, semicolons, backslashes
umls_df_useful = umls_df_useful.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('***REMOVED***','').str.replace('***REMOVED***','').str.replace('?','') # Edit 1/22/18
# Remove single character words
#umls_df_useful = umls_df_useful.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ').str.replace('|',' ')
# The pattern \b\w\b will replace any single word character with a word boundary
#umls_df_useful = umls_df_useful.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# Remove rows where length of descriptor is less than 3
umls_df_useful = list(umls_df_useful***REMOVED***umls_df_useful.str.len() > 2***REMOVED***)


# Get the first term in useful column
umls_df***REMOVED***'happy'***REMOVED*** = umls_df***REMOVED***'useful'***REMOVED***.str.extract('(.*?)\|', expand = True)
umls_df_happy = umls_df***REMOVED***'happy'***REMOVED***
# Remove blanks
umls_df_happy = umls_df_happy***REMOVED***umls_df_happy.notnull()***REMOVED***
# Remove numbers
umls_df_happy = umls_df_happy.str.replace('\d+', '')
# Remove apostrophes, underscores, commas, colons, semicolons, backslashes
umls_df_happy = umls_df_happy.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|','').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('***REMOVED***','').str.replace('***REMOVED***','').str.replace('?','') # Edit 1/22/18
# Remove single character words
umls_df_happy = umls_df_happy.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ').str.replace('|',' ')
# The pattern \b\w\b will replace any single word character with a word boundary
umls_df_happy = umls_df_happy.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# Remove rows where length of descriptor is less than 3
umls_df_happy = list(umls_df_happy***REMOVED***umls_df_happy.str.len() > 2***REMOVED***)


# Create list from crap df
umls_crap_list = list(umls_df_crap)
umls_crap_list = ***REMOVED***term.split() for term in umls_crap_list***REMOVED*** # convert each string into a list of the words in the string
umls_crap_list = ***REMOVED***item for sublist in umls_crap_list for item in sublist***REMOVED*** # flatten the list of lists into a single list
umls_crap_list = ***REMOVED***i.lower() for i in umls_crap_list***REMOVED*** # make all lower case
umls_crap_list = ***REMOVED***i.replace(' ','') for i in umls_crap_list***REMOVED*** # last check for spaces
#print(len(set(umls_crap_list)))

# Create list from label df
umls_label_list = list(umls_df_label)
umls_label_list = ***REMOVED***term.split() for term in umls_label_list***REMOVED*** # convert each string into a list of the words in the string
umls_label_list = ***REMOVED***item for sublist in umls_label_list for item in sublist***REMOVED*** # flatten the list of lists into a single list
umls_label_list = ***REMOVED***term.split() for term in umls_label_list***REMOVED*** # convert each string into a list of the words in the string
umls_label_list = ***REMOVED***item for sublist in umls_label_list for item in sublist***REMOVED*** # flatten the list of lists into a single list
umls_label_list = ***REMOVED***i.lower() for i in umls_label_list***REMOVED***
umls_label_list = ***REMOVED***i.replace(' ','') for i in umls_label_list***REMOVED*** # last check for spaces
#print(len(set(umls_label_list)))

# Create list from useful df
umls_useful_list = list(umls_df_useful)
umls_useful_list = ***REMOVED***term.split() for term in umls_useful_list***REMOVED*** # convert each string into a list of the words in the string
umls_useful_list = ***REMOVED***item for sublist in umls_useful_list for item in sublist***REMOVED*** # flatten the list of lists into a single list
umls_useful_list = ***REMOVED***i.lower() for i in umls_useful_list***REMOVED***
umls_useful_list = ***REMOVED***i.replace(' ','') for i in umls_useful_list***REMOVED*** # last check for spaces
#print ***REMOVED***s for s in umls_useful_list if "\\" in s***REMOVED***
#print(len(set(umls_useful_list)))

# Create list from happy df
umls_happy_list = list(umls_df_happy)
umls_happy_list = ***REMOVED***term.split() for term in umls_happy_list***REMOVED*** # convert each string into a list of the words in the string
umls_happy_list = ***REMOVED***item for sublist in umls_happy_list for item in sublist***REMOVED*** # flatten the list of lists into a single list
umls_happy_list = ***REMOVED***i.lower() for i in umls_happy_list***REMOVED***
umls_happy_list = ***REMOVED***i.replace(' ','') for i in umls_happy_list***REMOVED***
#print(len(set(umls_happy_list)))

#  Cancatenate all 4 lists
umls_list = list(set(umls_crap_list + umls_useful_list + umls_happy_list + umls_label_list))
umls_set = set(umls_list)


################################ descriptor_mesh.csv ###############################
# Read in the MeSH set of hierarchically-organized medical terms
des_mesh_df = pd.read_csv('descriptor_mesh.csv', delimiter = ',', usecols=***REMOVED***'type','value'***REMOVED***)
#print("descriptor_mesh.csv loaded")

# Only take the types of data we're potentially interested in:
# ENTRY = entry term
# MH = mesh heading
# PA = pharmacological action
# MS = mesh scope note
values = ***REMOVED***'ENTRY','MH','PA','MS'***REMOVED***
des_mesh_df = des_mesh_df.loc***REMOVED***des_mesh_df***REMOVED***'type'***REMOVED***.isin(values)***REMOVED***

# From the data types that we want, extract the only the initial value of interest
des_mesh_df***REMOVED***'descriptor'***REMOVED*** = des_mesh_df***REMOVED***'value'***REMOVED***.str.extract('(.*?)\|', expand = True)
# Drop the old 'value' column
des_mesh_df = des_mesh_df.drop('value', 1)
# Drop blanks
des_mesh_df = des_mesh_df***REMOVED***des_mesh_df.descriptor.notnull()***REMOVED***
# Remove numbers
des_mesh_df***REMOVED***'descriptor'***REMOVED*** = des_mesh_df***REMOVED***'descriptor'***REMOVED***.str.replace('\d+', '')
# Remove apostrophes
des_mesh_df***REMOVED***'descriptor'***REMOVED*** = des_mesh_df***REMOVED***'descriptor'***REMOVED***.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('***REMOVED***','').str.replace('***REMOVED***','').str.replace('?','')  # Edit 1/22/18
# Remove single character words
des_mesh_df***REMOVED***'descriptor'***REMOVED*** = des_mesh_df***REMOVED***'descriptor'***REMOVED***.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ')
# The pattern \b\w\b will replace any single word character with a word boundary
des_mesh_df***REMOVED***'descriptor'***REMOVED*** = des_mesh_df***REMOVED***'descriptor'***REMOVED***.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# Remove rows where length of descriptor is less than 3
des_mesh_df= des_mesh_df***REMOVED***des_mesh_df***REMOVED***'descriptor'***REMOVED***.str.len() > 2***REMOVED***


# Create list from mesh df
descriptor_mesh_list = list(des_mesh_df***REMOVED***'descriptor'***REMOVED***)
descriptor_mesh_list = ***REMOVED***term.split() for term in descriptor_mesh_list***REMOVED*** # convert each string into a list of the words in the string
descriptor_mesh_list = ***REMOVED***item for sublist in descriptor_mesh_list for item in sublist***REMOVED*** # flatten the list of lists into a single list
descriptor_mesh_list = ***REMOVED***i.lower() for i in descriptor_mesh_list***REMOVED*** #make lowercase
descriptor_mesh_list = ***REMOVED***i.replace(' ','') for i in descriptor_mesh_list***REMOVED*** # last check for spaces
des_mesh_set = set(descriptor_mesh_list)


################################ MeshTreeHierarchyWithScopeNotes.csv ###############################
### *** might not actually need this ***
# Read in the mesh terms and their associated scope notes
mesh_heir = pd.read_csv('MeshTreeHierarchyWithScopeNotes.csv',delimiter = ',', usecols=***REMOVED***'Term','Ms'***REMOVED***) # Term is the branches
#print("MeshTreeHierarchyWithScopeNotes.csv loaded")

# Create term list from mesh term df
mesh_heir_term_list = list(mesh_heir***REMOVED***'Term'***REMOVED***)
mesh_heir_term_list = ***REMOVED***term.split() for term in mesh_heir_term_list***REMOVED*** # convert each string into a list of the words in the string
mesh_heir_term_list = ***REMOVED***item for sublist in mesh_heir_term_list for item in sublist***REMOVED*** # flatten the list of lists into a single list
mesh_heir_term_list = ***REMOVED***i.lower() for i in mesh_heir_term_list***REMOVED***

# Get rid of parentheses, braces, pipes and apastrophes
mesh_heir_term_list = ***REMOVED***i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('***REMOVED***','').replace('***REMOVED***','').replace('?','') for i in mesh_heir_term_list***REMOVED***  # Edit 1/22/18
mesh_heir_term_list = ***REMOVED***i.replace(' ','') for i in mesh_heir_term_list***REMOVED*** # last check for spaces
mesh_heir_term_set = set(mesh_heir_term_list)

################################## mtrees2017.txt ###############################
# Read in a more full version of the descriptor mesh list
mesh = pd.read_csv('mtrees2017.txt',delimiter = ';') #high level headings
#print("mtrees2017.txt loaded")

# Create list from df
mesh_list = list(mesh***REMOVED***'Body Regions'***REMOVED***)
mesh_list = ***REMOVED***term.split() for term in mesh_list***REMOVED*** # convert each string into a list of the words in the string
mesh_list = ***REMOVED***item for sublist in mesh_list for item in sublist***REMOVED*** # flatten the list of lists into a single list
mesh_list = ***REMOVED***i.lower() for i in mesh_list***REMOVED***
# Get rid of parentheses, braces, pipes and apastrophes
mesh_list = ***REMOVED***i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('***REMOVED***','').replace('***REMOVED***','').replace('?','') for i in mesh_list***REMOVED***  # Edit 1/22/18
mesh_list = ***REMOVED***term.split() for term in mesh_list if type(term) is str***REMOVED***
mesh_list = ***REMOVED***item for sublist in mesh_list for item in sublist***REMOVED*** # flatten
mesh_set = set(mesh_list)


################################## list_of_med_abbreviations.csv ###############################
# Read in list of common medical abbreviations
abbreviations = pd.read_csv('list_of_med_abbreviations.csv', delimiter = ',')
#print("list_of_med_abbreviations.csv loaded")

# Create list from df
abbrev_list = list(abbreviations.abbreviation)
abbrev_list = ***REMOVED***i for i in abbrev_list if type(i) is str***REMOVED***
abbrev_list = ***REMOVED***i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|','').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('***REMOVED***','').replace('***REMOVED***','').replace('?','') for i in abbrev_list***REMOVED***
abbrev_list = ***REMOVED***i.lower() for i in abbrev_list***REMOVED***
abbrev_list = ***REMOVED***term.split() for term in abbrev_list if type(term) is str***REMOVED***
abbrev_list = ***REMOVED***item for sublist in abbrev_list for item in sublist***REMOVED*** # flatten
abbrev_set = set(abbrev_list)

### Medical abbreviations
more_abbreviations = pd.read_csv('medical_abbreviations.csv', delimiter = ',',encoding="latin-1")


abbreviations_list = list(more_abbreviations***REMOVED***'abbreviation'***REMOVED***)
abbreviations_list = ***REMOVED***str(i) for i in abbreviations_list***REMOVED***
abbreviations_list = ***REMOVED***i.lower() for i in abbreviations_list***REMOVED***

definitions_list = list(more_abbreviations***REMOVED***'definition'***REMOVED***)
definitions_list = ***REMOVED***term.split(" ") for term in definitions_list***REMOVED***
definitions_list = ***REMOVED***item for sublist in definitions_list for item in sublist***REMOVED***
definitions_list = ***REMOVED***i.replace("(",'').replace(")",'').replace(" ",'').replace("/",'')  for i in definitions_list***REMOVED***
definitions_list = ***REMOVED***i.lower() for i in definitions_list***REMOVED***

abbrevs_and_definitions_set = set(abbreviations_list + definitions_list) | abbrev_set


mp_set = set()
tree = ET.ElementTree(file='mplus.xml')
#print("mplus.xml loaded")

# also-called
for elem in tree.iter(tag='also-called'):
    mp_set = mp_set | set(elem.text.lower().split(' '))

# health-topic
for elem in tree.iterfind('health-topic'):
    mp_set = mp_set | set(elem.attrib***REMOVED***'title'***REMOVED***.lower().split(' '))


# Create a new set for mp that contains ascii characters only
# Edit 1/22/18:
mp_set_normalized = set()
for item in mp_set:
    if is_unicode(item):
        new_item = unicodedata.normalize('NFD', item).encode('ascii', 'ignore')
        mp_set_normalized.add(new_item)
    else:
        mp_set_normalized.add(item)


mp_set_normalized = set(***REMOVED***i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('***REMOVED***','').replace('***REMOVED***','').replace('?','') for i in mp_set_normalized***REMOVED***)  # Edit 1/22/18
mp_set_normalized = ***REMOVED***term.split() for term in mp_set_normalized if type(term) is str***REMOVED***
mp_set_normalized = set(***REMOVED***item for sublist in mp_set_normalized for item in sublist***REMOVED***) # flatten


################################## SNOMED CT ################################
# SNOMED is a huge database of medical terminology
# download the zip file https://www.nlm.nih.gov/healthit/snomedct/us_edition.html
# unzip the files and combine two files:
# Full/Terminology/sct2_TextDefinition_Full-en_US1000124_20170301.txt (need the term column)
# Full/Terminology/sct2_Description_Full-en_US1000124_20170301.txt (need the term column)
# transfer the combined files to csv file and change the name to "sno.csv"
# change Documentation/tls_Icd10cmHumanReadableMap_US1000124_20170301.tsv (2 columns: sctName, and icdName)
# to tls.csv.
# To cut: cut -d$'\t' -f8 sct2_TextDefinition_Full-en_US1000124_20170901.txt > textdef_terms.txt
#         cut -d$'\t' -f8 sct2_Description_Full-en_US1000124_20170901.txt > description_terms.txt
# tr "\\t" "," < sno_full.txt > sno_full.csv
# tr "\\t" "," < tls_full.tsv > tls_full.csv

snomed_set = set()

# Definitions of common medical terms
with open('sno_full.csv', 'r') as csvfile: # Edit 1/18/17
    sno = csv.reader(csvfile, delimiter=',', quotechar=' ')
    for row in sno:
        #print(row***REMOVED***7***REMOVED***)
        try:
            for i in row***REMOVED***7***REMOVED***.split(','):
                for j in i.lower().split(' '):
                    snomed_set.add(str(re.sub(r'\.','', j)))
        #firstname_set.add(row***REMOVED***3***REMOVED***.lower())
        except:
            print(row)

#print("sno_full.csv loaded")

# Definitions of various disorders and their classifications
with open('tls_full.csv', 'r') as csvfile: # Edit 1/18/17
    tls = csv.reader(csvfile, delimiter=',', quotechar=' ')
    for row in tls:
        #print(row***REMOVED***7***REMOVED***)
        try:
            # sctName
            for i in row***REMOVED***6***REMOVED***.split(','):
                for j in i.lower().split(' '):
                    snomed_set.add(str(re.sub(r'\.','', j)))
            # icdName
            for i in row***REMOVED***12***REMOVED***.split(','):
                for j in i.lower().split(' '):
                    snomed_set.add(str(re.sub(r'\.','', j)))
        #firstname_set.add(row***REMOVED***3***REMOVED***.lower())
        except:
            print(row)

#print("tls_full.csv loaded")
# Replace weird characters
snomed_set = set(***REMOVED***i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('***REMOVED***','').replace('***REMOVED***','').replace('?','') for i in snomed_set***REMOVED***) # Edit 1/22/18
snomed_set = ***REMOVED***term.split() for term in snomed_set if type(term) is str***REMOVED***
snomed_set = set(***REMOVED***item for sublist in snomed_set for item in sublist***REMOVED***) # flatten



################################# FDA: list of approved drugs, active ingredients, strengths, form ##################
# go to https://www.fda.gov/Drugs/InformationOnDrugs/ucm079750.htm and download the zip file
# copy "Products.txt" to csv and name "fda_drugs.csv"


fda_drugs_df = pd.read_csv('fda_drugs.csv', delimiter = ',') # Edit 1/22/18
#print("fda_drugs.csv loaded")

####### Form
# Get form column
form_df = fda_drugs_df***REMOVED***'Form'***REMOVED***
# Remove blanks
form_df = form_df***REMOVED***form_df.notnull()***REMOVED***
# Remove characters
form_df = form_df.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('***REMOVED***','').str.replace('***REMOVED***','').str.replace('?','') 
# Makes list 
form_list = list(form_df)
form_list = ***REMOVED***term.split(" ") for term in form_list***REMOVED***
form_list = ***REMOVED***item for sublist in form_list for item in sublist***REMOVED*** 
form_list = ***REMOVED***i.lower() for i in form_list***REMOVED***


######## Strengths
# Get strength column
strength_df = fda_drugs_df***REMOVED***'Strength'***REMOVED***
# Remove blanks
strength_df = strength_df***REMOVED***strength_df.notnull()***REMOVED***
# Remove characters
strength_df = strength_df.str.replace("*",'').str.replace(';',' ').str.replace('(','').str.replace(')','')
# Makes list 
strength_list = list(strength_df)
strength_list = ***REMOVED***term.split(" ") for term in strength_list***REMOVED***
strength_list = ***REMOVED***item for sublist in strength_list for item in sublist***REMOVED*** 
strength_list = ***REMOVED***i.lower() for i in strength_list***REMOVED***


###### Drug names
# Get drug names column 
drug_df = fda_drugs_df***REMOVED***'DrugName'***REMOVED***
# Remove blanks
drug_df = drug_df***REMOVED***drug_df.notnull()***REMOVED***
# Remove characters
drug_df = drug_df.str.replace("*",'').str.replace(';',' ').str.replace('(','').str.replace(')','')
# Makes list 
drug_list = list(drug_df)
drug_list = ***REMOVED***term.split(" ") for term in drug_list***REMOVED***
drug_list = ***REMOVED***item for sublist in drug_list for item in sublist***REMOVED*** 
drug_list = ***REMOVED***i.lower() for i in drug_list***REMOVED***


######## Actice ingredients
# Get drug names column 
ingredient_df = fda_drugs_df***REMOVED***'ActiveIngredient'***REMOVED***
# Remove blanks
ingredient_df = ingredient_df***REMOVED***ingredient_df.notnull()***REMOVED***
# Remove characters
ingredient_df = ingredient_df.str.replace("*",'').str.replace(';',' ').str.replace('(','').str.replace(')','')
# Makes list 
ingredient_list = list(ingredient_df)
ingredient_list = ***REMOVED***term.split(" ") for term in ingredient_list***REMOVED***
ingredient_list = ***REMOVED***item for sublist in ingredient_list for item in sublist***REMOVED*** 
ingredient_list = ***REMOVED***i.lower() for i in ingredient_list***REMOVED***


# Combine lists into set
drug_set = set(form_list + strength_list + ingredient_list)


############################### ICD9 diagnoses ###############################
# List of icd9 diagnoses, already separated by word
# Go to https://www.cms.gov/Medicare/Coding/ICD9ProviderDiagnosticCodes/codes.html and download the Version 32 Full and Abbreviated Code Titles Effective October 1, 2014 ***REMOVED***ZIP, 1MB***REMOVED***
# Combine all .txt files and copy to csv, name icd9_diagnoses.csv

# Import dataset
icd9_diagnoses = ***REMOVED******REMOVED***

with open('icd9_diagnoses.csv', encoding="latin-1") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        icd9_diagnoses.append(row)

# Get rid of blanks
for i in range(len(icd9_diagnoses)):
    current_sublist = icd9_diagnoses***REMOVED***i***REMOVED***
    new_sublist = ***REMOVED***item for item in current_sublist if not item == ''***REMOVED***
    icd9_diagnoses***REMOVED***i***REMOVED*** = new_sublist

# Flatten and take away characters
icd9_diagnoses = ***REMOVED***item for sublist in icd9_diagnoses for item in sublist***REMOVED***
icd9_diagnoses = ***REMOVED***i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('***REMOVED***','').replace('***REMOVED***','').replace('?','') for i in icd9_diagnoses***REMOVED***
icd9_diagnoses = ***REMOVED***term.split(" ") for term in icd9_diagnoses***REMOVED***
icd9_diagnoses = ***REMOVED***item for sublist in icd9_diagnoses for item in sublist***REMOVED*** 
icd9_diagnoses = ***REMOVED***i.lower() for i in icd9_diagnoses***REMOVED***

icd9_diagnoses_set = set(icd9_diagnoses)






############ First user input ################
########### My 20k English words ###########


english_words_all = pd.read_csv('20k_english_words.csv',delimiter = ',', encoding="latin-1")

# Get length of word list to add
add_words_length = len(english_words_all)
#add_words_length = int(add_20k_words_amt/100 * len(english_words_all))


# Get word list
english_words = list(english_words_all***REMOVED***'word'***REMOVED***)
english_words = english_words***REMOVED***:add_words_length***REMOVED***
english_words = ***REMOVED***str(i) for i in english_words***REMOVED***
english_20k_set = set(***REMOVED***i.lower() for i in english_words***REMOVED***)
print("20k words added:",len(english_20k_set))

########################## More common words #####################

### Verbs
# Go to https://www.worldclasslearning.com/english/five-verb-forms.html
# Copy all contents to csv and name "1k_verbs.csv"

thousand_verbs_df = pd.read_csv('1k_verbs.csv', delimiter = ',', encoding="latin-1")
thousand_verbs = list(thousand_verbs_df***REMOVED***'base'***REMOVED***) + list(thousand_verbs_df***REMOVED***'past'***REMOVED***) + list(thousand_verbs_df***REMOVED***'past_participle'***REMOVED***) + list(thousand_verbs_df***REMOVED***'present'***REMOVED***) + list(thousand_verbs_df***REMOVED***'present_participle'***REMOVED***)

# Get length of word list to add
add_verbs_length = int(len(thousand_verbs))

verbs_set = thousand_verbs***REMOVED***:add_verbs_length***REMOVED***
verbs_set = set(***REMOVED***i.lower() for i in verbs_set***REMOVED***)
print("1k verbs added:",len(verbs_set))






# import i2b2 frwquency table data
# unigram_freq_df1 = pd.read_csv('../ucsf_batch102_110_unigram_freq_table.csv', delimiter = ',', encoding="latin-1")

# safe_words1 = ***REMOVED******REMOVED***

# for index, row in unigram_freq_df1.iterrows():
#     word = row***REMOVED***'unigram'***REMOVED***
#     phi_count = row***REMOVED***'phi_count'***REMOVED***
#     safe_count = row***REMOVED***'non-phi_count'***REMOVED***
#     if type(word) == str:
#         split_word = ***REMOVED***term for term in word.split('.') if term != ''***REMOVED***
#         # don't want to keep any numbers
#         if not any(c.isdigit() for c in word):       
#             # we want to keep words that: a) have a PHI count of 0
#             if phi_count == 0:
#                 safe_words1 = safe_words1 + split_word
#             #1-3, or are special words (and, of)
#             elif phi_count == 1 or (word in ***REMOVED***'and','of','the','in'***REMOVED***):
#                 # have a non-phi count of >1000
#                 if safe_count > 1000:
#                     safe_words1 = safe_words1 + split_word

# import ucsf frwquency table data
# unigram_freq_df2 = pd.read_csv('../ucsf_batch102_110_unigram_freq_table.csv', delimiter = ',', encoding="latin-1")

# safe_words2 = ***REMOVED******REMOVED***

# for index, row in unigram_freq_df2.iterrows():
#     word = row***REMOVED***'unigram'***REMOVED***
#     phi_count = row***REMOVED***'phi_count'***REMOVED***
#     safe_count = row***REMOVED***'non-phi_count'***REMOVED***
#     split_word = ***REMOVED***term for term in str(word).split('.') if term != ''***REMOVED***
#     # don't want to keep any numbers
#     if not any(c.isdigit() for c in str(word)):       
#         # we want to keep words that: a) have a PHI count of 0
#         if phi_count == 0:
#             safe_words2 = safe_words2 + split_word
#         #1-3, or are special words (and, of)
#         elif phi_count == 1 or (word in ***REMOVED***'and','of','the','in'***REMOVED***):
#             # have a non-phi count of >1000
#             if safe_count > 1000:
#                 safe_words2 = safe_words2 + split_word

# safe_words_set = set(safe_words2)
# unsafe_words_set = set(***REMOVED***'acropolis','promptcare','montreal','kekela','christus','alaska','delnor','montefiore','manamana','kekela','cod'***REMOVED***)

single_letters = set(***REMOVED***'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'***REMOVED***)

################## Names analysis ######################
# Load firstnames and lastnames blacklists
######## Social Security Firstnames #######
# Go to https://www.ssa.gov/oact/babynames/limits.html and download the National data file
# Concatenate all text files (names from 1880 - 2017) into a mast file called ss_firstnames.txt
# Add the line "name,gender,count" to the top of the file
ss_firstnames_df = pd.read_csv('/Users/kathleenmuenzen/Desktop/whitelists_and_blacklists/white_black_optimization/whitelist_blacklist_files/ss_firstnames.txt', delimiter = ',', encoding="latin-1")
# Sort by occurrences
ss_firstnames_df = ss_firstnames_df.sort_values('count',ascending=False)
# Get names list
ss_firstnames = ss_firstnames_df***REMOVED***'name'***REMOVED***
list_100_first = list(ss_firstnames)
set_100_first = set(***REMOVED***str(i).lower() for i in list_100_first***REMOVED***)



######### Census Lastnames #######
# Go to https://www.census.gov/topics/population/genealogy/data/2010_surnames.html
# Download File B: Surnames Occurrign 100 or More Times, name "census_last_names.txt"
census_lastnames_df = pd.read_csv('/Users/kathleenmuenzen/Desktop/whitelists_and_blacklists/white_black_optimization/whitelist_blacklist_files/census_lastnames.csv', delimiter = ',', encoding="latin-1")
census_lastnames = census_lastnames_df***REMOVED***'name'***REMOVED***
list_100_last = list(census_lastnames)
set_100_last = set(***REMOVED***str(i).lower() for i in list_100_last***REMOVED***)

all_names_set = set_100_first | set_100_last

whitelist_medical_terms = umls_set | des_mesh_set | mesh_heir_term_set | mesh_set | abbrevs_and_definitions_set | mp_set_normalized | snomed_set | drug_set | icd9_diagnoses_set
#len(whitelist_medical_terms): 233528


intersection_firstnames = set(***REMOVED***x for x in set_100_first if x in whitelist_medical_terms***REMOVED***) #len 6220
intersection_lastnames = set(***REMOVED***x for x in set_100_last if x in whitelist_medical_terms***REMOVED***) #len 13142
intersection_allnames = set(***REMOVED***x for x in all_names_set if x in whitelist_medical_terms***REMOVED***) #len 14882



whitelist_medical_terms_no_names = whitelist_medical_terms - (whitelist_medical_terms&intersection_allnames)
#len(whitelist_medical_terms_no_names): 218646



# How many names are in the common words/verb set?
all_common_words = english_20k_set | verbs_set
intersection_firstnames_common_words = set(***REMOVED***x for x in set_100_first if x in all_common_words***REMOVED***)
intersection_lastnames_common_words = set(***REMOVED***x for x in set_100_last if x in all_common_words***REMOVED***)
intersection_allnames_common_words = set(***REMOVED***x for x in all_names_set if x in all_common_words***REMOVED***)


#######################################################

# Generate whitelist
#whitelist = umls_set | des_mesh_set | mesh_heir_term_set | mesh_set | abbrevs_and_definitions_set | mp_set_normalized | snomed_set | drug_set | icd9_diagnoses_set  
whitelist_add_sub = whitelist_medical_terms_no_names | english_20k_set | verbs_set
# Subtract updated names blacklist from whitelist
#whitelist_add_sub = whitelist_add - (whitelist_add&names_blacklist_set)
# whitelist_add_sub = set(***REMOVED***item for item in whitelist_add_sub if not any(c.isdigit() for c in item)***REMOVED***) # get rid of any and all words with digits in the whitelist
#whitelist_add_sub = set(***REMOVED***item for item in whitelist_add_sub if not isinstance(item,int)***REMOVED***)
whitelist_add_sub = whitelist_add_sub | single_letters

# Make sure there are no numbers in whitelist
whitelist_nodigits = ***REMOVED***item for item in whitelist_add_sub if not any(c.isdigit() for c in item)***REMOVED***
# This reduced the length of the whitelist from 236585 to 206666

# Make sure there is no punctuation in whitelist
whitelist_nopunct = ***REMOVED***re.split("\s",re.sub(r"***REMOVED***^a-z***REMOVED***", " ", item)) for item in whitelist_nodigits***REMOVED***
whitelist_nopunct_flattened = set(***REMOVED***item for sublist in whitelist_nopunct for item in sublist***REMOVED***) 



# original len(whitelist_nopunct_flattened): 196710


whitelist_nonames = whitelist_nopunct_flattened - (whitelist_nopunct_flattened&all_names_set)
# len(whitelist_nonames)
#whitelist_add_sub = whitelist_add_sub | safe_words_set
#whitelist_add_sub = whitelist_add_sub - (whitelist_add_sub&unsafe_words_set)

#print("Final whitelist length:", len(whitelist_add_sub))


# Whitelist with names
whitelist_dictionary = {}
for k in whitelist_nopunct_flattened:
    whitelist_dictionary***REMOVED***k***REMOVED*** = 1

with open("whitelist_061418_uncleaned.json",'w') as outfile:
    json.dump(whitelist_dictionary, outfile)


# Whitelist without names
whitelist_dictionary_nonames = {}
for k in whitelist_nonames:
    whitelist_dictionary_nonames***REMOVED***k***REMOVED*** = 1

with open("whitelist_090618_nonames_unlceaned.json",'w') as outfile:
    json.dump(whitelist_dictionary_nonames, outfile)






################## Using whitelist_plus_fps-3_cleaned.json ##########
whitelist_fps3 = json.loads(open("~/Desktop/de-id_stable1/filters/whitelists/whitelist_plus_fps-3_cleaned.json").read())
# >>> len(whitelist_fps3)
# 204568
# Get keys
whitelist_keys = set(whitelist_fps3.keys())
# len 204568

# Remove all names
whitelist_nonames = whitelist_keys - (whitelist_keys&all_names_set)
# >>> len(whitelist_nonames)
# 188473



# Whitelist without names
whitelist_dictionary_nonames = {}
for k in whitelist_nonames:
    whitelist_dictionary_nonames***REMOVED***k***REMOVED*** = 1

with open("whitelist_090618_nonames.json",'w') as outfile:
    json.dump(whitelist_dictionary_nonames, outfile)

len(whitelist_nonames)
# 188473


################### Add FPs back to whitelist ###############
# punctuation_matcher = re.compile(r"***REMOVED***^a-zA-Z0-9****REMOVED***")

# i2b2_whitelist_noname_fps = pd.read_csv('../../names_removal/i2b2_noname_whitelist_fps.csv')


# # # Edit data frame directly, to retain FP count information
# # for index, row in i2b2_whitelist_noname_fps.iterrows():
# #     current_word = str(row***REMOVED***'note_word'***REMOVED***)
# #     if any(punctuation_matcher.match(c) for c in current_word***REMOVED***1:-1***REMOVED***) or any(c.isdigit() for c in current_word):
# #         i2b2_whitelist_noname_fps = i2b2_whitelist_noname_fps.drop(int(index))
# #     else:
# #         cleaned_value = re.sub(punctuation_matcher, '', current_word).lower()
# #         i2b2_whitelist_noname_fps***REMOVED***'note_word'***REMOVED******REMOVED***int(index)***REMOVED*** = cleaned_value





#    # print row***REMOVED***'note_word'***REMOVED***, row***REMOVED***'occurrences'***REMOVED***


# fp_list = list(i2b2_whitelist_noname_fps***REMOVED***'note_word'***REMOVED***)
# # >>> len(fp_list)
# # 9727
# # Clean the list of FPs
# # Remove words with punctuation (except those beginning/ending with a period)
# fp_list = ***REMOVED***str(item) for item in fp_list***REMOVED***
# fp_list_nopunct = ***REMOVED***item for item in fp_list if not any(punctuation_matcher.match(c) for c in item***REMOVED***1:-1***REMOVED***)***REMOVED***
# fp_list_nopunct = ***REMOVED***re.sub(punctuation_matcher, '', item) for item in fp_list_nopunct***REMOVED***
# # >>> len(fp_list_nopunct)
# # 8567
# # Remove words with digits
# fp_list_nodigits = ***REMOVED***item for item in fp_list_nopunct if not any(c.isdigit() for c in item)***REMOVED***

# # Lowercase all words
# fp_list_cleaned = ***REMOVED***item.lower() for item in fp_list_nodigits***REMOVED***
# # >>> len(fp_list_cleaned)
# # 6845


# fp_list_top1 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.01)***REMOVED***
# fp_list_top5 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.05)***REMOVED***
# fp_list_top10 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.1)***REMOVED***
# fp_list_top20 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.2)***REMOVED***
# fp_list_top30 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.3)***REMOVED***
# fp_list_top40 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.4)***REMOVED***
# fp_list_top50 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.5)***REMOVED***
# fp_list_top60 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.6)***REMOVED***
# fp_list_top70 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.7)***REMOVED***
# fp_list_top80 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.8)***REMOVED***
# fp_list_top90 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.9)***REMOVED***
# fp_list_top100 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned))***REMOVED***


# # Add back varying numbers of FPs to whitelist_nonames
# whitelist_nonames_addback_1fps = whitelist_nonames | set(fp_list_top1)
# len(whitelist_nonames_addback_1fps) #188529
# whitelist_nonames_addback_5fps = whitelist_nonames | set(fp_list_top5)
# len(whitelist_nonames_addback_5fps) #188724
# whitelist_nonames_addback_10fps = whitelist_nonames | set(fp_list_top10)
# len(whitelist_nonames_addback_0fps)
# whitelist_nonames_addback_20fps = whitelist_nonames | set(fp_list_top20)
# len(whitelist_nonames_addback_20fps)
# whitelist_nonames_addback_30fps = whitelist_nonames | set(fp_list_top30)
# len(whitelist_nonames_addback_30fps)
# whitelist_nonames_addback_40fps = whitelist_nonames | set(fp_list_top40)
# len(whitelist_nonames_addback_40fps)
# whitelist_nonames_addback_50fps = whitelist_nonames | set(fp_list_top50)
# len(whitelist_nonames_addback_50fps)
# whitelist_nonames_addback_60fps = whitelist_nonames | set(fp_list_top60)
# len(whitelist_nonames_addback_60fps)
# whitelist_nonames_addback_70fps = whitelist_nonames | set(fp_list_top70)
# len(whitelist_nonames_addback_70fps)
# whitelist_nonames_addback_80fps = whitelist_nonames | set(fp_list_top80)
# len(whitelist_nonames_addback_80fps)
# whitelist_nonames_addback_90fps = whitelist_nonames | set(fp_list_top90)
# len(whitelist_nonames_addback_90fps)
# whitelist_nonames_addback_100fps = whitelist_nonames | set(fp_list_top100)
# len(whitelist_nonames_addback_100fps) #192211



# whitelist_addback_1 = {}
# for k in whitelist_nonames_addback_1fps:
#     whitelist_addback_1***REMOVED***k***REMOVED*** = 1

# whitelist_addback_5 = {}
# for k in whitelist_nonames_addback_5fps:
#     whitelist_addback_5***REMOVED***k***REMOVED*** = 1

# whitelist_addback_10 = {}
# for k in whitelist_nonames_addback_10fps:
#     whitelist_addback_10***REMOVED***k***REMOVED*** = 1

# whitelist_addback_20 = {}
# for k in whitelist_nonames_addback_20fps:
#     whitelist_addback_20***REMOVED***k***REMOVED*** = 1

# whitelist_addback_30 = {}
# for k in whitelist_nonames_addback_30fps:
#     whitelist_addback_30***REMOVED***k***REMOVED*** = 1

# whitelist_addback_40 = {}
# for k in whitelist_nonames_addback_40fps:
#     whitelist_addback_40***REMOVED***k***REMOVED*** = 1

# whitelist_addback_50 = {}
# for k in whitelist_nonames_addback_50fps:
#     whitelist_addback_50***REMOVED***k***REMOVED*** = 1

# whitelist_addback_60 = {}
# for k in whitelist_nonames_addback_60fps:
#     whitelist_addback_60***REMOVED***k***REMOVED*** = 1

# whitelist_addback_70 = {}
# for k in whitelist_nonames_addback_70fps:
#     whitelist_addback_70***REMOVED***k***REMOVED*** = 1

# whitelist_addback_80 = {}
# for k in whitelist_nonames_addback_80fps:
#     whitelist_addback_80***REMOVED***k***REMOVED*** = 1

# whitelist_addback_90 = {}
# for k in whitelist_nonames_addback_90fps:
#     whitelist_addback_90***REMOVED***k***REMOVED*** = 1

# whitelist_addback_100 = {}
# for k in whitelist_nonames_addback_100fps:
#     whitelist_addback_100***REMOVED***k***REMOVED*** = 1






# with open("whitelist_090618_nonames_addback1.json",'w') as outfile:
#     json.dump(whitelist_addback_1, outfile)


# with open("whitelist_090618_nonames_addback5.json",'w') as outfile:
#     json.dump(whitelist_addback_5, outfile)

# with open("whitelist_090618_nonames_addback10.json",'w') as outfile:
#     json.dump(whitelist_addback_10, outfile)

# with open("whitelist_090618_nonames_addback20.json",'w') as outfile:
#     json.dump(whitelist_addback_20, outfile)

# with open("whitelist_090618_nonames_addback30.json",'w') as outfile:
#     json.dump(whitelist_addback_30, outfile)

# with open("whitelist_090618_nonames_addback40.json",'w') as outfile:
#     json.dump(whitelist_addback_40, outfile)

# with open("whitelist_090618_nonames_addback50.json",'w') as outfile:
#     json.dump(whitelist_addback_50, outfile)

# with open("whitelist_090618_nonames_addback60.json",'w') as outfile:
#     json.dump(whitelist_addback_60, outfile)

# with open("whitelist_090618_nonames_addback70.json",'w') as outfile:
#     json.dump(whitelist_addback_70, outfile)

# with open("whitelist_090618_nonames_addback80.json",'w') as outfile:
#     json.dump(whitelist_addback_80, outfile)

# with open("whitelist_090618_nonames_addback90.json",'w') as outfile:
#     json.dump(whitelist_addback_90, outfile)

# with open("whitelist_090618_nonames_addback100.json",'w') as outfile:
#     json.dump(whitelist_addback_100, outfile)








# #################### Create configs with UCSF only FPs
# punctuation_matcher = re.compile(r"***REMOVED***^a-zA-Z0-9****REMOVED***")




# ucsf_whitelist_noname_fps = pd.read_csv('../../names_removal/ucsf_noname_whitelist_fps.csv')


# # # Edit data frame directly, to retain FP count information
# # for index, row in i2b2_whitelist_noname_fps.iterrows():
# #     current_word = str(row***REMOVED***'note_word'***REMOVED***)
# #     if any(punctuation_matcher.match(c) for c in current_word***REMOVED***1:-1***REMOVED***) or any(c.isdigit() for c in current_word):
# #         i2b2_whitelist_noname_fps = i2b2_whitelist_noname_fps.drop(int(index))
# #     else:
# #         cleaned_value = re.sub(punctuation_matcher, '', current_word).lower()
# #         i2b2_whitelist_noname_fps***REMOVED***'note_word'***REMOVED******REMOVED***int(index)***REMOVED*** = cleaned_value





#    # print row***REMOVED***'note_word'***REMOVED***, row***REMOVED***'occurrences'***REMOVED***


# fp_list = list(ucsf_whitelist_noname_fps***REMOVED***'note_word'***REMOVED***)
# # >>> len(fp_list)
# # 8170
# # Clean the list of FPs
# # Remove words with punctuation (except those beginning/ending with a period)
# fp_list = ***REMOVED***str(item) for item in fp_list***REMOVED***
# fp_list_nopunct = ***REMOVED***item for item in fp_list if not any(punctuation_matcher.match(c) for c in item***REMOVED***1:-1***REMOVED***)***REMOVED***
# fp_list_nopunct = ***REMOVED***re.sub(punctuation_matcher, '', item) for item in fp_list_nopunct***REMOVED***
# # >>> len(fp_list_nopunct)
# # 8049
# # Remove words with digits
# fp_list_nodigits = ***REMOVED***item for item in fp_list_nopunct if not any(c.isdigit() for c in item)***REMOVED***

# # Lowercase all words
# fp_list_cleaned = ***REMOVED***item.lower() for item in fp_list_nodigits***REMOVED***
# # >>> len(fp_list_cleaned)
# # 7547


# fp_list_top1 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.01)***REMOVED***
# fp_list_top5 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.05)***REMOVED***
# fp_list_top10 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.1)***REMOVED***
# fp_list_top20 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.2)***REMOVED***
# fp_list_top30 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.3)***REMOVED***
# fp_list_top40 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.4)***REMOVED***
# fp_list_top50 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.5)***REMOVED***
# fp_list_top60 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.6)***REMOVED***
# fp_list_top70 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.7)***REMOVED***
# fp_list_top80 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.8)***REMOVED***
# fp_list_top90 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.9)***REMOVED***
# fp_list_top100 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned))***REMOVED***


# # Add back varying numbers of FPs to whitelist_nonames
# whitelist_nonames_addback_1fps = whitelist_nonames | set(fp_list_top1)
# len(whitelist_nonames_addback_1fps) #188536
# whitelist_nonames_addback_5fps = whitelist_nonames | set(fp_list_top5)
# len(whitelist_nonames_addback_5fps) #188727
# whitelist_nonames_addback_10fps = whitelist_nonames | set(fp_list_top10)
# len(whitelist_nonames_addback_10fps)
# whitelist_nonames_addback_20fps = whitelist_nonames | set(fp_list_top20)
# len(whitelist_nonames_addback_20fps)
# whitelist_nonames_addback_30fps = whitelist_nonames | set(fp_list_top30)
# len(whitelist_nonames_addback_30fps)
# whitelist_nonames_addback_40fps = whitelist_nonames | set(fp_list_top40)
# len(whitelist_nonames_addback_40fps)
# whitelist_nonames_addback_50fps = whitelist_nonames | set(fp_list_top50)
# len(whitelist_nonames_addback_50fps)
# whitelist_nonames_addback_60fps = whitelist_nonames | set(fp_list_top60)
# len(whitelist_nonames_addback_60fps)
# whitelist_nonames_addback_70fps = whitelist_nonames | set(fp_list_top70)
# len(whitelist_nonames_addback_70fps)
# whitelist_nonames_addback_80fps = whitelist_nonames | set(fp_list_top80)
# len(whitelist_nonames_addback_80fps)
# whitelist_nonames_addback_90fps = whitelist_nonames | set(fp_list_top90)
# len(whitelist_nonames_addback_90fps)
# whitelist_nonames_addback_100fps = whitelist_nonames | set(fp_list_top100)
# len(whitelist_nonames_addback_100fps) #192534



# whitelist_addback_1 = {}
# for k in whitelist_nonames_addback_1fps:
#     whitelist_addback_1***REMOVED***k***REMOVED*** = 1

# whitelist_addback_5 = {}
# for k in whitelist_nonames_addback_5fps:
#     whitelist_addback_5***REMOVED***k***REMOVED*** = 1

# whitelist_addback_10 = {}
# for k in whitelist_nonames_addback_10fps:
#     whitelist_addback_10***REMOVED***k***REMOVED*** = 1

# whitelist_addback_20 = {}
# for k in whitelist_nonames_addback_20fps:
#     whitelist_addback_20***REMOVED***k***REMOVED*** = 1

# whitelist_addback_30 = {}
# for k in whitelist_nonames_addback_30fps:
#     whitelist_addback_30***REMOVED***k***REMOVED*** = 1

# whitelist_addback_40 = {}
# for k in whitelist_nonames_addback_40fps:
#     whitelist_addback_40***REMOVED***k***REMOVED*** = 1

# whitelist_addback_50 = {}
# for k in whitelist_nonames_addback_50fps:
#     whitelist_addback_50***REMOVED***k***REMOVED*** = 1

# whitelist_addback_60 = {}
# for k in whitelist_nonames_addback_60fps:
#     whitelist_addback_60***REMOVED***k***REMOVED*** = 1

# whitelist_addback_70 = {}
# for k in whitelist_nonames_addback_70fps:
#     whitelist_addback_70***REMOVED***k***REMOVED*** = 1

# whitelist_addback_80 = {}
# for k in whitelist_nonames_addback_80fps:
#     whitelist_addback_80***REMOVED***k***REMOVED*** = 1

# whitelist_addback_90 = {}
# for k in whitelist_nonames_addback_90fps:
#     whitelist_addback_90***REMOVED***k***REMOVED*** = 1

# whitelist_addback_100 = {}
# for k in whitelist_nonames_addback_100fps:
#     whitelist_addback_100***REMOVED***k***REMOVED*** = 1






# with open("whitelist_090618_nonames_addback1_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_1, outfile)


# with open("whitelist_090618_nonames_addback5_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_5, outfile)

# with open("whitelist_090618_nonames_addback10_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_10, outfile)

# with open("whitelist_090618_nonames_addback20_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_20, outfile)

# with open("whitelist_090618_nonames_addback30_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_30, outfile)

# with open("whitelist_090618_nonames_addback40_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_40, outfile)

# with open("whitelist_090618_nonames_addback50_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_50, outfile)

# with open("whitelist_090618_nonames_addback60_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_60, outfile)

# with open("whitelist_090618_nonames_addback70_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_70, outfile)

# with open("whitelist_090618_nonames_addback80_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_80, outfile)

# with open("whitelist_090618_nonames_addback90_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_90, outfile)

# with open("whitelist_090618_nonames_addback100_ucsf.json",'w') as outfile:
#     json.dump(whitelist_addback_100, outfile)






# #################### Intersection of UCSf and i2b2 whitelist fps #######
# punctuation_matcher = re.compile(r"***REMOVED***^a-zA-Z0-9****REMOVED***")




# ucsf_whitelist_noname_fps = pd.read_csv('../../names_removal/ucsf_noname_whitelist_fps.csv')


# # # Edit data frame directly, to retain FP count information
# # for index, row in i2b2_whitelist_noname_fps.iterrows():
# #     current_word = str(row***REMOVED***'note_word'***REMOVED***)
# #     if any(punctuation_matcher.match(c) for c in current_word***REMOVED***1:-1***REMOVED***) or any(c.isdigit() for c in current_word):
# #         i2b2_whitelist_noname_fps = i2b2_whitelist_noname_fps.drop(int(index))
# #     else:
# #         cleaned_value = re.sub(punctuation_matcher, '', current_word).lower()
# #         i2b2_whitelist_noname_fps***REMOVED***'note_word'***REMOVED******REMOVED***int(index)***REMOVED*** = cleaned_value





#    # print row***REMOVED***'note_word'***REMOVED***, row***REMOVED***'occurrences'***REMOVED***


# fp_list_ucsf = list(ucsf_whitelist_noname_fps***REMOVED***'note_word'***REMOVED***)
# # Clean the list of FPs
# # Remove words with punctuation (except those beginning/ending with a period)
# fp_list_ucsf = ***REMOVED***str(item) for item in fp_list_ucsf***REMOVED***
# fp_list_nopunct_ucsf = ***REMOVED***item for item in fp_list_ucsf if not any(punctuation_matcher.match(c) for c in item***REMOVED***1:-1***REMOVED***)***REMOVED***
# fp_list_nopunct_ucsf = ***REMOVED***re.sub(punctuation_matcher, '', item) for item in fp_list_nopunct_ucsf***REMOVED***
# # Remove words with digits
# fp_list_nodigits_ucsf = ***REMOVED***item for item in fp_list_nopunct_ucsf if not any(c.isdigit() for c in item)***REMOVED***

# # Lowercase all words
# fp_list_cleaned_uscf = ***REMOVED***item.lower() for item in fp_list_nodigits_ucsf***REMOVED***






# fp_list_i2b2 = list(i2b2_whitelist_noname_fps***REMOVED***'note_word'***REMOVED***)
# # Clean the list of FPs
# # Remove words with punctuation (except those beginning/ending with a period)
# fp_list_i2b2 = ***REMOVED***str(item) for item in fp_list_i2b2***REMOVED***
# fp_list_nopunct_i2b2 = ***REMOVED***item for item in fp_list_i2b2 if not any(punctuation_matcher.match(c) for c in item***REMOVED***1:-1***REMOVED***)***REMOVED***
# fp_list_nopunct_i2b2 = ***REMOVED***re.sub(punctuation_matcher, '', item) for item in fp_list_nopunct_i2b2***REMOVED***
# # Remove words with digits
# fp_list_nodigits_i2b2 = ***REMOVED***item for item in fp_list_nopunct_i2b2 if not any(c.isdigit() for c in item)***REMOVED***

# # Lowercase all words
# fp_list_cleaned_i2b2 = ***REMOVED***item.lower() for item in fp_list_nodigits_i2b2***REMOVED***


# ### Intersection list
# # len(fp_list_cleaned_uscf): 7547
# # len(fp_list_cleaned_i2b2): 6845
# # Iterate through UCSF Fps list in order to maintain frequency
# fp_list_cleaned = ***REMOVED******REMOVED***
# for word in fp_list_cleaned_uscf:
#     if word in fp_list_cleaned_i2b2:
#         fp_list_cleaned.append(word)

# # len(fp_list_cleaned): 4606


# fp_list_top1 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.01)***REMOVED***
# fp_list_top5 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.05)***REMOVED***
# fp_list_top10 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.1)***REMOVED***
# fp_list_top20 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.2)***REMOVED***
# fp_list_top30 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.3)***REMOVED***
# fp_list_top40 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.4)***REMOVED***
# fp_list_top50 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.5)***REMOVED***
# fp_list_top60 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.6)***REMOVED***
# fp_list_top70 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.7)***REMOVED***
# fp_list_top80 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.8)***REMOVED***
# fp_list_top90 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.9)***REMOVED***
# fp_list_top100 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned))***REMOVED***


# # Add back varying numbers of FPs to whitelist_nonames
# whitelist_nonames_addback_1fps = whitelist_nonames | set(fp_list_top1)
# len(whitelist_nonames_addback_1fps) #188513
# whitelist_nonames_addback_5fps = whitelist_nonames | set(fp_list_top5)
# len(whitelist_nonames_addback_5fps) #188639
# whitelist_nonames_addback_10fps = whitelist_nonames | set(fp_list_top10)
# len(whitelist_nonames_addback_10fps)
# whitelist_nonames_addback_20fps = whitelist_nonames | set(fp_list_top20)
# len(whitelist_nonames_addback_20fps)
# whitelist_nonames_addback_30fps = whitelist_nonames | set(fp_list_top30)
# len(whitelist_nonames_addback_30fps)
# whitelist_nonames_addback_40fps = whitelist_nonames | set(fp_list_top40)
# len(whitelist_nonames_addback_40fps)
# whitelist_nonames_addback_50fps = whitelist_nonames | set(fp_list_top50)
# len(whitelist_nonames_addback_50fps)
# whitelist_nonames_addback_60fps = whitelist_nonames | set(fp_list_top60)
# len(whitelist_nonames_addback_60fps)
# whitelist_nonames_addback_70fps = whitelist_nonames | set(fp_list_top70)
# len(whitelist_nonames_addback_70fps)
# whitelist_nonames_addback_80fps = whitelist_nonames | set(fp_list_top80)
# len(whitelist_nonames_addback_80fps)
# whitelist_nonames_addback_90fps = whitelist_nonames | set(fp_list_top90)
# len(whitelist_nonames_addback_90fps)
# whitelist_nonames_addback_100fps = whitelist_nonames | set(fp_list_top100)
# len(whitelist_nonames_addback_100fps) #190092



# whitelist_addback_1 = {}
# for k in whitelist_nonames_addback_1fps:
#     whitelist_addback_1***REMOVED***k***REMOVED*** = 1

# whitelist_addback_5 = {}
# for k in whitelist_nonames_addback_5fps:
#     whitelist_addback_5***REMOVED***k***REMOVED*** = 1

# whitelist_addback_10 = {}
# for k in whitelist_nonames_addback_10fps:
#     whitelist_addback_10***REMOVED***k***REMOVED*** = 1

# whitelist_addback_20 = {}
# for k in whitelist_nonames_addback_20fps:
#     whitelist_addback_20***REMOVED***k***REMOVED*** = 1

# whitelist_addback_30 = {}
# for k in whitelist_nonames_addback_30fps:
#     whitelist_addback_30***REMOVED***k***REMOVED*** = 1

# whitelist_addback_40 = {}
# for k in whitelist_nonames_addback_40fps:
#     whitelist_addback_40***REMOVED***k***REMOVED*** = 1

# whitelist_addback_50 = {}
# for k in whitelist_nonames_addback_50fps:
#     whitelist_addback_50***REMOVED***k***REMOVED*** = 1

# whitelist_addback_60 = {}
# for k in whitelist_nonames_addback_60fps:
#     whitelist_addback_60***REMOVED***k***REMOVED*** = 1

# whitelist_addback_70 = {}
# for k in whitelist_nonames_addback_70fps:
#     whitelist_addback_70***REMOVED***k***REMOVED*** = 1

# whitelist_addback_80 = {}
# for k in whitelist_nonames_addback_80fps:
#     whitelist_addback_80***REMOVED***k***REMOVED*** = 1

# whitelist_addback_90 = {}
# for k in whitelist_nonames_addback_90fps:
#     whitelist_addback_90***REMOVED***k***REMOVED*** = 1

# whitelist_addback_100 = {}
# for k in whitelist_nonames_addback_100fps:
#     whitelist_addback_100***REMOVED***k***REMOVED*** = 1






# with open("whitelist_090618_nonames_addback1_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_1, outfile)


# with open("whitelist_090618_nonames_addback5_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_5, outfile)

# with open("whitelist_090618_nonames_addback10_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_10, outfile)

# with open("whitelist_090618_nonames_addback20_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_20, outfile)

# with open("whitelist_090618_nonames_addback30_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_30, outfile)

# with open("whitelist_090618_nonames_addback40_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_40, outfile)

# with open("whitelist_090618_nonames_addback50_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_50, outfile)

# with open("whitelist_090618_nonames_addback60_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_60, outfile)

# with open("whitelist_090618_nonames_addback70_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_70, outfile)

# with open("whitelist_090618_nonames_addback80_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_80, outfile)

# with open("whitelist_090618_nonames_addback90_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_90, outfile)

# with open("whitelist_090618_nonames_addback100_ucsf_n_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_100, outfile)




# ########################## union of i2b2/ucsf fps


# fp_list_ucsf = list(ucsf_whitelist_noname_fps***REMOVED***'note_word'***REMOVED***)
# fp_list_i2b2 = list(i2b2_whitelist_noname_fps***REMOVED***'note_word'***REMOVED***)

# fp_list_ucsf_counts = list(ucsf_whitelist_noname_fps***REMOVED***'occurrences'***REMOVED***)
# fp_list_i2b2_counts = list(i2b2_whitelist_noname_fps***REMOVED***'occurrences'***REMOVED***)


# # Create list of tuples that contain word/coutn information for ucsf and i2b2 fps

# fp_list_words_counts = ***REMOVED******REMOVED***
# for i in range(len(fp_list_ucsf)):
#     word = fp_list_ucsf***REMOVED***i***REMOVED***
#     count = fp_list_ucsf_counts***REMOVED***i***REMOVED***
#     fp_list_words_counts.append((word,count))


# for i in range(len(fp_list_i2b2)):
#     word = fp_list_i2b2***REMOVED***i***REMOVED***
#     count = fp_list_i2b2_counts***REMOVED***i***REMOVED***
#     fp_list_words_counts.append((word,count))


# # Sort by occurrences
# fp_list_words_counts = sorted(fp_list_words_counts, key=lambda x: x***REMOVED***1***REMOVED***, reverse =True)

# # Clean each word
# # Remove words with punctuation (except those beginning/ending with a period)
# fp_list_counts = ***REMOVED***(str(item***REMOVED***0***REMOVED***),item***REMOVED***1***REMOVED***) for item in fp_list_words_counts***REMOVED***
# fp_list_counts_nopunct = ***REMOVED***item for item in fp_list_counts if not any(punctuation_matcher.match(c) for c in item***REMOVED***0***REMOVED******REMOVED***1:-1***REMOVED***)***REMOVED***
# fp_list_counts_nopunct = ***REMOVED***(re.sub(punctuation_matcher, '', item***REMOVED***0***REMOVED***),item***REMOVED***1***REMOVED***) for item in fp_list_counts_nopunct***REMOVED***
# # Remove words with digits
# fp_list_counts_nodigits = ***REMOVED***item for item in fp_list_counts_nopunct if not any(c.isdigit() for c in item***REMOVED***0***REMOVED***)***REMOVED***

# # Lowercase all words
# fp_list_counts_nodigits_cleaned = ***REMOVED***(item***REMOVED***0***REMOVED***.lower(),item***REMOVED***1***REMOVED***) for item in fp_list_counts_nodigits***REMOVED***

# # get rid of duplicates, separate lists
# fp_list_cleaned = ***REMOVED******REMOVED***

# for tup in fp_list_counts_nodigits_cleaned:
#     if tup***REMOVED***0***REMOVED*** not in fp_list_cleaned:
#         fp_list_cleaned.append(tup***REMOVED***0***REMOVED***)


# # len(fp_list_cleaned): 6229


# fp_list_top1 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.01)***REMOVED***
# fp_list_top5 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.05)***REMOVED***
# fp_list_top10 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.1)***REMOVED***
# fp_list_top20 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.2)***REMOVED***
# fp_list_top30 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.3)***REMOVED***
# fp_list_top40 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.4)***REMOVED***
# fp_list_top50 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.5)***REMOVED***
# fp_list_top60 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.6)***REMOVED***
# fp_list_top70 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.7)***REMOVED***
# fp_list_top80 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.8)***REMOVED***
# fp_list_top90 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.9)***REMOVED***
# fp_list_top100 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned))***REMOVED***


# # Add back varying numbers of FPs to whitelist_nonames
# whitelist_nonames_addback_1fps = whitelist_nonames | set(fp_list_top1)
# len(whitelist_nonames_addback_1fps) #188535
# whitelist_nonames_addback_5fps = whitelist_nonames | set(fp_list_top5)
# len(whitelist_nonames_addback_5fps) #188784
# whitelist_nonames_addback_10fps = whitelist_nonames | set(fp_list_top10)
# len(whitelist_nonames_addback_10fps)
# whitelist_nonames_addback_20fps = whitelist_nonames | set(fp_list_top20)
# len(whitelist_nonames_addback_20fps)
# whitelist_nonames_addback_30fps = whitelist_nonames | set(fp_list_top30)
# len(whitelist_nonames_addback_30fps)
# whitelist_nonames_addback_40fps = whitelist_nonames | set(fp_list_top40)
# len(whitelist_nonames_addback_40fps)
# whitelist_nonames_addback_50fps = whitelist_nonames | set(fp_list_top50)
# len(whitelist_nonames_addback_50fps)
# whitelist_nonames_addback_60fps = whitelist_nonames | set(fp_list_top60)
# len(whitelist_nonames_addback_60fps)
# whitelist_nonames_addback_70fps = whitelist_nonames | set(fp_list_top70)
# len(whitelist_nonames_addback_70fps)
# whitelist_nonames_addback_80fps = whitelist_nonames | set(fp_list_top80)
# len(whitelist_nonames_addback_80fps)
# whitelist_nonames_addback_90fps = whitelist_nonames | set(fp_list_top90)
# len(whitelist_nonames_addback_90fps)
# whitelist_nonames_addback_100fps = whitelist_nonames | set(fp_list_top100)
# len(whitelist_nonames_addback_100fps) #194653



# whitelist_addback_1 = {}
# for k in whitelist_nonames_addback_1fps:
#     whitelist_addback_1***REMOVED***k***REMOVED*** = 1

# whitelist_addback_5 = {}
# for k in whitelist_nonames_addback_5fps:
#     whitelist_addback_5***REMOVED***k***REMOVED*** = 1

# whitelist_addback_10 = {}
# for k in whitelist_nonames_addback_10fps:
#     whitelist_addback_10***REMOVED***k***REMOVED*** = 1

# whitelist_addback_20 = {}
# for k in whitelist_nonames_addback_20fps:
#     whitelist_addback_20***REMOVED***k***REMOVED*** = 1

# whitelist_addback_30 = {}
# for k in whitelist_nonames_addback_30fps:
#     whitelist_addback_30***REMOVED***k***REMOVED*** = 1

# whitelist_addback_40 = {}
# for k in whitelist_nonames_addback_40fps:
#     whitelist_addback_40***REMOVED***k***REMOVED*** = 1

# whitelist_addback_50 = {}
# for k in whitelist_nonames_addback_50fps:
#     whitelist_addback_50***REMOVED***k***REMOVED*** = 1

# whitelist_addback_60 = {}
# for k in whitelist_nonames_addback_60fps:
#     whitelist_addback_60***REMOVED***k***REMOVED*** = 1

# whitelist_addback_70 = {}
# for k in whitelist_nonames_addback_70fps:
#     whitelist_addback_70***REMOVED***k***REMOVED*** = 1

# whitelist_addback_80 = {}
# for k in whitelist_nonames_addback_80fps:
#     whitelist_addback_80***REMOVED***k***REMOVED*** = 1

# whitelist_addback_90 = {}
# for k in whitelist_nonames_addback_90fps:
#     whitelist_addback_90***REMOVED***k***REMOVED*** = 1

# whitelist_addback_100 = {}
# for k in whitelist_nonames_addback_100fps:
#     whitelist_addback_100***REMOVED***k***REMOVED*** = 1






# with open("whitelist_090618_nonames_addback1_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_1, outfile)


# with open("whitelist_090618_nonames_addback5_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_5, outfile)

# with open("whitelist_090618_nonames_addback10_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_10, outfile)

# with open("whitelist_090618_nonames_addback20_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_20, outfile)

# with open("whitelist_090618_nonames_addback30_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_30, outfile)

# with open("whitelist_090618_nonames_addback40_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_40, outfile)

# with open("whitelist_090618_nonames_addback50_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_50, outfile)

# with open("whitelist_090618_nonames_addback60_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_60, outfile)

# with open("whitelist_090618_nonames_addback70_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_70, outfile)

# with open("whitelist_090618_nonames_addback80_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_80, outfile)

# with open("whitelist_090618_nonames_addback90_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_90, outfile)

# with open("whitelist_090618_nonames_addback100_ucsf_u_i2b2.json",'w') as outfile:
#     json.dump(whitelist_addback_100, outfile)













######################### FP list updated i2b2/ucsf #############
#nohup python3 main.py -f /data/muenzenk/sub_names_from_whitelist/configs/whitelist_090618_nonames_addback0_whitelist_only_pipeline.json -a /data/muenzenk/de-id_stable1/data/i2b2_anno_updated/ -x /data/muenzenk/de-id_stable1/data/phi_notes_updated.json -i /data/muenzenk/de-id_stable1/data/i2b2_notes_updated/ -o /data/muenzenk/de-id_stable1/data/i2b2_results/ -c /data/muenzenk/de-id_stable1/data/coordinates.json --stanfordner /data/muenzenk/stanford-ner/ > i2b2_test_combined_results.txt 2>&1 &
#nohup python3 main.py -f /data/muenzenk/sub_names_from_whitelist/configs/whitelist_090618_nonames_addback0_whitelist_only_pipeline.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_results/ -c /data/muenzenk/batch_data/combined_102_110_r1_r2/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/batch_data/combined_102_110_r1_r2/ > all_ucsf_test_combined_results.txt 2>&1 &

i2b2_whitelist_noname_fps_noperiods = pd.read_csv('../../names_removal/i2b2_noname_whitelist_fps_noperiods.csv')
ucsf_whitelist_noname_fps_noperiods = pd.read_csv('../../names_removal/ucsf_noname_whitelist_fps_noperiods.csv')




############## Union whitelists updated


fp_list_ucsf = list(ucsf_whitelist_noname_fps_noperiods***REMOVED***'note_word'***REMOVED***)
fp_list_i2b2 = list(i2b2_whitelist_noname_fps_noperiods***REMOVED***'note_word'***REMOVED***)

fp_list_ucsf_counts = list(ucsf_whitelist_noname_fps_noperiods***REMOVED***'occurrences'***REMOVED***)
fp_list_i2b2_counts = list(i2b2_whitelist_noname_fps_noperiods***REMOVED***'occurrences'***REMOVED***)


# Create list of tuples that contain word/coutn information for ucsf and i2b2 fps

fp_list_words_counts = ***REMOVED******REMOVED***
for i in range(len(fp_list_ucsf)):
    word = fp_list_ucsf***REMOVED***i***REMOVED***
    count = fp_list_ucsf_counts***REMOVED***i***REMOVED***
    fp_list_words_counts.append((word,count))


for i in range(len(fp_list_i2b2)):
    word = fp_list_i2b2***REMOVED***i***REMOVED***
    count = fp_list_i2b2_counts***REMOVED***i***REMOVED***
    fp_list_words_counts.append((word,count))


# Sort by occurrences
fp_list_words_counts = sorted(fp_list_words_counts, key=lambda x: x***REMOVED***1***REMOVED***, reverse =True)

# Clean each word
# Remove words with punctuation (except those beginning/ending with a period)
fp_list_counts = ***REMOVED***(str(item***REMOVED***0***REMOVED***),item***REMOVED***1***REMOVED***) for item in fp_list_words_counts***REMOVED***
# fp_list_counts_nopunct = ***REMOVED***item for item in fp_list_counts if not any(punctuation_matcher.match(c) for c in item***REMOVED***0***REMOVED******REMOVED***1:-1***REMOVED***)***REMOVED***
# fp_list_counts_nopunct = ***REMOVED***(re.sub(punctuation_matcher, '', item***REMOVED***0***REMOVED***),item***REMOVED***1***REMOVED***) for item in fp_list_counts_nopunct***REMOVED***
# Remove words with digits
# fp_list_counts_nodigits = ***REMOVED***item for item in fp_list_counts_nopunct if not any(c.isdigit() for c in item***REMOVED***0***REMOVED***)***REMOVED***
fp_list_counts_nodigits = ***REMOVED***item for item in fp_list_counts if not item***REMOVED***0***REMOVED***.isdigit()***REMOVED***


# Lowercase all words
fp_list_counts_nodigits_cleaned = ***REMOVED***(item***REMOVED***0***REMOVED***.lower(),item***REMOVED***1***REMOVED***) for item in fp_list_counts_nodigits***REMOVED***

# get rid of duplicates, separate lists
fp_list_cleaned = ***REMOVED******REMOVED***

for tup in fp_list_counts_nodigits_cleaned:
    if tup***REMOVED***0***REMOVED*** not in fp_list_cleaned:
        fp_list_cleaned.append(tup***REMOVED***0***REMOVED***)


# # len(fp_list_cleaned): 6229


# fp_list_top1 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.01)***REMOVED***
# fp_list_top5 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.05)***REMOVED***
# fp_list_top10 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.1)***REMOVED***
# fp_list_top20 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.2)***REMOVED***
# fp_list_top30 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.3)***REMOVED***
# fp_list_top40 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.4)***REMOVED***
# fp_list_top50 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.5)***REMOVED***
# fp_list_top60 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.6)***REMOVED***
# fp_list_top70 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.7)***REMOVED***
# fp_list_top80 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.8)***REMOVED***
# fp_list_top90 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned)*0.9)***REMOVED***
fp_list_top100 = fp_list_cleaned***REMOVED***0:int(len(fp_list_cleaned))***REMOVED***


# # Add back varying numbers of FPs to whitelist_nonames
# whitelist_nonames_addback_1fps = whitelist_nonames | set(fp_list_top1)
# len(whitelist_nonames_addback_1fps) #188535
# whitelist_nonames_addback_5fps = whitelist_nonames | set(fp_list_top5)
# len(whitelist_nonames_addback_5fps) #188784
# whitelist_nonames_addback_10fps = whitelist_nonames | set(fp_list_top10)
# len(whitelist_nonames_addback_10fps)
# whitelist_nonames_addback_20fps = whitelist_nonames | set(fp_list_top20)
# len(whitelist_nonames_addback_20fps)
# whitelist_nonames_addback_30fps = whitelist_nonames | set(fp_list_top30)
# len(whitelist_nonames_addback_30fps)
# whitelist_nonames_addback_40fps = whitelist_nonames | set(fp_list_top40)
# len(whitelist_nonames_addback_40fps)
# whitelist_nonames_addback_50fps = whitelist_nonames | set(fp_list_top50)
# len(whitelist_nonames_addback_50fps)
# whitelist_nonames_addback_60fps = whitelist_nonames | set(fp_list_top60)
# len(whitelist_nonames_addback_60fps)
# whitelist_nonames_addback_70fps = whitelist_nonames | set(fp_list_top70)
# len(whitelist_nonames_addback_70fps)
# whitelist_nonames_addback_80fps = whitelist_nonames | set(fp_list_top80)
# len(whitelist_nonames_addback_80fps)
# whitelist_nonames_addback_90fps = whitelist_nonames | set(fp_list_top90)
# len(whitelist_nonames_addback_90fps)
whitelist_nonames_addback_100fps = whitelist_nonames | set(fp_list_top100)
len(whitelist_nonames_addback_100fps) #194653



# whitelist_addback_1 = {}
# for k in whitelist_nonames_addback_1fps:
#     whitelist_addback_1***REMOVED***k***REMOVED*** = 1

# whitelist_addback_5 = {}
# for k in whitelist_nonames_addback_5fps:
#     whitelist_addback_5***REMOVED***k***REMOVED*** = 1

# whitelist_addback_10 = {}
# for k in whitelist_nonames_addback_10fps:
#     whitelist_addback_10***REMOVED***k***REMOVED*** = 1

# whitelist_addback_20 = {}
# for k in whitelist_nonames_addback_20fps:
#     whitelist_addback_20***REMOVED***k***REMOVED*** = 1

# whitelist_addback_30 = {}
# for k in whitelist_nonames_addback_30fps:
#     whitelist_addback_30***REMOVED***k***REMOVED*** = 1

# whitelist_addback_40 = {}
# for k in whitelist_nonames_addback_40fps:
#     whitelist_addback_40***REMOVED***k***REMOVED*** = 1

# whitelist_addback_50 = {}
# for k in whitelist_nonames_addback_50fps:
#     whitelist_addback_50***REMOVED***k***REMOVED*** = 1

# whitelist_addback_60 = {}
# for k in whitelist_nonames_addback_60fps:
#     whitelist_addback_60***REMOVED***k***REMOVED*** = 1

# whitelist_addback_70 = {}
# for k in whitelist_nonames_addback_70fps:
#     whitelist_addback_70***REMOVED***k***REMOVED*** = 1

# whitelist_addback_80 = {}
# for k in whitelist_nonames_addback_80fps:
#     whitelist_addback_80***REMOVED***k***REMOVED*** = 1

# whitelist_addback_90 = {}
# for k in whitelist_nonames_addback_90fps:
#     whitelist_addback_90***REMOVED***k***REMOVED*** = 1

whitelist_addback_100 = {}
for k in whitelist_nonames_addback_100fps:
    whitelist_addback_100***REMOVED***k***REMOVED*** = 1






# with open("whitelist_090618_nonames_addback1_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_1, outfile)


# with open("whitelist_090618_nonames_addback5_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_5, outfile)

# with open("whitelist_090618_nonames_addback10_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_10, outfile)

# with open("whitelist_090618_nonames_addback20_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_20, outfile)

# with open("whitelist_090618_nonames_addback30_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_30, outfile)

# with open("whitelist_090618_nonames_addback40_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_40, outfile)

# with open("whitelist_090618_nonames_addback50_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_50, outfile)

# with open("whitelist_090618_nonames_addback60_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_60, outfile)

# with open("whitelist_090618_nonames_addback70_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_70, outfile)

# with open("whitelist_090618_nonames_addback80_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_80, outfile)

# with open("whitelist_090618_nonames_addback90_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_90, outfile)

# with open("whitelist_090618_nonames_addback100_ucsf_u_i2b2_noperiods.json",'w') as outfile:
#     json.dump(whitelist_addback_100, outfile)




#### Eponymous medical terms
# Goal: remove all dieases that are named after people from the whitelist

disease_names_df = pd.read_csv('../../names_removal/eponymous_medical_terms.csv')

disease_names = list(disease_names_df***REMOVED***'name'***REMOVED***)

disease_names = set(***REMOVED***item.lower()for item in disease_names***REMOVED***)


overlap = ***REMOVED******REMOVED***
non_overlap = ***REMOVED******REMOVED***
for word in disease_names:
    if word in whitelist_addback_100:
        overlap.append(word)
    else:
        non_overlap.append(word)

new_whitelist = whitelist_nonames_addback_100fps - (whitelist_nonames_addback_100fps&set(overlap))


whitelist_addback_100_no_eponyms = {}
for k in new_whitelist:
    whitelist_addback_100_no_eponyms***REMOVED***k***REMOVED*** = 1

with open("whitelist_090618_nonames_addback100_ucsf_u_i2b2_noperiods_noeponyms.json",'w') as outfile:
    json.dump(whitelist_addback_100_no_eponyms, outfile)


# Words to add back
common_words = set(***REMOVED***'may','day','hand','down','still','brown','white','tan','de'***REMOVED***)


new_whitelist_with_common_words = new_whitelist | common_words
    


whitelist_addback_100_no_eponyms_common = {}
for k in new_whitelist_with_common_words:
    whitelist_addback_100_no_eponyms_common***REMOVED***k***REMOVED*** = 1

with open("whitelist_090618_nonames_addback100_ucsf_u_i2b2_noperiods_noeponyms_commonwords.json",'w') as outfile:
    json.dump(whitelist_addback_100_no_eponyms_common, outfile)



############ Observe overlap between FP union list and names (from union FPS) ######
fp_firstnames_overlap = set(***REMOVED***x for x in fp_list_cleaned if x in set_100_first***REMOVED***) 
fp_lastnames_overlap = set(***REMOVED***x for x in fp_list_cleaned if x in set_100_last***REMOVED***) 
fp_names_overlap = set(***REMOVED***x for x in fp_list_cleaned if x in all_names_set***REMOVED***) 


len(fp_names_overlap) #2816
for name in fp_names_overlap:
    print(name)

clear_names = set(***REMOVED***'thiet','jane','sam','hodgkin','abraham','christian','hawkins','rutherford','epstein','hodgkins','bruce','smith','crohn','carol','huntington','parkinson','jackson','hartmann','madison','helen','hashimoto','fischer','patrick','sjogren','richard','wilson','tristan','connie','judah','babinski','mallory','allen','john','brad','hickman','chad','ron','michael'***REMOVED***)
# 37 names (including eponyms)



new_whitelist_with_common_words_nonames = new_whitelist_with_common_words - (new_whitelist_with_common_words&clear_names)
# 27 names subtracted


whitelist_addback_100_no_eponyms_common_nonames = {}
for k in new_whitelist_with_common_words_nonames:
    whitelist_addback_100_no_eponyms_common_nonames***REMOVED***k***REMOVED*** = 1

with open("whitelist_090618_nonames_addback100_ucsf_u_i2b2_noperiods_noeponyms_commonwords_nonames.json",'w') as outfile:
    json.dump(whitelist_addback_100_no_eponyms_common_nonames, outfile)



##### Gte full list of fps
full_fps_list = set(fp_list_top100) - (set(fp_list_top100)&disease_names) - (set(fp_list_top100)&clear_names)










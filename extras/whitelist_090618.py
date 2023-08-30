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
add_20k_words_amt = int(sys.argv[1])
print("20k words %: ", add_20k_words_amt)

# subtract_streets_amt = int(sys.argv[4])
# print("Street names %: ", subtract_streets_amt)
# subtract_cities_amt = int(sys.argv[5])
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
umls_df_crap = umls_df['crap']
# Remove blanks
umls_df_crap = umls_df_crap[umls_df_crap.notnull()]
# Remove numbers
umls_df_crap = umls_df_crap.str.replace('\d+', '')
# Remove apostrophes, underscores, backslashes
umls_df_crap = umls_df_crap.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') # Edit 1/22/18
# Remove single character words
umls_df_crap = umls_df_crap.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ')
# The pattern \b\w\b will replace any single word character with a word boundary
umls_df_crap = umls_df_crap.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# Remove rows where length of descriptor is less than 3
umls_df_crap = list(umls_df_crap[umls_df_crap.str.len() > 2])


# Get column of df that contains term stem and other crap
umls_df_label = umls_df['label']
# Remove blanks
umls_df_label = umls_df_label[umls_df_label.notnull()]
# Remove numbers
umls_df_label = umls_df_label.str.replace('\d+', '')
# Remove apostrophes, underscores, commas, colons, semicolons, backslashes
umls_df_label = umls_df_label.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') # Edit 1/22/18
# Remove single character words
umls_df_label = umls_df_label.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ')
# The pattern \b\w\b will replace any single word character with a word boundary
umls_df_label = umls_df_label.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# Remove rows where length of descriptor is less than 3
umls_df_label = list(umls_df_label[umls_df_label.str.len() > 2])


# Order Edit 1/18/17
# Get column of df that contains variations on the stem
umls_df_useful = umls_df['useful']
# Remove blanks
umls_df_useful = umls_df_useful[umls_df_useful.notnull()]
# Remove numbers
umls_df_useful = umls_df_useful.str.replace('\d+', '')
# Remove apostrophes, underscores, commas, colons, semicolons, backslashes
umls_df_useful = umls_df_useful.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') # Edit 1/22/18
# Remove single character words
#umls_df_useful = umls_df_useful.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ').str.replace('|',' ')
# The pattern \b\w\b will replace any single word character with a word boundary
#umls_df_useful = umls_df_useful.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# Remove rows where length of descriptor is less than 3
umls_df_useful = list(umls_df_useful[umls_df_useful.str.len() > 2])


# Get the first term in useful column
umls_df['happy'] = umls_df['useful'].str.extract('(.*?)\|', expand = True)
umls_df_happy = umls_df['happy']
# Remove blanks
umls_df_happy = umls_df_happy[umls_df_happy.notnull()]
# Remove numbers
umls_df_happy = umls_df_happy.str.replace('\d+', '')
# Remove apostrophes, underscores, commas, colons, semicolons, backslashes
umls_df_happy = umls_df_happy.str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|','').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','') # Edit 1/22/18
# Remove single character words
umls_df_happy = umls_df_happy.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ').str.replace('|',' ')
# The pattern \b\w\b will replace any single word character with a word boundary
umls_df_happy = umls_df_happy.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# Remove rows where length of descriptor is less than 3
umls_df_happy = list(umls_df_happy[umls_df_happy.str.len() > 2])


# Create list from crap df
umls_crap_list = list(umls_df_crap)
umls_crap_list = [term.split() for term in umls_crap_list] # convert each string into a list of the words in the string
umls_crap_list = [item for sublist in umls_crap_list for item in sublist] # flatten the list of lists into a single list
umls_crap_list = [i.lower() for i in umls_crap_list] # make all lower case
umls_crap_list = [i.replace(' ','') for i in umls_crap_list] # last check for spaces
#print(len(set(umls_crap_list)))

# Create list from label df
umls_label_list = list(umls_df_label)
umls_label_list = [term.split() for term in umls_label_list] # convert each string into a list of the words in the string
umls_label_list = [item for sublist in umls_label_list for item in sublist] # flatten the list of lists into a single list
umls_label_list = [term.split() for term in umls_label_list] # convert each string into a list of the words in the string
umls_label_list = [item for sublist in umls_label_list for item in sublist] # flatten the list of lists into a single list
umls_label_list = [i.lower() for i in umls_label_list]
umls_label_list = [i.replace(' ','') for i in umls_label_list] # last check for spaces
#print(len(set(umls_label_list)))

# Create list from useful df
umls_useful_list = list(umls_df_useful)
umls_useful_list = [term.split() for term in umls_useful_list] # convert each string into a list of the words in the string
umls_useful_list = [item for sublist in umls_useful_list for item in sublist] # flatten the list of lists into a single list
umls_useful_list = [i.lower() for i in umls_useful_list]
umls_useful_list = [i.replace(' ','') for i in umls_useful_list] # last check for spaces
#print [s for s in umls_useful_list if "\\" in s]
#print(len(set(umls_useful_list)))

# Create list from happy df
umls_happy_list = list(umls_df_happy)
umls_happy_list = [term.split() for term in umls_happy_list] # convert each string into a list of the words in the string
umls_happy_list = [item for sublist in umls_happy_list for item in sublist] # flatten the list of lists into a single list
umls_happy_list = [i.lower() for i in umls_happy_list]
umls_happy_list = [i.replace(' ','') for i in umls_happy_list]
#print(len(set(umls_happy_list)))

#  Cancatenate all 4 lists
umls_list = list(set(umls_crap_list + umls_useful_list + umls_happy_list + umls_label_list))
umls_set = set(umls_list)


################################ descriptor_mesh.csv ###############################
# Read in the MeSH set of hierarchically-organized medical terms
des_mesh_df = pd.read_csv('descriptor_mesh.csv', delimiter = ',', usecols=['type','value'])
#print("descriptor_mesh.csv loaded")

# Only take the types of data we're potentially interested in:
# ENTRY = entry term
# MH = mesh heading
# PA = pharmacological action
# MS = mesh scope note
values = ['ENTRY','MH','PA','MS']
des_mesh_df = des_mesh_df.loc[des_mesh_df['type'].isin(values)]

# From the data types that we want, extract the only the initial value of interest
des_mesh_df['descriptor'] = des_mesh_df['value'].str.extract('(.*?)\|', expand = True)
# Drop the old 'value' column
des_mesh_df = des_mesh_df.drop('value', 1)
# Drop blanks
des_mesh_df = des_mesh_df[des_mesh_df.descriptor.notnull()]
# Remove numbers
des_mesh_df['descriptor'] = des_mesh_df['descriptor'].str.replace('\d+', '')
# Remove apostrophes
des_mesh_df['descriptor'] = des_mesh_df['descriptor'].str.replace('(','').str.replace(')','').str.replace('{','').str.replace('}','').str.replace('|',' ').str.replace('\'', '').str.replace('_',' ').str.replace(',',' ').str.replace(':',' ').str.replace(';',' ').str.replace('\\',' ').str.replace('-',' ').str.replace('.','').str.replace('/',' ').str.replace('&', '').str.replace('[','').str.replace(']','').str.replace('?','')  # Edit 1/22/18
# Remove single character words
des_mesh_df['descriptor'] = des_mesh_df['descriptor'].str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ')
# The pattern \b\w\b will replace any single word character with a word boundary
des_mesh_df['descriptor'] = des_mesh_df['descriptor'].str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# Remove rows where length of descriptor is less than 3
des_mesh_df= des_mesh_df[des_mesh_df['descriptor'].str.len() > 2]


# Create list from mesh df
descriptor_mesh_list = list(des_mesh_df['descriptor'])
descriptor_mesh_list = [term.split() for term in descriptor_mesh_list] # convert each string into a list of the words in the string
descriptor_mesh_list = [item for sublist in descriptor_mesh_list for item in sublist] # flatten the list of lists into a single list
descriptor_mesh_list = [i.lower() for i in descriptor_mesh_list] #make lowercase
descriptor_mesh_list = [i.replace(' ','') for i in descriptor_mesh_list] # last check for spaces
des_mesh_set = set(descriptor_mesh_list)


################################ MeshTreeHierarchyWithScopeNotes.csv ###############################
### *** might not actually need this ***
# Read in the mesh terms and their associated scope notes
mesh_heir = pd.read_csv('MeshTreeHierarchyWithScopeNotes.csv',delimiter = ',', usecols=['Term','Ms']) # Term is the branches
#print("MeshTreeHierarchyWithScopeNotes.csv loaded")

# Create term list from mesh term df
mesh_heir_term_list = list(mesh_heir['Term'])
mesh_heir_term_list = [term.split() for term in mesh_heir_term_list] # convert each string into a list of the words in the string
mesh_heir_term_list = [item for sublist in mesh_heir_term_list for item in sublist] # flatten the list of lists into a single list
mesh_heir_term_list = [i.lower() for i in mesh_heir_term_list]

# Get rid of parentheses, braces, pipes and apastrophes
mesh_heir_term_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in mesh_heir_term_list]  # Edit 1/22/18
mesh_heir_term_list = [i.replace(' ','') for i in mesh_heir_term_list] # last check for spaces
mesh_heir_term_set = set(mesh_heir_term_list)

################################## mtrees2017.txt ###############################
# Read in a more full version of the descriptor mesh list
mesh = pd.read_csv('mtrees2017.txt',delimiter = ';') #high level headings
#print("mtrees2017.txt loaded")

# Create list from df
mesh_list = list(mesh['Body Regions'])
mesh_list = [term.split() for term in mesh_list] # convert each string into a list of the words in the string
mesh_list = [item for sublist in mesh_list for item in sublist] # flatten the list of lists into a single list
mesh_list = [i.lower() for i in mesh_list]
# Get rid of parentheses, braces, pipes and apastrophes
mesh_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in mesh_list]  # Edit 1/22/18
mesh_list = [term.split() for term in mesh_list if type(term) is str]
mesh_list = [item for sublist in mesh_list for item in sublist] # flatten
mesh_set = set(mesh_list)


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


mp_set = set()
tree = ET.ElementTree(file='mplus.xml')
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
        #print(row[7])
        try:
            for i in row[7].split(','):
                for j in i.lower().split(' '):
                    snomed_set.add(str(re.sub(r'\.','', j)))
        #firstname_set.add(row[3].lower())
        except:
            print(row)

#print("sno_full.csv loaded")

# Definitions of various disorders and their classifications
with open('tls_full.csv', 'r') as csvfile: # Edit 1/18/17
    tls = csv.reader(csvfile, delimiter=',', quotechar=' ')
    for row in tls:
        #print(row[7])
        try:
            # sctName
            for i in row[6].split(','):
                for j in i.lower().split(' '):
                    snomed_set.add(str(re.sub(r'\.','', j)))
            # icdName
            for i in row[12].split(','):
                for j in i.lower().split(' '):
                    snomed_set.add(str(re.sub(r'\.','', j)))
        #firstname_set.add(row[3].lower())
        except:
            print(row)

#print("tls_full.csv loaded")
# Replace weird characters
snomed_set = set([i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in snomed_set]) # Edit 1/22/18
snomed_set = [term.split() for term in snomed_set if type(term) is str]
snomed_set = set([item for sublist in snomed_set for item in sublist]) # flatten



################################# FDA: list of approved drugs, active ingredients, strengths, form ##################
# go to https://www.fda.gov/Drugs/InformationOnDrugs/ucm079750.htm and download the zip file
# copy "Products.txt" to csv and name "fda_drugs.csv"


fda_drugs_df = pd.read_csv('fda_drugs.csv', delimiter = ',') # Edit 1/22/18
#print("fda_drugs.csv loaded")

####### Form
# Get form column
form_df = fda_drugs_df['Form']
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
strength_df = fda_drugs_df['Strength']
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
drug_df = fda_drugs_df['DrugName']
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
ingredient_df = fda_drugs_df['ActiveIngredient']
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
drug_set = set(form_list + strength_list + ingredient_list)


############################### ICD9 diagnoses ###############################
# List of icd9 diagnoses, already separated by word
# Go to https://www.cms.gov/Medicare/Coding/ICD9ProviderDiagnosticCodes/codes.html and download the Version 32 Full and Abbreviated Code Titles Effective October 1, 2014 [ZIP, 1MB]
# Combine all .txt files and copy to csv, name icd9_diagnoses.csv

# Import dataset
icd9_diagnoses = []

with open('icd9_diagnoses.csv', encoding="latin-1") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        icd9_diagnoses.append(row)

# Get rid of blanks
for i in range(len(icd9_diagnoses)):
    current_sublist = icd9_diagnoses[i]
    new_sublist = [item for item in current_sublist if not item == '']
    icd9_diagnoses[i] = new_sublist

# Flatten and take away characters
icd9_diagnoses = [item for sublist in icd9_diagnoses for item in sublist]
icd9_diagnoses = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in icd9_diagnoses]
icd9_diagnoses = [term.split(" ") for term in icd9_diagnoses]
icd9_diagnoses = [item for sublist in icd9_diagnoses for item in sublist] 
icd9_diagnoses = [i.lower() for i in icd9_diagnoses]

icd9_diagnoses_set = set(icd9_diagnoses)






############ First user input ################
########### My 20k English words ###########


english_words_all = pd.read_csv('20k_english_words.csv',delimiter = ',', encoding="latin-1")

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






# import i2b2 frwquency table data
# unigram_freq_df1 = pd.read_csv('../ucsf_batch102_110_unigram_freq_table.csv', delimiter = ',', encoding="latin-1")

# safe_words1 = []

# for index, row in unigram_freq_df1.iterrows():
#     word = row['unigram']
#     phi_count = row['phi_count']
#     safe_count = row['non-phi_count']
#     if type(word) == str:
#         split_word = [term for term in word.split('.') if term != '']
#         # don't want to keep any numbers
#         if not any(c.isdigit() for c in word):       
#             # we want to keep words that: a) have a PHI count of 0
#             if phi_count == 0:
#                 safe_words1 = safe_words1 + split_word
#             #1-3, or are special words (and, of)
#             elif phi_count == 1 or (word in ['and','of','the','in']):
#                 # have a non-phi count of >1000
#                 if safe_count > 1000:
#                     safe_words1 = safe_words1 + split_word

# import ucsf frwquency table data
# unigram_freq_df2 = pd.read_csv('../ucsf_batch102_110_unigram_freq_table.csv', delimiter = ',', encoding="latin-1")

# safe_words2 = []

# for index, row in unigram_freq_df2.iterrows():
#     word = row['unigram']
#     phi_count = row['phi_count']
#     safe_count = row['non-phi_count']
#     split_word = [term for term in str(word).split('.') if term != '']
#     # don't want to keep any numbers
#     if not any(c.isdigit() for c in str(word)):       
#         # we want to keep words that: a) have a PHI count of 0
#         if phi_count == 0:
#             safe_words2 = safe_words2 + split_word
#         #1-3, or are special words (and, of)
#         elif phi_count == 1 or (word in ['and','of','the','in']):
#             # have a non-phi count of >1000
#             if safe_count > 1000:
#                 safe_words2 = safe_words2 + split_word

# safe_words_set = set(safe_words2)
# unsafe_words_set = set(['acropolis','promptcare','montreal','kekela','christus','alaska','delnor','montefiore','manamana','kekela','cod'])

single_letters = set(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'])

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
ss_firstnames = ss_firstnames_df['name']
list_100_first = list(ss_firstnames)
set_100_first = set([str(i).lower() for i in list_100_first])



######### Census Lastnames #######
# Go to https://www.census.gov/topics/population/genealogy/data/2010_surnames.html
# Download File B: Surnames Occurrign 100 or More Times, name "census_last_names.txt"
census_lastnames_df = pd.read_csv('/Users/kathleenmuenzen/Desktop/whitelists_and_blacklists/white_black_optimization/whitelist_blacklist_files/census_lastnames.csv', delimiter = ',', encoding="latin-1")
census_lastnames = census_lastnames_df['name']
list_100_last = list(census_lastnames)
set_100_last = set([str(i).lower() for i in list_100_last])

all_names_set = set_100_first | set_100_last

whitelist_medical_terms = umls_set | des_mesh_set | mesh_heir_term_set | mesh_set | abbrevs_and_definitions_set | mp_set_normalized | snomed_set | drug_set | icd9_diagnoses_set
#len(whitelist_medical_terms): 233528


intersection_firstnames = set([x for x in set_100_first if x in whitelist_medical_terms]) #len 6220
intersection_lastnames = set([x for x in set_100_last if x in whitelist_medical_terms]) #len 13142
intersection_allnames = set([x for x in all_names_set if x in whitelist_medical_terms]) #len 14882



whitelist_medical_terms_no_names = whitelist_medical_terms - (whitelist_medical_terms&intersection_allnames)
#len(whitelist_medical_terms_no_names): 218646



# How many names are in the common words/verb set?
all_common_words = english_20k_set | verbs_set
intersection_firstnames_common_words = set([x for x in set_100_first if x in all_common_words])
intersection_lastnames_common_words = set([x for x in set_100_last if x in all_common_words])
intersection_allnames_common_words = set([x for x in all_names_set if x in all_common_words])


#######################################################

# Generate whitelist
#whitelist = umls_set | des_mesh_set | mesh_heir_term_set | mesh_set | abbrevs_and_definitions_set | mp_set_normalized | snomed_set | drug_set | icd9_diagnoses_set  
whitelist_add_sub = whitelist_medical_terms_no_names | english_20k_set | verbs_set
# Subtract updated names blacklist from whitelist
#whitelist_add_sub = whitelist_add - (whitelist_add&names_blacklist_set)
# whitelist_add_sub = set([item for item in whitelist_add_sub if not any(c.isdigit() for c in item)]) # get rid of any and all words with digits in the whitelist
#whitelist_add_sub = set([item for item in whitelist_add_sub if not isinstance(item,int)])
whitelist_add_sub = whitelist_add_sub | single_letters

# Make sure there are no numbers in whitelist
whitelist_nodigits = [item for item in whitelist_add_sub if not any(c.isdigit() for c in item)]
# This reduced the length of the whitelist from 236585 to 206666

# Make sure there is no punctuation in whitelist
whitelist_nopunct = [re.split("\s",re.sub(r"[^a-z]", " ", item)) for item in whitelist_nodigits]
whitelist_nopunct_flattened = set([item for sublist in whitelist_nopunct for item in sublist]) 



# original len(whitelist_nopunct_flattened): 196710


whitelist_nonames = whitelist_nopunct_flattened - (whitelist_nopunct_flattened&all_names_set)
# len(whitelist_nonames)
#whitelist_add_sub = whitelist_add_sub | safe_words_set
#whitelist_add_sub = whitelist_add_sub - (whitelist_add_sub&unsafe_words_set)

#print("Final whitelist length:", len(whitelist_add_sub))


# Whitelist with names
whitelist_dictionary = {}
for k in whitelist_nopunct_flattened:
    whitelist_dictionary[k] = 1

with open("whitelist_061418_uncleaned.json",'w') as outfile:
    json.dump(whitelist_dictionary, outfile)


# Whitelist without names
whitelist_dictionary_nonames = {}
for k in whitelist_nonames:
    whitelist_dictionary_nonames[k] = 1

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
    whitelist_dictionary_nonames[k] = 1

with open("whitelist_090618_nonames.json",'w') as outfile:
    json.dump(whitelist_dictionary_nonames, outfile)

len(whitelist_nonames)
# 188473


################### Add FPs back to whitelist ###############
# punctuation_matcher = re.compile(r"[^a-zA-Z0-9*]")

# i2b2_whitelist_noname_fps = pd.read_csv('../../names_removal/i2b2_noname_whitelist_fps.csv')


# # # Edit data frame directly, to retain FP count information
# # for index, row in i2b2_whitelist_noname_fps.iterrows():
# #     current_word = str(row['note_word'])
# #     if any(punctuation_matcher.match(c) for c in current_word[1:-1]) or any(c.isdigit() for c in current_word):
# #         i2b2_whitelist_noname_fps = i2b2_whitelist_noname_fps.drop(int(index))
# #     else:
# #         cleaned_value = re.sub(punctuation_matcher, '', current_word).lower()
# #         i2b2_whitelist_noname_fps['note_word'][int(index)] = cleaned_value





#    # print row['note_word'], row['occurrences']


# fp_list = list(i2b2_whitelist_noname_fps['note_word'])
# # >>> len(fp_list)
# # 9727
# # Clean the list of FPs
# # Remove words with punctuation (except those beginning/ending with a period)
# fp_list = [str(item) for item in fp_list]
# fp_list_nopunct = [item for item in fp_list if not any(punctuation_matcher.match(c) for c in item[1:-1])]
# fp_list_nopunct = [re.sub(punctuation_matcher, '', item) for item in fp_list_nopunct]
# # >>> len(fp_list_nopunct)
# # 8567
# # Remove words with digits
# fp_list_nodigits = [item for item in fp_list_nopunct if not any(c.isdigit() for c in item)]

# # Lowercase all words
# fp_list_cleaned = [item.lower() for item in fp_list_nodigits]
# # >>> len(fp_list_cleaned)
# # 6845


# fp_list_top1 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.01)]
# fp_list_top5 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.05)]
# fp_list_top10 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.1)]
# fp_list_top20 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.2)]
# fp_list_top30 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.3)]
# fp_list_top40 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.4)]
# fp_list_top50 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.5)]
# fp_list_top60 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.6)]
# fp_list_top70 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.7)]
# fp_list_top80 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.8)]
# fp_list_top90 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.9)]
# fp_list_top100 = fp_list_cleaned[0:int(len(fp_list_cleaned))]


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
#     whitelist_addback_1[k] = 1

# whitelist_addback_5 = {}
# for k in whitelist_nonames_addback_5fps:
#     whitelist_addback_5[k] = 1

# whitelist_addback_10 = {}
# for k in whitelist_nonames_addback_10fps:
#     whitelist_addback_10[k] = 1

# whitelist_addback_20 = {}
# for k in whitelist_nonames_addback_20fps:
#     whitelist_addback_20[k] = 1

# whitelist_addback_30 = {}
# for k in whitelist_nonames_addback_30fps:
#     whitelist_addback_30[k] = 1

# whitelist_addback_40 = {}
# for k in whitelist_nonames_addback_40fps:
#     whitelist_addback_40[k] = 1

# whitelist_addback_50 = {}
# for k in whitelist_nonames_addback_50fps:
#     whitelist_addback_50[k] = 1

# whitelist_addback_60 = {}
# for k in whitelist_nonames_addback_60fps:
#     whitelist_addback_60[k] = 1

# whitelist_addback_70 = {}
# for k in whitelist_nonames_addback_70fps:
#     whitelist_addback_70[k] = 1

# whitelist_addback_80 = {}
# for k in whitelist_nonames_addback_80fps:
#     whitelist_addback_80[k] = 1

# whitelist_addback_90 = {}
# for k in whitelist_nonames_addback_90fps:
#     whitelist_addback_90[k] = 1

# whitelist_addback_100 = {}
# for k in whitelist_nonames_addback_100fps:
#     whitelist_addback_100[k] = 1






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
# punctuation_matcher = re.compile(r"[^a-zA-Z0-9*]")




# ucsf_whitelist_noname_fps = pd.read_csv('../../names_removal/ucsf_noname_whitelist_fps.csv')


# # # Edit data frame directly, to retain FP count information
# # for index, row in i2b2_whitelist_noname_fps.iterrows():
# #     current_word = str(row['note_word'])
# #     if any(punctuation_matcher.match(c) for c in current_word[1:-1]) or any(c.isdigit() for c in current_word):
# #         i2b2_whitelist_noname_fps = i2b2_whitelist_noname_fps.drop(int(index))
# #     else:
# #         cleaned_value = re.sub(punctuation_matcher, '', current_word).lower()
# #         i2b2_whitelist_noname_fps['note_word'][int(index)] = cleaned_value





#    # print row['note_word'], row['occurrences']


# fp_list = list(ucsf_whitelist_noname_fps['note_word'])
# # >>> len(fp_list)
# # 8170
# # Clean the list of FPs
# # Remove words with punctuation (except those beginning/ending with a period)
# fp_list = [str(item) for item in fp_list]
# fp_list_nopunct = [item for item in fp_list if not any(punctuation_matcher.match(c) for c in item[1:-1])]
# fp_list_nopunct = [re.sub(punctuation_matcher, '', item) for item in fp_list_nopunct]
# # >>> len(fp_list_nopunct)
# # 8049
# # Remove words with digits
# fp_list_nodigits = [item for item in fp_list_nopunct if not any(c.isdigit() for c in item)]

# # Lowercase all words
# fp_list_cleaned = [item.lower() for item in fp_list_nodigits]
# # >>> len(fp_list_cleaned)
# # 7547


# fp_list_top1 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.01)]
# fp_list_top5 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.05)]
# fp_list_top10 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.1)]
# fp_list_top20 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.2)]
# fp_list_top30 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.3)]
# fp_list_top40 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.4)]
# fp_list_top50 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.5)]
# fp_list_top60 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.6)]
# fp_list_top70 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.7)]
# fp_list_top80 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.8)]
# fp_list_top90 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.9)]
# fp_list_top100 = fp_list_cleaned[0:int(len(fp_list_cleaned))]


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
#     whitelist_addback_1[k] = 1

# whitelist_addback_5 = {}
# for k in whitelist_nonames_addback_5fps:
#     whitelist_addback_5[k] = 1

# whitelist_addback_10 = {}
# for k in whitelist_nonames_addback_10fps:
#     whitelist_addback_10[k] = 1

# whitelist_addback_20 = {}
# for k in whitelist_nonames_addback_20fps:
#     whitelist_addback_20[k] = 1

# whitelist_addback_30 = {}
# for k in whitelist_nonames_addback_30fps:
#     whitelist_addback_30[k] = 1

# whitelist_addback_40 = {}
# for k in whitelist_nonames_addback_40fps:
#     whitelist_addback_40[k] = 1

# whitelist_addback_50 = {}
# for k in whitelist_nonames_addback_50fps:
#     whitelist_addback_50[k] = 1

# whitelist_addback_60 = {}
# for k in whitelist_nonames_addback_60fps:
#     whitelist_addback_60[k] = 1

# whitelist_addback_70 = {}
# for k in whitelist_nonames_addback_70fps:
#     whitelist_addback_70[k] = 1

# whitelist_addback_80 = {}
# for k in whitelist_nonames_addback_80fps:
#     whitelist_addback_80[k] = 1

# whitelist_addback_90 = {}
# for k in whitelist_nonames_addback_90fps:
#     whitelist_addback_90[k] = 1

# whitelist_addback_100 = {}
# for k in whitelist_nonames_addback_100fps:
#     whitelist_addback_100[k] = 1






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
# punctuation_matcher = re.compile(r"[^a-zA-Z0-9*]")




# ucsf_whitelist_noname_fps = pd.read_csv('../../names_removal/ucsf_noname_whitelist_fps.csv')


# # # Edit data frame directly, to retain FP count information
# # for index, row in i2b2_whitelist_noname_fps.iterrows():
# #     current_word = str(row['note_word'])
# #     if any(punctuation_matcher.match(c) for c in current_word[1:-1]) or any(c.isdigit() for c in current_word):
# #         i2b2_whitelist_noname_fps = i2b2_whitelist_noname_fps.drop(int(index))
# #     else:
# #         cleaned_value = re.sub(punctuation_matcher, '', current_word).lower()
# #         i2b2_whitelist_noname_fps['note_word'][int(index)] = cleaned_value





#    # print row['note_word'], row['occurrences']


# fp_list_ucsf = list(ucsf_whitelist_noname_fps['note_word'])
# # Clean the list of FPs
# # Remove words with punctuation (except those beginning/ending with a period)
# fp_list_ucsf = [str(item) for item in fp_list_ucsf]
# fp_list_nopunct_ucsf = [item for item in fp_list_ucsf if not any(punctuation_matcher.match(c) for c in item[1:-1])]
# fp_list_nopunct_ucsf = [re.sub(punctuation_matcher, '', item) for item in fp_list_nopunct_ucsf]
# # Remove words with digits
# fp_list_nodigits_ucsf = [item for item in fp_list_nopunct_ucsf if not any(c.isdigit() for c in item)]

# # Lowercase all words
# fp_list_cleaned_uscf = [item.lower() for item in fp_list_nodigits_ucsf]






# fp_list_i2b2 = list(i2b2_whitelist_noname_fps['note_word'])
# # Clean the list of FPs
# # Remove words with punctuation (except those beginning/ending with a period)
# fp_list_i2b2 = [str(item) for item in fp_list_i2b2]
# fp_list_nopunct_i2b2 = [item for item in fp_list_i2b2 if not any(punctuation_matcher.match(c) for c in item[1:-1])]
# fp_list_nopunct_i2b2 = [re.sub(punctuation_matcher, '', item) for item in fp_list_nopunct_i2b2]
# # Remove words with digits
# fp_list_nodigits_i2b2 = [item for item in fp_list_nopunct_i2b2 if not any(c.isdigit() for c in item)]

# # Lowercase all words
# fp_list_cleaned_i2b2 = [item.lower() for item in fp_list_nodigits_i2b2]


# ### Intersection list
# # len(fp_list_cleaned_uscf): 7547
# # len(fp_list_cleaned_i2b2): 6845
# # Iterate through UCSF Fps list in order to maintain frequency
# fp_list_cleaned = []
# for word in fp_list_cleaned_uscf:
#     if word in fp_list_cleaned_i2b2:
#         fp_list_cleaned.append(word)

# # len(fp_list_cleaned): 4606


# fp_list_top1 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.01)]
# fp_list_top5 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.05)]
# fp_list_top10 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.1)]
# fp_list_top20 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.2)]
# fp_list_top30 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.3)]
# fp_list_top40 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.4)]
# fp_list_top50 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.5)]
# fp_list_top60 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.6)]
# fp_list_top70 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.7)]
# fp_list_top80 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.8)]
# fp_list_top90 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.9)]
# fp_list_top100 = fp_list_cleaned[0:int(len(fp_list_cleaned))]


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
#     whitelist_addback_1[k] = 1

# whitelist_addback_5 = {}
# for k in whitelist_nonames_addback_5fps:
#     whitelist_addback_5[k] = 1

# whitelist_addback_10 = {}
# for k in whitelist_nonames_addback_10fps:
#     whitelist_addback_10[k] = 1

# whitelist_addback_20 = {}
# for k in whitelist_nonames_addback_20fps:
#     whitelist_addback_20[k] = 1

# whitelist_addback_30 = {}
# for k in whitelist_nonames_addback_30fps:
#     whitelist_addback_30[k] = 1

# whitelist_addback_40 = {}
# for k in whitelist_nonames_addback_40fps:
#     whitelist_addback_40[k] = 1

# whitelist_addback_50 = {}
# for k in whitelist_nonames_addback_50fps:
#     whitelist_addback_50[k] = 1

# whitelist_addback_60 = {}
# for k in whitelist_nonames_addback_60fps:
#     whitelist_addback_60[k] = 1

# whitelist_addback_70 = {}
# for k in whitelist_nonames_addback_70fps:
#     whitelist_addback_70[k] = 1

# whitelist_addback_80 = {}
# for k in whitelist_nonames_addback_80fps:
#     whitelist_addback_80[k] = 1

# whitelist_addback_90 = {}
# for k in whitelist_nonames_addback_90fps:
#     whitelist_addback_90[k] = 1

# whitelist_addback_100 = {}
# for k in whitelist_nonames_addback_100fps:
#     whitelist_addback_100[k] = 1






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


# fp_list_ucsf = list(ucsf_whitelist_noname_fps['note_word'])
# fp_list_i2b2 = list(i2b2_whitelist_noname_fps['note_word'])

# fp_list_ucsf_counts = list(ucsf_whitelist_noname_fps['occurrences'])
# fp_list_i2b2_counts = list(i2b2_whitelist_noname_fps['occurrences'])


# # Create list of tuples that contain word/coutn information for ucsf and i2b2 fps

# fp_list_words_counts = []
# for i in range(len(fp_list_ucsf)):
#     word = fp_list_ucsf[i]
#     count = fp_list_ucsf_counts[i]
#     fp_list_words_counts.append((word,count))


# for i in range(len(fp_list_i2b2)):
#     word = fp_list_i2b2[i]
#     count = fp_list_i2b2_counts[i]
#     fp_list_words_counts.append((word,count))


# # Sort by occurrences
# fp_list_words_counts = sorted(fp_list_words_counts, key=lambda x: x[1], reverse =True)

# # Clean each word
# # Remove words with punctuation (except those beginning/ending with a period)
# fp_list_counts = [(str(item[0]),item[1]) for item in fp_list_words_counts]
# fp_list_counts_nopunct = [item for item in fp_list_counts if not any(punctuation_matcher.match(c) for c in item[0][1:-1])]
# fp_list_counts_nopunct = [(re.sub(punctuation_matcher, '', item[0]),item[1]) for item in fp_list_counts_nopunct]
# # Remove words with digits
# fp_list_counts_nodigits = [item for item in fp_list_counts_nopunct if not any(c.isdigit() for c in item[0])]

# # Lowercase all words
# fp_list_counts_nodigits_cleaned = [(item[0].lower(),item[1]) for item in fp_list_counts_nodigits]

# # get rid of duplicates, separate lists
# fp_list_cleaned = []

# for tup in fp_list_counts_nodigits_cleaned:
#     if tup[0] not in fp_list_cleaned:
#         fp_list_cleaned.append(tup[0])


# # len(fp_list_cleaned): 6229


# fp_list_top1 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.01)]
# fp_list_top5 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.05)]
# fp_list_top10 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.1)]
# fp_list_top20 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.2)]
# fp_list_top30 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.3)]
# fp_list_top40 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.4)]
# fp_list_top50 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.5)]
# fp_list_top60 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.6)]
# fp_list_top70 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.7)]
# fp_list_top80 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.8)]
# fp_list_top90 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.9)]
# fp_list_top100 = fp_list_cleaned[0:int(len(fp_list_cleaned))]


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
#     whitelist_addback_1[k] = 1

# whitelist_addback_5 = {}
# for k in whitelist_nonames_addback_5fps:
#     whitelist_addback_5[k] = 1

# whitelist_addback_10 = {}
# for k in whitelist_nonames_addback_10fps:
#     whitelist_addback_10[k] = 1

# whitelist_addback_20 = {}
# for k in whitelist_nonames_addback_20fps:
#     whitelist_addback_20[k] = 1

# whitelist_addback_30 = {}
# for k in whitelist_nonames_addback_30fps:
#     whitelist_addback_30[k] = 1

# whitelist_addback_40 = {}
# for k in whitelist_nonames_addback_40fps:
#     whitelist_addback_40[k] = 1

# whitelist_addback_50 = {}
# for k in whitelist_nonames_addback_50fps:
#     whitelist_addback_50[k] = 1

# whitelist_addback_60 = {}
# for k in whitelist_nonames_addback_60fps:
#     whitelist_addback_60[k] = 1

# whitelist_addback_70 = {}
# for k in whitelist_nonames_addback_70fps:
#     whitelist_addback_70[k] = 1

# whitelist_addback_80 = {}
# for k in whitelist_nonames_addback_80fps:
#     whitelist_addback_80[k] = 1

# whitelist_addback_90 = {}
# for k in whitelist_nonames_addback_90fps:
#     whitelist_addback_90[k] = 1

# whitelist_addback_100 = {}
# for k in whitelist_nonames_addback_100fps:
#     whitelist_addback_100[k] = 1






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


fp_list_ucsf = list(ucsf_whitelist_noname_fps_noperiods['note_word'])
fp_list_i2b2 = list(i2b2_whitelist_noname_fps_noperiods['note_word'])

fp_list_ucsf_counts = list(ucsf_whitelist_noname_fps_noperiods['occurrences'])
fp_list_i2b2_counts = list(i2b2_whitelist_noname_fps_noperiods['occurrences'])


# Create list of tuples that contain word/coutn information for ucsf and i2b2 fps

fp_list_words_counts = []
for i in range(len(fp_list_ucsf)):
    word = fp_list_ucsf[i]
    count = fp_list_ucsf_counts[i]
    fp_list_words_counts.append((word,count))


for i in range(len(fp_list_i2b2)):
    word = fp_list_i2b2[i]
    count = fp_list_i2b2_counts[i]
    fp_list_words_counts.append((word,count))


# Sort by occurrences
fp_list_words_counts = sorted(fp_list_words_counts, key=lambda x: x[1], reverse =True)

# Clean each word
# Remove words with punctuation (except those beginning/ending with a period)
fp_list_counts = [(str(item[0]),item[1]) for item in fp_list_words_counts]
# fp_list_counts_nopunct = [item for item in fp_list_counts if not any(punctuation_matcher.match(c) for c in item[0][1:-1])]
# fp_list_counts_nopunct = [(re.sub(punctuation_matcher, '', item[0]),item[1]) for item in fp_list_counts_nopunct]
# Remove words with digits
# fp_list_counts_nodigits = [item for item in fp_list_counts_nopunct if not any(c.isdigit() for c in item[0])]
fp_list_counts_nodigits = [item for item in fp_list_counts if not item[0].isdigit()]


# Lowercase all words
fp_list_counts_nodigits_cleaned = [(item[0].lower(),item[1]) for item in fp_list_counts_nodigits]

# get rid of duplicates, separate lists
fp_list_cleaned = []

for tup in fp_list_counts_nodigits_cleaned:
    if tup[0] not in fp_list_cleaned:
        fp_list_cleaned.append(tup[0])


# # len(fp_list_cleaned): 6229


# fp_list_top1 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.01)]
# fp_list_top5 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.05)]
# fp_list_top10 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.1)]
# fp_list_top20 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.2)]
# fp_list_top30 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.3)]
# fp_list_top40 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.4)]
# fp_list_top50 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.5)]
# fp_list_top60 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.6)]
# fp_list_top70 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.7)]
# fp_list_top80 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.8)]
# fp_list_top90 = fp_list_cleaned[0:int(len(fp_list_cleaned)*0.9)]
fp_list_top100 = fp_list_cleaned[0:int(len(fp_list_cleaned))]


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
#     whitelist_addback_1[k] = 1

# whitelist_addback_5 = {}
# for k in whitelist_nonames_addback_5fps:
#     whitelist_addback_5[k] = 1

# whitelist_addback_10 = {}
# for k in whitelist_nonames_addback_10fps:
#     whitelist_addback_10[k] = 1

# whitelist_addback_20 = {}
# for k in whitelist_nonames_addback_20fps:
#     whitelist_addback_20[k] = 1

# whitelist_addback_30 = {}
# for k in whitelist_nonames_addback_30fps:
#     whitelist_addback_30[k] = 1

# whitelist_addback_40 = {}
# for k in whitelist_nonames_addback_40fps:
#     whitelist_addback_40[k] = 1

# whitelist_addback_50 = {}
# for k in whitelist_nonames_addback_50fps:
#     whitelist_addback_50[k] = 1

# whitelist_addback_60 = {}
# for k in whitelist_nonames_addback_60fps:
#     whitelist_addback_60[k] = 1

# whitelist_addback_70 = {}
# for k in whitelist_nonames_addback_70fps:
#     whitelist_addback_70[k] = 1

# whitelist_addback_80 = {}
# for k in whitelist_nonames_addback_80fps:
#     whitelist_addback_80[k] = 1

# whitelist_addback_90 = {}
# for k in whitelist_nonames_addback_90fps:
#     whitelist_addback_90[k] = 1

whitelist_addback_100 = {}
for k in whitelist_nonames_addback_100fps:
    whitelist_addback_100[k] = 1






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

disease_names = list(disease_names_df['name'])

disease_names = set([item.lower()for item in disease_names])


overlap = []
non_overlap = []
for word in disease_names:
    if word in whitelist_addback_100:
        overlap.append(word)
    else:
        non_overlap.append(word)

new_whitelist = whitelist_nonames_addback_100fps - (whitelist_nonames_addback_100fps&set(overlap))


whitelist_addback_100_no_eponyms = {}
for k in new_whitelist:
    whitelist_addback_100_no_eponyms[k] = 1

with open("whitelist_090618_nonames_addback100_ucsf_u_i2b2_noperiods_noeponyms.json",'w') as outfile:
    json.dump(whitelist_addback_100_no_eponyms, outfile)


# Words to add back
common_words = set(['may','day','hand','down','still','brown','white','tan','de'])


new_whitelist_with_common_words = new_whitelist | common_words
    


whitelist_addback_100_no_eponyms_common = {}
for k in new_whitelist_with_common_words:
    whitelist_addback_100_no_eponyms_common[k] = 1

with open("whitelist_090618_nonames_addback100_ucsf_u_i2b2_noperiods_noeponyms_commonwords.json",'w') as outfile:
    json.dump(whitelist_addback_100_no_eponyms_common, outfile)



############ Observe overlap between FP union list and names (from union FPS) ######
fp_firstnames_overlap = set([x for x in fp_list_cleaned if x in set_100_first]) 
fp_lastnames_overlap = set([x for x in fp_list_cleaned if x in set_100_last]) 
fp_names_overlap = set([x for x in fp_list_cleaned if x in all_names_set]) 


len(fp_names_overlap) #2816
for name in fp_names_overlap:
    print(name)

clear_names = set(['thiet','jane','sam','hodgkin','abraham','christian','hawkins','rutherford','epstein','hodgkins','bruce','smith','crohn','carol','huntington','parkinson','jackson','hartmann','madison','helen','hashimoto','fischer','patrick','sjogren','richard','wilson','tristan','connie','judah','babinski','mallory','allen','john','brad','hickman','chad','ron','michael'])
# 37 names (including eponyms)



new_whitelist_with_common_words_nonames = new_whitelist_with_common_words - (new_whitelist_with_common_words&clear_names)
# 27 names subtracted


whitelist_addback_100_no_eponyms_common_nonames = {}
for k in new_whitelist_with_common_words_nonames:
    whitelist_addback_100_no_eponyms_common_nonames[k] = 1

with open("whitelist_090618_nonames_addback100_ucsf_u_i2b2_noperiods_noeponyms_commonwords_nonames.json",'w') as outfile:
    json.dump(whitelist_addback_100_no_eponyms_common_nonames, outfile)



##### Gte full list of fps
full_fps_list = set(fp_list_top100) - (set(fp_list_top100)&disease_names) - (set(fp_list_top100)&clear_names)










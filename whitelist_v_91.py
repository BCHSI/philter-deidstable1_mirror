import pandas as pd
import pickle
import csv
import xml.etree.ElementTree as ET
import re
import string # Edit 1/18/18
import unicodedata # Edit 1/22/18
import csv


# Will be used to check whether there are common names in whitelist
name_debug_word = 'bailey' # Edit 1/18/18
cap_debug_word = "Tylenol" # Edit 1/18/18



############################### umls_LEXICON.csv ###############################
# Read in the NLM Lexicon containing common English words and medical terms
umls_df = pd.read_csv('umls_LEXICON.csv', delimiter = ',', encoding="latin-1") # Edit 1/22/18
print("umls_LEXICON.csv loaded")

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

"""
print [s for s in umls_list if "," in s]
print [s for s in umls_list if ":" in s]
print [s for s in umls_list if ";" in s]
print [s for s in umls_list if "\\" in s]
print [s for s in umls_list if "_" in s]
print [s for s in umls_list if "'" in s]
print [s for s in umls_list if "(" in s]
print [s for s in umls_list if ")" in s]
print [s for s in umls_list if "{" in s]
print [s for s in umls_list if "}" in s]
print [s for s in umls_list if "." in s]
print [s for s in umls_list if "|" in s]
print [s for s in umls_list if "/" in s]
print [s for s in umls_list if "&" in s]
print [s for s in umls_list if "[" in s]
print [s for s in umls_list if "]" in s]
print [s for s in umls_list if "?" in s]

"""


################################ descriptor_mesh.csv ###############################
# Read in the MeSH set of hierarchically-organized medical terms
des_mesh_df = pd.read_csv('descriptor_mesh.csv', delimiter = ',', usecols=['type','value'])
print("descriptor_mesh.csv loaded")

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

"""
print [s for s in descriptor_mesh_list if "," in s]
print [s for s in descriptor_mesh_list if ":" in s]
print [s for s in descriptor_mesh_list if ";" in s]
print [s for s in descriptor_mesh_list if "\\" in s]
print [s for s in descriptor_mesh_list if "_" in s]
print [s for s in descriptor_mesh_list if "'" in s]
print [s for s in descriptor_mesh_list if "(" in s]
print [s for s in descriptor_mesh_list if ")" in s]
print [s for s in descriptor_mesh_list if "{" in s]
print [s for s in descriptor_mesh_list if "}" in s]
print [s for s in descriptor_mesh_list if "." in s]
print [s for s in descriptor_mesh_list if "|" in s]
print [s for s in descriptor_mesh_list if "/" in s]
print [s for s in descriptor_mesh_list if "&" in s]
print [s for s in descriptor_mesh_list if "[" in s]
print [s for s in descriptor_mesh_list if "]" in s]
print [s for s in descriptor_mesh_list if "?" in s]
"""

################################ MeshTreeHierarchyWithScopeNotes.csv ###############################
### *** might not actually need this ***
# Read in the mesh terms and their associated scope notes
mesh_heir = pd.read_csv('MeshTreeHierarchyWithScopeNotes.csv',delimiter = ',', usecols=['Term','Ms']) # Term is the branches
print("MeshTreeHierarchyWithScopeNotes.csv loaded")

# Create term list from mesh term df
mesh_heir_term_list = list(mesh_heir['Term'])
mesh_heir_term_list = [term.split() for term in mesh_heir_term_list] # convert each string into a list of the words in the string
mesh_heir_term_list = [item for sublist in mesh_heir_term_list for item in sublist] # flatten the list of lists into a single list
mesh_heir_term_list = [i.lower() for i in mesh_heir_term_list]

# Get rid of parentheses, braces, pipes and apastrophes
mesh_heir_term_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in mesh_heir_term_list]  # Edit 1/22/18
mesh_heir_term_list = [i.replace(' ','') for i in mesh_heir_term_list] # last check for spaces

"""
print [s for s in mesh_heir_term_list if "," in s]
print [s for s in mesh_heir_term_list if ":" in s]
print [s for s in mesh_heir_term_list if ";" in s]
print [s for s in mesh_heir_term_list if "\\" in s]
print [s for s in mesh_heir_term_list if "_" in s]
print [s for s in mesh_heir_term_list if "'" in s]
print [s for s in mesh_heir_term_list if "(" in s]
print [s for s in mesh_heir_term_list if ")" in s]
print [s for s in mesh_heir_term_list if "{" in s]
print [s for s in mesh_heir_term_list if "}" in s]
print [s for s in mesh_heir_term_list if "." in s]
print [s for s in mesh_heir_term_list if "|" in s]
print [s for s in mesh_heir_term_list if "/" in s]
print [s for s in mesh_heir_term_list if "&" in s]
print [s for s in mesh_heir_term_list if "[" in s]
print [s for s in mesh_heir_term_list if "]" in s]
print [s for s in mesh_heir_term_list if "?" in s]
"""

# Create ms list from mesh term df
mesh_heir_ms_list = list(mesh_heir['Ms'])
mesh_heir_ms_list = [term.split() for term in mesh_heir_ms_list if type(term) is str] # convert each string into a list of the words in the string
mesh_heir_ms_list = [item for sublist in mesh_heir_ms_list for item in sublist] # flatten the list of lists into a single list
mesh_heir_ms_list = [i.lower() for i in mesh_heir_ms_list]



################################ 20kwords.csv ###############################
# Read in set of 20,000 most common English words
english_goog = pd.read_csv('20kwords.csv',delimiter = ',') # from https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt
print("20kwords.csv loaded")

# Create list from df
english_goog = list(english_goog.word) # Edit 1/18/18
english_goog = [str(i) for i in english_goog]
english_goog = set([i.lower() for i in english_goog])
# Edit 1/18/18
# Rremove single character words
english_goog_list = [i.replace(r'\b\w\b', '').replace(r'\s+', ' ') for i in english_goog]
#print(len(english_goog_list))

"""
print [s for s in english_goog_list if "," in s]
print [s for s in english_goog_list if ":" in s]
print [s for s in english_goog_list if ";" in s]
print [s for s in english_goog_list if "\\" in s]
print [s for s in english_goog_list if "_" in s]
print [s for s in english_goog_list if "'" in s]
print [s for s in english_goog_list if "(" in s]
print [s for s in english_goog_list if ")" in s]
print [s for s in english_goog_list if "{" in s]
print [s for s in english_goog_list if "}" in s]
print [s for s in english_goog_list if "." in s]
print [s for s in english_goog_list if "|" in s]
print [s for s in english_goog_list if "/" in s]
print [s for s in english_goog_list if "&" in s]
print [s for s in english_goog_list if "[" in s]
print [s for s in english_goog_list if "]" in s]
print [s for s in english_goog_list if "?" in s]
"""

################################ 1k_words_noNames.csv ###############################
# 1000 most common English words
english_1k = pd.read_csv('1k_words_noNames.csv',delimiter = ',')
print("1k_words_noNames.csv loaded")
english_1k = list(english_1k.word)
english_1k = [i.lower() for i in english_1k]
english_1k = [i.replace(r'\b\w\b', '').replace(r'\s+', ' ').replace('\'','') for i in english_1k]  # Edit 1/22/18
#print(len(english_1k))

"""
print [s for s in english_1k if "," in s]
print [s for s in english_1k if ":" in s]
print [s for s in english_1k if ";" in s]
print [s for s in english_1k if "\\" in s]
print [s for s in english_1k if "_" in s]
print [s for s in english_1k if "'" in s]
print [s for s in english_1k if "(" in s]
print [s for s in english_1k if ")" in s]
print [s for s in english_1k if "{" in s]
print [s for s in english_1k if "}" in s]
print [s for s in english_1k if "." in s]
print [s for s in english_1k if "|" in s]
print [s for s in english_1k if "/" in s]
print [s for s in english_1k if "&" in s]
print [s for s in english_1k if "[" in s]
print [s for s in english_1k if "]" in s]
print [s for s in english_1k if "?" in s]

"""

################################ 3k_words_noNames.csv ###############################
# 3000 most common English words
english_3k = pd.read_csv('3k_words_noNames.csv',delimiter = ',')
print("3k_words_noNames.csv loaded")
english_3k = list(english_3k.word)
english_3k = [i.lower() for i in english_3k]
english_3k = [i.replace(r'\b\w\b', '').replace(r'\s+', ' ').replace('\'','') for i in english_3k]  # Edit 1/22/18
#print(len(english_3k))

"""
print [s for s in english_3k if "," in s]
print [s for s in english_3k if ":" in s]
print [s for s in english_3k if ";" in s]
print [s for s in english_3k if "\\" in s]
print [s for s in english_3k if "_" in s]
print [s for s in english_3k if "'" in s]
print [s for s in english_3k if "(" in s]
print [s for s in english_3k if ")" in s]
print [s for s in english_3k if "{" in s]
print [s for s in english_3k if "}" in s]
print [s for s in english_3k if "." in s]
print [s for s in english_3k if "|" in s]
print [s for s in english_3k if "." in s]
print [s for s in english_3k if "/" in s]
print [s for s in english_3k if "&" in s]
print [s for s in english_3k if "[" in s]
print [s for s in english_3k if "]" in s]
print [s for s in english_3k if "?" in s]
"""


# Concatenate the 1k, 3k and 20k lists
common_english_list = list(set(english_goog_list + english_1k + english_3k))
#print(len(common_english_list))


################################## list_of_med_abbreviations.csv ###############################
# Read in list of common medical abbreviations
abbreviations = pd.read_csv('list_of_med_abbreviations.csv', delimiter = ',')
print("list_of_med_abbreviations.csv loaded")

# Create list from df
abbrev_list = list(abbreviations.abbreviation)
abbrev_list = [i for i in abbrev_list if type(i) is str]
abbrev_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|','').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in abbrev_list]
abbrev_list = [i.lower() for i in abbrev_list]
abbrev_list = [term.split() for term in abbrev_list if type(term) is str]
abbrev_list = [item for sublist in abbrev_list for item in sublist] # flatten


################################## mtrees2017.txt ###############################
# Read in a more full version of the descriptor mesh list
mesh = pd.read_csv('mtrees2017.txt',delimiter = ';') #high level headings
print("mtrees2017.txt loaded")

# Create list from df
mesh_list = list(mesh['Body Regions'])
mesh_list = [term.split() for term in mesh_list] # convert each string into a list of the words in the string
mesh_list = [item for sublist in mesh_list for item in sublist] # flatten the list of lists into a single list
mesh_list = [i.lower() for i in mesh_list]
# Get rid of parentheses, braces, pipes and apastrophes
mesh_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in mesh_list]  # Edit 1/22/18
mesh_list = [term.split() for term in mesh_list if type(term) is str]
mesh_list = [item for sublist in mesh_list for item in sublist] # flatten


"""
print [s for s in mesh_list if "," in s]
print [s for s in mesh_list if ":" in s]
print [s for s in mesh_list if ";" in s]
print [s for s in mesh_list if "\\" in s]
print [s for s in mesh_list if "_" in s]
print [s for s in mesh_list if "'" in s]
print [s for s in mesh_list if "(" in s]
print [s for s in mesh_list if ")" in s]
print [s for s in mesh_list if "{" in s]
print [s for s in mesh_list if "}" in s]
print [s for s in mesh_list if "." in s]
print [s for s in mesh_list if "|" in s]
print [s for s in mesh_list if "." in s]
print [s for s in mesh_list if "/" in s]
print [s for s in mesh_list if "&" in s]
print [s for s in mesh_list if "[" in s]
print [s for s in mesh_list if "]" in s]
print [s for s in mesh_list if "?" in s]
"""
############################## Medline Plus ############################
# download MedlinePlus Health Topic XML from https://medlineplus.gov/xml.html
# then change the file name to "mplus.xml"
# This also contains medical terms in other languages!

 # Edit 1/22/18:
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


mp_set = set()
tree = ET.ElementTree(file='mplus.xml')
print("mplus.xml loaded")

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

"""
print [s for s in mp_set_normalized if "," in s]
print [s for s in mp_set_normalized if ":" in s]
print [s for s in mp_set_normalized if ";" in s]
print [s for s in mp_set_normalized if "\\" in s]
print [s for s in mp_set_normalized if "_" in s]
print [s for s in mp_set_normalized if "'" in s]
print [s for s in mp_set_normalized if "(" in s]
print [s for s in mp_set_normalized if ")" in s]
print [s for s in mp_set_normalized if "{" in s]
print [s for s in mp_set_normalized if "}" in s]
print [s for s in mp_set_normalized if "." in s]
print [s for s in mp_set_normalized if "|" in s]
print [s for s in mp_set_normalized if "." in s]
print [s for s in mp_set_normalized if "/" in s]
print [s for s in mp_set_normalized if "&" in s]
print [s for s in mp_set_normalized if "[" in s]
print [s for s in mp_set_normalized if "]" in s]
print [s for s in mp_set_normalized if "?" in s]

"""

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

print("sno_full.csv loaded")

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

print("tls_full.csv loaded")
# Replace weird characters
snomed_set = set([i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in snomed_set]) # Edit 1/22/18
snomed_set = [term.split() for term in snomed_set if type(term) is str]
snomed_set = set([item for sublist in snomed_set for item in sublist]) # flatten

"""
print [s for s in snomed_set if "," in s]
print [s for s in snomed_set if ":" in s]
print [s for s in snomed_set if ";" in s]
print [s for s in snomed_set if "\\" in s]
print [s for s in snomed_set if "_" in s]
print [s for s in snomed_set if "'" in s]
print [s for s in snomed_set if "(" in s]
print [s for s in snomed_set if ")" in s]
print [s for s in snomed_set if "{" in s]
print [s for s in snomed_set if "}" in s]
print [s for s in snomed_set if "." in s]
print [s for s in snomed_set if "|" in s]
print [s for s in snomed_set if "." in s]
print [s for s in snomed_set if "/" in s]
print [s for s in snomed_set if "&" in s]
print [s for s in snomed_set if "[" in s]
print [s for s in snomed_set if "]" in s]
print [s for s in snomed_set if "?" in s]
"""

################################# ICD9 and ICD10 #####################
# Set of icd9 and icd10 diagnostic codes

pattern_word = re.compile(r"[^\w+]")

icd9_code = []
with open('ICD9_Code.csv', 'r') as csvfile:
    icd9 = csv.reader(csvfile, delimiter=',', quotechar=' ')
    for row in icd9:
        icd9_code.append(str(pattern_word.sub('', row[0])).lower())


#  Remove header and blanks
icd9_code.remove('icd9_code')
icd9_code.remove('null')
icd9_code = set(icd9_code)

icd10_code = []
with open('ICD10_Code.csv', 'r') as csvfile:
    icd10 = csv.reader(csvfile, delimiter=',', quotechar=' ')
    for row in icd10:
        icd10_code.append(str(pattern_word.sub('', row[0])).lower())





icd10_code.remove('icd10_code')
icd10_code.remove('null')
icd10_code = set(icd10_code)

print("ICD9_Code.csv and ICD10_Code.csv loaded")



################ Pysionet Rescources ########
# From https://www.physionet.org/physiotools/deid/
################################# Physionet: common_words.txt ################
# Read in list of ~50,000 common words from Physionet
with open('common_words.txt', 'r') as f:
    physio_common_words = f.readlines()



print("common_words.txt loaded")
# Create list from each line of the text file
physio_common_words = [x.strip() for x in physio_common_words]
# Get rid of apostrophes and remove duplicates
physio_common_words = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in physio_common_words]
physio_common_words = [i.lower() for i in physio_common_words]
physio_common_words = [term.split() for term in physio_common_words if type(term) is str]
physio_common_words = [item for sublist in physio_common_words for item in sublist] # flatten

################################# Physionet: commonest_words.txt ################
# Read in list of ~5,000 commonest words from Physionet
with open('commonest_words.txt', 'r') as f:
    physio_commonest_words = f.readlines()




print("commonest_words.txt loaded")
# Create list from each line of the text file
physio_commonest_words = [x.strip() for x in physio_commonest_words]
# Get rid of apostrophes and remove duplicates
physio_commonest_words = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|','').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in physio_commonest_words]
physio_commonest_words = [i.lower() for i in physio_commonest_words]
physio_commonest_words = [term.split() for term in physio_commonest_words if type(term) is str]
physio_commonest_words = [item for sublist in physio_commonest_words for item in sublist] # flatten

################################# Physionet: notes_common.txt ##################
# Read in list of common words in nursing notes
with open('notes_common.txt', 'r') as f:
    physio_notes_common = f.readlines()




print("notes_common.txt loaded")
# Create list from each line of the text file
physio_notes_common = [x.strip() for x in physio_notes_common]
# Get rid of apostrophes and remove duplicates
physio_notes_common = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in physio_notes_common]
physio_notes_common = [i.lower() for i in physio_notes_common]
physio_notes_common = [term.split() for term in physio_notes_common if type(term) is str]
physio_notes_common = [item for sublist in physio_notes_common for item in sublist] # flatten

################################ Physionet: sno_edited.txt ######################
# Read in list of words from SNOMED
with open('sno_edited.txt', 'r') as f:
    sno_edited_notes = f.readlines()




print("sno_edited.txt loaded")
# Create list from each line of the text file
sno_edited_notes = [x.strip() for x in sno_edited_notes]
# Get rid of apostrophes and remove duplicates
sno_edited_notes = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in sno_edited_notes]
sno_edited_notes = [i.lower() for i in sno_edited_notes]
sno_edited_notes = [term.split() for term in sno_edited_notes if type(term) is str]
sno_edited_notes = [item for sublist in sno_edited_notes for item in sublist] # flatten

################################ Physionet: medical_phrases.txt ######################
# Read in list of words from SNOMED
with open('medical_phrases.txt', 'r') as f:
    medical_phrases = f.readlines()




print("medical_phrases.txt loaded")
# Create list from each line of the text file
medical_phrases = [x.strip() for x in medical_phrases]
# Get rid of apostrophes and remove duplicates
medical_phrases = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in medical_phrases]
medical_phrases = [term.split(" ") for term in medical_phrases] # convert each string into a list of the words in the string
medical_phrases = [item for sublist in medical_phrases for item in sublist] 
medical_phrases = [i.lower() for i in medical_phrases]


################################# FDA: list of approved drugs, active ingredients, strengths, form ##################
# go to https://www.fda.gov/Drugs/InformationOnDrugs/ucm079750.htm and download the zip file
# copy "Products.txt" to csv and name "fda_drugs.csv"


fda_drugs_df = pd.read_csv('fda_drugs.csv', delimiter = ',') # Edit 1/22/18
print("fda_drugs.csv loaded")

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



########################## More common words #####################

### Verbs
# Go to https://www.worldclasslearning.com/english/five-verb-forms.html
# Copy all contents to csv and name "1k_verbs.csv"

thousand_verbs_df = pd.read_csv('1k_verbs.csv', delimiter = ',', encoding="latin-1")
thousand_verbs = list(thousand_verbs_df['base']) + list(thousand_verbs_df['past']) + list(thousand_verbs_df['past_participle']) + list(thousand_verbs_df['present']) + list(thousand_verbs_df['present_participle'])
thousand_verbs_set = set([i.lower() for i in thousand_verbs])

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

abbrevs_and_definitions_set = set(abbreviations_list + definitions_list)

################################# Names ########################################

################## Edit 1/22/18 ###############
######### Lastnames #######
# Go to https://www.census.gov/topics/population/genealogy/data/2010_surnames.html
# Download File B: Surnames Occurrign 100 or More Times, name "census_last_names.txt"
with open('census_last_names.txt', 'rU') as f:
    census_lastnames = f.readlines()


#
census_lastnames = [x.strip() for x in census_lastnames]
census_lastnames = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in census_lastnames]
census_lastnames = [term.split(" ") for term in census_lastnames]
census_lastnames = [item for sublist in census_lastnames for item in sublist] 
census_lastnames = [i.lower() for i in census_lastnames]
census_lastnames_set = set(census_lastnames)


######### Census Firstnames #######
# Copy text file from http://deron.meranda.us/data/census-derived-all-first.txt to csv
# Name "census_first_names.txt"
with open('census_first_names.txt', 'rU') as f:
    census_firstnames = f.readlines()



census_firstnames = [x.strip() for x in census_firstnames]
census_firstnames = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in census_firstnames]
census_firstnames = [term.split(" ") for term in census_firstnames]
census_firstnames = [item for sublist in census_firstnames for item in sublist] 
census_firstnames = [i.lower() for i in census_firstnames]
census_firstnames_set = set(census_firstnames)


######### Social Security Firstnames ######
# Go to https://www.ssa.gov/oact/babynames/limits.html and download all 3 data files
# Concatenate all text files, copy to csv and name "ss_firstnames.csv"

ss_firstnames_df = pd.read_csv('ss_firstnames.csv', delimiter = ',')
ss_firstnames = ss_firstnames_df['name']
ss_firstnames = list(ss_firstnames)
ss_firstnames = [str(i) for i in ss_firstnames]
ss_firstnames_set = set([i.lower() for i in ss_firstnames])



########## Prefixes #######
# Downloaded from Physionet resources
with open('prefixes.txt', 'r') as f:
    prefixes = f.readlines()



prefixes = [x.strip() for x in prefixes]
prefixes = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in prefixes]
prefixes = [term.split(" ") for term in prefixes] # convert each string into a list of the words in the string
prefixes = [item for sublist in prefixes for item in sublist] 
prefixes = [i.lower() for i in prefixes]
prefix_set = set(prefixes)

print("all name files loaded")

"""
###### 1. Separate ambiguous names and unambiguous names ######
ambiguous_names_set = census_firstnames_set | ss_firstnames_set | census_lastnames_set

###### 2. Cut out 1,000 most common words #######
ambiguous_names_set = set([item for item in ambiguous_names_set if not item in english_1k])

###### 3. Add in unambiguous names and prefixes #####
name_set = ambiguous_names_set | prefix_set
"""

name_set = census_firstnames_set | ss_firstnames_set | census_lastnames_set | prefix_set

################################# Locations #########################

# ******** Edit 1/23/18 ********
# Import address data
# Download zip files for the US northeast, midwest, south and west from http://results.openaddresses.io
# Decompress the zip files, and combine (by region) all *.csv files from us/


# Northeast states addresses
northeast_street_names = []

with open('northeast_combined.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        northeast_street_names.append(row[3])

# Split, flatten, etc.
northeast_street_names = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in northeast_street_names]
northeast_street_names = [term.split(" ") for term in northeast_street_names] # takes a long time
northeast_street_names = [item for sublist in northeast_street_names for item in sublist] # takes a long time
northeast_street_names = [i.lower() for i in northeast_street_names]
northeast_street_names_set = set(northeast_street_names)

print("northeast street names complete")

# Midwest states addresses
midwest_street_names = []

with open('midwest_combined.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        midwest_street_names.append(row[3])

# Split, flatten, etc.
midwest_street_names = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in midwest_street_names]
midwest_street_names = [term.split(" ") for term in midwest_street_names] # takes a long time
midwest_street_names = [item for sublist in midwest_street_names for item in sublist] # takes a long time
midwest_street_names = [i.lower() for i in midwest_street_names]
midwest_street_names_set = set(midwest_street_names)

print("midwest street names complete")

# South street addresses
south_street_names = []

with open('south_combined.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        south_street_names.append(row[3])

# Split, flatten, etc.
south_street_names = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in south_street_names]
south_street_names = [term.split(" ") for term in south_street_names] # takes a long time
south_street_names = [item for sublist in south_street_names for item in sublist] # takes a long time
south_street_names = [i.lower() for i in south_street_names]
south_street_names_set = set(south_street_names)

print("south street names complete")

# West street addresses
west_street_names = []

with open('west_combined.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        west_street_names.append(row[3])

# Split, flatten, etc.
west_street_names = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in west_street_names]
west_street_names = [term.split(" ") for term in west_street_names] # takes a long time
west_street_names = [item for sublist in west_street_names for item in sublist] # takes a long time
west_street_names = [i.lower() for i in west_street_names]
west_street_names_set = set(west_street_names)

print("west street names complete")

# Import city and county data
# Go to https://simplemaps.com/static/data/us-cities/uscitiesv1.3.csv
# Copy to csv, save as cities_and_counties.csv

city_county_state_df = pd.read_csv('cities_counties_states.csv', delimiter = ',', encoding="latin-1")
print("cities_counties_states.csv loaded")

# Extract cities column
city_df = city_county_state_df['city_ascii']
# Remove blanks
city_df = city_df[city_df.notnull()]
# Create list from city df and split
city_df_list = list(city_df)
city_df_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in city_df_list]
city_df_list = [term.split() for term in city_df_list] # convert each string into a list of the words in the string
city_df_list = [item for sublist in city_df_list for item in sublist] # flatten the list of lists into a single list
city_df_list = [i.lower() for i in city_df_list] # make lowercase
city_set = set(city_df_list)

# Extract counties column
county_df = city_county_state_df['county_name']
# Remove blanks
county_df = county_df[county_df.notnull()]
# Create list from city df and split
county_df_list = list(county_df)
county_df_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in county_df_list]
county_df_list = [term.split() for term in county_df_list] # convert each string into a list of the words in the string
county_df_list = [item for sublist in county_df_list for item in sublist] # flatten the list of lists into a single list
county_df_list = [i.lower() for i in county_df_list] # make lowercase
county_set = set(county_df_list)


# Extract states column
state_df = city_county_state_df['state_name']
# Remove blanks
state_df = state_df[state_df.notnull()]
# Create list from city df and split
state_df_list = list(state_df)
state_df_list = [term.split() for term in state_df_list] # convert each string into a list of the words in the string
state_df_list = [item for sublist in state_df_list for item in sublist] # flatten the list of lists into a single list
state_df_list = [i.lower() for i in state_df_list] # make lowercase
state_set = set(state_df_list)

print("city county state complete")

## Import country, continent and region data
# Go to https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv
# Copy to csv, name countries_continents.csv
country_continent_df = pd.read_csv('countries_continents.csv', delimiter = ',',  encoding="latin-1")
print("countries_continents.csv loaded")

# Extract countries column
country_df = country_continent_df['name']
# Remove blanks
country_df = country_df[country_df.notnull()]
# Create list from city df and split
country_df_list = list(country_df)
country_df_list = [term.split() for term in country_df_list] # convert each string into a list of the words in the string
country_df_list = [item for sublist in country_df_list for item in sublist] # flatten the list of lists into a single list
country_df_list = [i.lower() for i in country_df_list] # make lowercase
country_df_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '') for i in country_df_list]
country_set = set(country_df_list)


# Extract country codes column
code_df = country_continent_df['alpha-3']
# Remove blanks
code_df = code_df[code_df.notnull()]
# Create list from city df and split
code_df_list = list(code_df)
code_df_list = [term.split() for term in code_df_list] # convert each string into a list of the words in the string
code_df_list = [item for sublist in code_df_list for item in sublist] # flatten the list of lists into a single list
code_df_list = [i.lower() for i in code_df_list] # make lowercase
code_set = set(code_df_list)


# Extract region column
region_df = country_continent_df['sub-region']
# Remove blanks
region_df = region_df[region_df.notnull()]
# Create list from city df and split
region_df_list = list(region_df)
region_df_list = [term.split() for term in region_df_list] # convert each string into a list of the words in the string
region_df_list = [item for sublist in region_df_list for item in sublist] # flatten the list of lists into a single list
region_df_list = [i.lower() for i in region_df_list] # make lowercase
region_set = set(region_df_list)


# Critical words to keep:
critical_locations_df = pd.read_csv('critical_locations.csv', delimiter = ',',  encoding="latin-1")
print("critical_location.csv loaded")

# Base names
critical_base = critical_locations_df['base']
# Remove blanks
critical_base = critical_base[critical_base.notnull()]
# Create list and split
base_list = list(critical_base)
base_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in base_list]
base_list = [term.split() for term in base_list] # convert each string into a list of the words in the string
base_list = [item for sublist in base_list for item in sublist] # flatten the list of lists into a single list
base_list = [i.lower() for i in base_list] # make lowercase
base_set = set(base_list)

# Common_names
critical_common = critical_locations_df['common']
# Remove blanks
critical_common = critical_common[critical_common.notnull()]
# Create list and split
common_list = list(critical_common)
common_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in common_list]
common_list = [term.split() for term in common_list] # convert each string into a list of the words in the string
common_list = [item for sublist in common_list for item in sublist] # flatten the list of lists into a single list
common_list = [i.lower() for i in common_list] # make lowercase
common_set = set(common_list)

# Abbreviations
critical_abbrev = critical_locations_df['abbrev']
# Remove blanks
critical_abbrev = critical_abbrev[critical_abbrev.notnull()]
# Create list and split
abbrev_list = list(critical_abbrev)
abbrev_list = [i.replace('(','').replace(')','').replace('{','').replace('}','').replace('|',' ').replace('\'', '').replace('_',' ').replace(',',' ').replace(':',' ').replace(';',' ').replace('\\',' ').replace('-',' ').replace('.','').replace('/',' ').replace('&', '').replace('[','').replace(']','').replace('?','') for i in abbrev_list]
abbrev_list = [term.split() for term in abbrev_list] # convert each string into a list of the words in the string
abbrev_list = [item for sublist in abbrev_list for item in sublist] # flatten the list of lists into a single list
abbrev_list = [i.lower() for i in abbrev_list] # make lowercase
abbrev_set = set(abbrev_list)

# Other critical words:
manual_location_set = set(["north", "east", "south", "west", "first", "second", "third", "fourth","fifth","sixth","seventh","eighth","ninth","tenth","main","floor","box","post","mail"])

"""
# Combine all location sets
location_set = northeast_street_names_set | midwest_street_names_set | south_street_names_set| west_street_names_set | county_set # | state_set | country_set | code_set | region_set

# Subtract common words
location_set = set([item for item in location_set if not item in english_1k])

# Add back critical location words
location_set = location_set | base_set | common_set | abbrev_set | manual_location_set
"""
location_set = northeast_street_names_set | midwest_street_names_set | south_street_names_set| west_street_names_set | county_set | base_set | common_set | abbrev_set | manual_location_set

print("location set complete")




# Here are words that keep popping up in the notes that appear safe:

words_from_notes_list = ['patient','disease', 'todays',  'saver', 'crtp', 'sch', 'aud', 'plavix', 'steadily','reconstructions',  'charted', 'pricosec', 'flomax', 'mls', 'neg', 'neb',  'transaminitis', 'hypokinesis', 'tolerating', 'disclaims', 'spoke', 'discrepancies', 'calc', 'paperwork', 'backbleeding',  'recovers', 'lad', 'reconciled', 'audiogram', 
'counseled', 'walgreens',  'afib', 'hydrodiuril',  'edits', 'mgml', 'mgmt', 'diag', 'diagnosishistory',  'notified',  'pmappointment', 'creamcommonly', 'signing', 'mds', 'rt', 'rv', 'rs', 'rx', 'rf', 'rl', 'rm', 'ro','amappointment', 'certifies','westside', 'robitussin', 'hood',  'elevator', 'neobladder', 
 'gyn', 'signup',  'shower',  'tcells',  'lbs', 'pvcs', 'talking', '375mg', 'sulfamethoxazoletrimethoprim', 'paramedics', 'panleukocyte', 'bcells', 'agressive', 'ipss', 'irrigated',  'definitely', 'lpc', 'signatures',  'reschedule', 'hrs', 'pnd', 'claritin', 'benazepril', 'aetiology', 'ventolinproventil', 'dx', 'dw',
 'upreg', 'hypoxemia', 'ems', 'emr', 'psych',  'meshworks', 'gentleman', 'hematogones', 'wc', 'deltasone',  'tfts', 'jello','arteriotomy', 'angiograms', 'mcg',  'hepc', 'neurontin', 'cardiomediastinal', 'dept','dexon', 'cont', 'io',  'zofran', 'meets','stiffener', 'pantcell',
 'lvcs', 'eps', 'urethrotomy', 'mammo', 'yours','sonographer', 'offwhite', 'progressed','mastoids', 'lcd',  'ambulating',  'colacetake', 'bpm', 'bps', 'extrastimuli', 'infrahepatic', 'dorzolamidetimolol', 'prepping', 'painfree', 'bulbocavernous', 'denies', 'cnt',  'floaters', 'aldorenin', 'icd', 'ucsf', 'housestaff',
 'hsv', 'playroom', 'scds', 'andreadis',  'dinner', 'monospot',  'sob', 'omnipaque', 'homogenization', 'verbalizes',  'verbalized',  'appts', 'underestimated', 'unoriented', 'overthecounter',  'anticoag', 'fibroids', 'vicodin',
 'fell','flushed',  'overdue','answered',  'slash', 'diaphoretic', 'fatigued', 'trouble',  'anesthetized', 'concurs', 'mycophenolate', 'tums', 'bumex', 'shave', 
 'peds', 'pmd',  'pmc', 'pmh',  'consolidations', 'postbiopsy', 'aquaphor', 'asault', 'guardian', 'deo',  'refused', 'wait', 'ekg', 'ptnb', 'hbv', 'valcyte', 'sincerely', 'perm',  'tachycardic', 'checkout',
  'prep', 'sessions', 'solumedrol', 'dermatologist', 'flr',  'soup', 'spr',  'sph', 'orthosurgery',  'intrasinus', 'prelim', 'speaks', 'contraindicated', 'superolateral', 'interoperative',
  'sf', 'refund', 'tty',  'ttp', 'vte', 'vti', 'upstrokes',  'intl', 'moms', 'luken', 'sooner', 'fibroglandular', 'logans','prompted', 'begun', 'approximated',
    'nonafrican', 'plex',  'tomorrow', 'slept', 'electrograms', 'participated',  'sores', 'appreciated','rehab', 'quadrants', 'silhouette', 'advil', 'instructed',
   'rationale', 'pager',  'osteopenia', 'neuro',  'mrn', 'mrg','mlhr','datetime', 'lithotomy', 'surveilance','histories', 'sdi','reps', 'ssi',  'encouraged', 'checks', 'abutting', 
    'tizanidine','yearly', 'betablockers', 'pos', 'hvf', 'birads', 'flowsheetpatient', 'declining', 'wants', 'groins', 
     'consultant', 'ivf', 'compensations', 'ivc', 'consults', 'hent', 'mgdl', 'dilations','hba1c', 'ropivacaine', 'oxycontin', 
     'cialis', 'anesthesiologist',  'kneeling', 'refills', 'proventil',  'dissected', 'mychart', 'mom', 'towel',  'perinephric', 
     'thinks','asap',  'rncomment',  'radiographs',  'discussed', 'ob', 'weekend','sonographic','asst', 'ao', 'maxed', 'rvr', 'stigmata', 'walks', 'girlfriend', 
      'bisected', 'faxed', 'mcal',  'booked', 'complicationsno', 'disp', 'cardiologist', 'polyphagia',  'securely', 'ambien','flowsheets','preop', 'assailants',  'dial', 
       'tdap',  'zostavax', 'bathe','prilosec','postradiation','launch','mirtazapine','stayed', 'wellcontrolled', 'okay','petite', 'tries',  'eats', 'vitals', 'sonograms',
       'bathes', 'basename',  'logan', 'etoh', 'avenue', 'dont','screenings','flonase', 'inch',  'disorderptsd',  'todo',  'colace','bcell',
        'protonix', 'dictations','fidgeting', 'nonlabored','zyprexa','hydrocodoneacetaminophen', 'oxybutynin',  'complained', 'gotten', 'treater','preprocedure','remembers',
        'focally', 'sentences', 'understands',  'uscf', 'wheezes','prepped','reassessed', 'morphologies', 'ambulates', 'guarding', 'deferred', 'prostituting', 'unlabored', 'anymore',
        'retractions', 'thryoid', 'yesterday', 'synopsis','residentfellow', 'bicarb', 'sedated','complains', 'judgement', 'lipitor', 'restroom', 'sfmta', 'accelerations', 'meds',  'lasted','negatives','dictated',
'womens', 'bleeds', 'attends', 'selfharm','stitches', 'motrin',  'collapses',  'percocet', 'extubated', 'uc', 'sickles', 'nighttime', 'nonclinical', 'nap','reportedly', 'calcifications', 'nauseavomiting', 'eval',
'viewsleft','soaks', 'valuables','renalkidney', 'medicalfamily','premed', 'uploaded', 'lasix', 'reopened','ctr', 'whereucsf','addressed', 'preventative','upcoming','zyrtec', 'ucsfmychartorg',
'sig', 'connors','belongings', 'biopsyproven', 'interpreter','dad','sweets', 'lumpectomy', 'witness','await', 'shots', 'grunting', 'levitra', 'straining', 'punctured', 'steet',  'tabs', 'gently', 'reassuring',
 'expires', 'looked', 'approx', 'insync','nebulization', 'combo','hopefully', 'legacy', 'outpt', 'micropuncture', 'admin', 'noncontributory', 'copied', 'username', 'cvs', 'orthopnea', 'transitioned','dosestrength',
  'drips', 'helped', 'nonfasting', 'phd', 'nightly','clipped', 'inheriting', 'discontd', 'benadryl', 'sfgh',  'immunizations', 'underwent', 'shes', 'inhalational', 'trimmed',  'aleve',
  'puts','childrens', 'obliterated', 'cyclobenzaprine', 'forget', 'prozac', 'palpated', 'appt', 'bump', 'yrs','mailed','temp','polysubstance',
   'ins', 'camping','bushwhacking','distance','hours','not','tick','well','headache','away','neck','pain','chills','sleeping','wake','rash','photo','mostly','rolaids','empty','eats','stool','melena','ate','hungry','active','mild','stress','oral','panic','attack','severe','sinus','medical','comment','positive','swell','resolves','testing', 'abcesses','lumbar','radical','sometimes','lateral','chronic','joint','running','depression','freshman','sophomore','junior','senior','review','marked','takes','encounter','ortho','tri','tab','daily','weekly','yearly','products','cream','drying','frequent','entire','faces','needs','needed','pulse','temp','weights','developed','supple','clearly','breath','regular','rate','rhythm','rhythms','rhythmic','bowels','sounds','softly','tender','nondistended','guarded','skinned','patch']



####################################################################################
# Words that are still in the whitelist, despite being PHI:
unsafe_words = set(["dispo","echo", "ste", "3-year-old", "voicebox"])

# List of months and abbreviations that should be subtracted
month_names = set(["january", "jan", "february", "feb", "march", "mar", "april", "apr", "may", "june", "jun", "july", "jul", "august", "aug", "september", "sep", "october", "oct","november","nov","december","dec" ])

punctation_added = ['', '-', '(',')']
# according to the filter summary and every institution's terms, manually add words
manual_add = 'UCare,RunSafe,MPFL,Lachman,RTC,TTG,ROS,UTD,vax,debrox,TLIF,Micromedex,CLARITIN,ROXICODONE,MIRALAX,NSVD,Clinda,UOP,withdrawl,walker,dgim,lusb,b.c.i.a,lexicomp,labs,day,person,rads'
manual_add_set = set(manual_add.lower().split(','))

# mesh_heir_ms_list seems to contain some phi, not including it for now. mesh_heir_list
whitelist = set(mesh_list + abbrev_list + common_english_list + umls_list  + mesh_heir_term_list +  descriptor_mesh_list+ punctation_added + physio_common_words + physio_commonest_words + physio_notes_common + sno_edited_notes + medical_phrases)
whitelist = whitelist | mp_set_normalized | snomed_set | icd9_code | icd10_code | drug_set | icd9_diagnoses_set | abbrevs_and_definitions_set | thousand_verbs_set | manual_add_set
whitelist = whitelist - (whitelist&name_set)
whitelist = whitelist - (whitelist&location_set)
whitelist = whitelist - (whitelist&month_names)
whitelist = whitelist - (whitelist&unsafe_words)
whitelist = set([item for item in whitelist if not any(c.isdigit() for c in item)]) # get rid of any and all words with digits in the whitelist
whitelist = set([item for item in whitelist if not isinstance(item,int)])
whitelist = set([item for item in whitelist if len(item) > 2]) # final check to remove all single letters
#whitelist = whitelist | set(words_from_notes_list) # add in safe words from notes
print("Whitelist final length: ") + str(len(whitelist))


# 1. Name checks:
print("goldman" in whitelist)
print("ames" in whitelist)
print("phy" in whitelist)
print("ascher" in whitelist)
print("m" in whitelist)
print("m")
print("punch" in whitelist) # where is this
print("hwa" in whitelist)
print("krishna" in whitelist)
print("agarwal" in whitelist)
print("soper" in whitelist)
print("soper")
print("jo" in whitelist)
print("yi" in whitelist)
print("marion" in whitelist)
print("maritza" in whitelist)
print("ko" in whitelist)
print("ko")
print("echo" in whitelist)
print("gerhardt" in whitelist)
print("hang" in whitelist) # where is this
print("d" in whitelist)
print("t" in whitelist)
print("t")
print("p" in whitelist)
print("ports" in whitelist)
print("chi" in whitelist)
print("dispo" in whitelist)
print("virginia" in whitelist)
print("virginia")
print("franc" in whitelist) # where is this
print("hu" in whitelist)
print("s" in whitelist)
print("mz" in whitelist)
print("dale" in whitelist)
print("dale")
print("n" in whitelist)
print("pollack" in whitelist)
print("lao" in whitelist)
print("pong" in whitelist)
print("lo" in whitelist)
print("lo")
print("fern" in whitelist) # where is this
print("lm" in whitelist)

least_common_names_df = pd.read_csv('100k_least_common_surnames.csv', delimiter = ',')
least_common_names = least_common_names_df['name']
least_common_names = list(least_common_names)
least_common_names = [str(i) for i in least_common_names]
least_common_names = [i.lower() for i in least_common_names]

most_common_names_df = pd.read_csv('50k_most_common_surnames.csv', delimiter = ',')
most_common_names = most_common_names_df['name']
most_common_names = list(most_common_names)
most_common_names = [str(i) for i in most_common_names]
most_common_names = [i.lower() for i in most_common_names]


for item in least_common_names:
	if item in whitelist:
		print(item)

for item in most_common_names:
	if item in whitelist:
		print(item)

for item in ss_firstnames_set:
	if item in whitelist:
		print(item)

# 2. Location checks:
print("ca" in whitelist)
print("san" in whitelist)
print("main" in whitelist) # where is this
print("3rd" in whitelist)
print("floor" in whitelist) # where is this
print("ste" in whitelist)
print("16th" in whitelist)
print("parnassus" in whitelist)
print("fl" in whitelist)
print("st" in whitelist)
print("west" in whitelist)
print("first" in whitelist)
print("street" in whitelist)
print("box" in whitelist)
print("post" in whitelist)
print("4th" in whitelist)
print("avenue" in whitelist)

# 3. Number checks
print([s for s in whitelist if s.isdigit()])

# 4. Email checks
print([s for s in whitelist if "@" in s])

# 5. URL checks
print([s for s in whitelist if "http" in s])
print([s for s in whitelist if "www." in s])


print('len of final whitelist: {}'.format(len(whitelist)))


pickle.dump(whitelist, open( "whitelist_v_91_take2.pkl", "wb" ) )



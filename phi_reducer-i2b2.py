# De-id script
# import modules
from __future__ import print_function
import os
import sys
import pickle
import glob
import string
import re
import time
import argparse

# import multiprocess
import multiprocessing
from multiprocessing import Pool

# import NLP packages
import nltk
from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.tree import Tree
from nltk import pos_tag_sents
from nltk import pos_tag
from nltk import ne_chunk
import spacy
from pkg_resources import resource_filename
from nltk.tag.perceptron import AveragedPerceptron
from nltk.tag import SennaTagger
from nltk.tag import HunposTagger
"""
Replace PHI words with a safe filtered word: '**PHI**'

Does:
1. regex to search for salutations (must be done prior to splitting into sentences b/c of '.' present in most salutations)
2. split document into sentences.
3.Run regex patterns to identify PHI considering only 1 word at a time:emails, phone numbers, DOB, SSN, Postal codes, or any word containing 5 or more consecutive digits or
    8 or more characters that begins and ends with digits.

4. Split sentences into words

5. Run regex patterns to identify PHI looking at the context for each word. For example DOB checks the preceding words for 'age' or 'years' etc. 
addresses which include ***REMOVED***streets, rooms, states, etc***REMOVED***,age over 90. 

6. Use nltk to label POS. 

7. Identify names: We run 2 separate methods to check if a word is a name based on it's context at the chunk/phrase level. To do this:
First: Spacy nlp() is run on the sentence level and outputs NER labels at the chunk/phrase level. 
Second: For chunks/phrases that spacy thinks are 'person', get a second opinion by running nltk ne_chunck which uses nltk POS 
to assign an NER label to the chunk/phrases. 
*If both spacy and nltk provide a 'person' NER label for a chunk/phrase: check the in the chunk 1-by-1 with nltk to determine if
 the word's POS tag is a proper noun.
    - sometimes the label 'person' may be applied to more than 1 word, and occassionally 1 of those words is just a normal noun, not a name.
    - If word is a proper noun, flag the word and add it to name_set
*If spacy labels word as person but nltk does not label person but labels word as another category of NER, use spacy on the all UPPERCASE version words
in the chunk 1-by-1 to see if spacy still believes that the uppercase word is NER of any category
    - If it is, add word to name_set; 
    - If spacy thinks the uppercase version of the word no longer has an NER label, then treat word as any other noun and send to be filtered through the whitelist. 

8. If word is noun, send it on to check it against the whitelist. If word is not noun,
consider it safe and pass it on to output.For nouns, if word is in whitelist,
                                    check if word is in name_set, if so -> filter.
                                        If not in name_set,
                                            use spacy to check if word is a name based on the single word's meaning and format.
                                            Spacy does a per-word look up and assigns most frequent use of that word as a flag
                                            (eg'HUNT':-organization, 'Hunt'-name, 'hunt':verb).
                                            If the flags is name -> filter
                                            If flag is not name pass word through as safe
                                if word not in whitelist -> filter
9. Search for middle initials by checking if single Uppercase letter is between PHI infos, if so, consider the letter as a middle initial and filter it. e.g. Ane H Berry.

NOTE: All of the above numbered steps happen in filter_task(). Other functions either support filter task or simply involve
dealing with I/O and multiprocessing

"""


nlp = spacy.load('en')  # load spacy english library
# pretrain = SennaTagger('senna')

# configure the regex patterns
# we're going to want to remove all special characters
pattern_word = re.compile(r"***REMOVED***^\w+***REMOVED***")

# Find numbers like SSN/PHONE/FAX
# 3 patterns: 1. 6 or more digits will be filtered 2. digit followed by - followed by digit. 3. Ignore case of characters
pattern_number = re.compile(r"""\b(
(\d***REMOVED***\(\)\-\'***REMOVED***?\s?){6}(***REMOVED***\(\)\-\'***REMOVED***?\d)+   # SSN/PHONE/FAX XXX-XX-XXXX, XXX-XXX-XXXX, XXX-XXXXXXXX, etc.
|(\d***REMOVED***\(\)\-.\'***REMOVED***?){7}(***REMOVED***\(\)\-.\'***REMOVED***?\d)+  # test
)\b""", re.X)

pattern_4digits = re.compile(r"""\b(
\d{4}***REMOVED***A-Z0-9***REMOVED****  # devid/mrn/benid
)\b""", re.X)

pattern_devid = re.compile(r"""\b(
***REMOVED***A-Z0-9\-/***REMOVED***{6}***REMOVED***A-Z0-9\-/***REMOVED****
)\b""", re.X)
# postal code
# 5 digits or, 5 digits followed dash and 4 digits
pattern_postal = re.compile(r"""\b(
\d{5}(-\d{4})?             # postal code XXXXX, XXXXX-XXXX
)\b""", re.X)

# match DOB
pattern_dob = re.compile(r"""\b(
.*?(?=\b(\d{1,2}***REMOVED***-./\s***REMOVED***\d{1,2}***REMOVED***-./\s***REMOVED***\d{2}  # X/X/XX
|\d{1,2}***REMOVED***-./\s***REMOVED***\d{1,2}***REMOVED***-./\s***REMOVED***\d{4}          # XX/XX/XXXX
|\d{2}***REMOVED***-./\s***REMOVED***\d{1,2}***REMOVED***-./\s***REMOVED***\d{1,2}          # xx/xx/xx
|\d{4}***REMOVED***-./\s***REMOVED***\d{1,2}***REMOVED***-./\s***REMOVED***\d{1,2}          # xxxx/xx/xx
)\b)
)\b""", re.X | re.I)

# match emails
pattern_email = re.compile(r"""\b(
***REMOVED***a-zA-Z0-9_.+-@\"***REMOVED***+@***REMOVED***a-zA-Z0-9-\:\***REMOVED***\***REMOVED******REMOVED***+***REMOVED***a-zA-Z0-9-.***REMOVED****
)\b""", re.X | re.I)

# match date, similar to DOB but does not include any words
month_name = "Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?"
pattern_date = re.compile(r"""\b(
\d{4}***REMOVED***\-/***REMOVED***(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")\-\d{4}***REMOVED***\-/***REMOVED***(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")  # YYYY/MM-YYYY/MM
|(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")***REMOVED***\-/***REMOVED***\d{4}\-(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")***REMOVED***\-/***REMOVED***\d{4}  # MM/YYYY-MM/YYYY
|(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")/\d{2}\-(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")/\d{2}  # MM/YY-MM/YY
|(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")/\d{2}\-(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")/\d{4}  # MM/YYYY-MM/YYYY
|(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")/(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)\-(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")/(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)  #MM/DD-MM/DD
|(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)/(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")\-(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)/(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")  #DD/MM-DD/MM
|(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")***REMOVED***\-/\s***REMOVED***(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)***REMOVED***\-/\s***REMOVED***\d{2}  # MM/DD/YY
|(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")***REMOVED***\-/\s***REMOVED***(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)***REMOVED***\-/\s***REMOVED***\d{4}  # MM/DD/YYYY
|(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)***REMOVED***\-/\s***REMOVED***(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")***REMOVED***\-/\s***REMOVED***\d{2}  # DD/MM/YY
|(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)***REMOVED***\-/\s***REMOVED***(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")***REMOVED***\-/\s***REMOVED***\d{4}  # DD/MM/YYYY
|\d{2}***REMOVED***\-./\s***REMOVED***(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")***REMOVED***\-\./\s***REMOVED***(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)   # YY/MM/DD
|\d{4}***REMOVED***\-./\s***REMOVED***(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")***REMOVED***\-\./\s***REMOVED***(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)   # YYYY/MM/DD
|\d{4}***REMOVED***\-/***REMOVED***(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")  # YYYY/MM
|(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")***REMOVED***\-/***REMOVED***\d{4}  # MM/YYYY
|(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")/\d{2}  # MM/YY
|(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")/\d{2}  # MM/YYYY
|(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")/(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)  #MM/DD
|(***REMOVED***1-2***REMOVED******REMOVED***0-9***REMOVED***|3***REMOVED***0-1***REMOVED***|0?***REMOVED***1-9***REMOVED***)/(0?***REMOVED***1-9***REMOVED***|1***REMOVED***0-2***REMOVED***|"""+month_name+r""")  #DD/MM
)\b""", re.X | re.I)
pattern_mname = re.compile(r'\b(' + month_name + r')\b')

# match names, A'Bsfs, Absssfs, A-Bsfsfs
pattern_name = re.compile(r"""^***REMOVED***A-Z***REMOVED***\'?***REMOVED***-a-zA-Z***REMOVED***+$""")

# match age
pattern_age = re.compile(r"""\b(
age|year***REMOVED***s-***REMOVED***?\s?old|y.o***REMOVED***.***REMOVED***?
)\b""", re.X | re.I)

# match salutation
pattern_salutation = re.compile(r"""
(Dr\.|Mr\.|Mrs\.|Ms\.|Miss|Sir|Madam)\s
((***REMOVED***A-Z***REMOVED***\'?***REMOVED***A-Z***REMOVED***?***REMOVED***\-a-z***REMOVED***+(\s***REMOVED***A-Z***REMOVED***\'?***REMOVED***A-Z***REMOVED***?***REMOVED***\-a-z***REMOVED***+)*)
)""", re.X)

# match middle initial
# if single char or Jr is surround by 2 phi words, filter. 
pattern_middle = re.compile(r"""\*\*PHI\*\*,? ((***REMOVED***A-CE-LN-Z***REMOVED******REMOVED***Rr***REMOVED***?|***REMOVED***DM***REMOVED***)\.?) | ((***REMOVED***A-CE-LN-Z***REMOVED******REMOVED***Rr***REMOVED***?|***REMOVED***DM***REMOVED***)\.?),? \*\*PHI\*\*""")


# match url
pattern_url = re.compile(r'\b((http***REMOVED***s***REMOVED***?://)?(***REMOVED***a-zA-Z0-9$-_@.&+:!\*\(\),***REMOVED***)****REMOVED***\.\/***REMOVED***(***REMOVED***a-zA-Z0-9$-_@.&+:\!\*\(\),***REMOVED***)*)\b', re.I)

# check if the folder exists
def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The folder %s does not exist. Please input a new folder or create one." % arg)
    else:
        return arg

# check if word is in name_set, if not, check the word by single word level
def namecheck(word_output, name_set, screened_words, safe):
    # check if the word is in the name list
    if word_output.title() in name_set:
        # with open("name.txt", 'a') as fout:
           # fout.write(word_output + '\n')
        # print('Name:', word_output)
        screened_words.append(word_output)
        word_output = "**PHI**"
        safe = False

    else:
    # check spacy, and add the word to the name list if it is a name
    # check the word's title version and its uppercase version
        word_title = nlp(word_output.title())
        # search Title or UPPER version of word in the english dictionary: nlp()
        # nlp() returns the most likely NER tag (word.ents) for the word 
        # If word_title has NER = person AND word_upper has ANY NER tag, filter
        word_upper = nlp(word_output.upper())
        if (word_title.ents != () and word_title.ents***REMOVED***0***REMOVED***.label_ == 'PERSON' and
                word_upper.ents != () and word_upper.ents***REMOVED***0***REMOVED***.label_ is not None):
            # with open("name.txt", 'a') as fout:
               # fout.write(word_output + '\n')
            # print('Name:', word_output)
            screened_words.append(word_output)
            name_set.add(word_output.title())
            word_output = "**PHI**"
            safe = False

    return word_output, name_set, screened_words, safe


def filter_task(f, whitelist_dict, foutpath, key_name):

    # pretrain = HunposTagger('hunpos.model', 'hunpos-1.0-linux/hunpos-tag')
    pretrain = SennaTagger('senna')

    """
    Uses: namecheck() to check if word that has been tagged as name by either nltk or spacy. namecheck() first searches
    nameset which is generated by checking words at the sentence level and tagging names. If word is not in nameset,
    namecheck() uses spacy.nlp() to check if word is likely to be a name at the word level. 

    """
    with open(f, encoding='utf-8', errors='ignore') as fin:
        # define intial variables
        head, tail = os.path.split(f)
        #f_name = re.findall(r'***REMOVED***\w\d***REMOVED***+', tail)***REMOVED***0***REMOVED***  # get the file number
        print(tail)
        start_time_single = time.time()
        total_records = 1
        phi_containing_records = 0
        safe = True
        screened_words = ***REMOVED******REMOVED***
        name_set = set()
        phi_reduced = ''
        address_indictor = ***REMOVED***'street', 'avenue', 'road', 'boulevard',
                            'drive', 'trail', 'way', 'lane', 'ave',
                            'blvd', 'st', 'rd', 'trl', 'wy', 'ln',
                            'court', 'ct', 'place', 'plc', 'terrace', 'ter'***REMOVED***

        note = fin.read()
        # Begin Step 1: saluation check
        re_list = pattern_salutation.findall(note)
        for i in re_list:
            name_set = name_set | set(i***REMOVED***1***REMOVED***.split(' '))

        # note_length = len(word_tokenize(note))
        # Begin step 2: split document into sentences
        note = sent_tokenize(note)

        for sent in note: # Begin Step 3: Pattern checking
            # postal code check
            # print(sent)
            if pattern_postal.findall(sent) != ***REMOVED******REMOVED***:
                safe = False
                for item in pattern_postal.findall(sent):
                    screened_words.append(item***REMOVED***0***REMOVED***)
            sent = str(pattern_postal.sub('**PHIPostal**', sent))

            if pattern_devid.findall(sent) != ***REMOVED******REMOVED***:
                safe = False
                for item in pattern_devid.findall(sent):
                    if (re.search(r'\d', item) is not None and
                        re.search(r'***REMOVED***A-Z***REMOVED***',item) is not None):
                        screened_words.append(item)
                        sent = sent.replace(item, '**PHI**')

            # number check
            if pattern_number.findall(sent) != ***REMOVED******REMOVED***:
                safe = False
                for item in pattern_number.findall(sent):
                    # print(item)
                    #if pattern_date.match(item***REMOVED***0***REMOVED***) is None:
                    sent = sent.replace(item***REMOVED***0***REMOVED***, '**PHI**')
                    screened_words.append(item***REMOVED***0***REMOVED***)
                    #print(item***REMOVED***0***REMOVED***)
            #sent = str(pattern_number.sub('**PHI**', sent))
            if pattern_date.findall(sent) != ***REMOVED******REMOVED***:
                safe = False
                for item in pattern_date.findall(sent):
                    if '-' in item***REMOVED***0***REMOVED***:
                        if (len(set(re.findall(r'***REMOVED***^\w\-***REMOVED***',item***REMOVED***0***REMOVED***))) <= 1):
                            screened_words.append(item***REMOVED***0***REMOVED***)
                            #print(item***REMOVED***0***REMOVED***)
                            sent = sent.replace(item***REMOVED***0***REMOVED***, '**PHIDate**')
                    else:
                        if len(set(re.findall(r'***REMOVED***^\w***REMOVED***',item***REMOVED***0***REMOVED***))) == 1:
                            screened_words.append(item***REMOVED***0***REMOVED***)
                            #print(item***REMOVED***0***REMOVED***)
                            sent = sent.replace(item***REMOVED***0***REMOVED***, '**PHIDate**')

            #sent = str(pattern_date.sub('**PHI**', sent))
            #print(sent)
            if pattern_4digits.findall(sent) != ***REMOVED******REMOVED***:
                safe = False
                for item in pattern_4digits.findall(sent):
                    screened_words.append(item)
            sent = str(pattern_4digits.sub('**PHI**', sent))
            # email check
            if pattern_email.findall(sent) != ***REMOVED******REMOVED***:
                safe = False
                for item in pattern_email.findall(sent):
                    screened_words.append(item)
            sent = str(pattern_email.sub('**PHI**', sent))
            # url check
            if pattern_url.findall(sent) != ***REMOVED******REMOVED***:
                safe = False
                for item in pattern_url.findall(sent):
                    #print(item***REMOVED***0***REMOVED***)
                    if (re.search(r'***REMOVED***a-z***REMOVED***', item***REMOVED***0***REMOVED***) is not None and
                        '.' in item***REMOVED***0***REMOVED*** and
                        re.search(r'***REMOVED***A-Z***REMOVED***', item***REMOVED***0***REMOVED***) is None and
                        len(item***REMOVED***0***REMOVED***)>10):
                        print(item***REMOVED***0***REMOVED***)
                        screened_words.append(item***REMOVED***0***REMOVED***)
                        sent = sent.replace(item***REMOVED***0***REMOVED***, '**PHI**')
                        #print(item***REMOVED***0***REMOVED***)
            #sent = str(pattern_url.sub('**PHI**', sent))
            # dob check
            '''
            re_list = pattern_dob.findall(sent)
            i = 0
            while True:
                if i >= len(re_list):
                    break
                else:
                    text = ' '.join(re_list***REMOVED***i***REMOVED******REMOVED***0***REMOVED***.split(' ')***REMOVED***-6:***REMOVED***)
                    if re.findall(r'\b(birth|dob)\b', text, re.I) != ***REMOVED******REMOVED***:
                        safe = False
                        sent = sent.replace(re_list***REMOVED***i***REMOVED******REMOVED***1***REMOVED***, '**PHI**')
                        screened_words.append(re_list***REMOVED***i***REMOVED******REMOVED***1***REMOVED***)
                    i += 2
            '''

            # Begin Step 4
            # substitute spaces for special characters 
            sent = re.sub(r'***REMOVED***\/\-\:\~\_***REMOVED***', ' ', sent)
            # label all words for NER using the sentence level context. 
            spcy_sent_output = nlp(sent)
            # split sentences into words
            sent = ***REMOVED***word_tokenize(sent)***REMOVED***
            #print(sent)
            # Begin Step 5: context level pattern matching with regex 
            for position in range(0, len(sent***REMOVED***0***REMOVED***)):
                word = sent***REMOVED***0***REMOVED******REMOVED***position***REMOVED***
                # age check
                if word.isdigit() and int(word) > 90:
                    if position <= 2:  # check the words before age
                        word_previous = ' '.join(sent***REMOVED***0***REMOVED******REMOVED***:position***REMOVED***)
                    else:
                        word_previous = ' '.join(sent***REMOVED***0***REMOVED******REMOVED***position - 2:position***REMOVED***)
                    if position >= len(sent***REMOVED***0***REMOVED***) - 2:  # check the words after age
                        word_after = ' '.join(sent***REMOVED***0***REMOVED******REMOVED***position+1:***REMOVED***)
                    else:
                        word_after = ' '.join(sent***REMOVED***0***REMOVED******REMOVED***position+1:position +3***REMOVED***)

                    age_string = str(word_previous) + str(word_after)
                    if pattern_age.findall(age_string) != ***REMOVED******REMOVED***:
                        screened_words.append(sent***REMOVED***0***REMOVED******REMOVED***position***REMOVED***)
                        sent***REMOVED***0***REMOVED******REMOVED***position***REMOVED*** = '**PHI**'
                        safe = False
                # check if the context around comma is name
                elif (word == ',' and 0<position<len(sent***REMOVED***0***REMOVED***) and
                    (sent***REMOVED***0***REMOVED******REMOVED***position-1***REMOVED***.isupper()) and
                    (sent***REMOVED***0***REMOVED******REMOVED***position+1***REMOVED***.isupper())):
                    # upper version check
                        comma_text = sent***REMOVED***0***REMOVED******REMOVED***position-1***REMOVED***.upper()+','+sent***REMOVED***0***REMOVED******REMOVED***position+1***REMOVED***.upper()
                        comma_spacy = nlp(comma_text)
                        if comma_spacy.ents != ():
                            for ent in comma_spacy.ents:
                                #if ent.label_ == 'PERSON':
                                #print(ent.text)
                                    #print(ent.text.split(','))
                                comma_set = set(ent.text.split(',')) - set(***REMOVED***'M.D', 'M.D.'***REMOVED***)
                                for j in comma_set:
                                    if re.search(r'***REMOVED***aeiou***REMOVED***', j, re.I) is not None and nltk.pos_tag(***REMOVED***j***REMOVED***)***REMOVED***0***REMOVED******REMOVED***1***REMOVED*** == 'NN':
                                        #print(j)
                                        name_set.add(j.title())
                    # title version check
                        comma_text = sent***REMOVED***0***REMOVED******REMOVED***position-1***REMOVED***.title()+','+sent***REMOVED***0***REMOVED******REMOVED***position+1***REMOVED***.title()
                        comma_spacy = nlp(comma_text)
                        if comma_spacy.ents != ():
                            for ent in comma_spacy.ents:
                                #if ent.label_ == 'PERSON':
                                #print(ent.text)
                                    #print(ent.text.split(','))
                                comma_set = set(ent.text.split(',')) - set(***REMOVED***'M.D', 'M.D.'***REMOVED***)
                                for j in comma_set:
                                    if re.search(r'***REMOVED***aeiou***REMOVED***', j, re.I) is not None and nltk.pos_tag(***REMOVED***j***REMOVED***)***REMOVED***0***REMOVED******REMOVED***1***REMOVED*** == 'NN':
                                        #print(j)
                                        name_set.add(j.title())

                # address check
                elif (position >= 1 and position < len(sent***REMOVED***0***REMOVED***)-1 and
                      (word.lower() in address_indictor or
                       (word.lower() == 'dr' and sent***REMOVED***0***REMOVED******REMOVED***position+1***REMOVED*** != '.')) and
                      (word.istitle() or word.isupper())):

                    if sent***REMOVED***0***REMOVED******REMOVED***position - 1***REMOVED***.istitle() or sent***REMOVED***0***REMOVED******REMOVED***position-1***REMOVED***.isupper():
                        screened_words.append(sent***REMOVED***0***REMOVED******REMOVED***position - 1***REMOVED***)
                        sent***REMOVED***0***REMOVED******REMOVED***position - 1***REMOVED*** = '**PHI**'
                        i = position - 1
                        # find the closet number, should be the number of street
                        while True:
                            if re.findall(r'^***REMOVED***\d-***REMOVED***+$', sent***REMOVED***0***REMOVED******REMOVED***i***REMOVED***) != ***REMOVED******REMOVED***:
                                begin_position = i
                                break
                            elif i == 0 or position - i > 5:
                                begin_position = position
                                break
                            else:
                                i -= 1
                        i = position + 1
                        # block the info of city, state, apt number, etc.
                        while True:
                            if '**PHIPostal**' in sent***REMOVED***0***REMOVED******REMOVED***i***REMOVED***:
                                end_position = i
                                break
                            elif i == len(sent***REMOVED***0***REMOVED***) - 1:
                                end_position = position
                                break
                            else:
                                i += 1
                        if end_position <= position:
                            end_position = position

                        for i in range(begin_position, end_position):
                            #if sent***REMOVED***0***REMOVED******REMOVED***i***REMOVED*** != '**PHIPostal**':
                            screened_words.append(sent***REMOVED***0***REMOVED******REMOVED***i***REMOVED***)
                            sent***REMOVED***0***REMOVED******REMOVED***i***REMOVED*** = '**PHI**'
                            safe = False

            # Begin Step 6: NLTK POS tagging
            sent_tag = nltk.pos_tag_sents(sent)
            #try:
                # senna cannot handle long sentence.
                #sent_tag = ***REMOVED******REMOVED******REMOVED******REMOVED***
                #length_100 = len(sent***REMOVED***0***REMOVED***)//100
                #for j in range(0, length_100+1):
                    #***REMOVED***sent_tag***REMOVED***0***REMOVED***.append(j) for j in pretrain.tag(sent***REMOVED***0***REMOVED******REMOVED***100*j:100*(j+1)***REMOVED***)***REMOVED***
                # hunpos needs to change the type from bytes to string
                #print(sent_tag***REMOVED***0***REMOVED***)
                #sent_tag = ***REMOVED***pretrain.tag(sent***REMOVED***0***REMOVED***)***REMOVED***
                #for j in range(len(sent_tag***REMOVED***0***REMOVED***)):
                    #sent_tag***REMOVED***0***REMOVED******REMOVED***j***REMOVED*** = list(sent_tag***REMOVED***0***REMOVED******REMOVED***j***REMOVED***)
                    #sent_tag***REMOVED***0***REMOVED******REMOVED***j***REMOVED******REMOVED***1***REMOVED*** = sent_tag***REMOVED***0***REMOVED******REMOVED***j***REMOVED******REMOVED***1***REMOVED***.decode('utf-8')
            #except:
                #print('POS error:', tail, sent***REMOVED***0***REMOVED***)
                #sent_tag = nltk.pos_tag_sents(sent)
            # Begin Step 7: Use both NLTK and Spacy to check if the word is a name based on sentence level NER label for the word.
            for ent in spcy_sent_output.ents:  # spcy_sent_output contains a dict with each word in the sentence and its NLP labels
                #spcy_sent_ouput.ents is a list of dictionaries containing chunks of words (phrases) that spacy believes are Named Entities
                # Each ent has 2 properties: text which is the raw word, and label_ which is the NER category for the word
                if ent.label_ == 'PERSON':
                #print(ent.text)
                    # if word is person, recheck that spacy still thinks word is person at the word level
                    spcy_chunk_output = nlp(ent.text)
                    if spcy_chunk_output.ents != () and spcy_chunk_output.ents***REMOVED***0***REMOVED***.label_ == 'PERSON':
                        # Now check to see what labels NLTK provides for the word
                        name_tag = word_tokenize(ent.text)
                        # senna & hunpos
                        #name_tag = pretrain.tag(name_tag)
                        # hunpos needs to change the type from bytes to string
                        #for j in range(len(name_tag)):
                            #name_tag***REMOVED***j***REMOVED*** = list(name_tag***REMOVED***j***REMOVED***)
                            #name_tag***REMOVED***j***REMOVED******REMOVED***1***REMOVED*** = name_tag***REMOVED***j***REMOVED******REMOVED***1***REMOVED***.decode('utf-8')
                        #chunked = ne_chunk(name_tag)
                        # default
                        name_tag = pos_tag_sents(***REMOVED***name_tag***REMOVED***)
                        chunked = ne_chunk(name_tag***REMOVED***0***REMOVED***)
                        for i in chunked:
                            if type(i) == Tree: # if ne_chunck thinks chunk is NER, creates a tree structure were leaves are the words in the chunk (and their POS labels) and the trunk is the single NER label for the chunk
                                if i.label() == 'PERSON':
                                    for token, pos in i.leaves():
                                        if pos == 'NNP':
                                            name_set.add(token)

                                else:
                                    for token, pos in i.leaves():
                                        spcy_upper_output = nlp(token.upper())
                                        if spcy_upper_output.ents != ():
                                            name_set.add(token)

            # BEGIN STEP 8: whitelist check
            # sent_tag is the nltk POS tagging for each word at the sentence level.
            for i in range(len(sent_tag***REMOVED***0***REMOVED***)):
                # word contains the i-th word and it's POS tag
                word = sent_tag***REMOVED***0***REMOVED******REMOVED***i***REMOVED***
                # print(word)
                # word_output is just the raw word itself
                word_output = word***REMOVED***0***REMOVED***

                if word_output not in string.punctuation:
                    word_check = str(pattern_word.sub('', word_output))
                    #if word_check.title() in ***REMOVED***'Dr', 'Mr', 'Mrs', 'Ms'***REMOVED***:
                        #print(word_check)
                        # remove the speical chars
                    try:
                        # word***REMOVED***1***REMOVED*** is the pos tag of the word

                        if (((word***REMOVED***1***REMOVED*** == 'NN' or word***REMOVED***1***REMOVED*** == 'NNP') or
                            ((word***REMOVED***1***REMOVED*** == 'NNS' or word***REMOVED***1***REMOVED*** == 'NNPS') and word_check.istitle()))):
                            if word_check.lower() not in whitelist_dict:
                                screened_words.append(word_output)
                                word_output = "**PHI**"
                                safe = False
                            else:
                                # For words that are in whitelist, check to make sure that we have not identified them as names
                                if ((word_output.istitle() or word_output.isupper()) and
                                    pattern_name.findall(word_output) != ***REMOVED******REMOVED*** and
                                    re.search(r'\b(***REMOVED***A-Z***REMOVED***)\b', word_check) is None):
                                    word_output, name_set, screened_words, safe = namecheck(word_output, name_set, screened_words, safe)

                        # check day/year according to the month name
                        elif word***REMOVED***1***REMOVED*** == 'CD':
                            if i > 2:
                                context_before = sent_tag***REMOVED***0***REMOVED******REMOVED***i-3:i***REMOVED***
                            else:
                                context_before = sent_tag***REMOVED***0***REMOVED******REMOVED***0:i***REMOVED***
                            if i <= len(sent_tag***REMOVED***0***REMOVED***) - 4:
                                context_after = sent_tag***REMOVED***0***REMOVED******REMOVED***i+1:i+4***REMOVED***
                            else:
                                context_after = sent_tag***REMOVED***0***REMOVED******REMOVED***i+1:***REMOVED***
                            #print(word_output, context_before+context_after)
                            for j in (context_before + context_after):
                                if pattern_mname.search(j***REMOVED***0***REMOVED***) is not None:
                                    screened_words.append(word_output)
                                    #print(word_output)
                                    word_output = "**PHI**"
                                    safe = False
                                    break
                        else:
                            word_output, name_set, screened_words, safe = namecheck(word_output, name_set, screened_words, safe)


                    except:
                        print(word_output, sys.exc_info())
                    if word_output.lower()***REMOVED***0***REMOVED*** == '\'s':
                        if phi_reduced***REMOVED***-7:***REMOVED*** != '**PHI**':
                            phi_reduced = phi_reduced + word_output
                        #print(word_output)
                    else:
                        phi_reduced = phi_reduced + ' ' + word_output
                # Format output for later use by eval.py
                else:
                    if (i > 0 and sent_tag***REMOVED***0***REMOVED******REMOVED***i-1***REMOVED******REMOVED***0***REMOVED******REMOVED***-1***REMOVED*** in string.punctuation and
                        sent_tag***REMOVED***0***REMOVED******REMOVED***i-1***REMOVED******REMOVED***0***REMOVED******REMOVED***-1***REMOVED*** != '*'):
                        phi_reduced = phi_reduced + word_output
                    elif word_output == '.' and sent_tag***REMOVED***0***REMOVED******REMOVED***i-1***REMOVED******REMOVED***0***REMOVED*** in ***REMOVED***'Dr', 'Mr', 'Mrs', 'Ms'***REMOVED***:
                        phi_reduced = phi_reduced + word_output
                    else:
                        phi_reduced = phi_reduced + ' ' + word_output
            #print(phi_reduced)

            # Begin Step 8: check middle initial and month name
            if pattern_mname.findall(phi_reduced) != ***REMOVED******REMOVED***:
                for item in pattern_mname.findall(phi_reduced):
                    screened_words.append(item***REMOVED***0***REMOVED***)
            phi_reduced = pattern_mname.sub('**PHI**', phi_reduced)

            if pattern_middle.findall(phi_reduced) != ***REMOVED******REMOVED***:
                for item in pattern_middle.findall(phi_reduced):
                #    print(item***REMOVED***0***REMOVED***)
                    screened_words.append(item***REMOVED***0***REMOVED***)
            phi_reduced = pattern_middle.sub('**PHI** **PHI** ', phi_reduced)
        # print(phi_reduced)

        if not safe:
            phi_containing_records = 1

        # save phi_reduced file
        filename = '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***)+"_" + key_name + ".txt"
        filepath = os.path.join(foutpath, filename)
        with open(filepath, "w") as phi_reduced_note:
            phi_reduced_note.write(phi_reduced)

        # save filtered words
        #screened_words = list(filter(lambda a: a!= '**PHI**', screened_words))
        filepath = os.path.join(foutpath,'filter_summary.txt')
        #print(filepath)
        screened_words = list(filter(lambda a: '**PHI' not in a, screened_words))
        #screened_words = list(filter(lambda a: a != '**PHI**', screened_words))
        #print(screened_words)
        with open(filepath, 'a') as fout:
            fout.write('.'.join(tail.split('.')***REMOVED***:-1***REMOVED***)+' ' + str(len(screened_words)) +
                ' ' + ' '.join(screened_words)+'\n')
            # fout.write(' '.join(screened_words))

        print(total_records, f, "--- %s seconds ---" % (time.time() - start_time_single))
        # hunpos needs to close session
        #pretrain.close()
        return total_records, phi_containing_records


def main():
    # get input/output/filename
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", default="input_test/",
                    help="Path to the directory or the file that contains the PHI note, the default is ./input_test/.",
                    type=lambda x: is_valid_file(ap, x))
    ap.add_argument("-r", "--recursive", action = 'store_true', default = False,
                    help="whether to read files in the input folder recursively.")
    ap.add_argument("-o", "--output", default="output_test/",
                    help="Path to the directory to save the PHI-reduced notes in, the default is ./output_test/.",
                    type=lambda x: is_valid_file(ap, x))
    ap.add_argument("-w", "--whitelist",
                    #default=os.path.join(os.path.dirname(__file__), 'whitelist.pkl'),
                    default=resource_filename(__name__, 'whitelist.pkl'),
                    help="Path to the whitelist, the default is phireducer/whitelist.pkl")
    ap.add_argument("-n", "--name", default="phi_reduced",
                    help="The key word of the output file name, the default is *_phi_reduced.txt.")
    ap.add_argument("-p", "--process", default=1, type=int,
                    help="The number of processes to run simultaneously, the default is 1.")
    args = ap.parse_args()

    finpath = args.input
    foutpath = args.output
    key_name = args.name
    whitelist_file = args.whitelist
    process_number = args.process
    if_dir = os.path.isdir(finpath)

    start_time_all = time.time()
    if if_dir:
        print('input folder:', finpath)
        print('recursive?:', args.recursive)
    else:
        print('input file:', finpath)
        head, tail = os.path.split(finpath)
        # f_name = re.findall(r'***REMOVED***\w\d***REMOVED***+', tail)***REMOVED***0***REMOVED***
    print('output folder:', foutpath)
    print('Using whitelist:', whitelist_file)
    try:
        with open(whitelist_file, "rb") as fin:
            whitelist = pickle.load(fin)
        print('length of whitelist: {}'.format(len(whitelist)))
        if if_dir:
            print('phi_reduced file\'s name would be:', "*_"+key_name+".txt")
        else:
            print('phi_reduced file\'s name would be:', '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***)+"_"+key_name+".txt")
        print('run in {} process(es)'.format(process_number))
    except FileNotFoundError:
        print("No whitelist is found. The script will stop.")
        os._exit(0)

    filepath = os.path.join(foutpath,'filter_summary.txt')
    with open(filepath, 'w') as fout:
        fout.write("")
    # start multiprocess
    pool = Pool(processes=process_number)

    results_list = ***REMOVED******REMOVED***
    filter_time = time.time()

    # apply_async() allows a worker to begin a new task before other works have completed their current task
    if os.path.isdir(finpath):
        if args.recursive:
            results = ***REMOVED***pool.apply_async(filter_task, (f,)+(whitelist, foutpath, key_name)) for f in glob.glob   (finpath+"/**/*.txt", recursive=True)***REMOVED***
        else:
            results = ***REMOVED***pool.apply_async(filter_task, (f,)+(whitelist, foutpath, key_name)) for f in glob.glob   (finpath+"/*.txt")***REMOVED***
    else:
        results = ***REMOVED***pool.apply_async(filter_task, (f,)+(whitelist, foutpath, key_name)) for f in glob.glob(  finpath)***REMOVED***
    try:
        results_list = ***REMOVED***r.get() for r in results***REMOVED***
        total_records, phi_containing_records = zip(*results_list)
        total_records = sum(total_records)
        phi_containing_records = sum(phi_containing_records)

        print("total records:", total_records, "--- %s seconds ---" % (time.time() - start_time_all))
        print('filter_time', "--- %s seconds ---" % (time.time() - filter_time))
        print('total records processed: {}'.format(total_records))
        print('num records with phi: {}'.format(phi_containing_records))
    except ValueError:
        print("No txt file in the input folder.")
        pass

    pool.close()
    pool.join()


    # close multiprocess


if __name__ == "__main__":
    multiprocessing.freeze_support()  # must run for windows
    main()

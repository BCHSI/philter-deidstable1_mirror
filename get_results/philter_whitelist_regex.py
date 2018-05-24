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


# configure the regex patterns
# we're going to want to remove all special characters
pattern_word = re.compile(r"[^\w+]")

# Find numbers like SSN/PHONE/FAX
# 3 patterns: 1. 6 or more digits will be filtered 2. digit followed by - followed by digit. 3. Ignore case of characters
pattern_number = re.compile(r"""\b(
(\d[\(\)\-\']?\s?){6}([\(\)\-\']?\d)+   # SSN/PHONE/FAX XXX-XX-XXXX, XXX-XXX-XXXX, XXX-XXXXXXXX, etc.
|(\d[\(\)\-.\']?){7}([\(\)\-.\']?\d)+  # test
)\b""", re.X)

pattern_4digits = re.compile(r"""\b(
\d{5}[A-Z0-9]*
)\b""", re.X)

pattern_devid = re.compile(r"""\b(
[A-Z0-9\-/]{6}[A-Z0-9\-/]*
)\b""", re.X)
# postal code
# 5 digits or, 5 digits followed dash and 4 digits
pattern_postal = re.compile(r"""\b(
\d{5}(-\d{4})?             # postal code XXXXX, XXXXX-XXXX
)\b""", re.X)

# match DOB
pattern_dob = re.compile(r"""\b(
.*?(?=\b(\d{1,2}[-./\s]\d{1,2}[-./\s]\d{2}  # X/X/XX
|\d{1,2}[-./\s]\d{1,2}[-./\s]\d{4}          # XX/XX/XXXX
|\d{2}[-./\s]\d{1,2}[-./\s]\d{1,2}          # xx/xx/xx
|\d{4}[-./\s]\d{1,2}[-./\s]\d{1,2}          # xxxx/xx/xx
)\b)
)\b""", re.X | re.I)

# match emails
pattern_email = re.compile(r"""\b(
[a-zA-Z0-9_.+-@\"]+@[a-zA-Z0-9-\:\]\[]+[a-zA-Z0-9-.]*
)\b""", re.X | re.I)

# match date, similar to DOB but does not include any words
month_name = "Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?"
pattern_date = re.compile(r"""\b(
\d{4}[\-/](0?[1-9]|1[0-2]|"""+month_name+r""")\-\d{4}[\-/](0?[1-9]|1[0-2]|"""+month_name+r""")  # YYYY/MM-YYYY/MM
|(0?[1-9]|1[0-2]|"""+month_name+r""")[\-/]\d{4}\-(0?[1-9]|1[0-2]|"""+month_name+r""")[\-/]\d{4}  # MM/YYYY-MM/YYYY
|(0?[1-9]|1[0-2]|"""+month_name+r""")/\d{2}\-(0?[1-9]|1[0-2]|"""+month_name+r""")/\d{2}  # MM/YY-MM/YY
|(0?[1-9]|1[0-2]|"""+month_name+r""")/\d{2}\-(0?[1-9]|1[0-2]|"""+month_name+r""")/\d{4}  # MM/YYYY-MM/YYYY
|(0?[1-9]|1[0-2]|"""+month_name+r""")/([1-2][0-9]|3[0-1]|0?[1-9])\-(0?[1-9]|1[0-2]|"""+month_name+r""")/([1-2][0-9]|3[0-1]|0?[1-9])  #MM/DD-MM/DD
|([1-2][0-9]|3[0-1]|0?[1-9])/(0?[1-9]|1[0-2]|"""+month_name+r""")\-([1-2][0-9]|3[0-1]|0?[1-9])/(0?[1-9]|1[0-2]|"""+month_name+r""")  #DD/MM-DD/MM
|(0?[1-9]|1[0-2]|"""+month_name+r""")[\-/\s]([1-2][0-9]|3[0-1]|0?[1-9])[\-/\s]\d{2}  # MM/DD/YY
|(0?[1-9]|1[0-2]|"""+month_name+r""")[\-/\s]([1-2][0-9]|3[0-1]|0?[1-9])[\-/\s]\d{4}  # MM/DD/YYYY
|([1-2][0-9]|3[0-1]|0?[1-9])[\-/\s](0?[1-9]|1[0-2]|"""+month_name+r""")[\-/\s]\d{2}  # DD/MM/YY
|([1-2][0-9]|3[0-1]|0?[1-9])[\-/\s](0?[1-9]|1[0-2]|"""+month_name+r""")[\-/\s]\d{4}  # DD/MM/YYYY
|\d{2}[\-./\s](0?[1-9]|1[0-2]|"""+month_name+r""")[\-\./\s]([1-2][0-9]|3[0-1]|0?[1-9])   # YY/MM/DD
|\d{4}[\-./\s](0?[1-9]|1[0-2]|"""+month_name+r""")[\-\./\s]([1-2][0-9]|3[0-1]|0?[1-9])   # YYYY/MM/DD
|\d{4}[\-/](0?[1-9]|1[0-2]|"""+month_name+r""")  # YYYY/MM
|(0?[1-9]|1[0-2]|"""+month_name+r""")[\-/]\d{4}  # MM/YYYY
|(0?[1-9]|1[0-2]|"""+month_name+r""")/\d{2}  # MM/YY
|(0?[1-9]|1[0-2]|"""+month_name+r""")/\d{2}  # MM/YYYY
|(0?[1-9]|1[0-2]|"""+month_name+r""")/([1-2][0-9]|3[0-1]|0?[1-9])  #MM/DD
|([1-2][0-9]|3[0-1]|0?[1-9])/(0?[1-9]|1[0-2]|"""+month_name+r""")  #DD/MM
)\b""", re.X | re.I)
pattern_mname = re.compile(r'\b(' + month_name + r')\b')

# match names, A'Bsfs, Absssfs, A-Bsfsfs
pattern_name = re.compile(r"""^[A-Z]\'?[-a-zA-Z]+$""")

# match age
pattern_age = re.compile(r"""\b(
age|year[s-]?\s?old|y.o[.]?
)\b""", re.X | re.I)

# match salutation
pattern_salutation = re.compile(r"""
(Dr\.|Mr\.|Mrs\.|Ms\.|Miss|Sir|Madam)\s
(([A-Z]\'?[A-Z]?[\-a-z]+(\s[A-Z]\'?[A-Z]?[\-a-z]+)*)
)""", re.X)

# match middle initial
# if single char or Jr is surround by 2 phi words, filter. 
pattern_middle = re.compile(r"""\*\*PHI\*\*,? (([A-CE-LN-Z][Rr]?|[DM])\.?) | (([A-CE-LN-Z][Rr]?|[DM])\.?),? \*\*PHI\*\*""")


# match url
pattern_url = re.compile(r'\b((http[s]?://)?([a-zA-Z0-9$-_@.&+:!\*\(\),])*[\.\/]([a-zA-Z0-9$-_@.&+:\!\*\(\),])*)\b', re.I)


# check if the folder exists
def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The folder %s does not exist. Please input a new folder or create one." % arg)
    else:
        return arg


def filter_task(f, whitelist_dict, foutpath, key_name):
    with open(f, encoding='utf-8', errors='ignore') as fin:
        # define intial variables
        head, tail = os.path.split(f)
        #f_name = re.findall(r'[\w\d]+', tail)[0]  # get the file number
        print(tail)
        start_time_single = time.time()
        total_records = 1
        phi_containing_records = 0
        safe = True
        screened_words = []
        name_set = set()
        phi_reduced = ''

        address_indictor = ['street', 'avenue', 'road', 'boulevard',
                            'drive', 'trail', 'way', 'lane', 'ave',
                            'blvd', 'st', 'rd', 'trl', 'wy', 'ln',
                            'court', 'ct', 'place', 'plc', 'terrace', 'ter',
                            'highway', 'freeway', 'autoroute', 'autobahn', 'expressway',
                            'autostrasse', 'autostrada', 'byway', 'auto-estrada', 'motorway',
                            'avenue', 'boulevard', 'road', 'street', 'alley', 'bay', 'drive',
                            'gardens', 'gate', 'grove', 'heights', 'highlands', 'lane', 'mews',
                            'pathway', 'terrace', 'trail', 'vale', 'view', 'walk', 'way', 'close',
                            'court', 'place', 'cove', 'circle', 'crescent', 'square', 'loop', 'hill',
                            'causeway', 'canyon', 'parkway', 'esplanade', 'approach', 'parade', 'park',
                            'plaza', 'promenade', 'quay', 'bypass']

        note = fin.read()
        note = re.sub(r'=', ' = ', note)

        # Begin Step 1: saluation check
        re_list = pattern_salutation.findall(note)
        for i in re_list:
            name_set = name_set | set(i[1].split(' '))

        note = sent_tokenize(note)
        for sent in note:
            # Begin Step 3: Pattern checking
            
            if pattern_postal.findall(sent) != []:
                safe = False
                for item in pattern_postal.findall(sent):
                    screened_words.append(item[0])
            sent = str(pattern_postal.sub('**PHIPostal**', sent))

            if pattern_devid.findall(sent) != []:
                safe = False
                for item in pattern_devid.findall(sent):
                    if (re.search(r'\d', item) is not None and
                        re.search(r'[A-Z]',item) is not None):
                        screened_words.append(item)
                        sent = sent.replace(item, '**PHI**')

            # number check
            if pattern_number.findall(sent) != []:
                safe = False
                for item in pattern_number.findall(sent):
                    # print(item)
                    #if pattern_date.match(item[0]) is None:
                    sent = sent.replace(item[0], '**PHI**')
                    screened_words.append(item[0])

            data_list = []
            if pattern_date.findall(sent) != []:
                safe = False
                for item in pattern_date.findall(sent):
                    if '-' in item[0]:
                        if (len(set(re.findall(r'[^\w\-]',item[0]))) <= 1):
                            #screened_words.append(item[0])
                            #print(item[0])
                            data_list.append(item[0])
                            #sent = sent.replace(item[0], '**PHIDate**')
                    else:
                        if len(set(re.findall(r'[^\w]',item[0]))) == 1:
                            #screened_words.append(item[0])
                            #print(item[0])
                            data_list.append(item[0])
                            #sent = sent.replace(item[0], '**PHIDate**')
            data_list.sort(key=len, reverse=True) 
            for item in data_list:
                sent = sent.replace(item, '**PHIDate**')

            #sent = str(pattern_date.sub('**PHI**', sent))
            #print(sent)
            if pattern_4digits.findall(sent) != []:
                safe = False
                for item in pattern_4digits.findall(sent):
                    screened_words.append(item)
            sent = str(pattern_4digits.sub('**PHI**', sent))
            # email check
            if pattern_email.findall(sent) != []:
                safe = False
                for item in pattern_email.findall(sent):
                    screened_words.append(item)
            sent = str(pattern_email.sub('**PHI**', sent))
            # url check
            if pattern_url.findall(sent) != []:
                safe = False
                for item in pattern_url.findall(sent):
                    #print(item[0])
                    if (re.search(r'[a-z]', item[0]) is not None and
                        '.' in item[0] and
                        re.search(r'[A-Z]', item[0]) is None and
                        len(item[0])>10):
                        print(item[0])
                        screened_words.append(item[0])
                        sent = sent.replace(item[0], '**PHI**')

            # Begin Step 4
            sent = re.sub(r'[\/\-\:\~\_]', ' ', sent)
            sent = [word_tokenize(sent)]
            

            # Begin Step 5: context level pattern matching with regex 
            for position in range(0, len(sent[0])):
                word = sent[0][position]
                # age check
                if word.isdigit() and int(word) > 90:
                    if position <= 2:  # check the words before age
                        word_previous = ' '.join(sent[0][:position])
                    else:
                        word_previous = ' '.join(sent[0][position - 2:position])
                    if position >= len(sent[0]) - 2:  # check the words after age
                        word_after = ' '.join(sent[0][position+1:])
                    else:
                        word_after = ' '.join(sent[0][position+1:position +3])

                    age_string = str(word_previous) + str(word_after)
                    if pattern_age.findall(age_string) != []:
                        screened_words.append(sent[0][position])
                        sent[0][position] = '**PHI**'
                        safe = False

                # address check
                elif (position >= 1 and position < len(sent[0])-1 and
                      (word.lower() in address_indictor or
                       (word.lower() == 'dr' and sent[0][position+1] != '.')) and
                      (word.istitle() or word.isupper())):

                    if sent[0][position - 1].istitle() or sent[0][position-1].isupper():
                        screened_words.append(sent[0][position - 1])
                        sent[0][position - 1] = '**PHI**'
                        i = position - 1
                        # find the closet number, should be the number of street
                        while True:
                            if re.findall(r'^[\d-]+$', sent[0][i]) != []:
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
                            if '**PHIPostal**' in sent[0][i]:
                                end_position = i
                                break
                            elif i == len(sent[0]) - 1:
                                end_position = position
                                break
                            else:
                                i += 1
                        if end_position <= position:
                            end_position = position

                        for i in range(begin_position, end_position):
                            #if sent[0][i] != '**PHIPostal**':
                            screened_words.append(sent[0][i])
                            sent[0][i] = '**PHI**'
                            safe = False


            sent_tag = nltk.pos_tag_sents(sent)
            for i in range(len(sent_tag[0])):
                # Get word
                word = sent_tag[0][i]
                # print(word)
                # word_output is just the raw word itself
                word_output = word[0]


                if word_output not in string.punctuation:
                    word_check = str(pattern_word.sub('', word_output))
                    #if word_check.title() in ['Dr', 'Mr', 'Mrs', 'Ms']:
                        #print(word_check)
                        # remove the speical chars
                    try:

                        if word_check.lower() not in whitelist_dict:
                            screened_words.append(word_output)
                            word_output = "**PHI**"
                            safe = False

                    except:
                        print(word_output, sys.exc_info())
                    
                    if word_output.lower()[0] == '\'s':
                        if phi_reduced[-7:] != '**PHI**':
                            phi_reduced = phi_reduced + word_output
                        #print(word_output)
                    else:
                        phi_reduced = phi_reduced + ' ' + word_output
                # Format output for later use by eval.py
                else:
                    if (i > 0 and sent_tag[0][i-1][0][-1] in string.punctuation and
                        sent_tag[0][i-1][0][-1] != '*'):
                        phi_reduced = phi_reduced + word_output
                    elif word_output == '.' and sent_tag[0][i-1][0] in ['Dr', 'Mr', 'Mrs', 'Ms']:
                        phi_reduced = phi_reduced + word_output
                    else:
                        phi_reduced = phi_reduced + ' ' + word_output                 

            # Begin Step 8: check middle initial and month name
            if pattern_mname.findall(phi_reduced) != []:
                for item in pattern_mname.findall(phi_reduced):
                    screened_words.append(item[0])
            phi_reduced = pattern_mname.sub('**PHI**', phi_reduced)

            if pattern_middle.findall(phi_reduced) != []:
                for item in pattern_middle.findall(phi_reduced):
                #    print(item[0])
                    screened_words.append(item[0])
            phi_reduced = pattern_middle.sub('**PHI** **PHI** ', phi_reduced)

        if not safe:
            phi_containing_records = 1

        # save phi_reduced file
        filename = '.'.join(tail.split('.')[:-1])+"_" + key_name + ".txt"
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
            fout.write('.'.join(tail.split('.')[:-1])+' ' + str(len(screened_words)) +
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
        # f_name = re.findall(r'[\w\d]+', tail)[0]
    print('output folder:', foutpath)
    print('Using whitelist:', whitelist_file)
    try:
        try:
            with open(whitelist_file, "rb") as fin:
                whitelist = pickle.load(fin)
        except UnicodeDecodeError:
            with open(whitelist_file, "rb") as fin:
                whitelist = pickle.load(fin, encoding = 'latin1')
        print('length of whitelist: {}'.format(len(whitelist)))
        if if_dir:
            print('phi_reduced file\'s name would be:', "*_"+key_name+".txt")
        else:
            print('phi_reduced file\'s name would be:', '.'.join(tail.split('.')[:-1])+"_"+key_name+".txt")
        print('run in {} process(es)'.format(process_number))
    except FileNotFoundError:
        print("No whitelist is found. The script will stop.")
        os._exit(0)

    filepath = os.path.join(foutpath,'filter_summary.txt')
    with open(filepath, 'w') as fout:
        fout.write("")
    # start multiprocess
    pool = Pool(processes=process_number)

    results_list = []
    filter_time = time.time()

    # apply_async() allows a worker to begin a new task before other works have completed their current task
    if os.path.isdir(finpath):
        if args.recursive:
            results = [pool.apply_async(filter_task, (f,)+(whitelist, foutpath, key_name)) for f in glob.glob   (finpath+"/**/*.txt", recursive=True)]
        else:
            results = [pool.apply_async(filter_task, (f,)+(whitelist, foutpath, key_name)) for f in glob.glob   (finpath+"/*.txt")]
    else:
        results = [pool.apply_async(filter_task, (f,)+(whitelist, foutpath, key_name)) for f in glob.glob(  finpath)]
    try:
        results_list = [r.get() for r in results]
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
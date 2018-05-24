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


pattern_word = re.compile(r"[^\w+]")

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

        note = fin.read()
        note = re.sub(r'=', ' = ', note)

        note = sent_tokenize(note)
        for sent in note: # Begin Step 3: Pattern checking
            sent = [word_tokenize(sent)]
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
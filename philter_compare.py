from nltk import sent_tokenize
from nltk import word_tokenize
import argparse
from string import punctuation
import pickle
import os
import re
import glob
import random
from difflib import ndiff

"""
Compare two annotated files

"""


def compare(anno1, anno2, anno1_path, anno2_path):
    """
    Does:

    Uses:

    Arguments:

    Returns:

    """
    category_dict = {'0':'safe', '1':'philtered', '2':'False positive', 'n':'Name', 'l':'Location', 'd':'Date', 
                    'c':'Contact', 'i':'ID', 'a':'Age(>90)', 'o':'Others', 'punc':'Punctuation'}

    for i in range(len(anno1)):
        assert anno1***REMOVED***i***REMOVED******REMOVED***0***REMOVED*** == anno2***REMOVED***i***REMOVED******REMOVED***0***REMOVED***
        if anno1***REMOVED***i***REMOVED******REMOVED***1***REMOVED*** != anno2***REMOVED***i***REMOVED******REMOVED***1***REMOVED***:
            context_before = ***REMOVED******REMOVED***
            context_after = ***REMOVED******REMOVED***
            if i >= 5:
                ***REMOVED***context_before.append(word***REMOVED***0***REMOVED***) for word in anno1***REMOVED***i-5:i***REMOVED******REMOVED***
            else:
                ***REMOVED***context_before.append(word***REMOVED***0***REMOVED***) for word in anno1***REMOVED***0:i***REMOVED******REMOVED***
            if i < len(anno1)-5:
                ***REMOVED***context_after.append(word***REMOVED***0***REMOVED***) for word in anno1***REMOVED***i+1:i+6***REMOVED******REMOVED***
            else:
                ***REMOVED***context_after.append(word***REMOVED***0***REMOVED***) for word in anno1***REMOVED***i+1:(len(anno1)-1)***REMOVED******REMOVED***
            print(' '.join(context_before), '***REMOVED***', anno1***REMOVED***i***REMOVED******REMOVED***0***REMOVED***, '***REMOVED***', ' '.join(context_after))
            print(anno1_path ,':', category_dict***REMOVED***anno1***REMOVED***i***REMOVED******REMOVED***1***REMOVED******REMOVED***)
            print(anno2_path ,':', category_dict***REMOVED***anno2***REMOVED***i***REMOVED******REMOVED***1***REMOVED******REMOVED***)


def main():
    """
Does:

Uses:

Arguments:

Returns:

    """

    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--anno", required=True,
                    help="Path to the file 1 you would like to compare.")
    ap.add_argument("-c", "--compare", required=True,
                    help="Path to the file 2 you would like to compare.")
    ap.add_argument("-r", "--random", action='store_true',
                   help="In random mode, the script will randomly choose a file in the input folder to annotate")

    args = ap.parse_args()
    # print(args.random)
    anno1_path = args.anno
    anno2_path = args.compare

    if not os.path.isfile(anno1_path):
        print('{} is not a file or does not exist.'.format(anno1_path))
        os._exit(0)
    elif not os.path.isfile(anno2_path):
        print('{} is not a file or does not exist.'.format(anno2_path))
        os._exit(0)
    else:
        head, tail = os.path.split(anno1_path)
        if tail.split('.')***REMOVED***-1***REMOVED*** != 'ano':
            print('{} is not a annottaion.'.format(anno1_path))
            os._exit(0)
        head, tail = os.path.split(anno2_path)
        if tail.split('.')***REMOVED***-1***REMOVED*** != 'ano':
            print('{} is not a annottaion.'.format(anno2_path))
            os._exit(0)
        with open(anno1_path, 'rb') as fin:
            anno1 = pickle.load(fin)
        with open(anno2_path, 'rb') as fin:
            anno2 = pickle.load(fin)
        if len(anno1) != len(anno2):
            print('Two annotation files\' content do not match.')
            os._exit(0)
        else:
            compare(anno1, anno2, anno1_path, anno2_path)


if __name__ == "__main__":
    main()

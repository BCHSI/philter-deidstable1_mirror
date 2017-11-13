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


def compare(anno1, anno2, anno1_path, anno2_path, mode):
    """
    Does:

    Uses:

    Arguments:

    Returns:

    """
    category_dict = {'0':'safe', '1':'philtered', '2':'False positive', 'n':'Name', 'l':'Location', 'd':'Date', 
                    'c':'Contact', 'i':'ID', 'a':'Age(>90)', 'o':'Others', 'punc':'Punctuation'}
    difference_list = []


    if mode == 'detail':
        index_number = 1
        for i in range(len(anno1)):
            assert anno1[i][0] == anno2[i][0]
            if anno1[i][1] != anno2[i][1]:
                context_before = []
                context_after = []
                if i >= 5:
                    [context_before.append(word[0]) for word in anno1[i-5:i]]
                else:
                    [context_before.append(word[0]) for word in anno1[0:i]]
                if i < len(anno1)-5:
                    [context_after.append(word[0]) for word in anno1[i+1:i+6]]
                else:
                    [context_after.append(word[0]) for word in anno1[i+1:(len(anno1)-1)]]
                print('word_number:', index_number)
                index_number += 1
                print(' '.join(context_before), '[', anno1[i][0], ']', ' '.join(context_after))
                print(anno1_path ,':', category_dict[anno1[i][1]])
                print(anno2_path ,':', category_dict[anno2[i][1]])
                print('')
                difference_list.append(i)
        return difference_list
    elif mode == 'general':
        counts = 0
        for i in range(len(anno1)):
            assert anno1[i][0] == anno2[i][0]
            if anno1[i][1] != anno2[i][1]:
                counts += 1
        return counts


def change(anno1, anno2, anno1_path, anno2_path):
    category_fn = 'Category of False Negative: 0:Philter safe, n:Name, l:Location, d:Date, c:Contact, i:ID, a:Age(>90), o:Others'
    allowed_category = ('n', 'l', 'd', 'c', 'i', 'a', 'o', '0')
    while True:
        difference_list = compare(anno1, anno2, anno1_path, anno2_path, 'detail')
        if len(difference_list) == 0:
            print('No more difference. Will quit.\n')
            break
        else:
            word_index = input('Please input the word number you want to change, press d to exit:')
            if word_index == 'd':
                break
            elif str.isdigit(word_index) and int(word_index) - 1  in list(range(len(difference_list))):
                # print(difference_list)
                print('Word:', anno1[difference_list[int(word_index) - 1]][0])
                print(category_fn)
                user_input = input('which phi-category do you want to assign to these words? > ')
                if user_input in allowed_category:
                    anno1[difference_list[int(word_index) - 1]][1] = user_input
                    anno2[difference_list[int(word_index) - 1]][1] = user_input
                    with open(anno1_path, 'wb') as fout:
                        pickle.dump(anno1, fout)
                    with open(anno2_path, 'wb') as fout:
                        pickle.dump(anno2, fout)
                    print('')
                else:
                    print('Wrong category.\n')
            else:
                print('Wrong input.\n')
                continue

def compare_all(dir1, dir2, check_list):
    dir1_set = set()
    dir2_set = set()
    same_set = set()
    total_counts = 0
    diff_list = []
    diff_dict = {}

    if check_list == []:
        for f in glob.glob(os.path.join(dir1, '*.ano')):
            head, tail = os.path.split(f)
            dir1_set.add(tail)
        for f in glob.glob(os.path.join(dir2, '*.ano')):
            head, tail = os.path.split(f)
            dir2_set.add(tail)

        same_set = dir1_set & dir2_set

        for f in same_set:
            anno1_path = os.path.join(dir1, f)
            anno2_path = os.path.join(dir2, f)
            with open(anno1_path, 'rb') as fin:
                anno1 = pickle.load(fin)
            with open(anno2_path, 'rb') as fin:
                anno2 = pickle.load(fin)
            counts = compare(anno1, anno2, anno1_path, anno2_path, 'general')
            if counts > 0:
                total_counts += 1
                diff_dict[f] = counts
                diff_list.append(f)

        print('{} files are same and have been compared.\n'.format(len(same_set)))
        print('{} files have different annotation.\n'.format(len(diff_list)))
        for i in range(len(diff_list)):
            file_name = diff_list[i]
            print('index:',i+1)
            print('file name: {}, number of different annotation: {}\n'.format(file_name, diff_dict[file_name]))

    else:
        for f in check_list:
            anno1_path = os.path.join(dir1, f)
            anno2_path = os.path.join(dir2, f)
            with open(anno1_path, 'rb') as fin:
                anno1 = pickle.load(fin)
            with open(anno2_path, 'rb') as fin:
                anno2 = pickle.load(fin)
            counts = compare(anno1, anno2, anno1_path, anno2_path, 'general')
            if counts > 0:
                total_counts += 1
                diff_dict[f] = counts
                diff_list.append(f)

        print('{} files still have different annotation.\n'.format(len(diff_list)))
        for i in range(len(diff_list)):
            file_name = diff_list[i]
            print('index:',i+1)
            print('file name: {}, number of different annotation: {}\n'.format(file_name, diff_dict[file_name]))

    return diff_list


def main():
    """
Does:

Uses:

Arguments:

Returns:

    """

    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--anno", required=True,
                    help="Path to the folder 1 you would like to compare.")
    ap.add_argument("-c", "--compare", required=True,
                    help="Path to the folder 2  you would like to compare.")
    ap.add_argument("-r", "--random", action='store_true',
                   help="In random mode, the script will randomly choose a file in the input folder to annotate")

    args = ap.parse_args()
    # print(args.random)
    anno1_dir = args.anno
    anno2_dir = args.compare

    if not os.path.isdir(anno1_dir):
        print('{} is not a file or does not exist.'.format(anno1_path))
        os._exit(0)
    elif not os.path.isdir(anno2_dir):
        print('{} is not a file or does not exist.'.format(anno2_path))
        os._exit(0)
    else:
        check_list = []
        while True:
            diff_list = compare_all(anno1_dir, anno2_dir, check_list)
            user_input = input('Please enter the index of the files you want to check/change, press anything else to exit:')
            print('')

            if str.isdigit(user_input) and int(user_input) - 1 in list(range(len(diff_list))):
                file_name = diff_list[int(user_input) - 1]
                anno1_path = os.path.join(anno1_dir, file_name)
                anno2_path = os.path.join(anno2_dir, file_name)
                with open(anno1_path, 'rb') as fin:
                    anno1 = pickle.load(fin)
                with open(anno2_path, 'rb') as fin:
                    anno2 = pickle.load(fin)
                change(anno1, anno2, anno1_path, anno2_path)
                check_list = diff_list
            else:
                print('Quiting.')
                os._exit(0)




if __name__ == "__main__":
    main()

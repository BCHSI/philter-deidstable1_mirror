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
Annotate each word in a text file as either being PHI (if so, annotate the type of PHI)
or not.

When the program launches, each word from the input file is displayed preceded by it's word index for reference, one sentence
at a time.

Labels each word as a category of PHI (not-phi is an option). Writes the annotated file out as a list of lists
Into a pickle file with the original file name and .ano as the file extention.
Each sublist contains 2 elements: ***REMOVED***word_from_original_text, phi_label***REMOVED***

This is useful to generate a ground-truth corpus for the evaluation of the phi-reducer
software on your own files, or for the creation of a training corpus for machine learning de-id
methods.

"""
def annotating(note, phifile):

    """
    Does:Labels each word as a category of PHI (not-phi is an option). Takes document splits into sentences. Takes sentences splits in
    words and ignores words that are only punctuation. Takes output (words) and allows
    user to assign a phi-category to a single word or group of words (depending on the command mode).
    Takes words splits on special characters, and assigns the phi-category of the parent to each of the children.  

    Uses:
    nltk.sent_tokenize: Splits a file into sentence-by-sentence chunks.
    nltk.word_tokenize: Splits a sentence in word-by-word chunks.
    string.punctuation: Checks characters to see if they are punctuation. Punctuation is displayed for annotation
    but will be defined as non-phi within the annotated file
    re: Some words contain special characters such as '-' or '/'. The phi-reducer script splits words on these
    characters as filters each subword independently. RE are used to also split words for annotation on special characters

    Arguments: none

    Returns:

    """
    annotation_list = ***REMOVED******REMOVED***
    philter_phi = ***REMOVED******REMOVED***
    question_mark = ***REMOVED******REMOVED***
    note = re.sub(r'***REMOVED***\/\-\:\~\_***REMOVED***', ' ', note)
    notelist = word_tokenize(note)
    notelist = ***REMOVED***word for word in notelist if word != ''***REMOVED***
    for i in range(len(notelist)):
        if len(notelist***REMOVED***i***REMOVED***) > 1 and notelist***REMOVED***i***REMOVED******REMOVED***-1***REMOVED*** in punctuation:
            notelist***REMOVED***i***REMOVED*** = notelist***REMOVED***i***REMOVED******REMOVED***:-1***REMOVED***
    phifile = word_tokenize(phifile)
    phifile = ***REMOVED***word for word in phifile if '**PHI' not in word and word != ''***REMOVED***
    for i in range(len(phifile)):
        if len(phifile***REMOVED***i***REMOVED***) > 1 and phifile***REMOVED***i***REMOVED******REMOVED***-1***REMOVED*** in punctuation:
            phifile***REMOVED***i***REMOVED*** = phifile***REMOVED***i***REMOVED******REMOVED***:-1***REMOVED***
    #print(notelist)
    #print(phifile)
    note = ''
    for word_index, marker_and_word in enumerate(ndiff(notelist, phifile)):
        #print(word_index, marker_and_word)
        #if marker_and_word***REMOVED***0***REMOVED*** == '+' and re.findall(r'\w+', marker_and_word***REMOVED***2:***REMOVED***) != ***REMOVED******REMOVED***:
            #question_mark.append(marker_and_word***REMOVED***2:***REMOVED***)
        if marker_and_word***REMOVED***0***REMOVED*** == '-' and re.findall(r'\w+', marker_and_word***REMOVED***2:***REMOVED***) != ***REMOVED******REMOVED***:
            philter_phi.append(marker_and_word***REMOVED***2:***REMOVED***)
            note += '**PHI-' + marker_and_word***REMOVED***2:***REMOVED*** + '** '
        elif marker_and_word***REMOVED***0***REMOVED*** == '+':
            note = note
        else:
            note += marker_and_word***REMOVED***2:***REMOVED*** + ' '

    #print(philter_phi)
    #print(question_mark)
    allowed_category = ('n', 'l', 'd', 'c', 'i', 'a', 'o')
    allowed_command = ('exit', 'h', 'c', 'd', 'p', 's')
    category_fn = 'Category of False Negative: 0:Philter safe, n:Name, l:Location, d:Date, c:Contact, i:ID, a:Age(>90), o:Others'
    category_dict = {'0':'safe', '1':'philtered', '2':'False positive', 'n':'Name', 'l':'Location', 'd':'Date', 'c':'Contact', 'i':'ID', 'a':'Age(>90)', 'o':'Others', 'punc':'Punctuation'}
    note = sent_tokenize(note)
    sent_list = ***REMOVED******REMOVED***

    for i in range(len(note)):
        # sent_list: list of words that have not yet been divided by special characters
        #print(sent)
        #print(sent)
        sent = note***REMOVED***i***REMOVED***
        words = word_tokenize(sent)
        word = ***REMOVED***word for word in words if word not in punctuation***REMOVED***
        default_length = len(sent_list)
        #print('***********************************************************************')
        #print(sent)
        #print('')
        for j in range(len(word)):
            if '**PHI' in word***REMOVED***j***REMOVED***:
                try:
                    phi_word = re.findall(r'\*\*PHI\-(.*)\*\*', word***REMOVED***j***REMOVED***)***REMOVED***0***REMOVED***
                    sent_list.append(***REMOVED***phi_word, '1', default_length+j + 1***REMOVED***)
                except IndexError:
                    phi_word = re.findall(r'\*\*PHI\-(.*)', word***REMOVED***j***REMOVED***)***REMOVED***0***REMOVED***
                    sent_list.append(***REMOVED***phi_word, '1', default_length+j + 1***REMOVED***)
            else:
                sent_list.append(***REMOVED***word***REMOVED***j***REMOVED***, '0', default_length+j + 1***REMOVED***)
        # display the sentence with the index of each word and the current category assigned to each word
        # temp***REMOVED***2***REMOVED***: index, temp***REMOVED***0***REMOVED***:word, temp***REMOVED***1***REMOVED***:phi-category
        #print(sent)
        #***REMOVED***print("({}){}***REMOVED***{}***REMOVED***".format(temp***REMOVED***2***REMOVED***, temp***REMOVED***0***REMOVED***, temp***REMOVED***1***REMOVED***), end=' ') for temp in sent_list***REMOVED***
        #print('\n')
        #print(category_print)

        if len(sent_list) < 100 and i != len(note) - 1:
            sent_list.append(***REMOVED***'.', 'punc', len(sent_list)***REMOVED***)
            continue
        else:
            print('\n')
            temp_sent = ''
            for temp in sent_list:
                if temp***REMOVED***1***REMOVED*** == '0':
                    #safe_list.append(temp***REMOVED***0***REMOVED***)
                    temp_sent += temp***REMOVED***0***REMOVED***+' '
                elif temp***REMOVED***1***REMOVED*** == '2':
                    #fp_list.append(temp***REMOVED***0***REMOVED***)
                    temp_sent += temp***REMOVED***0***REMOVED***+' '
                elif temp***REMOVED***1***REMOVED*** == 'punc':
                    temp_sent += temp***REMOVED***0***REMOVED***+ ' '
                else:
                    #phi_list.append(temp***REMOVED***0***REMOVED***)
                    temp_sent += '**PHI-'+temp***REMOVED***0***REMOVED***+'** '
            print('***********************************************************************')
            #print(sent_list)
            #print(len(sent_list))
            print(temp_sent)
            print('\n')
            while True:
                user_input = input('Please input command (enter \'h\' for more info): ')

                if user_input not in allowed_command:
                    print("Command is not right, please re-input.")

                else:
                    if user_input == 'exit':
                        print('Quitting without saving...')
                        return ***REMOVED******REMOVED***

                    elif user_input == 'p':
                        allowed_position = ***REMOVED******REMOVED***
                        for temp in sent_list:
                            if temp***REMOVED***1***REMOVED*** == '1' or temp***REMOVED***1***REMOVED*** in allowed_category:
                                print("({}){}***REMOVED***{}***REMOVED***\n".format(temp***REMOVED***2***REMOVED***, temp***REMOVED***0***REMOVED***, temp***REMOVED***1***REMOVED***))
                                allowed_position.append(temp***REMOVED***2***REMOVED***)
                        if len(allowed_position) != 0:
                            user_input = input('which words do you want to assign to non-phi? seperated by space, press enter to quit: > ')
                            if user_input == '':
                                continue
                            else:
                                user_input = user_input.split(' ')
                                for position in user_input:
                                    if position.isdigit() and int(position) in allowed_position:
                                        sent_list***REMOVED***int(position)-1***REMOVED******REMOVED***1***REMOVED*** = '2'
                                    else:
                                        print('{} is not a right position.'.format(position))
                        else:
                            print('No philtered word in this sentence.')


                    elif user_input == 'c':
                        for temp in sent_list:
                            if temp***REMOVED***1***REMOVED*** != list:
                                print("({}){}***REMOVED***{}***REMOVED***".format(temp***REMOVED***2***REMOVED***, temp***REMOVED***0***REMOVED***, category_dict***REMOVED***temp***REMOVED***1***REMOVED******REMOVED***), end=' ')
                            else:
                                multiple_anno = ***REMOVED******REMOVED***
                                for j in temp***REMOVED***1***REMOVED***:
                                    multiple_anno.append(category_dict***REMOVED***j***REMOVED***)
                                print("({}){}***REMOVED***{}***REMOVED***".format(temp***REMOVED***2***REMOVED***, temp***REMOVED***0***REMOVED***, multiple_anno), end=' ')
                        #***REMOVED***print("({}){}***REMOVED***{}***REMOVED***".format(temp***REMOVED***2***REMOVED***, temp***REMOVED***0***REMOVED***, temp***REMOVED***1***REMOVED***), end=' ') for temp in sent_list***REMOVED***
                        print('\n')
                        print(category_fn)
                        user_input = input('which words are you going to edit, seperated by space, press enter to quit: ')
                        if user_input == '':
                            continue
                        else:
                            pick_list = user_input.split(' ')
                            user_input = input('which phi-category do you want to assign to these words? > ')
                            if user_input in allowed_category:
                                input_category = user_input
                                for j in pick_list:
                                    if j.isdigit() and 0 < int(j) <= len(sent_list):
                                        # check if the word contain special character and will be splitted later
                                        # if so, check if different categories would be assigned.
                                        if re.findall(r'***REMOVED***\/\-\:\~\_***REMOVED***', sent_list***REMOVED***int(j) - 1***REMOVED******REMOVED***0***REMOVED***) != ***REMOVED******REMOVED***:
                                            response_split = input('{} contains multiple elements. Do you want to annotate them seperately? press y to assign       seperately, others to assign the same.'.format(sent_list***REMOVED***int(j) - 1***REMOVED******REMOVED***0***REMOVED***))
                                            split_category = ***REMOVED******REMOVED***
                                            if response_split == 'y':
                                                temp = re.sub(r'***REMOVED***\/\-\:\~\_***REMOVED***', ' ', sent_list***REMOVED***int(j) - 1***REMOVED******REMOVED***0***REMOVED***)
                                                temp = temp.split(' ')
                                                temp = list(filter(None, temp))
                                                for k in temp:
                                                    split_input = input('the phi-category of {} is:'.format(k))
                                                    if split_input in allowed_category:
                                                        split_category.append(split_input)
                                                    else:
                                                        print('Input is not correct. Will assign non-phi to {}'.format(k))
                                                        split_category.append('0')
                                                sent_list***REMOVED***int(j) - 1***REMOVED******REMOVED***1***REMOVED*** = split_category
                                            else:
                                                #split_category.append(input_category)
                                                sent_list***REMOVED***int(j) - 1***REMOVED******REMOVED***1***REMOVED*** = input_category
                                        else:
                                            sent_list***REMOVED***int(j) - 1***REMOVED******REMOVED***1***REMOVED*** = input_category
                                        print('{} is changed.'.format(sent_list***REMOVED***int(j) - 1***REMOVED******REMOVED***0***REMOVED***))
                                    else:
                                        print('{} is not a right sequence'.format(j))
                            else:
                                print('Wrong category. Will go back to the word you were editing.')

                    elif user_input == 's':

                        temp_sent = ''
                        for temp in sent_list:
                            if temp***REMOVED***1***REMOVED*** == '0':
                                temp_sent += temp***REMOVED***0***REMOVED***+' '
                            elif temp***REMOVED***1***REMOVED*** == '2':
                                temp_sent += temp***REMOVED***0***REMOVED***+' '
                            elif temp***REMOVED***1***REMOVED*** == 'punc':
                                temp_sent += temp***REMOVED***0***REMOVED***+' '
                            else:
                                temp_sent += '**PHI-'+temp***REMOVED***0***REMOVED***+'** '
                        print('***********************************************************************')
                        print(temp_sent)
                        print('\n')
                        # display the sentence with the index of each word and the current category assigned to each word
                        # temp***REMOVED***2***REMOVED***: index, temp***REMOVED***0***REMOVED***:word, temp***REMOVED***1***REMOVED***:phi-category
                        #***REMOVED***print("({}){}***REMOVED***{}***REMOVED***".format(temp***REMOVED***2***REMOVED***, temp***REMOVED***0***REMOVED***, temp***REMOVED***1***REMOVED***), end=' ') for temp in sent_list***REMOVED***
                        #print('\n\n', category_print)
                        #print('\n')
                    elif user_input == 'd':
                        for result in sent_list:
                            # divide words by special characters, replace special chars with space: ' '
                            if result***REMOVED***1***REMOVED*** == 'punc':
                                continue
                            elif re.findall(r'***REMOVED***\/\-\:\~\_***REMOVED***', result***REMOVED***0***REMOVED***) != ***REMOVED******REMOVED***:
                                temp = re.sub(r'***REMOVED***\/\-\:\~\_***REMOVED***', ' ', result***REMOVED***0***REMOVED***)
                            # take each new 'sub-word'
                                temp = temp.split(' ')
                                temp = list(filter(None, temp))
                            # sub-word inherits the parent-word's phi-category
                                if type(result***REMOVED***1***REMOVED***) == list:
                                    for j in range(len(temp)):
                                        annotation_list.append(***REMOVED***temp***REMOVED***j***REMOVED***, result***REMOVED***1***REMOVED******REMOVED***j***REMOVED******REMOVED***)
                                else:
                                    for j in range(len(temp)):
                                        annotation_list.append(***REMOVED***temp***REMOVED***j***REMOVED***, result***REMOVED***1***REMOVED******REMOVED***)
                            else:
                                annotation_list.append(***REMOVED***result***REMOVED***0***REMOVED***, result***REMOVED***1***REMOVED******REMOVED***)
                        print("\n")
                        sent_list = ***REMOVED******REMOVED***
                        break

                    elif user_input == 'h':
                        print('(X)WORD***REMOVED***Y***REMOVED***: X is the sequence number of the word,'
                            ' Y is the current phi-category of the word. All words'
                            ' will be set to 0, non-phi, as default.')
                        print('Command:')
                        print('p: enter \'s\' to show all the phi words and choose to assigne as non-phi')
                        print('n: enter \'n\' to show all the words and choose words to assign')
                        print('s: enter \'s\' to show the current phi-category of all words')
                        print('d: enter \'d\' to finish annotating the current'
                            ' sentence and start the next one.')
                        print('exit: enter \'exit\' to exit the script without saving. \n')
        # each word in sent_list has a phi-category assigned to it
        # result is a list ***REMOVED***word, phi-category***REMOVED***


    return annotation_list


def main():

    """
Does: labels each word as a category of PHI (not-phi is an option). Writes the annotated file out as a list of lists
Into a pickle file with the original file name and .ano as the file extention.
Each sublist contains 2 elements: ***REMOVED***word_from_original_text, phi_label***REMOVED***

Uses:
nltk.sent_tokenize: Splits a file into sentence-by-sentence chunks.
nltk.word_tokenize: Splits a sentence in word-by-word chunks.
string.punctuation: Checks characters to see if they are punctuation. Punctuation is displayed for annotation
but will be defined as non-phi within the annotated file
re: Some words contain special characters such as '-' or '/'. The phi-reducer script splits words on these
characters as filters each subword independently. RE are used to also split words for annotation on special characters.


Arguments:
"-i", "--inputfile", help="Path to the file you would like to annotate.")
"-o", "--output", help="Path to the directory where the annotated note will be saved.")

Returns:
pickled list of lists with the original file name and .ano as the file extention.
Each sublist contains 2 elements: ***REMOVED***word_from_original_text, phi_label***REMOVED***

    """

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True,
                    help="Path to the file or the folder you would like to annotate.")
    ap.add_argument("-p", "--phi", required=True,
                    help="Path to the folder contains the philtered file.")
    ap.add_argument("-o", "--output", required=True,
                    help="Path to the directory where the annotated note will be saved.")
    ap.add_argument("-n", "--name", default="phi_reduced",
                   help="The key word of the annotated file, the default is *_phi_reduced.ano.")
    ap.add_argument("-r", "--random", action='store_true',
                   help="In random mode, the script will randomly choose a file in the input folder to annotate")

    args = ap.parse_args()
    #print(args.random)
    key_word = args.name
    finpath = args.input
    phipath = args.phi
    anno_mode = args.random
    foutpath = args.output

    if anno_mode == False:
        if os.path.isfile(finpath):
            head, tail = os.path.split(finpath)
        else:
            print("Input file does not exist.")
            os._exit(0)
        if not os.path.isdir(foutpath):
            user_input = input("Output folder:{} does not exist, would you like to create it?: press y to create: ".format(foutpath))
            if user_input == 'y':
                print("Creating {}".format(foutpath))
                os.mkdir(foutpath)
            else:
                print("Quitting")
                os._exit(0)
        if not os.path.isdir(phipath):
            print('the phi folder did not exist. Quitting')
            os._exit(0)
        else:
            phi_filename = '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***) + "_phi_reduced.txt"
            phi_file = os.path.join(phipath, phi_filename)
            if not os.path.isfile(phi_file):
                print("philter file does not exist.")
                os._exit(0)
        with open(finpath, encoding='utf-8', errors='ignore') as fin:
            note = fin.read()
        with open(phi_file, encoding='utf-8', errors='ignore') as fin:
            phifile = fin.read()
        doing_name = '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***) + ".txt.doing"
        doing_path = os.path.join(head, doing_name)
        doing_check = 'y'
        done_name = '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***) + ".txt.done"
        done_path = os.path.join(head, done_name)
        done_check = 'y'
        if os.path.isfile(done_path):
            done_check = input("This input file is already annotated. Do you want to continue? press y to continue, others to quit > ")
        elif os.path.isfile(doing_path):
            doing_check = input("This input file is being annotated. Do you want to continue? press y to continue, others to quit > ")
        if done_check == 'y' and doing_check == 'y':
            with open(doing_path, 'w') as fout: # create doing file to show this file is being annoated
                fout.write('')
            annotation_list = annotating(note, phifile)
            try:  # rmove doing file
                os.remove(doing_path)
            except OSError:
                pass
            file_name = '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***) + "_"+ key_word + ".ano"
            file_path = os.path.join(foutpath, file_name)
            if annotation_list != ***REMOVED******REMOVED***:
                print(len(annotation_list))
                with open(file_path, 'wb') as fout:
                    pickle.dump(annotation_list, fout)
                with open(done_path, 'w') as fout:
                    fout.write('')
        else:
            os._exit(0)
    else:  # random mode
        if not os.path.isdir(finpath):
            print("Input folder does not exist.")
            os._exit(0)
        if not os.path.isdir(foutpath):
            user_input = input("Output folder:{} does not exist, would you like to create it?: press y to create: ".format(foutpath))
            if user_input == 'y':
                print("Creating {}".format(foutpath))
                os.mkdir(foutpath)
            else:
                print("Quitting")
                os._exit(0)
        if not os.path.isdir(phipath):
            print('the phi folder did not exist. Quitting')
            os._exit(0)
        annotation_set = set()
        for f in glob.glob(os.path.join(finpath, '*.txt')):
            head,tail = os.path.split(''.join(f.split('.txt')***REMOVED***:-1***REMOVED***))
            annotation_set.add(tail)
        done_set = set()
        for f in glob.glob(os.path.join(finpath, '*.txt.done')):
            head,tail = os.path.split(''.join(f.split('.txt.done')***REMOVED***:-1***REMOVED***))
            done_set.add(tail)
        doing_set = set()
        for f in glob.glob(os.path.join(finpath, '*.txt.doing')):
            head,tail = os.path.split(''.join(f.split('.txt.doing')***REMOVED***:-1***REMOVED***))
            doing_set.add(tail)
        phi_set = set()
        for f in glob.glob(os.path.join(phipath, '*_phi_reduced.txt')):
            head,tail = os.path.split(''.join(f.split('_phi_reduced.txt')***REMOVED***:-1***REMOVED***))
            phi_set.add(tail)
        to_do_set = (annotation_set-done_set-doing_set) & phi_set
        print(to_do_set)
        if len(to_do_set) > 0:
            to_do = ''.join(random.sample(to_do_set, 1))
            todo_path = os.path.join(finpath, to_do + '.txt')
        else:
            print('All files in that folder are annotated or being annotataged.')
            os._exit(0)
        print("You will annotate:", to_do)
        with open(todo_path, encoding='utf-8', errors='ignore') as fin:
            note = fin.read()
        doing_path = os.path.join(finpath, to_do + '.txt.doing')
        done_path =  os.path.join(finpath, to_do + '.txt.done')
        phi_path = os.path.join(phipath, to_do + '_phi_reduced.txt')
        with open(phi_path, encoding='utf-8', errors='ignore') as fin:
            phifile = fin.read()
        with open(doing_path, 'w') as fout: # create doing file to show this file is being annoated
            fout.write('')
        annotation_list = annotating(note, phifile)
        # remove doing file
        try:
            os.remove(doing_path)
        except OSError:
            pass
        head, tail = os.path.split(todo_path)
        file_name = '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***) + "_"+ key_word + ".ano"
        file_path = os.path.join(foutpath, file_name)
        if annotation_list != ***REMOVED******REMOVED***:
            print(len(annotation_list***REMOVED***0***REMOVED***))
            #print(annotation_list)
            with open(file_path, 'wb') as fout:
                pickle.dump(annotation_list, fout)
            with open(done_path, 'w') as fout:
                fout.write('')


if __name__ == "__main__":
    main()

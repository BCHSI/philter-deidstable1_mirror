from nltk import sent_tokenize
from nltk import word_tokenize
import argparse
from string import punctuation
import pickle
import os
import re
import glob
import random

"""
Annotate each word in a text file as either being PHI (if so, annotate the type of PHI)
or not.

When the program launches, each word from the input file is displayed preceded by it's word index for reference, one sentence
at a time.

Labels each word as a category of PHI (not-phi is an option). Writes the annotated file out as a list of lists
Into a pickle file with the original file name and .ano as the file extention.
Each sublist contains 2 elements: [word_from_original_text, phi_label]

This is useful to generate a ground-truth corpus for the evaluation of the phi-reducer
software on your own files, or for the creation of a training corpus for machine learning de-id
methods.

"""
def annotating(note):

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
    annotation_list = []
    note = sent_tokenize(note)
    allowed_category = ('0', '1', '2', '3', '4', '5', '6')
    allowed_command = ('exit', 'all', 'range', 'select', 'show', 'done', 'help')
    category_print = 'Category to use: 0:Non-phi, 1:Contact, 2:Date, 3:ID, 4:Location, 5:Name, 6:Age\n'
    for sent in note:
        # sent_list: list of words that have not yet been divided by special characters
        sent_list = []
        words = word_tokenize(sent)
        word = [word for word in words if word not in punctuation]
        print('***********************************************************************')
        print(sent)
        print('')
        for j in range(len(word)):
            sent_list.append([word[j], '0', j + 1])
        # display the sentence with the index of each word and the current category assigned to each word
        # temp[2]: index, temp[0]:word, temp[1]:phi-category
        [print("({}){}[{}]".format(temp[2], temp[0], temp[1]), end=' ') for temp in sent_list]
        print('\n')
        print(category_print)

        while True:
            user_input = input('Please input command (enter \'help\' for more info): ')

            if user_input not in allowed_command:
                print("Command is not right, please re-input.")

            else:
                if user_input == 'exit':
                    return []

                elif user_input == 'all':
                    user_input = input('which phi-category do you want to assign to all words? > ')
                    if user_input in allowed_category:
                        for j in range(0, len(word)):
                            sent_list[j][1] = user_input
                        user_input = input('Press Enter to finish the'
                                     ' editing of this sentence, or others'
                                     ' to go back to the commend type. > ')
                        if user_input == '':
                            break
                    else:
                        print('Wrong category. Will go back to the commend type.')

                elif user_input == 'range':
                    start_word = input('From which word to edit at the same time: ')
                    if start_word.isdigit() and 0 < int(start_word) <= len(word):
                        end_word = input('To which word to edit at the same time: ')
                        if end_word.isdigit() and int(start_word) < int(end_word) <= len(word):
                            category = input('which phi-category do you want to assign to these words? > ')
                            if category in allowed_category:
                                for j in range(int(start_word)-1, int(end_word)):
                                    sent_list[j][1] = category
                            else:
                                print('Wrong category. Will go back to the commend type.')
                        else:
                            print('Wrong word. Will go back to the commend type.')
                    else:
                        print('Wrong word. Will go back to the commend type.')

                elif user_input == 'select':
                    user_input = input('which words are you going to edit, seperated by space: ')
                    pick_list = user_input.split(' ')
                    user_input = input('which phi-category do you want to assign to these words? > ')
                    if user_input in allowed_category:
                        input_category = user_input
                        for j in pick_list:
                            if j.isdigit() and 0 < int(j) <= len(word):
                                # check if the word contain special character and will be splitted later
                                # if so, check if different categories would be assigned.
                                if re.findall(r'[\/\-\:\~\_]', sent_list[int(j) - 1][0]) != []:
                                    user_input = input('{} contains multiple elements. Do you want to annotate them seperately? press y to assign seperately, others to assign the same.'.format(sent_list[int(j) - 1][0]))
                                    split_category = []
                                    if user_input == 'y':
                                        temp = re.sub(r'[\/\-\:\~\_]', ' ', sent_list[int(j) - 1][0])
                                        temp = temp.split(' ')
                                        temp = list(filter(None, temp))
                                        for k in temp:
                                            split_input = input('the phi-category of {} is:'.format(k))
                                            if split_input in allowed_category:
                                                split_category.append(split_input)
                                            else:
                                                print('Input is not correct. Will assign non-phi to {}'.format(k))
                                                split_category.append('0')
                                        sent_list[int(j) - 1][1] = split_category
                                    else:
                                        #split_category.append(input_category)
                                        sent_list[int(j) - 1][1] = input_category
                                else:
                                    sent_list[int(j) - 1][1] = input_category
                                print('{} is changed.'.format(sent_list[int(j) - 1][0]))
                            else:
                                print('{} is not a right sequence'.format(j))
                    else:
                        print('Wrong category. Will go back to the word you were editing.')

                elif user_input == 'show':
                    safe_list = []
                    phi_list = []
                    for temp in sent_list:
                        if temp[1] != '0':
                            phi_list.append(temp[0])
                        else:
                            safe_list.append(temp[0])
                    print('***********************************************************************')
                    print(sent)
                    print('')
                    print('phi:', (" ").join(phi_list))
                    print('safe:', (" ").join(safe_list))
                    # display the sentence with the index of each word and the current category assigned to each word
                    # temp[2]: index, temp[0]:word, temp[1]:phi-category
                    #[print("({}){}[{}]".format(temp[2], temp[0], temp[1]), end=' ') for temp in sent_list]
                    #print('\n\n', category_print)
                    #print('\n')

                elif user_input == 'done':
                    break

                elif user_input == 'help':
                    print('(X)WORD[Y]: X is the sequence number of the word,'
                        ' Y is the current phi-category of the word. All words'
                        ' will be set to 0, non-phi, as default.')
                    print('Command:')
                    print('all: enter \'all\' to change the phi-category of all'
                         ' words in the document at the same time.')
                    print('range: enter \'range\' to select a range of word indices'
                         ' and then assign the same phi-category to all words in'
                         ' that range. Enter the index of the first word and hit'
                         ' RETURN.Enter the index of the last word and hit RETURN. ')
                    print('select: enter \'select\' to select a list of word indices'
                         ' and then assign the same phi-category to all words in that'
                         ' list.Enter the index of each word, using spaces to separate'
                         ' each word index, hit RETURN when you have listed all desired word indices.')
                    print('show: enter \'show\' to show the current phi-category of all words')
                    print('done: enter \'done\' to finish annotating the current'
                        ' sentence and start the next one.')
                    print('exit: enter \'exit\' to exit the script without saving. \n')
        # each word in sent_list has a phi-category assigned to it
        # result is a list [word, phi-category]
        for result in sent_list:
            # divide words by special characters, replace special chars with space: ' '
            if re.findall(r'[\/\-\:\~\_]', result[0]) != []:
                temp = re.sub(r'[\/\-\:\~\_]', ' ', result[0])
            # take each new 'sub-word'
                temp = temp.split(' ')
                temp = list(filter(None, temp))
            # sub-word inherits the parent-word's phi-category
                if type(result[1]) == list:
                    for j in range(len(temp)):
                        annotation_list.append([temp[j], result[1][j]])
                else:
                    for j in range(len(temp)):
                        annotation_list.append([temp[j], result[1]])
            else:
                annotation_list.append([result[0], result[1]])
        print("\n")

    return annotation_list


def main():

    """
Does: labels each word as a category of PHI (not-phi is an option). Writes the annotated file out as a list of lists
Into a pickle file with the original file name and .ano as the file extention.
Each sublist contains 2 elements: [word_from_original_text, phi_label]

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
Each sublist contains 2 elements: [word_from_original_text, phi_label]

    """

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True,
                    help="Path to the file or the folder you would like to annotate.")
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
        with open(finpath, encoding='utf-8', errors='ignore') as fin:
            note = fin.read()
        doing_name = '.'.join(tail.split('.')[:-1]) + ".txt.doing"
        doing_path = os.path.join(head, doing_name)
        doing_check = 'y'
        done_name = '.'.join(tail.split('.')[:-1]) + ".txt.done"
        done_path = os.path.join(head, done_name)
        done_check = 'y'
        if os.path.isfile(done_path):
            done_check = input("This input file is already annotated. Do you want to continue? press y to continue, others to quit > ")
        elif os.path.isfile(doing_path):
            doing_check = input("This input file is being annotated. Do you want to continue? press y to continue, others to quit > ")
        if done_check == 'y' and doing_check == 'y':
            with open(doing_path, 'w') as fout: # create doing file to show this file is being annoated
                fout.write('')
            annotation_list = annotating(note)
            try:  # rmove doing file
                os.remove(doing_path)
            except OSError:
                pass
            file_name = '.'.join(tail.split('.')[:-1]) + "_"+ key_word + ".ano"
            file_path = os.path.join(foutpath, file_name)
            if annotation_list != []:
                print(annotation_list)
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
        annotation_set = set(glob.glob(os.path.join(finpath, '*.txt')))
        done_set = set()
        for f in glob.glob(os.path.join(finpath, '*.txt.done')):
            done_set.add(''.join(f.split('.done')[:-1]))
        doing_set = set()
        for f in glob.glob(os.path.join(finpath, '*.txt.doing')):
            doing_set.add(''.join(f.split('.doing')[:-1]))
        if len(annotation_set-done_set-doing_set) > 0:
            to_do = ''.join(random.sample(annotation_set-done_set-doing_set, 1))
        else:
            print('All files in that folder are annotated or being annotataged.')
            os._exit(0)
        print("You will annotate:", to_do)
        with open(to_do, encoding='utf-8', errors='ignore') as fin:
            note = fin.read()
        doing_path = to_do + '.doing'
        done_path = to_do + '.done'
        with open(doing_path, 'w') as fout: # create doing file to show this file is being annoated
            fout.write('')
        annotation_list = annotating(note)
        # remove doing file
        try:
            os.remove(doing_path)
        except OSError:
            pass
        head, tail = os.path.split(to_do)
        file_name = '.'.join(tail.split('.')[:-1]) + "_"+ key_word + ".ano"
        file_path = os.path.join(foutpath, file_name)
        if annotation_list != []:
            print(annotation_list)
            with open(file_path, 'wb') as fout:
                pickle.dump(annotation_list, fout)
            with open(done_path, 'w') as fout:
                fout.write('')


if __name__ == "__main__":
    main()

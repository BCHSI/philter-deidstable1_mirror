from nltk import sent_tokenize
from nltk import word_tokenize
import argparse
from string import punctuation
import pickle
from difflib import ndiff
import os
import re
import glob

"""
Compares the outputs of annotation.py and phi-reducer.py to evaluate phi-reduction performance. 
Provides
    - True and False Positive words found, and the total count of each
    - False Negative words found, and the total count
    - Precision and Recall scores

annotation.py returns a list of lists containing all words in the clinical note and their annotated phi-category: 
    - [[word1, phi-category],[word2, phi-category]]

phi-reducer.py returns a txt file (phi-reduced.txt) in which words that are phi have 'hopefully' been replaced with the safe word: **PHI**

eval.py 
1. extracts all words from the annotation.py list for which the phi-category is 0 (not-phi) and adds them to a list (annot_list)
    - annot_list contains the True Negatives
2. extracts all non-**PHI** words from phi-reduced.txt and adds them to a list (phi_r_list)
3. get a count of all the **PHI** words that occurred in phi-reduced.txt (filtered_count)
4. Use ndiff() to compare annot_list to phi_r_list. Returns lines of strings containing the elements that were present in 1 list 
    but not in the other, with a symbol to identify which list element was present in. 
    - words that are in annot_list but not in phi_r_list are False Negatives (a phi-word got through)
    - words that are in phi_r_list but not in annot_list are False Positives (a non-phi word was filtered)
4. Filtered_Count = TP + FP - FN
    TP = Filtered_Count - FP + FN
    Use TP to calculate Precision and Recall

Returns:    (summary_dict.pkl) pickled file which is a dictionary of all FP and FN in all files that were processed. 
                Key: filename
                Values: list of FP words, list of FN words, Count of TP words
            (summary_text.txt) report containing the same information in summary_dict.pkl for each note and
                the precision/recall for each note and the counts of TP, FN, FP for all notes and the overall precision/recall for all notes
"""

def comparison(filename, file1path, file2path):

    summary_dict = {}
    output = ''

    with open(file1path, 'r', errors = 'ignore') as fin:
        phi_reduced_note = fin.read()
    with open(file2path, 'rb') as fin:
        annotation_note = pickle.load(fin)
    #print(file1path)


    # Begin Step 1
    #annot_list = [word[0] if (word[1] == '0' or word[1] == '2')and word[0] != ''
                  #else "PHIinfo" for word in annotation_note ]
    annot_list = [word[0] for word in annotation_note if (word[1] == '0' or word[1] == '2')and word[0] != '']
    anno_text = ' '.join(annot_list)
    anno_text = re.sub(r'[\/\-\:\~\_\=\*]', ' ', anno_text)
    annot_list = anno_text.split(' ')
    annot_list = [word for word in annot_list if word != '']
    for i in range(len(annot_list)):
        if annot_list[i][-1] in punctuation:
            annot_list[i] = annot_list[i][:-1]
            # for j in range(len(annot_list[i])-2, 0 ,-1):
               # if annot_list[i][j] not in punctuation:
                   # annot_list[i] = annot_list[i][:j+1]
                   # break


    #print(annot_list)
    # Begin Step 2
    # get a list of sentences within the note , returns a list of lists  [[sent1],[sent2]] 
    phi_reduced_sentences = sent_tokenize(phi_reduced_note)
    # get a list of words within each sentence, returns a list of lists [[sent1_word1, sent1_word2, etc],[sent2_word1, sent2_word2, etc] ]
    phi_reduced_words = [word_tokenize(sent) for sent in phi_reduced_sentences]
    # a list of all words from the phi_reduced note: [word1, word2, etc]

    phi_reduced_list = [word for sent in phi_reduced_words for word in sent if word not in punctuation]
    phi_r_list = [word for word in phi_reduced_list if '**PHI' not in word]
    #temp = [word for word in phi_reduced_list if '**PHI' in word]
    phi_dict = {}
    j = 0
    for i in range(len(phi_reduced_list)):
        if '**PHI' not in phi_reduced_list[i]:
            phi_dict[j] = i
            j += 1
    #print(len(phi_reduced_list))
    #print(len(phi_r_list))
    #print(len(temp))
    #print(j)
    #phi_r_list = [word if '**PHI' not in word else "PHIinfo" for word in phi_reduced_list ]
    phi_reduced_text = ' '.join(phi_r_list)
    phi_reduced_text = re.sub(r'[\/\-\:\~\_\=\*]', ' ', phi_reduced_text)
    phi_r_list = phi_reduced_text.split(' ')
    phi_r_list = [word for word in phi_r_list if word != '']
    for i in range(len(phi_r_list)):
        if phi_r_list[i][-1] in punctuation:
             phi_r_list[i] = phi_r_list[i][:-1]
               # for j in range(len(phi_r_list[i])-2, 0 ,-1):
               # if phi_r_list[i][j] not in punctuation:
                  # phi_r_list[i] = phi_r_list[i][:j+1]
                   # break
    #print(phi_r_list)
    # Begin Step 3
    #filtered_count = [word[0] for word in annotation_note if word[1] != '0' and word[1] != '2' and word[0] != '']
    filtered_count = [word[0] for word in annotation_note if word[1] != '0' and word[1] != '2' and word[0] != '']


    filtered_count = len(filtered_count)
    summary_dict['false_positive'] = []
    summary_dict['false_negative'] = []
    #print(filtered_count)
    #print(annot_list)

    # marker_and_word are a string, eg "+ word" or "- word"
    # + means that the word appears in the first list but not in the second list
    # - means that the word appears in the second list but not in the first list
    # marker_and_word[2] is the first character of the word. 
    #new_text = ''
    j = 0
    fn_list = []
    for word_index, marker_and_word in enumerate(ndiff(phi_r_list, annot_list)):
        #if marker_and_word[0] == '+' and re.findall(r'\w+', marker_and_word[2:]) != []:
            #summary_dict['false_positive'].append(marker_and_word[2:])
            #print(marker_and_word[2:])
        #print(word_index, marker_and_word)
        # print(j)
        if marker_and_word[0] == '-' and re.findall(r'\w+', marker_and_word[2:]) != []:
            summary_dict['false_negative'].append(marker_and_word[2:])
            fn_list.append(j)
            j += 1
            #print(j)
            #new_text += marker_and_word[2:]+'_FN '
        elif marker_and_word[0] == '+':
            if re.findall(r'\w+', marker_and_word[2:]) != []:
                summary_dict['false_positive'].append(marker_and_word[2:])
            else:
                continue
            #new_text += 'PHIinfo '
        else:
            #new_text += marker_and_word[2:] + ' '
            j += 1

    if filtered_count == 0:
        true_positive = 0
    else:
        true_positive = filtered_count-len(summary_dict['false_negative'])

    summary_dict['true_positive'] = true_positive
    if true_positive < 0:
        summary_dict['false_positive'] = []
        summary_dict['false_negative'] = []
        summary_dict['true_positive'] = 'Need to check'

    # new_text_sentences = sent_tokenize(new_text)
    # new_text_words = [word_tokenize(sent) for sent in new_text_sentences]
    # new_text_list = [word for sent in new_text_words for word in sent]

    words_list = []
    for index in fn_list:
        true_index = phi_dict[index]
        if true_index < 3:
            index_before = 0
        else:
            index_before = true_index-3
        if true_index > len(phi_reduced_list) - 4:
            index_after = len(phi_reduced_list) -1
        else:
            index_after = true_index + 4
        words_sentence = ' '.join(phi_reduced_list[index_before:index_after])

        words_list.append(phi_reduced_list[true_index]+':'+words_sentence)
    #print(words_list)
    summary_dict['3words_fn'] = words_list

    # get a list of words within each sentence, returns a list of lists [[sent1_word1, sent1_word2, etc],[sent2_word1, sent2_word2, etc] ]

    '''
    output = 'Note: ' + filename + '\n'
    output += "Script filtered: " + str(filtered_count) + '\n'
    output += "True positive: " + str(true_positive) + '\n'
    output += "False Positive: " + ' '.join(summary_dict['false_positive']) + '\n'
    output += "FP number: " + str(len(summary_dict['false_positive'])) + '\n'
    output += "False Negative: " + ' '.join(summary_dict['false_negative']) + '\n'
    output += "FN number: " + str(len(summary_dict['false_negative'])) + '\n'
    if true_positive == 0 and len(summary_dict['false_negative']) == 0:
        output += "Recall: N/A\n"
    else:
        output += "Recall: {:.2%}".format(true_positive/(true_positive+len(summary_dict['false_negative']))) + '\n'
    if true_positive == 0 and len(summary_dict['false_positive']) == 0:
        output += "Precision: N/A\n"
    else:
        output += "Precision: {:.2%}".format(true_positive/(true_positive+len(summary_dict['false_positive']))) + '\n'
    output += '\n'
    '''
    #print(summary_dict)

    return summary_dict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--phinote", required=True,
                    help="Path to the phi reduced note, *.txt.")
    ap.add_argument("-a", "--annotation", required=True,
                    help="Path to the annotated file, *.ano.")
    ap.add_argument("-o", "--output", required=True,
                    help="Path to save the summary pkl and statistics text.")
    ap.add_argument("-r", "--recursive", action = 'store_true', default = False,
                    help="whether read files in the input folder recursively.")
    args = ap.parse_args()

    file1path = args.phinote
    file2path = args.annotation
    foutpath = args.output
    if_recursive = args.recursive
    summary_dict_all = {}
    summary_text = ''
    phi_reduced_dict = {}
    annotation_dict = {}
    miss_file = []
    TP_all = 0
    FP_all = 0
    FN_all = 0
    processed_count = 0
    output = ''
    if_update = False

    if os.path.isfile(file1path) != os.path.isfile(file2path):
        print("phi note input and annotation input should be both files or folders.")
    else:
        if os.path.isfile(file1path):
            head1, tail1 = os.path.split(file1path)
            head2, tail2 = os.path.split(file2path)
            file1name = '.'.join(tail1.split('.')[:-1])
            file2name = '.'.join(tail2.split('.')[:-1])
            if file1name != file2name:
                print('Please make sure the filenames are the same in both file.')
            else:
                summary_dict = comparison(file1name, file1path, file2path)
                summary_dict_all[file1name] = summary_dict
                summary_text += output
                processed_count += 1
                if_update = True
        else:
            reply = input('Please make sure all files are ready.'
                        'Press Enter to process or others to quit.> ')
            if reply == '':
                if if_recursive:
                    for f in glob.glob(file1path + "/**/*.txt", recursive=True):
                        head, tail = os.path.split(f)
                        filename = '.'.join(tail.split('.')[:-1])
                        #if filename != '':
                            # note_id = re.findall(r'\d+', tail)[0]
                        phi_reduced_dict[filename] = f
                        processed_count += 1
                    for f in glob.glob(file2path + "/**/*.ano", recursive=True):
                        head, tail = os.path.split(f)
                        filename = '.'.join(tail.split('.')[:-1])
                        #if re.findall(r'\d+', tail) != []:
                        #    note_id = re.findall(r'\d+', tail)[0]
                        annotation_dict[filename] = f
                else:
                    for f in glob.glob(file1path + "/*.txt"):
                        head, tail = os.path.split(f)
                        filename = '.'.join(tail.split('.')[:-1])
                        #if re.findall(r'\d+', tail) != []:
                           # note_id = re.findall(r'\d+', tail)[0]
                        phi_reduced_dict[filename] = f
                        processed_count += 1
                    for f in glob.glob(file2path + "/*.ano"):
                        head, tail = os.path.split(f)
                        filename = '.'.join(tail.split('.')[:-1])
                        #if re.findall(r'\d+', tail) != []:
                        #    note_id = re.findall(r'\d+', tail)[0]
                        annotation_dict[filename] = f

                for i in phi_reduced_dict.keys():
                    if i in annotation_dict.keys():
                        summary_dict = comparison(i, phi_reduced_dict[i], annotation_dict[i])
                        summary_dict_all[i] = summary_dict
                        summary_text += output
                        if_update = True
                    else:
                        miss_file.append(phi_reduced_dict[i])

                with open(foutpath + "/summary_dict.pkl", 'wb') as fout:
                    pickle.dump(summary_dict_all, fout)

        print('{:d} out of {:d} phi reduced notes have been compared.'.format(processed_count-len(miss_file), processed_count))
        print('{} files have not found corresponding annotation as below.'.format(len(miss_file)))
        print('\n'.join(miss_file)+'\n')
        if processed_count != 0:
            for k,v in sorted(summary_dict_all.items()):
                output += 'Note: ' + k + '\n'
                #output += "Script filtered: " + str(filtered_count) + '\n'
                output += "True positive: " + str(v['true_positive']) + '\n'
                output += "False Positive: " + ' '.join(v['false_positive']) + '\n'
                output += "FP number: " + str(len(v['false_positive'])) + '\n'
                output += "False Negative: " + ' '.join(v['false_negative']) + '\n'
                output += "FN number: " + str(len(v['false_negative'])) + '\n'
                output += '3words around FN:\n'
                output += '\n'.join(v['3words_fn'])
                output += '\n'
                if v['true_positive'] == 'Need to check':
                    output += 'Need to further check'
                elif v['true_positive'] == 0 and len(v['false_negative']) == 0:
                    output += "Recall: N/A\n"
                elif v['true_positive'] + len(v['false_negative']) == 0:
                    output += "Need to further check true_positive & false_negative.\n"
                else:
                    output += "Recall: {:.2%}".format(v['true_positive']/(v['true_positive']+len(v['false_negative']))) + '\n'

                if v['true_positive'] == 'Need to check':
                    output += 'Need to further check'
                elif v['true_positive'] == 0 and len(v['false_positive']) == 0:
                    output += "Precision: N/A\n"
                elif v['true_positive'] + len(v['false_positive']) == 0:
                    output +=  "Need to further check true_positive & false_negative.\n"
                else:
                    #print(v['true_positive'], len(v['false_positive']))
                    output += "Precision: {:.2%}".format(v['true_positive']/(v['true_positive']+len(v['false_positive']))) + '\n'
                output += '\n'
                if v['true_positive'] != 'Need to check':
                    TP_all += v['true_positive']
                FP_all += len(v['false_positive'])
                FN_all += len(v['false_negative'])
            summary_text = "{} notes have been evaulated.\n".format(processed_count-len(miss_file))
            summary_text += "True Positive in all notes: " + str(TP_all) + '\n'
            summary_text += "False Positive in all notes: " + str(FP_all) + '\n'
            summary_text += "False Negative in all notes: " + str(FN_all) + '\n'
            if TP_all == 0 and FN_all == 0:
                summary_text += "Recall: N/A\n"
            else:
                summary_text += "Recall: {:.2%}".format(TP_all/(TP_all+FN_all)) + '\n'
            if TP_all == 0 and FP_all == 0:
                summary_text += "Precision: N/A\n"
            else:
                summary_text += "Precision: {:.2%}".format(TP_all/(TP_all+FP_all)) + '\n'
            print(summary_text)
            summary_text = output + summary_text
        else:
            print("Please re-run the script after all the files are ok.")

        #print(output)
        if if_update:
            with open(foutpath + "/summary_dict.pkl", 'wb') as fout:
                pickle.dump(summary_dict_all, fout)
            with open(foutpath + '/summary_text.txt', 'w') as fout:
                fout.write(summary_text)


if __name__ == "__main__":
    main()

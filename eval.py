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
    - ***REMOVED******REMOVED***word1, phi-category***REMOVED***,***REMOVED***word2, phi-category***REMOVED******REMOVED***

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

    with open(file1path, 'r') as fin:
        phi_reduced_note = fin.read()
    with open(file2path, 'rb') as fin:
        annotation_note = pickle.load(fin)
    # get a list of sentences within the note , returns a list of lists  ***REMOVED******REMOVED***sent1***REMOVED***,***REMOVED***sent2***REMOVED******REMOVED*** 
    phi_reduced_sentences = sent_tokenize(phi_reduced_note)
    # get a list of words within each sentence, returns a list of lists ***REMOVED******REMOVED***sent1_word1, sent1_word2, etc***REMOVED***,***REMOVED***sent2_word1, sent2_word2, etc***REMOVED*** ***REMOVED***
    phi_reduced_words = ***REMOVED***word_tokenize(sent) for sent in phi_reduced_sentences***REMOVED***
    # a list of all words from the phi_reduced note: ***REMOVED***word1, word2, etc***REMOVED***
    phi_reduced_list = ***REMOVED***word for sent in phi_reduced_words for word in sent if word not in punctuation***REMOVED***

    # Begin Step 1
    annot_list = ***REMOVED***word***REMOVED***0***REMOVED*** for word in annotation_note if word***REMOVED***1***REMOVED*** == '0' and word***REMOVED***0***REMOVED*** != ''***REMOVED***
    # Begin Step 2
    phi_r_list = ***REMOVED***word for word in phi_reduced_list if '**PHI' not in word***REMOVED***
    # Begin Step 3
    filtered_count = ***REMOVED***word for word in phi_reduced_list if '**PHI' in word***REMOVED***

    filtered_count = len(filtered_count)
    summary_dict***REMOVED***'false_positive'***REMOVED*** = ***REMOVED******REMOVED***
    summary_dict***REMOVED***'false_negative'***REMOVED*** = ***REMOVED******REMOVED***
    #print(filtered_count)
    #print(annot_list)

    # marker_and_word are a string, eg "+ word" or "- word"
    # + means that the word appears in the first list but not in the second list
    # - means that the word appears in the second list but not in the first list
    # marker_and_word***REMOVED***2***REMOVED*** is the first character of the word. 
    for word_index, marker_and_word in enumerate(ndiff(phi_r_list, annot_list)):
        if marker_and_word***REMOVED***0***REMOVED*** == '+' and re.findall(r'\w+', marker_and_word***REMOVED***2:***REMOVED***) != ***REMOVED******REMOVED***:
            summary_dict***REMOVED***'false_positive'***REMOVED***.append(marker_and_word***REMOVED***2:***REMOVED***)
        elif marker_and_word***REMOVED***0***REMOVED*** == '-' and re.findall(r'\w+', marker_and_word***REMOVED***2:***REMOVED***) != ***REMOVED******REMOVED***:
            summary_dict***REMOVED***'false_negative'***REMOVED***.append(marker_and_word***REMOVED***2:***REMOVED***)

    true_positive = filtered_count-len(summary_dict***REMOVED***'false_positive'***REMOVED***)+len(summary_dict***REMOVED***'false_negative'***REMOVED***)
    summary_dict***REMOVED***'true_positive'***REMOVED*** = true_positive

    output = 'Note: ' + filename + '\n'
    output += "Script filtered: " + str(filtered_count) + '\n'
    output += "True positive: " + str(true_positive) + '\n'
    output += "False Positive: " + ' '.join(summary_dict***REMOVED***'false_positive'***REMOVED***) + '\n'
    output += "FP number: " + str(len(summary_dict***REMOVED***'false_positive'***REMOVED***)) + '\n'
    output += "False Negative: " + ' '.join(summary_dict***REMOVED***'false_negative'***REMOVED***) + '\n'
    output += "FN number: " + str(len(summary_dict***REMOVED***'false_negative'***REMOVED***)) + '\n'
    output += "Recall: {:.2%}".format(true_positive/(true_positive+len(summary_dict***REMOVED***'false_negative'***REMOVED***))) + '\n'
    output += "Precision: {:.2%}".format(true_positive/(true_positive+len(summary_dict***REMOVED***'false_positive'***REMOVED***))) + '\n'
    output += '\n'
    #print(summary_dict)
    return summary_dict, output


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
    miss_file = ***REMOVED******REMOVED***
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
            file1name = '.'.join(tail1.split('.')***REMOVED***:-1***REMOVED***)
            file2name = '.'.join(tail2.split('.')***REMOVED***:-1***REMOVED***)
            if file1name != file2name:
                print('Please make sure the filenames are the same in both file.')
            else:
                summary_dict, output = comparison(file1name, file1path, file2path)
                summary_dict_all***REMOVED***file1name***REMOVED*** = summary_dict
                summary_text += output
                if_update = True
        else:
            reply = input('Please make sure all files are ready.'
                        'Press Enter to process or others to quit.> ')
            if reply == '':
                if if_recursive:
                    for f in glob.glob(file1path + "/**/*.txt", recursive=True):
                        head, tail = os.path.split(f)
                        filename = '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***)
                        #if filename != '':
                            # note_id = re.findall(r'\d+', tail)***REMOVED***0***REMOVED***
                        phi_reduced_dict***REMOVED***filename***REMOVED*** = f
                        processed_count += 1
                    for f in glob.glob(file2path + "/**/*.ano", recursive=True):
                        head, tail = os.path.split(f)
                        filename = '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***)
                        #if re.findall(r'\d+', tail) != ***REMOVED******REMOVED***:
                        #    note_id = re.findall(r'\d+', tail)***REMOVED***0***REMOVED***
                        annotation_dict***REMOVED***filename***REMOVED*** = f
                else:
                    for f in glob.glob(file1path + "/*.txt"):
                        head, tail = os.path.split(f)
                        filename = '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***)
                        #if re.findall(r'\d+', tail) != ***REMOVED******REMOVED***:
                           # note_id = re.findall(r'\d+', tail)***REMOVED***0***REMOVED***
                        phi_reduced_dict***REMOVED***filename***REMOVED*** = f
                        processed_count += 1
                    for f in glob.glob(file2path + "/*.ano"):
                        head, tail = os.path.split(f)
                        filename = '.'.join(tail.split('.')***REMOVED***:-1***REMOVED***)
                        #if re.findall(r'\d+', tail) != ***REMOVED******REMOVED***:
                        #    note_id = re.findall(r'\d+', tail)***REMOVED***0***REMOVED***
                        annotation_dict***REMOVED***filename***REMOVED*** = f

                for i in phi_reduced_dict.keys():
                    if i in annotation_dict.keys():
                        summary_dict, output = comparison(i, phi_reduced_dict***REMOVED***i***REMOVED***, annotation_dict***REMOVED***i***REMOVED***)
                        summary_dict_all***REMOVED***i***REMOVED*** = summary_dict
                        summary_text += output
                        if_update = True
                    else:
                        miss_file.append(phi_reduced_dict***REMOVED***i***REMOVED***)

                print('{:d} out of {:d} phi reduced notes have been compared.'.format(processed_count-len(miss_file), processed_count))
                print('{} files have not found corresponding annotation as below.'.format(len(miss_file)))
                print('\n'.join(miss_file)+'\n')
                if processed_count != 0:
                    for k,v in summary_dict_all.items():
                        TP_all += v***REMOVED***'true_positive'***REMOVED***
                        FP_all += len(v***REMOVED***'false_positive'***REMOVED***)
                        FN_all += len(v***REMOVED***'false_negative'***REMOVED***)

                    output = "{} notes have been evaulated.\n".format(processed_count-len(miss_file))
                    output += "True Positive in all notes: " + str(TP_all) + '\n'
                    output += "False Positive in all notes: " + str(FP_all) + '\n'
                    output += "False Negative in all notes: " + str(FN_all) + '\n'
                    output += "Recall: {:.2%}".format(TP_all/(TP_all+FN_all)) + '\n'
                    output += "Precision: {:.2%}".format(TP_all/(TP_all+FP_all)) + '\n'
                    summary_text += output
            else:
                print("Please re-run the script after all the files are ok.")

        print(output)
        if if_update:
            with open(foutpath + "/summary_dict.pkl", 'wb') as fout:
                pickle.dump(summary_dict_all, fout)
            with open(foutpath + '/summary_text.txt', 'w') as fout:
                fout.write(summary_text)


if __name__ == "__main__":
    main()

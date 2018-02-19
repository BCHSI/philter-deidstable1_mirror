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
Calculate by the annotation file. 

"""

def comparison(filename, file2path):

    summary_dict = {}

    with open(file2path, 'rb') as fin:
        annotation_note = pickle.load(fin)

    # Begin Step 1
    summary_dict***REMOVED***'true_positive'***REMOVED*** = ***REMOVED***word***REMOVED***0***REMOVED*** for word in annotation_note if word***REMOVED***1***REMOVED*** == '1' and word***REMOVED***0***REMOVED*** != ''***REMOVED***
    summary_dict***REMOVED***'false_positive'***REMOVED*** = ***REMOVED***word***REMOVED***0***REMOVED*** for word in annotation_note if word***REMOVED***1***REMOVED*** == '2' and word***REMOVED***0***REMOVED*** != ''***REMOVED***
    summary_dict***REMOVED***'fn_name'***REMOVED*** = ***REMOVED***word***REMOVED***0***REMOVED*** for word in annotation_note if word***REMOVED***1***REMOVED*** == 'n' and word***REMOVED***0***REMOVED*** != ''***REMOVED***  # FN name
    summary_dict***REMOVED***'fn_location'***REMOVED*** = ***REMOVED***word***REMOVED***0***REMOVED*** for word in annotation_note if word***REMOVED***1***REMOVED*** == 'l' and word***REMOVED***0***REMOVED*** != ''***REMOVED***  # FN location
    summary_dict***REMOVED***'fn_date'***REMOVED*** = ***REMOVED***word***REMOVED***0***REMOVED*** for word in annotation_note if word***REMOVED***1***REMOVED*** == 'd' and word***REMOVED***0***REMOVED*** != ''***REMOVED***  # FN date
    summary_dict***REMOVED***'fn_contact'***REMOVED*** = ***REMOVED***word***REMOVED***0***REMOVED*** for word in annotation_note if word***REMOVED***1***REMOVED*** == 'c' and word***REMOVED***0***REMOVED*** != ''***REMOVED***  # FN contact
    summary_dict***REMOVED***'fn_id'***REMOVED*** = ***REMOVED***word***REMOVED***0***REMOVED*** for word in annotation_note if word***REMOVED***1***REMOVED*** == 'i' and word***REMOVED***0***REMOVED*** != ''***REMOVED***  # FN id
    summary_dict***REMOVED***'fn_age'***REMOVED*** = ***REMOVED***word***REMOVED***0***REMOVED*** for word in annotation_note if word***REMOVED***1***REMOVED*** == 'a' and word***REMOVED***0***REMOVED*** != ''***REMOVED***  # FN age
    summary_dict***REMOVED***'fn_other'***REMOVED*** = ***REMOVED***word***REMOVED***0***REMOVED*** for word in annotation_note if word***REMOVED***1***REMOVED*** == 'o' and word***REMOVED***0***REMOVED*** != ''***REMOVED***  # FN other

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
                summary_dict = comparison(file1name, file2path)
                summary_dict_all***REMOVED***file1name***REMOVED*** = summary_dict
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
                        summary_dict = comparison(i, annotation_dict***REMOVED***i***REMOVED***)
                        summary_dict_all***REMOVED***i***REMOVED*** = summary_dict
                        summary_text += output
                        if_update = True
                    else:
                        miss_file.append(phi_reduced_dict***REMOVED***i***REMOVED***)

                with open(foutpath + "/summary_dict.pkl", 'wb') as fout:
                    pickle.dump(summary_dict_all, fout)

        print('{:d} out of {:d} phi reduced notes have been compared.'.format(processed_count-len(miss_file), processed_count))
        print('{} files have not found corresponding annotation as below.'.format(len(miss_file)))
        print('\n'.join(miss_file)+'\n')
        if processed_count != 0:
            for k,v in sorted(summary_dict_all.items()):
                output += 'Note: ' + k + '\n'
                #output += "Script filtered: " + str(filtered_count) + '\n'
                output += "True positive: " + str(len(v***REMOVED***'true_positive'***REMOVED***)) + '\n'
                output += "False Positive: " + ' '.join(v***REMOVED***'false_positive'***REMOVED***) + '\n'
                output += "FP number: " + str(len(v***REMOVED***'false_positive'***REMOVED***)) + '\n'

                fn_list = v***REMOVED***'fn_name'***REMOVED*** + v***REMOVED***'fn_location'***REMOVED*** + v***REMOVED***'fn_date'***REMOVED*** + v***REMOVED***'fn_contact'***REMOVED*** + \
                          v***REMOVED***'fn_id'***REMOVED*** + v***REMOVED***'fn_age'***REMOVED*** + v***REMOVED***'fn_other'***REMOVED***
                output += "False Negative: " + ' '.join(fn_list) + '\n'
                output += "FN number: " + str(len(fn_list)) + '\n'
                if len(v***REMOVED***'true_positive'***REMOVED***) == 0 and len(fn_list) == 0:
                    output += "Recall: N/A\n"
                elif len(v***REMOVED***'true_positive'***REMOVED***) + len(fn_list) == 0:
                    output += "Need to further check true_positive & false_negative.\n"
                else:
                    output += "Recall: {:.2%}".format(len(v***REMOVED***'true_positive'***REMOVED***)/(len(v***REMOVED***'true_positive'***REMOVED***)+len(fn_list))) + '\n'
                if len(v***REMOVED***'true_positive'***REMOVED***) == 0 and len(v***REMOVED***'false_positive'***REMOVED***) == 0:
                    output += "Precision: N/A\n"
                elif len(v***REMOVED***'true_positive'***REMOVED***) + len(v***REMOVED***'false_positive'***REMOVED***) == 0:
                    output +=  "Need to further check true_positive & false_positive.\n"
                else:
                    #print(v***REMOVED***'true_positive'***REMOVED***, len(v***REMOVED***'false_positive'***REMOVED***))
                    output += "Precision: {:.2%}".format(len(v***REMOVED***'true_positive'***REMOVED***)/(len(v***REMOVED***'true_positive'***REMOVED***)+len(v***REMOVED***'false_positive'***REMOVED***))) + '\n'
                output += '\n'
                TP_all += len(v***REMOVED***'true_positive'***REMOVED***)
                FP_all += len(v***REMOVED***'false_positive'***REMOVED***)
                FN_all += len(fn_list)
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

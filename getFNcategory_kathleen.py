import pickle
import pandas as pd
import os


def getcategory(summary, anno_path):
    '''
    return FN's category
    input:
    summary: dict[filename: dict[false_negative, false_positive, ture_positive]]
    anno_path: path to the annotation files
    output:
    FN_category: list["FN type"]
    FN_dict: dict[type:[FNs]]
    '''
    # summary_path = 'summary_dict.pkl'
    # anno_path = '/media/DataHD/philter-annotations/pooneh/pooneh-done'


    FN_dict = {'Name FNs':[], 'Location FNs':[], 'Date FNs':[], 'Contact FNs':[], 'ID FNs':[], 'Age(>90) FNs':[], 'Not PHI':[],
                'True Negatives':[], 'True Positives':[], 'False Positives':[]}
    category_dict = {'0':'Not PHI','o':'Not PHI',
                     'n':'Name FNs', 'l':'Location FNs', 'd':'Date FNs',
                     'c':'Contact FNs', 'i':'ID FNs', 'a':'Age(>90) FNs'}

    # Populate dictionary with csv data
    # fn_categories_new = pd.read_csv("fn_categories.csv", delimiter = ',', encoding="latin-1")
    # fn_no_labels = list(fn_categories_new['word'])
    # fn_labels = list(fn_categories_new['category'])

    # for i in range(0,len(fn_no_labels)):
    #     fn_unlabeled = fn_no_labels[i]
    #     fn_label = str(fn_labels[i])
    #     phi_category = category_dict[fn_label]
    #     FN_dict[phi_category].append(fn_unlabeled)

    for (anno_file, results_dict) in summary.items():
        finpath = os.path.join(anno_path, anno_file + '.ano')
        # load annotation    
        if os.path.isfile(finpath):
            with open(finpath, 'rb') as fin:
                anno = pickle.load(fin)
            # Initialize lists
            TN_list = []
            TP_list = []
            FP_list = results_dict['false_positive']  
            FN_list = results_dict['false_negative']
            

            # Get plain anno text
            anno_text = [item[0] for item in anno]

            # Get FNs (and category labels, if possible. Otherwise add to 'Other FNs')
            for false_negative in FN_list:
                for i in range(0,len(anno)):
                    annotation = anno[i]
                    if annotation[1] != '1':
                        if false_negative == annotation[0] and (annotation[1] != '0' and annotation[1] != '2'):
                            # Add word to correct PHI list
                            phi_category = category_dict[annotation[1]]
                            FN_dict[phi_category].append(false_negative)
                            
                            # print phi and context if no phi label
                            if annotation[1] == '1':
                                if i > 4 and i < (len(anno)-4):
                                    phi_context = ' '.join(anno_text[i-4:i+5])
                                elif i > 4 and i > (len(anno)-4):
                                    phi_context = ' '.join(anno_text[i-4:])
                                elif i < 4 and i < (len(anno)-4):
                                    phi_context = ' '.join(anno_text[0:i+5])
                                print(false_negative, phi_context)
                            break
                        # if i == len(anno)-1:
                        #     print(false_negative, annotation[1])  
                        # if false_negative == annotation[0] and (annotation[1] == '0' or annotation[1] == '2'):
                        #     print(false_negative, finpath)
            # Get TPs and TNs
            for annotation in anno:
                if annotation[1] != '1':
                    # Get TPs
                    if (annotation[1] != '0' and annotation[1] != '2') and annotation[0] not in FN_list:
                        TP_list.append(annotation[0])
                    # Get TNs
                    if (annotation[1] == '0' or annotation[1] == '2') and annotation[0] not in FP_list:
                        TN_list.append(annotation[0])

            
            FN_dict['True Negatives'] = FN_dict['True Negatives'] + TN_list    
            FN_dict['True Positives'] = FN_dict['True Positives'] + TP_list
            FN_dict['False Positives'] = FN_dict['False Positives'] + FP_list
    

    print('True Negatives:',len(FN_dict['True Negatives']))
    print('True Positives:',len(FN_dict['True Positives']))
    print('False Positives:',len(FN_dict['False Positives']))
    print('False Negatives:',len(FN_dict['Name FNs'])+len(FN_dict['Location FNs'])+len(FN_dict['Date FNs'])+len(FN_dict['Contact FNs'])+len(FN_dict['ID FNs'])+len(FN_dict['Age(>90) FNs']))
    #print('False Negatives:',len(FN_dict['False Negatives']))

    return FN_dict
    


def main():
    summary_path = input("where is summary?>")
    with open(summary_path, 'rb') as fin:
        summary = pickle.load(fin)
    anno_path = input("where are annotations?>")
    FN_dict = getcategory(summary, anno_path)

    with open('FN_dict.pkl', 'wb') as fout:
        pickle.dump(FN_dict, fout)


if __name__ == "__main__":
    main()

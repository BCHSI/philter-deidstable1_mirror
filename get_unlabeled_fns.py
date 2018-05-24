import pickle
import os
import sys
import json


def getcategory(summary, anno_path, fn_correction_path):
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


    phi_counter = 0
    unlabeled_counter = 0
    labeled_counter = 0
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
            # phi_counter += len(results_dict['false_negative'])
            # Get plain anno text
            anno_text = [item[0] for item in anno]
            # Get FNs (and category labels, if possible. Otherwise add to 'Other FNs')           
            for i in range(0,len(anno)):
                annotation = anno[i]
                false_negative = annotation[0]
                if annotation[1] in ['n','l','d','c','i','a','o'] and false_negative in FN_list:
                    FN_list.remove(annotation[0])
                    labeled_counter += 1
            phi_counter += len(FN_list)       
            for i in range(0,len(anno)):
                for false_negative in FN_list:
                    annotation = anno[i]
                    if annotation[1] == '1' and false_negative == annotation[0]:
                        # if false_negative == 'Mendelson':
                        #     print(i)
                        #     print(len(anno)-4)
                        #     print(annotation)
                        #     print(anno)
                        if i >= 4 and i <= (len(anno)-4):
                            phi_context = ' '.join(anno_text[i-4:i+5])
                        elif i >= 4 and i >= (len(anno)-4):
                            phi_context = ' '.join(anno_text[i-4:])
                        elif i <= 4 and i <= (len(anno)-4):
                            phi_context = ' '.join(anno_text[0:i+5])
                        # else:
                        #     print(false_negative)
                        #     print(i)
                        #     print(len(anno)-4)
                        #     print(annotation)
                        #     print(anno)                        
                        print(false_negative, phi_context)
                        unlabeled_counter += 1
                        break



def main():
    summary_path = sys.argv[1]
    
    with open(summary_path, 'rb') as fin:
        summary = pickle.load(fin)
  
    anno_path = sys.argv[2]
    
    FN_output = getcategory(summary, anno_path)
    

if __name__ == "__main__":
    main()

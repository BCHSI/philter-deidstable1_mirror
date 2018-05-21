import pickle
import json
import os


def getcatgory(summary, anno_path):
    '''
    return FN's category
    input:
    summary: dict[filename: dict[false_negative, false_positive, ture_positive]]
    anno_path: path to the annotation files
    output:
    FN_category: list["FN type"]
    FN_dict: dict[type:[FNs]]
    '''

    FN_category = []
    FN_dict = {}
    FN_dict['cannot find'] = []
    category_dict = {'0':'safe', '1':'phi', '2':'FP',
                     'n':'Name', 'l':'Location', 'd':'Date',
                     'c':'Contact', 'i':'ID', 'a':'Age(>90)',
                     'o':'Others'}
    num = 1
    for (k, v) in summary.items():
        finpath = os.path.join(anno_path, k + '.ano')
        # load annotation
        
        if os.path.isfile(finpath):
            with open(finpath, 'rb') as fin:
                anno = pickle.load(fin)
            # get FN for a file
            FN_list = v['false_negative']
            start_position = 0
            print(FN_list)

            for i in FN_list:
                print(num)
                num+=1
                iffound = False
                while True:
                    old_position = start_position
                    j = start_position
                    if j >= len(anno):
                        break
                    start_position += 1
                    if anno[j][0] == i:
                        try:
                            FN_category.append(i + ' ' + category_dict[anno[j][1]] + ' ' + k)
                            iffound = True
                            if category_dict[anno[j][1]] in FN_dict.keys():
                                FN_dict[category_dict[anno[j][1]]].append(i)
                                break
                            else:
                                FN_dict[category_dict[anno[j][1]]] = [i]
                                break
                        except:
                            print(i, j[1])

                if not iffound:
                    FN_category.append(i + ' ' + 'cannot find ' + k)
                    FN_dict['cannot find'].append(i)
                    start_position = old_position


    return FN_category, FN_dict


def main():
    summary_path = input("where is summary?>")
    with open(summary_path, 'rb') as fin:
        summary = pickle.load(fin)
    anno_path = input("where are annotations?>")
    FN_category, FN_dict = getcatgory(summary, anno_path)

    with open('FN_category.pkl', 'wb') as fout:
        pickle.dump(FN_category, fout)

    out_path = summary_path.split("summary_dict.pkl")[0] + 'FN_dict.json'
    with open('FN_dict.json', 'w') as fout:
        json.dump(FN_dict, fout)


if __name__ == "__main__":
    main()

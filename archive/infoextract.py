#import cPickle
#import _pickle as cPickle 
import pickle
import os, sys
import glob, glob
from multiprocessing.dummy import Pool as ThreadPool
#import MySQLdb as mdb
import string
import re
from collections import Counter 
from collections import OrderedDict
from collections import defaultdict
from Autocorrection import *
import nltk
from nltk.stem.porter import *
from nltk import sent_tokenize, word_tokenize
import csv


#finpath = "/media/DataHD/beau/baby_notes/"
#finpath = "/media/DataHD/corpus/notes/"
#foutpath ="/media/DataHD/r_phi_corpus/"
finpath = "input_test\\Ext\\"
foutpath = "output_test\\"

pattern=re.compile("[^\w+]") #we're going to want to remove all special characters
pattern_sens = re.compile(r"""\b(
addr|street|lane|ave       # addres
|phone|fax|number|tel      # phone
|ip                        # ip address
|date                      # date
|md                        # MD ID
|age|year[s]?\sold           # age             
)""",re.X|re.I)   


pattern_date = re.compile(r"""\b(
\d{4}(-(\d+))+    # date-format
)""",re.X|re.I)   


#with open('data\\ext.pkl', 'rb') as fin:
#    filter_set = pickle.load(fin)
columnlist = ['temp', 'resp', 'rate', 'pulse', 'pressure']
columnnames = ','.join(columnlist)
#columnlist = list(filter_set)
reg = '|'.join(columnlist)
reg = '\\b('+reg+')'
pattern_ext = re.compile(reg, re.X|re.I)
total_records = 0
ext_dict_all = {}
print(columnlist)

for f in glob.glob(finpath+"*.txt"):
        
    with open(f, encoding='utf-8', errors='ignore') as fin:
        head, tail = os.path.split(f)
        note_id = re.findall(r'\d+', tail)[0]  # get the file number
        total_records += 1
        ext_dict = defaultdict(lambda: 'Unknown')
        #ext_dict = {}
        #take the note name for writing
        out_name = 'ext_'+ note_id
        note = fin.read()
        #note_id = re.search(r'\b(\d{5}\d+)', note).group(0)
        #date = pattern_date.search(note).group(0)
        note = sent_tokenize(note.replace('-', ' '))
        word_sent = [word_tokenize(sent) for sent in note]
        #ext_dict['date'] = date 
        ext_dict['note_id'] = note_id
        for sent in word_sent:
            tmp = ' '.join(sent)
            sent_tag = nltk.pos_tag_sents([sent])
            for word in sent_tag[0]:
                if word[0] not in string.punctuation:
                    word_position = sent.index(word[0])
                    #print(word)
                    # keep the number format, others will remove the special chars
                    if word[1] != 'CD':
                        word_str = str(pattern.sub('',word[0])) #actually remove the speical chars
                    try:
                        if  word[1]  == 'CD':
                            #print(word)
                            if word_position <= 2:
                                word_previous = ' '.join(sent[0:word_position])
                            else:
                                word_previous = ' '.join(sent[word_position-3:word_position])
                                
                            if word_position == len(sent):
                                word_after = ''
                            else:
                                word_after = sent[word_position+1]
                            #print(word_previous)
                            #print(word_after)
                            #context = word_previous + word_after
                            #print(context)
                            
                            if pattern_ext.search(word_previous):
                                data_type = pattern_ext.search(word_previous).group(0).lower()
                                #print(data_type)
                                if data_type in ext_dict.keys():
                                    ext_dict[data_type] += '/'+str(word[0])
                                else:
                                    ext_dict[data_type] = str(word[0])
                            else:
                                #print(word_after)
                                if pattern_ext.search(word_after):
                                    data_type = pattern_ext.search(word_after).group(0).lower()
                                    #print(data_type)
                                    if data_type in ext_dict.keys():
                                        ext_dict[data_type] += '/'+str(word[0])
                                    else:
                                        ext_dict[data_type] = str(word[0])
                                #print(ext_dict)
                        elif word[0].lower() == 'alcohol':
                            min_dist = 0
                            jj_posi = None
                            ext_dict['alcohol'] = 'none'
                            #print(len(sent))
                            
                            for i in range(len(sent_tag[0])):
                                #print(sent_tag[0][i][0])
                                if sent_tag[0][i][1] == 'JJ':
                                   # print(2)
                                    if (min_dist == 0 or min_dist > abs(i-word_position)) and abs(i-word_position)<3:
                                        min_dist == abs(i-word_position)
                                        jj_posi = i
                                        ext_dict['alcohol'] = sent_tag[0][i][0]
    
                                
                    except:
                        #print(word)
                        #print(sent.index(word))
                        #print(nltk.pos_tag(word))
                        pass
        ext_dict_all[note_id] = ext_dict
        #print(ext_dict)

print(ext_dict_all)
fout = "output_test\\info_ext.pkl"
#with open(fout,"wb") as fout:
 #   pickle.dump(ext_dict_all, fout)

 
with open('infoext_reduced.csv', 'w', newline="\n", encoding="utf-8") as csvfile:
    #fieldnames = ['note_id', 'date', 'alcohol'] + columnlist
    fieldnames = ['note_id', 'alcohol'] + columnlist
   # writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    f_csv = csv.DictWriter(csvfile, fieldnames)
    f_csv.writeheader()
    
    for k,v in ext_dict_all.items():
        for i in fieldnames:
            v[i]
            #print(v[i])
        f_csv.writerow(v)


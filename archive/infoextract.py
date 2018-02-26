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

pattern=re.compile("***REMOVED***^\w+***REMOVED***") #we're going to want to remove all special characters
pattern_sens = re.compile(r"""\b(
addr|street|lane|ave       # addres
|phone|fax|number|tel      # phone
|ip                        # ip address
|date                      # date
|md                        # MD ID
|age|year***REMOVED***s***REMOVED***?\sold           # age             
)""",re.X|re.I)   


pattern_date = re.compile(r"""\b(
\d{4}(-(\d+))+    # date-format
)""",re.X|re.I)   


#with open('data\\ext.pkl', 'rb') as fin:
#    filter_set = pickle.load(fin)
columnlist = ***REMOVED***'temp', 'resp', 'rate', 'pulse', 'pressure'***REMOVED***
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
        note_id = re.findall(r'\d+', tail)***REMOVED***0***REMOVED***  # get the file number
        total_records += 1
        ext_dict = defaultdict(lambda: 'Unknown')
        #ext_dict = {}
        #take the note name for writing
        out_name = 'ext_'+ note_id
        note = fin.read()
        #note_id = re.search(r'\b(\d{5}\d+)', note).group(0)
        #date = pattern_date.search(note).group(0)
        note = sent_tokenize(note.replace('-', ' '))
        word_sent = ***REMOVED***word_tokenize(sent) for sent in note***REMOVED***
        #ext_dict***REMOVED***'date'***REMOVED*** = date 
        ext_dict***REMOVED***'note_id'***REMOVED*** = note_id
        for sent in word_sent:
            tmp = ' '.join(sent)
            sent_tag = nltk.pos_tag_sents(***REMOVED***sent***REMOVED***)
            for word in sent_tag***REMOVED***0***REMOVED***:
                if word***REMOVED***0***REMOVED*** not in string.punctuation:
                    word_position = sent.index(word***REMOVED***0***REMOVED***)
                    #print(word)
                    # keep the number format, others will remove the special chars
                    if word***REMOVED***1***REMOVED*** != 'CD':
                        word_str = str(pattern.sub('',word***REMOVED***0***REMOVED***)) #actually remove the speical chars
                    try:
                        if  word***REMOVED***1***REMOVED***  == 'CD':
                            #print(word)
                            if word_position <= 2:
                                word_previous = ' '.join(sent***REMOVED***0:word_position***REMOVED***)
                            else:
                                word_previous = ' '.join(sent***REMOVED***word_position-3:word_position***REMOVED***)
                                
                            if word_position == len(sent):
                                word_after = ''
                            else:
                                word_after = sent***REMOVED***word_position+1***REMOVED***
                            #print(word_previous)
                            #print(word_after)
                            #context = word_previous + word_after
                            #print(context)
                            
                            if pattern_ext.search(word_previous):
                                data_type = pattern_ext.search(word_previous).group(0).lower()
                                #print(data_type)
                                if data_type in ext_dict.keys():
                                    ext_dict***REMOVED***data_type***REMOVED*** += '/'+str(word***REMOVED***0***REMOVED***)
                                else:
                                    ext_dict***REMOVED***data_type***REMOVED*** = str(word***REMOVED***0***REMOVED***)
                            else:
                                #print(word_after)
                                if pattern_ext.search(word_after):
                                    data_type = pattern_ext.search(word_after).group(0).lower()
                                    #print(data_type)
                                    if data_type in ext_dict.keys():
                                        ext_dict***REMOVED***data_type***REMOVED*** += '/'+str(word***REMOVED***0***REMOVED***)
                                    else:
                                        ext_dict***REMOVED***data_type***REMOVED*** = str(word***REMOVED***0***REMOVED***)
                                #print(ext_dict)
                        elif word***REMOVED***0***REMOVED***.lower() == 'alcohol':
                            min_dist = 0
                            jj_posi = None
                            ext_dict***REMOVED***'alcohol'***REMOVED*** = 'none'
                            #print(len(sent))
                            
                            for i in range(len(sent_tag***REMOVED***0***REMOVED***)):
                                #print(sent_tag***REMOVED***0***REMOVED******REMOVED***i***REMOVED******REMOVED***0***REMOVED***)
                                if sent_tag***REMOVED***0***REMOVED******REMOVED***i***REMOVED******REMOVED***1***REMOVED*** == 'JJ':
                                   # print(2)
                                    if (min_dist == 0 or min_dist > abs(i-word_position)) and abs(i-word_position)<3:
                                        min_dist == abs(i-word_position)
                                        jj_posi = i
                                        ext_dict***REMOVED***'alcohol'***REMOVED*** = sent_tag***REMOVED***0***REMOVED******REMOVED***i***REMOVED******REMOVED***0***REMOVED***
    
                                
                    except:
                        #print(word)
                        #print(sent.index(word))
                        #print(nltk.pos_tag(word))
                        pass
        ext_dict_all***REMOVED***note_id***REMOVED*** = ext_dict
        #print(ext_dict)

print(ext_dict_all)
fout = "output_test\\info_ext.pkl"
#with open(fout,"wb") as fout:
 #   pickle.dump(ext_dict_all, fout)

 
with open('infoext_reduced.csv', 'w', newline="\n", encoding="utf-8") as csvfile:
    #fieldnames = ***REMOVED***'note_id', 'date', 'alcohol'***REMOVED*** + columnlist
    fieldnames = ***REMOVED***'note_id', 'alcohol'***REMOVED*** + columnlist
   # writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    f_csv = csv.DictWriter(csvfile, fieldnames)
    f_csv.writeheader()
    
    for k,v in ext_dict_all.items():
        for i in fieldnames:
            v***REMOVED***i***REMOVED***
            #print(v***REMOVED***i***REMOVED***)
        f_csv.writerow(v)


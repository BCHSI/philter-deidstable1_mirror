import string
import random
import io
import sys
import string
import random


'''
    python3 meta_data_fake.py <meta_file.txt> <Output_meta_file>
'''

mfpath = sys.argv[1]
meta = {}
mfile = open(mfpath)
outpath = sys.argv[2]

''' Loading the Meta file into a hash'''
head = mfile.readline()
for line in mfile:
    line = line.rstrip('\n')
    line  = line.replace('.0','')
    key,value = line.split('\t',1)
    meta[key] = value
print("loaded into hash")

'''Creating random deid note key for the notes that are missing de id note key'''
for key, value in meta.items():
    #print(value)
    note_value = value.split('\t')
    # print(note_value)
    if not note_value[1]:
       random_value = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(14))
       identifiable_random_value = random_value + "B"
       note_value[1] = identifiable_random_value
       meta[key] = "\t".join(note_value)




''' Creating random date offsets for patients missing a date offset'''
patient = {}
for key, value in meta.items():
    note_value = value.split('\t')
    if not note_value[0]:
       if note_value[2] not in patient:
          patient[note_value[2]] = str(random.randint(730,1094))
          print(note_value[2]+"\t"+ patient[note_value[2]])           
''' Updating the meta values with the random data offset '''

for key, value in meta.items():
    note_value = value.split('\t')
    if not note_value[0]:            
       if note_value[2] in patient:
          note_value[0] = patient[note_value[2]]
          meta[key] = "\t".join(note_value)
    #print("\t".join(note_value))
 
''' Writing updated meta file '''
dfile = open(outpath, "w+")  
dfile.write("note_key"+"\t"+"date_offset"+"\t"+"deid_note_key"+"\t"+"patient_ID"+"\n")
for key, value in meta.items():
    dfile.write(key + '\t' + ''.join(value) + '\n') 

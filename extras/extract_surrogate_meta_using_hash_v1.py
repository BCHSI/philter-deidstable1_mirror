#############################
#Program Usage:
## Python3 extract_using_hash_v1.py <file with the list of directory to traverse> <META 58M file>
### Note: This script assumes the META file you provide it has four columns in it in the order note_key, date_offset, patient_id and deid_note_key
############################
import sys

dirpath = sys.argv[1]
mfpath = sys.argv[2]
dirfile = open(dirpath)

# Generate the Hash table for the Meta file

meta = {}
mfile = open(mfpath)
for line in mfile:
    line = line.rstrip('\n')
    line  = line.replace('.0','')
    key,value = line.split('\t',1)
    meta[key] = value
print("loaded into hash")
#Walk through each of the directory in the list and create batch meta files for each of the batches
for dirline in dirfile:
    dirline = dirline.replace('\n','')
    kpath = dirline+'/batch_input.in'
    dfile = open(dirline+"/meta_data.txt", "w+")     
    #Generate keeper set
    keepers = set()
    kdict = dict()
    kfile = open(kpath)
    #head = kfile.readline()
    for line in kfile:
        line = line.replace('\n','')
        line = line.replace('.txt','')
        line = line.replace('_utf8','')
        line = line.lstrip('0')
        keepers.add(line)
    kfile.close()
    print("Creating meta file for"+dirline)
    dfile.write("note_key"+"\t"+"date_offset"+"\t"+"patient_ID"+"\t"+"deid_note_key"+"\n")
    for k in keepers:
        if k in meta:
           dfile.write(k+"\t"+meta[k]+"\n")
dirfile.close()      
   

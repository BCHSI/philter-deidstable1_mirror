#############################
#Program Usage:
## Python3 extract_using_hash_v1.py <file with the list of directory to traverse> <META 58M file>
### Note: This script uses the raw metadata file from the notes extract
############################
import sys

dirpath = sys.argv[1]
mfpath = sys.argv[2]
dirfile = open(dirpath)

# Generate the Hash table for the Meta file
# dirpath='/data/muenzenk/low_hanging_fruit_tests/notes/primarymrn_dir_list.txt'
# mfpath='/data/notes/Notes_2020_09_04/NOTE_INFO_MAPS.txt'
meta = {}
mfile = open(mfpath)
for line in mfile:
    line = line.rstrip('\n')
    line  = line.replace('.0','')
    split = line.split('\t')
    
    if len(split) > 1:
        # key = note_key
        key = split[16]
        value = split[16]+'\t'+split[12]+'\t'+split[1]+'\t'+split[17]+'\t'+split[2]+'\t'+split[3]+'\t'+split[4]+'\t'+split[5]+'\t'+split[6]+"\n"
        meta[key] = value

print("Meta loaded into hash")
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
    dfile.write("note_key"+"\t"+"date_offset"+"\t"+"patient_ID"+"\t"+"deid_note_key"+"\t"+"BirthDate"+"\t"+"Deid_BirthDate"+"\t"+"DeathDate"+"\t"+"status"+"\t"+"deid_turns_91_date"+"\n")
    for k in keepers:
        if k in meta:
           dfile.write(meta[k])
dirfile.close()      
   

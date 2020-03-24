#############################
#Program Usage:
## Python3 probes_extract_using_hash_v1.py <file with the list of directory to traverse> <probe file part1> <probe file part 2> probe file part 3> <probe file part 4> <meta file>
############################
import sys

#dirpath = '../test_dir_2.txt'

#mfpath = '/data/shared/mapping_files/note_info_re_id_pat_mapping_final_mod.txt'

# Generate the Hash table for the Meta file
def load_probe_to_hash(prbpath):
    probe = {}
    prbfile = open(prbpath)
    for line in prbfile:
        line = line.rstrip('\n')
        line  = line.replace('.0','')
        value = line.split('\t')
        if value[1] in probe:
           val = value[2] +"\t" + value[5]
           probe[value[1]].add(val)
        else:
           probe[value[1]] = set()
           probe[value[1]].add(value[2] +"\t" + value[5])
    print("loaded "+ prbpath +" into hash")
    return probe

def create_batch_dict(dirline):
    #dirfile = open(dirpath)
    #for dirline in dirfile:
    dirline = dirline.replace('\n','')
    kpath = dirline+'/batch_input.in'
           
    #Generate keeper set
    keepers = set()
    
    kfile = open(kpath)
    #head = kfile.readline()
    for line in kfile:
        line = line.replace('\n','')
        line = line.replace('.txt','')
        line = line.replace('_utf8','')
        line = line.lstrip('0')
        keepers.add(line)
    kfile.close()
    print("Dict of note_key for batch " + dirline + " created")
    return keepers


dirpath = sys.argv[1]
p0path = sys.argv[2]
p1path = sys.argv[3]
p2path = sys.argv[4]
p3path = sys.argv[5]
mpath = sys.argv[6] 
meta = {}
mfile = open(mpath)
for line in mfile:
    line = line.rstrip('\n')
    line  = line.replace('.0','')
    key= line.split('\t')
    meta[key[0]] = key[2]
print("loaded into hash")

dirfile = open(dirpath)


for dirline in dirfile:
    found = set()
    dirline = dirline.rstrip('\n')
    dfile = open(dirline+"/knownphi_data.txt", "w+")
    dfile.write("patient_ID"+"\t"+"phi_type"+"\t"+"clean_value"+"\t"+"note_key"+"\n")
    print(dirline)
    keepers = create_batch_dict(dirline)
    kdict = {}
    for i in range(4):
        n = i+2
        prbpath = sys.argv[n]
        probe = load_probe_to_hash(prbpath)
        for k in keepers:
           print(k)      
           if k in meta:
              kdict[meta[k]] = k
           for k in kdict:
             print(k)
             if k not in found:
               if k in probe:
                 found.add(k)
                 print(probe[k])
                 for x in probe[k]:
                     dfile.write(k+"\t"+x+"\t"+kdict[k]+"\n")
dfile.close()
dirfile.close()      
   

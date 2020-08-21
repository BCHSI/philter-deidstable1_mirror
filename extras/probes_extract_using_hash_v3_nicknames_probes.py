#############################
#Program Usage:
## Python3 probes_extract_using_hash_v2.py <file with the list of directory to traverse> <probe file>
############################
import sys
import os.path

#dirpath = '../test_dir_2.txt'

#mfpath = '/data/shared/mapping_files/note_info_re_id_pat_mapping_final_mod.txt'

# Generate the Hash table for the Meta file
def load_probe_to_hash(prbpath):
    probe = {}
    prbfile = open(prbpath)
    print(prbpath + " loading")
    for line in prbfile:
        line = line.rstrip('\n')
        line = line.replace('.0','')
        line = line.replace('\"','')
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
#p0path = sys.argv[2]
#p1path = sys.argv[3]
#p2path = sys.argv[4]
#p3path = sys.argv[5]


dirfile = open(dirpath)
probe = load_probe_to_hash(sys.argv[2])
print("Probes loaded into hash")

for dirline in dirfile:
  found = set()
  dirline = dirline.rstrip('\n')
  dfile = open(dirline+"/knownphi_data_nicknames.txt", "w+")
  dfile.write("patient_ID"+"\t"+"phi_type"+"\t"+"value"+"\t"+"note_key"+"\n")
  print(dirline)
  meta = {}
  mpath = dirline+'/meta_data.txt'
  if os.path.exists(mpath): 
    mfile = open(mpath)

    for line in mfile:
        line = line.rstrip('\n')
        line  = line.replace('.0','')
        key= line.split('\t')
        meta[key[0]] = key[3]
    print(mpath+" meta data loaded into hash")

    keepers = create_batch_dict(dirline)
    kdict = {}
    for k in keepers:
       if k in meta:
          kdict[meta[k]] = k
       for k in kdict:
         if k not in found:
           if k in probe:
             found.add(k)
             for x in probe[k]:
                dfile.write(k+"\t"+x+"\t"+kdict[k]+"\n")
dfile.close()
dirfile.close()      
   

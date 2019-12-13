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
        
        if value***REMOVED***1***REMOVED*** in probe:
           val = value***REMOVED***2***REMOVED*** +"\t" + value***REMOVED***5***REMOVED***
           probe***REMOVED***value***REMOVED***1***REMOVED******REMOVED***.add(val)
        else:
           probe***REMOVED***value***REMOVED***1***REMOVED******REMOVED*** = set()
           probe***REMOVED***value***REMOVED***1***REMOVED******REMOVED***.add(value***REMOVED***2***REMOVED*** +"\t" + value***REMOVED***5***REMOVED***)
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


dirpath = sys.argv***REMOVED***1***REMOVED***
#p0path = sys.argv***REMOVED***2***REMOVED***
#p1path = sys.argv***REMOVED***3***REMOVED***
#p2path = sys.argv***REMOVED***4***REMOVED***
#p3path = sys.argv***REMOVED***5***REMOVED***


dirfile = open(dirpath)
probe = load_probe_to_hash(sys.argv***REMOVED***2***REMOVED***)
print("Probes loaded into hash")

for dirline in dirfile:
  found = set()
  dirline = dirline.rstrip('\n')
  dfile = open(dirline+"/knownphi_data_original.txt", "w+")
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
        meta***REMOVED***key***REMOVED***0***REMOVED******REMOVED*** = key***REMOVED***3***REMOVED***
    print(mpath+" meta data loaded into hash")

    keepers = create_batch_dict(dirline)
    kdict = {}
    for k in keepers:
       if k in meta:
          kdict***REMOVED***meta***REMOVED***k***REMOVED******REMOVED*** = k
       for k in kdict:
         if k not in found:
           if k in probe:
             found.add(k)
             for x in probe***REMOVED***k***REMOVED***:
                dfile.write(k+"\t"+x+"\t"+kdict***REMOVED***k***REMOVED***+"\n")
dfile.close()
dirfile.close()      
   

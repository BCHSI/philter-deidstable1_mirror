import sys
## Takes in the list of batch folders as input 

# Name of directory list
fpath = sys.argv***REMOVED***1***REMOVED***
dirfile = open(fpath)

# Name of the chunk file to generate
chunk_name = sys.argv***REMOVED***2***REMOVED***

# Path to metadata folder
meta_dir = sys.argv***REMOVED***3***REMOVED***

# Path to input notes folder
input_dir = sys.argv***REMOVED***4***REMOVED***

# Path to output folder
output_dir = sys.argv***REMOVED***5***REMOVED***

# Meta file names
meta_name = sys.argv***REMOVED***6***REMOVED***

# Knownphi file names
knownphi_name = sys.argv***REMOVED***7***REMOVED***

# Generate the Hash table for the Meta file
dfile = open(chunk_name, "w+")  
for line in dirfile:
    line = line.rstrip('\n')
    meta = line + "/" + meta_name
    inp = line.replace(meta_dir,input_dir)
    out = line.replace(meta_dir,output_dir)
    known_phi = line + "/" + knownphi_name
    dfile.write(inp + "\t" + meta + "\t" + out + "\t" + known_phi + "\n")

dirfile.close()
dfile.close()
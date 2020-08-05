import sys
## Takes in the list of batch folders as input 

# Name of directory list
fpath = sys.argv[1]
dirfile = open(fpath)

# Name of the chunk file to generate
chunk_name = sys.argv[2]

# Path to metadata folder
meta_dir = sys.argv[3]

# Path to input notes folder
input_dir = sys.argv[4]

# Path to output folder
output_dir = sys.argv[5]

# Meta file names
meta_name = sys.argv[6]

# Knownphi file names
knownphi_name = sys.argv[7]

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
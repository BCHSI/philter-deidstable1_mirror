import os,re
from chardet.universaldetector import UniversalDetector


# Removes extra punctuation from the notes
# Compares the 2 sets of documents and 
# adds in missing punctuation

notes_folder = "data/i2b2_notes/"
anno_folder = "data/i2b2_anno/"
output = "data/i2b2_notes_nopunc/"
anno_suffix = "_phi_reduced.ano"
anno_output = "data/i2b2_anno_nophi/"

def detect_encoding(fp):
    detector = UniversalDetector()
    with open(fp, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done: 
                break
        detector.close()
    return detector.result

orig_character_set = {}
missing_char_set = {}
anno_character_set = {}

#detect the missing characters 
for root, dirs, files in os.walk(notes_folder):
           
    for f in files:

        if not os.path.exists(anno_folder+f.split(".")[0]+anno_suffix):
            print("FILE DOESNT EXIST", anno_folder+f.split(".")[0]+anno_suffix)
            continue
        
        orig_filename = root+f
        encoding1 = detect_encoding(orig_filename)
        orig = open(orig_filename,"r", encoding=encoding1['encoding']).read()
        
        
        for c in orig:
            orig_character_set[c] = 1

        anno_filename = anno_folder+f.split(".")[0]+anno_suffix
        encoding2 = detect_encoding(anno_filename)
        anno = open(anno_filename,"r", encoding=encoding2['encoding']).read()
        
        
        for c in anno:
            anno_character_set[c] = 1

        

for c in orig_character_set:
    if c not in anno_character_set:
        missing_char_set[c] = 1


#missing_chars = [":","-","/","_","~"] #these characters were stripped from the anno file
missing_chars = missing_char_set.keys()

print(missing_chars)

#remove extra chars from the original files so we can compare correctly
for root, dirs, files in os.walk(notes_folder):      
    for f in files:
        
        orig_filename = root+f
        encoding1 = detect_encoding(orig_filename)
        orig = open(orig_filename,"r", encoding=encoding1['encoding']).read()
        
        
        for c in missing_chars:
            orig = orig.replace(c," ")


        with open(output+f,"w") as f:
            f.write(orig)


#remove the **PHI** from the anno notes
for root, dirs, files in os.walk(notes_folder):      
    for f in files:

        if not os.path.exists(anno_folder+f.split(".")[0]+anno_suffix):
            print("FILE DOESNT EXIST", anno_folder+f.split(".")[0]+anno_suffix)
            continue
        
       
        anno_filename = anno_folder+f.split(".")[0]+anno_suffix
        encoding2 = detect_encoding(anno_filename)
        anno = open(anno_filename,"r", encoding=encoding2['encoding']).read()
        anno = anno.replace("**PHI**"," ")

        with open(anno_output+f.split(".")[0]+anno_suffix,"w") as f:
            f.write(anno)

"""
TODO: do actual search and replace sequance matching


Look for non-matches, 
look for a situation where the next item + punc if it creates a match, add to our list, 

"""
# for root, dirs, files in os.walk(notes_folder):      
#     for f in files:

#         if not os.path.exists(anno_folder+f.split(".")[0]+anno_suffix):
#             print("FILE DOESNT EXIST", anno_folder+f.split(".")[0]+anno_suffix)
#             continue
        
#         orig_filename = root+f
#         encoding1 = detect_encoding(orig_filename)
#         orig = open(orig_filename,"r", encoding=encoding1['encoding']).read()
#         orig_words = re.split("\s+", orig)
        
#         anno_filename = anno_folder+f.split(".")[0]+anno_suffix
#         encoding2 = detect_encoding(anno_filename)
#         anno = open(anno_filename,"r", encoding=encoding2['encoding']).read()
#         anno_words = re.split("\s+", anno)

#         cursor1 = 0
#         cursor2 = 0

#         notes = [] #stored words

#         while True:

#             if cursor1 >= len(orig_words):
#                 break

#             w1 = orig_words[cursor1]
#             w2 = anno_words[cursor2]

#             if w2[0:4] == "**PHI":
#                 print("phi", w2)
#                 #advance the cursor and continue
#                 cursor1 += 1
#                 cursor2 += 1
#                 continue

#             if w1 != w2:
#                 #check if the next word + a punc will match, if so combine and add to our words
                
#                 for c in missing_chars:
#                     if re.search(c, w1):
                        
#                         new_word = w2+c+anno_words[cursor2+1]
#                         print("found", c, w1, new_word)
#                         if new_word == w1:
#                             print("match", new_word)
#                             #save or new word
#                             notes.append(new_word)
#                             #move our anno cursor forward
#                             cursor2 += 1
#                         else:
#                             print("no match")

#             cursor1 += 1
#             cursor2 += 1



        
        






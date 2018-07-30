from subprocess import check_output
import sys
import os
import io
import re

result={}
filename = sys.argv[1]
directory = sys.argv[2]
filename = "./names.txt"
words = [line.strip() for line in open(filename)]

#directory = os.fsencode(directory)
i = 0

for root, dirs, files in os.walk(directory):
    #print(root, dirs, files)
    path = root.split(os.sep)
    for filename in files:
        #print(root, filename)
        if filename.endswith("txt"):
            with io.open(os.path.join(root, filename), "r", encoding="utf-8") as f:
                data=f.read()
                #print(data)
                i+=1
                if i%1000==0:
                    print(i)
                for word in words:

                    print(filename)
                    if re.search(r"\b"+word+r"\b", data,re.IGNORECASE):
                        #start,end = re.search(r"\b"+word+r"\b", data,re.IGNORECASE).span()
                        #start = start - 20
                        #end = end + 20
                        ##print(start, end)
                        ##print(word+"\t"+filename)
                        #print( data[start:end])
                        #print("#############################")
                        print(":\t"+word, end="\t")

        
"""
for filename in os.listdir(directory):
    #print(f)
    with io.open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
        data=f.read()
        #print(data)
        for word in words:
            #print(word)
            if re.search(r"\b"+word+r"\b", data,re.IGNORECASE):
                pass
                #print(filename)
                #print("\t"+word)
    #print()

 """
#for word in words: # regx is a list of all the filters
#   #result[word] = check_output('grep -liwr "' + word + '" ' + directory + ' | wc -l',shell=True) 

#print(result)

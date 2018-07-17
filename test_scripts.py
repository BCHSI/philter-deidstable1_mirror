import os
import sys
from subprocess import call,check_output
import filecmp
from shutil import rmtree

script1 = sys.argv[1]
script2 = sys.argv[2]


if not os.path.exists("testtemp1"):
    os.mkdir("testtemp1")

if not os.path.exists("testtemp2"):
    os.mkdir("testtemp2")

print("################")
print("RUNNING SCRIPT 1")
print("################")

call(["python3", script1,"-i=./data/i2b2_notes/","-a=./data/i2b2_anno/",
"-o=./testtemp1/","-f=./configs/regex_tests/address_regex_test_transformed.json","-e=False"])


print("################")
print("RUNNING SCRIPT 2")
print("################")

#a = check_output
call(["python3", script2,"-i=./data/i2b2_notes/","-a=./data/i2b2_anno/",
"-o=./testtemp2/","-f=./configs/regex_tests/date_regex_test_transformed.json","-e=False"])

print("################")
print("TESTING OUTPUTS")
print("################")

directory = os.fsencode("testtemp1")

total_files = 0
different_files = 0
for f in os.listdir(directory):
    filename = os.fsdecode(f)
    if filename.endswith(".txt"): 
        total_files+=1
        #if the two files' contents are equal
        if not filecmp.cmp('testtemp1/'+filename, 'testtemp2/'+filename):
            print(filename+" doesn't match")
            different_files+=1
    else:
        continue

print(str(total_files-different_files)+ " tests have passed successfully!. ")
if different_files == 0:
    print("NO ERRORS FOUND")
else:
    print(str(different_files)+ " TESTS HAVE FAILED.")

rmtree("./testtemp1/")
rmtree("./testtemp2/")

#copy data
#let congs = [conf1, conf2, conf3, ...]
#for each congs:
    #run first program on the data and store results in x1
    #run second program on the data and store results in x2

    #compare x1 and x2

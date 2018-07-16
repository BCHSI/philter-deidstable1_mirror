import os
import sys
from subprocess import call,check_output
import filecmp
from shutil import rmtree

script = sys.argv[1]

BLACK_LIST_OUTPUT_DIR = "black_list/test_output/"
BLACK_LIST_CONF_DIR = "black_list/confs"
BLACK_LIST_DATA = "./black_list/data/"

WHITE_LIST_OUTPUT_DIR = "white_list/test_output/"
WHITE_LIST_CONF_DIR = "white_list/confs"
WHITE_LIST_DATA = "./white_list/data/"

def black_list_test():
    for directory in os.listdir(BLACK_LIST_CONF_DIR):
        if not os.path.isdir(os.path.join(BLACK_LIST_CONF_DIR, directory)):
            continue
        conf_file = os.path.join(BLACK_LIST_CONF_DIR, directory, "conf.json")
        true_output = os.path.join(BLACK_LIST_CONF_DIR, directory, "real_output")

        if not os.path.exists(BLACK_LIST_OUTPUT_DIR):
            os.mkdir(BLACK_LIST_OUTPUT_DIR)
        
        call(["python3", script,"-i="+BLACK_LIST_DATA,"-a="+BLACK_LIST_DATA,
        "-o="+BLACK_LIST_OUTPUT_DIR,"-f="+conf_file,"-e=False"])

        #a = input("please enter to continue")
        
        dir_diff(true_output,BLACK_LIST_OUTPUT_DIR)
        rmtree(BLACK_LIST_OUTPUT_DIR)

def white_list_test():
    for directory in os.listdir(WHITE_LIST_CONF_DIR):
        if not os.path.isdir(os.path.join(WHITE_LIST_CONF_DIR, directory)):
            continue
        conf_file = os.path.join(WHITE_LIST_CONF_DIR, directory, "conf.json")
        true_output = os.path.join(WHITE_LIST_CONF_DIR, directory, "real_output")

        if not os.path.exists(WHITE_LIST_OUTPUT_DIR):
            os.mkdir(WHITE_LIST_OUTPUT_DIR)
        
        call(["python3", script,"-i="+WHITE_LIST_DATA,"-a="+WHITE_LIST_DATA,
        "-o="+WHITE_LIST_OUTPUT_DIR,"-f="+conf_file,"-e=False"])

        #a = input("please enter to continue")
        
        dir_diff(true_output,WHITE_LIST_OUTPUT_DIR)
        rmtree(WHITE_LIST_OUTPUT_DIR)

def dir_diff(true_output, test_output):
    total_files = 0
    different_files = 0
    for f in os.listdir(true_output):
        filename = os.fsdecode(f)
        if filename.endswith(".txt"): 
            total_files+=1
            #if the two files' contents are equal
            
            if not filecmp.cmp( os.path.join(true_output, filename) , os.path.join(test_output, filename) ):
                print(filename+" doesn't match")
                different_files+=1
        else:
            continue
    print(str(total_files-different_files)+ " tests have passed successfully!. ")
    if different_files == 0:
        print("NO ERRORS FOUND")
    else:
        print(str(different_files)+ " TESTS HAVE FAILED.")

if __name__=="__main__":
    print("Running blacklist tests:...")
    black_list_test()
    print("Running whitelist tests:...")
    white_list_test()

#copy data
#let congs = [conf1, conf2, conf3, ...]
#for each congs:
    #run first program on the data and store results in x1
    #run second program on the data and store results in x2

    #compare x1 and x2

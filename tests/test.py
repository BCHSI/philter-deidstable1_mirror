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

def new_script_test(new_script, config_path):
    if not os.path.exists("testtemp1"):
        os.mkdir("testtemp1")
    if not os.path.exists("testtemp2"):
        os.mkdir("testtemp2")
    #run the current script
    print("RUNNING SCRIPT 1")
    call(["python3", script,"-i=../data/i2b2_notes/","-a=../data/i2b2_anno/",
    "-o=./testtemp1/","-f="+config_path,"-e=False"])
    #run the new script
    print("RUNNING SCRIPT 2")
    call(["python3", new_script,"-i=../data/i2b2_notes/","-a=../data/i2b2_anno/",
    "-o=./testtemp2/","-f="+config_path,"-e=False"])
    print("TESTING OUTPUTS")
    #compare the output
    dir_diff("testtemp1","testtemp2")
    rmtree("./testtemp1/")
    rmtree("./testtemp2/")

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
    
    if len(sys.argv) > 2:
        new_script = sys.argv[2]
        print("Running new script tests:...")
        new_script_test(new_script,"../configs/philter_alpha.json")


import os
import sys
from subprocess import call,check_output
import filecmp
from shutil import rmtree

script = os.path.abspath(sys.argv[1])

GOLDEN_OUTPUT = "golden_output"
PROGRAM_OUTPUT = "program_output"
INPUT_DATA = "input_data"

BLACK_LIST_CONF_DIR = os.path.abspath("black_list")+"/"
WHITE_LIST_CONF_DIR = os.path.abspath("white_list")+"/"
REGEX_CONF_DIR = os.path.abspath("regex")+"/"

SCRIPT_TEST_DATA = os.path.abspath("../data/i2b2_notes/")+"/"
SCRIPT_TEST_TEMP_FOLDER_1 = os.path.abspath("./testtemp1/")+"/"
SCRIPT_TEST_TEMP_FOLDER_2 = os.path.abspath("./testtemp2/")+"/"

WORKING_DIR = os.getcwd()

def black_list_test():
    for directory in os.listdir(BLACK_LIST_CONF_DIR):
        if not os.path.isdir(os.path.join(BLACK_LIST_CONF_DIR, directory)):
            continue
        conf_file = os.path.join(BLACK_LIST_CONF_DIR, directory, "conf.json")
        golden_output = os.path.join(BLACK_LIST_CONF_DIR, directory, GOLDEN_OUTPUT)+"/"
        program_output = os.path.join(BLACK_LIST_CONF_DIR, directory, PROGRAM_OUTPUT)+"/"
        input_data = os.path.join(BLACK_LIST_CONF_DIR, directory, INPUT_DATA)+"/"

        if os.path.exists(program_output):
            rmtree(program_output)
        os.mkdir(program_output)
        
        
        os.chdir(os.path.abspath(os.path.dirname(script)))
        call(["python3", script,"-i="+input_data,"-a="+input_data,
        "-o="+program_output,"-f="+conf_file,"-e=False"])
        os.chdir(WORKING_DIR)
        
                
        dir_diff(golden_output,program_output)

def white_list_test():
    for directory in os.listdir(WHITE_LIST_CONF_DIR):
        if not os.path.isdir(os.path.join(WHITE_LIST_CONF_DIR, directory)):
            continue
        conf_file = os.path.join(WHITE_LIST_CONF_DIR, directory, "conf.json")
        golden_output = os.path.join(WHITE_LIST_CONF_DIR, directory, GOLDEN_OUTPUT)+"/"
        program_output = os.path.join(WHITE_LIST_CONF_DIR, directory, PROGRAM_OUTPUT)+"/"
        input_data = os.path.join(WHITE_LIST_CONF_DIR, directory, INPUT_DATA)+"/"

        if os.path.exists(program_output):
            rmtree(program_output)
        os.mkdir(program_output)
        
        
        os.chdir(os.path.abspath(os.path.dirname(script)))
        call(["python3", script,"-i="+input_data,"-a="+input_data,
        "-o="+program_output,"-f="+conf_file,"-e=False"])
        os.chdir(WORKING_DIR)
        
                
        dir_diff(golden_output,program_output)

def regex_test():
    for directory in os.listdir(REGEX_CONF_DIR):
        if not os.path.isdir(os.path.join(REGEX_CONF_DIR, directory)):
            continue
        conf_file = os.path.join(REGEX_CONF_DIR, directory, "conf.json")
        golden_output = os.path.join(REGEX_CONF_DIR, directory, GOLDEN_OUTPUT)+"/"
        program_output = os.path.join(REGEX_CONF_DIR, directory, PROGRAM_OUTPUT)+"/"
        input_data = os.path.join(REGEX_CONF_DIR, directory, INPUT_DATA)+"/"

        if os.path.exists(program_output):
            rmtree(program_output)
        os.mkdir(program_output)
        
        
        os.chdir(os.path.abspath(os.path.dirname(script)))
        call(["python3", script,"-i="+input_data,"-a="+input_data,
        "-o="+program_output,"-f="+conf_file,"-e=False"])
        os.chdir(WORKING_DIR)
        
                
        dir_diff(golden_output,program_output)

def new_script_test(new_script, config_path):
    if os.path.exists(SCRIPT_TEST_TEMP_FOLDER_1):
        rmtree(SCRIPT_TEST_TEMP_FOLDER_1)
    os.mkdir(SCRIPT_TEST_TEMP_FOLDER_1)
    
    if os.path.exists(SCRIPT_TEST_TEMP_FOLDER_2):
        rmtree(SCRIPT_TEST_TEMP_FOLDER_2)
    os.mkdir(SCRIPT_TEST_TEMP_FOLDER_2)
    
    absolute_config_path = os.path.abspath(conf_path)
    absolute_script = os.path.abspath(script)
    absolute_new_script = os.path.abspath(new_script)


    #run the current script
    print("RUNNING SCRIPT 1")

    os.chdir(os.path.abspath(".."))
    call(["python3", absolute_script,"-i="+SCRIPT_TEST_DATA,"-a="+SCRIPT_TEST_DATA,"-o="+SCRIPT_TEST_TEMP_FOLDER_1,"-f="+absolute_config_path,"-e=False"])
    os.chdir(WORKING_DIR)

    #run the new script
    
    os.chdir(os.path.abspath(os.path.dirname(new_script)))
    print("RUNNING SCRIPT 2")
    call(["python3", absolute_new_script,"-i="+SCRIPT_TEST_DATA,"-a="+SCRIPT_TEST_DATA,"-o="+SCRIPT_TEST_TEMP_FOLDER_2,"-f="+absolute_config_path,"-e=False"])
    os.chdir(WORKING_DIR)

    print("TESTING OUTPUTS")
    #compare the output
    dir_diff(SCRIPT_TEST_TEMP_FOLDER_1,SCRIPT_TEST_TEMP_FOLDER_2)


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
    print("______________________________")

    print("Running whitelist tests:...")
    white_list_test()
    print("______________________________")

    print("Running regex tests:...")
    regex_test()
    print("______________________________")

    
    if len(sys.argv) > 2:
        new_script = sys.argv[2]
        conf_path = os.path.abspath("../configs/philter_alpha.json")
        print("Running new script tests:...")
        new_script_test(new_script,conf_path)


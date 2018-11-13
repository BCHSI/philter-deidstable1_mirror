import os
import sys
from subprocess import call,check_output
import filecmp
from shutil import rmtree
import argparse

script = os.path.abspath(sys.argv***REMOVED***3***REMOVED***)

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

def black_list_test(test_id=None, test_script=None):
    if test_id:
        print ("Running blacklist test: " + test_id)
        test_dir = os.path.join(BLACK_LIST_CONF_DIR, test_id)

        conf_file = os.path.join(test_dir, "conf.json")
        golden_output = os.path.join(test_dir, GOLDEN_OUTPUT)+"/"
        program_output = os.path.join(test_dir, PROGRAM_OUTPUT)+"/"
        input_data = os.path.join(test_dir, INPUT_DATA)+"/"

        if os.path.exists(program_output):
            rmtree(program_output)
        os.mkdir(program_output)
            
        test_script = os.path.abspath(test_script)
        os.chdir(os.path.abspath(os.path.dirname(test_script)))
        call(***REMOVED***"python3", test_script,"-i="+input_data,"-a="+input_data,
        "-o="+program_output,"-f="+conf_file,"-e=False"***REMOVED***)
        os.chdir(WORKING_DIR)                   
        dir_diff(golden_output,program_output)

    else:
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
            # print (os.getcwd())
            call(***REMOVED***"python3", script,"-i="+input_data,"-a="+input_data,
            "-o="+program_output,"-f="+conf_file,"-e=False"***REMOVED***)
            os.chdir(WORKING_DIR)
            
                    
            dir_diff(golden_output,program_output)

def white_list_test(test_id=None, test_script=None):
    if test_id:
        print ("Running whitelist test: " + test_id)
        test_dir = os.path.join(WHITE_LIST_CONF_DIR, test_id)

        conf_file = os.path.join(test_dir, "conf.json")
        golden_output = os.path.join(test_dir, GOLDEN_OUTPUT)+"/"
        program_output = os.path.join(test_dir, PROGRAM_OUTPUT)+"/"
        input_data = os.path.join(test_dir, INPUT_DATA)+"/"

        if os.path.exists(program_output):
            rmtree(program_output)
        os.mkdir(program_output)
            
        test_script = os.path.abspath(test_script)
        os.chdir(os.path.abspath(os.path.dirname(test_script)))
        call(***REMOVED***"python3", test_script,"-i="+input_data,"-a="+input_data,
        "-o="+program_output,"-f="+conf_file,"-e=False"***REMOVED***)
        os.chdir(WORKING_DIR)                   
        dir_diff(golden_output,program_output)
    else:
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
            call(***REMOVED***"python3", script,"-i="+input_data,"-a="+input_data,
            "-o="+program_output,"-f="+conf_file,"-e=False"***REMOVED***)
            os.chdir(WORKING_DIR)
            
                    
            dir_diff(golden_output,program_output)

def regex_test(test_id=None, test_script=None):
    if test_id:
        print ("Running blacklist test: " + test_id)
        test_dir = os.path.join(REGEX_CONF_DIR, test_id)

        conf_file = os.path.join(test_dir, "conf.json")
        golden_output = os.path.join(test_dir, GOLDEN_OUTPUT)+"/"
        program_output = os.path.join(test_dir, PROGRAM_OUTPUT)+"/"
        input_data = os.path.join(test_dir, INPUT_DATA)+"/"

        if os.path.exists(program_output):
            rmtree(program_output)
        os.mkdir(program_output)
            
        test_script = os.path.abspath(test_script)
        os.chdir(os.path.abspath(os.path.dirname(test_script)))
        call(***REMOVED***"python3", test_script,"-i="+input_data,"-a="+input_data,
        "-o="+program_output,"-f="+conf_file,"-e=False"***REMOVED***)
        os.chdir(WORKING_DIR)                   
        dir_diff(golden_output,program_output)
    else:
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
            call(***REMOVED***"python3", script,"-i="+input_data,"-a="+input_data,
            "-o="+program_output,"-f="+conf_file,"-e=False"***REMOVED***)
            os.chdir(WORKING_DIR)
        
                
        dir_diff(golden_output,program_output)

def new_script_test(scrip1, script2, conf1, conf2, in_dir):
    if os.path.exists(SCRIPT_TEST_TEMP_FOLDER_1):
        rmtree(SCRIPT_TEST_TEMP_FOLDER_1)
    os.mkdir(SCRIPT_TEST_TEMP_FOLDER_1)
    
    if os.path.exists(SCRIPT_TEST_TEMP_FOLDER_2):
        rmtree(SCRIPT_TEST_TEMP_FOLDER_2)
    os.mkdir(SCRIPT_TEST_TEMP_FOLDER_2)
    
    absolute_conf1_path = os.path.abspath(conf1)
    absolute_conf2_path = os.path.abspath(conf2)
    absolute_script1 = os.path.abspath(script1)
    absolute_script2 = os.path.abspath(script2)
    absolute_in_dir = os.path.abspath(in_dir)


    #run the current script
    print("RUNNING SCRIPT 1")

    os.chdir(os.path.abspath(".."))
    call(***REMOVED***"python3", absolute_script1,"-i="+absolute_in_dir ,"-a="+absolute_in_dir ,"-o="+SCRIPT_TEST_TEMP_FOLDER_1,"-f="+absolute_conf1_path,"-e=False"***REMOVED***)
    os.chdir(WORKING_DIR)

    #run the new script
    
    os.chdir(os.path.abspath(os.path.dirname(script2)))
    print("RUNNING SCRIPT 2")
    call(***REMOVED***"python3", absolute_script2,"-i="+absolute_in_dir ,"-a="+absolute_in_dir ,"-o="+SCRIPT_TEST_TEMP_FOLDER_2,"-f="+absolute_conf2_path,"-e=False"***REMOVED***)
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
    # version testing
    if sys.argv***REMOVED***2***REMOVED*** == 'v':
        # easy version testing - same default config & same default input
        # python3 test.py -m v script1.py script2.py
        if len(sys.argv) == 5:
            script1 = sys.argv***REMOVED***3***REMOVED***
            script2 = sys.argv***REMOVED***4***REMOVED***
            conf_path = os.path.abspath("../configs/philter_gamma.json")
            in_dir = os.path.abspath("../data/i2b2_notes/")
            print("Running easy version testing:...")
            new_script_test(script1, script2, conf_path, conf_path, in_dir)
        # version testing on existing outputs
        # python3 test.py -m v -o1 output1 -o2 output2
        elif len(sys.argv) == 7:
            help_str = """ Philter python3 test.py -i """
            ap = argparse.ArgumentParser(description=help_str)
            ap.add_argument("-m", "--mode", required=True, help="Three testing mode allowed: w, b, r, v.", type=str, choices=***REMOVED***'w','b','r', 'v'***REMOVED***,)
            ap.add_argument("-o1", "--out1", required=True, help="path to configuration file for script 1", type=str)
            ap.add_argument("-o2", "--out2", required=True, help="path to configuration file for script 2", type=str)
            args = ap.parse_args()
            output1 = args.out1
            output2 = args.out2
            print ('Running output checking:...')
            dir_diff(output1, output2)
        # version testing with user-specified configurations and inputs
        # python3 test.py -m v -s1 script1.py -s2 script2.py (-c1 conf1.json) (-c2 conf2.json) (-i input_data)
        # arguments in () are optional
        else:
            help_str = """ Philter python3 test.py -i """
            ap = argparse.ArgumentParser(description=help_str)
            ap.add_argument("-m", "--mode", required=True, help="Three testing mode allowed: w, b, r, v.", type=str, choices=***REMOVED***'w','b','r', 'v'***REMOVED***,)
            ap.add_argument("-i", "--input", default = './data/i2b2_notes/', required=False, help="path to input testing data", type=str)
            ap.add_argument("-c1", "--conf1", default = '../configs/philter_alpha.json', required=False, help="path to configuration file for script 1", type=str)
            ap.add_argument("-c2", "--conf2", default = '../configs/philter_alpha.json',required=False, help="path to configuration file for script 2", type=str)
            ap.add_argument("-s1", "--script1", required=True, help="path to script 1", type=str)
            ap.add_argument("-s2", "--script2", required=True, help="path to script 2", type=str)
            args = ap.parse_args()

            script1 = args.script1
            script2 = args.script2
            conf1 = args.conf1
            conf2 = args.conf2
            in_dir = args.input
            print("Running user-specified version testing:...")
            new_script_test(script1, script2, conf1, conf2, in_dir)
    # python3 test.py -m b script
    elif sys.argv***REMOVED***2***REMOVED*** == 'b':
        # running all blacklist tests
        if len(sys.argv) == 4:
            print("Running all blacklist tests:...")
            black_list_test()
            print("______________________________")
        # running only user-specified blacklist test case
        # python3 test.py -m b -t ID -s script.py
        elif len(sys.argv) == 7:
            help_str = """ Philter python3 test.py -i """
            ap = argparse.ArgumentParser(description=help_str)
            ap.add_argument("-m", "--mode", required=True, help="Three testing mode allowed: w, b, r, v.", type=str, choices=***REMOVED***'w','b','r', 'v'***REMOVED***,)
            ap.add_argument("-t", "--test_id", required=True, help="user-specified test ID", type=str)
            ap.add_argument("-s", "--script", required=True, help="script for testing", type=str)
            args = ap.parse_args()
            test_id = args.test_id
            script = args.script
            black_list_test(test_id,script)
            print("______________________________")
            

    elif sys.argv***REMOVED***2***REMOVED*** == 'w':
        # python3 test.py -m w script.py
        if len(sys.argv) == 4:
            print("Running all whitelist tests:...")
            white_list_test()
            print("______________________________")
        # running only user-specified blacklist test case
        # python3 test.py -m w -t ID -s script.py
        elif len(sys.argv) == 7:
            help_str = """ Philter python3 test.py -i """
            ap = argparse.ArgumentParser(description=help_str)
            ap.add_argument("-m", "--mode", required=True, help="Three testing mode allowed: w, b, r, v.", type=str, choices=***REMOVED***'w','b','r', 'v'***REMOVED***,)
            ap.add_argument("-t", "--test_id", required=True, help="user-specified test ID", type=str)
            ap.add_argument("-s", "--script", required=True, help="script for testing", type=str)
            args = ap.parse_args()
            test_id = args.test_id
            script = args.script
            white_list_test(test_id,script)
            print("______________________________")
    elif sys.argv***REMOVED***2***REMOVED*** == 'r':
        # python3 test.py -m w script.py
        if len(sys.argv) == 4:
            print("Running all whitelist tests:...")
            white_list_test()
            print("______________________________")
        # running only user-specified blacklist test case
        # python3 test.py -m w -t ID -s script.py
        elif len(sys.argv) == 7:
            help_str = """ Philter python3 test.py -i """
            ap = argparse.ArgumentParser(description=help_str)
            ap.add_argument("-m", "--mode", required=True, help="Three testing mode allowed: w, b, r, v.", type=str, choices=***REMOVED***'w','b','r', 'v'***REMOVED***,)
            ap.add_argument("-t", "--test_id", required=True, help="user-specified test ID", type=str)
            ap.add_argument("-s", "--script", required=True, help="script for testing", type=str)
            args = ap.parse_args()
            test_id = args.test_id
            script = args.script
            regex_test(test_id,script)
            print("______________________________")








            





    


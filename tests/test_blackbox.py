import os
import sys
from subprocess import call,check_output
import filecmp
from shutil import rmtree

script1 = sys.argv[1]
#script2 = sys.argv[2]

BLACK_BOX_TESTS = "tests/black_box_examples"
TEST_OUTPUT_DIR = "black_box/test_output"


def blackbox_test():
    #conf_dir = os.fsencode("black_box/confs")
    conf_dir = "black_box/confs"
    print(0)
    for directory in os.listdir(conf_dir):
        #directory = os.fsdecode(directory)
        if not os.path.isdir(os.path.join(conf_dir, directory)):
            print(directory)
            continue
        print("yes")
        conf_file = os.path.join(conf_dir, directory, "conf.json")
        true_output = os.path.join(conf_dir, directory, "real_output")

        if not os.path.exists(TEST_OUTPUT_DIR):
            os.mkdir(TEST_OUTPUT_DIR)
        
        call(["python3", script1,"-i=./black_box/data/","-a=./black_box/data/",
        "-o="+TEST_OUTPUT_DIR,"-f="+conf_file,"-e=False"])

        a = input("please enter to continue")
        
        dir_diff(true_output,TEST_OUTPUT_DIR)
        rmtree(TEST_OUTPUT_DIR)

 
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
    blackbox_test()
#copy data
#let congs = [conf1, conf2, conf3, ...]
#for each congs:
    #run first program on the data and store results in x1
    #run second program on the data and store results in x2

    #compare x1 and x2

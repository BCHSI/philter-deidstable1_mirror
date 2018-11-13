import argparse
import os
import sys
import uuid
import shutil
from shutil import copyfile
from glob import glob

GOLDEN_OUTPUT = "golden_output"
PROGRAM_OUTPUT = "program_output"
INPUT_DATA = "input_data"

BLACK_LIST_CONF_DIR = os.path.abspath("black_list")+"/"
WHITE_LIST_CONF_DIR = os.path.abspath("white_list")+"/"
REGEX_CONF_DIR = os.path.abspath("regex")+"/"


def add_conf(path_to_conf, test_mode):
    # add confs to black list testing
    if test_mode == 'b':
        # assign unique id for the new config
        new_conf_dir = str(id_counter(BLACK_LIST_CONF_DIR))
        new_conf_path = os.path.join(BLACK_LIST_CONF_DIR, new_conf_dir)
    elif test_mode == 'w':
        new_conf_dir = str(id_counter(WHITE_LIST_CONF_DIR))
        new_conf_path = os.path.join(WHITE_LIST_CONF_DIR, new_conf_dir)
    elif test_mode == 'r':
        new_conf_dir = str(id_counter(REGEX_CONF_DIR))
        new_conf_path = os.path.join(REGEX_CONF_DIR, new_conf_dir)
    else:
        print ("Invalid testing mode!")  

    if not os.path.exists(new_conf_path):
        os.mkdir(new_conf_path)
        conf_name = path_to_conf.split('/')[-1]
        shutil.copy(path_to_conf, new_conf_path)
        os.rename(os.path.join(new_conf_path, conf_name), os.path.join(new_conf_path, 'conf.json'))
        print ("The ID for your new configuration file is: " + new_conf_dir)
        os.mkdir(os.path.join(new_conf_path, GOLDEN_OUTPUT))
        # os.mkdir(os.path.join(new_conf_path, PROGRAM_OUTPUT))
        os.mkdir(os.path.join(new_conf_path, INPUT_DATA))
        # rename configuration file to conf.json


def add_test(test_mode, input, gold, conf_id):
    if test_mode == 'b':
        gold_path = os.path.join(BLACK_LIST_CONF_DIR, conf_id, GOLDEN_OUTPUT)
        data_path = os.path.join(BLACK_LIST_CONF_DIR, conf_id, INPUT_DATA)
        conf_path = os.path.join(BLACK_LIST_CONF_DIR, conf_id)
        print ("Testing mode: blacklist")

    elif test_mode == 'w':
        gold_path = os.path.join(WHITE_LIST_CONF_DIR, conf_id, GOLDEN_OUTPUT)
        data_path = os.path.join(WHITE_LIST_CONF_DIR, conf_id, INPUT_DATA)
        conf_path = os.path.join(WHITE_LIST_CONF_DIR, conf_id)
        print ("Testing mode: whitelist")

    elif test_mode == 'r':
        gold_path = os.path.join(REGEX_CONF_DIR, conf_id, GOLDEN_OUTPUT)
        data_path = os.path.join(REGEX_CONF_DIR, conf_id, INPUT_DATA)
        conf_path = os.path.join(REGEX_CONF_DIR, conf_id)
        print ("Testing mode: regex")
    # copy input data
    if os.path.isdir(input):
        print ("copying input testing directory: " + input)
        for f in os.listdir(input):
            filename = os.fsdecode(f)
            if filename.endswith(".txt"):
                input_path = os.path.join(input, f)
                shutil.copy(input_path, data_path)

    elif os.path.isfile(input):
        shutil.copy(input, data_path)
        print ("copying input testing file: " + input)

    # copy golden output
    if os.path.isdir(gold):
        print ("copying input testing directory: " + gold)
        for f in os.listdir(gold):
            filename = os.fsdecode(f)
            if filename.endswith(".txt"):
                gold_file = os.path.join(gold, f)
                shutil.copy(gold_file, gold_path)

    elif os.path.isfile(gold):
        shutil.copy(gold, gold_path)
        print ("copying golden output file: " + gold)

def id_counter(dir):
    # handle empty dir
    if len(os.listdir(dir) ) == 0:
        return 0
    else:
        return int(max(next(os.walk(dir))[1])) + 1

# check if the number of files and file names in golden file and input file match
def check_input(input, gold):
    if os.path.isdir(input) and os.path.isdir(gold):
        gold_file = os.listdir(gold)
        for f in os.listdir(input):
            filename = os.fsdecode(f)
            if filename.endswith(".txt"):
                if not filename in gold_file:
                    return False, 'Input error: file in input dir but not in golden dir'
            elif filename.endswith(".DS_Store"):
                pass
            else:
                return False, 'Input error: input must be txt file'
        return True, ''

    elif os.path.isdir(input) and os.path.isfile(gold):
        return False, 'Input error: input is dir but golden is file'
    
    elif os.path.isfile(input) and os.path.isdir(gold):
        return False, 'Input error: golden is dir but input is file'

    elif os.path.isfile(input) and os.path.isdir(gold):
        return True, ''

# increamentally add
def add_stdin_test(mode, input, gold, conf_id):
    if mode == 'b':
        gold_path = os.path.join(BLACK_LIST_CONF_DIR, conf_id, GOLDEN_OUTPUT, input + '.txt')
        data_path = os.path.join(BLACK_LIST_CONF_DIR, conf_id, INPUT_DATA, input + '.txt')
        conf_path = os.path.join(BLACK_LIST_CONF_DIR, conf_id)
        print ("Testing mode: blacklist")
        with open(data_path, 'w') as fout:
            fout.write(input)
            print ("Write to input file: " + data_path)
        with open(gold_path, 'w') as fout:
            fout.write(gold)
            print ("Write to golden file: " + gold_path)

    elif mode == 'w':
        gold_path = os.path.join(WHITE_LIST_CONF_DIR, conf_id, GOLDEN_OUTPUT, input + '.txt')
        data_path = os.path.join(WHITE_LIST_CONF_DIR, conf_id, INPUT_DATA, input + '.txt')
        conf_path = os.path.join(WHITE_LIST_CONF_DIR, conf_id)
        print ("Testing mode: whitelist")
        with open(data_path, 'w') as fout:
            fout.write(input)
            print ("Write to input file: " + data_path)
        with open(gold_path, 'w') as fout:
            fout.write(gold)
            print ("Write to golden file: " + gold_path)

    elif mode == 'r':
        gold_path = os.path.join(REGEX_CONF_DIR, conf_id, GOLDEN_OUTPUT, input + '.txt')
        data_path = os.path.join(REGEX_CONF_DIR, conf_id, INPUT_DATA, input + '.txt')
        conf_path = os.path.join(REGEX_CONF_DIR, conf_id)
        print ("Testing mode: regex")
        with open(data_path, 'w') as fout:
            fout.write(input)
            print ("Write to input file: " + data_path)
        with open(gold_path, 'w') as fout:
            fout.write(gold)
            print ("Write to golden file: " + gold_path)

if __name__=="__main__":
    # python3 add_test.py w ../confs/test1.json
    # only 3 args: adding conf file, return conf_id 
    if len(sys.argv) == 3:
        # ap = argparse.ArgumentParser(description=help_str)
        path_to_conf = sys.argv[2]
        test_mode = sys.argv[1]
        conf_path = os.path.abspath(path_to_conf)
        print("Adding configuration file......")
        add_conf(path_to_conf, test_mode)

    # # # python3 add_test.py -m w -i path_to_input -g path_to_gold_standard -c config_id
    # # # 9 args: adding input test file, golden file to directory specified by config_id
    elif len(sys.argv) == 9:
        
        help_str = """ Philter python3 add_test.py -i """
        ap = argparse.ArgumentParser(description=help_str)
        ap.add_argument("-m", "--mode", required=True, help="Three testing mode allowed: w, b, r.", type=str, choices=['w','b','r'],)
        ap.add_argument("-i", "--input", required=True, help="path to input testing data", type=str)
        ap.add_argument("-g", "--gold", required=True, help="path to gold standard annotated data", type=str)
        ap.add_argument("-c", "--conf_id", required=True, help="Unique ID of configuration file", type=str)
        args = ap.parse_args()
        signal, err = check_input(args.input, args.gold)
        if signal:
            add_test(args.mode, args.input, args.gold, args.conf_id)
        else:
            print (err)

    # # # stdin testing mode
    # # # python3 add_test.py -s True -i 'I am John' -g 'I am ****' -c ID -m b
    elif len(sys.argv) == 11 and sys.argv[1] == '-s':
        help_str = """ Philter python3 add_test.py -i """
        ap = argparse.ArgumentParser(description=help_str)
        ap.add_argument("-m", "--mode", required=True, help="Three testing mode allowed: w, b, r.", type=str, choices=['w','b','r'],)
        ap.add_argument("-i", "--input", required=True, help="input test string", type=str)
        ap.add_argument("-g", "--gold", required=True, help="golden standard string", type=str)
        ap.add_argument("-c", "--conf_id", required=True, help="Unique ID of configuration file", type=str)
        ap.add_argument("-s", "--std_in", required=True, help="Unique ID of configuration file", type=str)
        args = ap.parse_args()
        add_stdin_test(args.mode, args.input, args.gold, args.conf_id)
        


        

       


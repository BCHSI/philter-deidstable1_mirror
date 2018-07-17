import os
import sys
from subprocess import call
import filecmp
from shutil import rmtree

script = sys.argv[1]


REGEX_OUTPUT_DIR = "./src/tests/regex/test_output/"
REGEX_CONF_DIR = "./src/tests/regex/confs"
REGEX_DATA = "./src/tests/regex/data/"


def regex_test():
    for directory in os.listdir(REGEX_CONF_DIR):
        if not os.path.isdir(os.path.join(REGEX_CONF_DIR, directory)):
            continue
        conf_file = os.path.join(REGEX_CONF_DIR, directory, "conf.json")
        true_output = os.path.join(REGEX_CONF_DIR, directory, "real_output")

        if not os.path.exists(REGEX_OUTPUT_DIR):
            os.mkdir(REGEX_OUTPUT_DIR)

        call(["python3", script, "-i=" + REGEX_DATA, "-a=" + REGEX_DATA,
              "-o=" + REGEX_OUTPUT_DIR, "-f=" + conf_file, "-e=False"])

        dir_diff(true_output, REGEX_OUTPUT_DIR)
        rmtree(REGEX_OUTPUT_DIR)


def dir_diff(true_output, test_output):
    total_files = 0
    different_files = 0
    for f in os.listdir(true_output):
        filename = os.fsdecode(f)
        if filename.endswith(".txt"):
            total_files += 1
            # if the two files' contents are equal

            if not filecmp.cmp(os.path.join(true_output, filename), os.path.join(test_output, filename)):
                print(filename + " doesn't match")
                different_files += 1
        else:
            continue
    print(str(total_files - different_files) + " tests have passed successfully!. ")
    if different_files == 0:
        print("NO ERRORS FOUND")
    else:
        print(str(different_files) + " TESTS HAVE FAILED.")


if __name__ == "__main__":
    print("Running regex tests:...")
    regex_test()


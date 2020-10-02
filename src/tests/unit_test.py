import unittest
import sys
import os
import filecmp
from subprocess import call
# sys.path.append('./')


class TestPhilter(unittest.TestCase):

    def test_regex(self):
        # Add testing code here
        script1 = sys.argv[1]
        script2 = sys.argv[2]

        if not os.path.exists("testtemp1"):
            os.mkdir("testtemp1")

        if not os.path.exists("testtemp2"):
            os.mkdir("testtemp2")

        print ("################")
        print ("TESTING REGEX CONFIGS")

        # TODO: Modify the path to be the path of your testing data
        regex_config_dir = './src/tests/test_config/test_regex_configs/'
        test_data_dir = './src/tests/test_data/'
        test_anno_dir = './src/tests/test_anno/'

        for file in os.listdir(regex_config_dir):
            if file.endswith('.json'):
                if not os.path.exists("testtemp1"):
                    os.mkdir("testtemp1")

                if not os.path.exists("testtemp2"):
                    os.mkdir("testtemp2")
                print ("-------------------- REGEX CONFIG TESTING: " + file + ' ----------------------')
                print("################")
                print("RUNNING SCRIPT 1")
                print("################")
                call(["python3", script1, "-i=" + test_data_dir, "-a=" + test_anno_dir,
                        "-o=./testtemp1/", "-f=" + regex_config_dir+ file, "-e=False"])
                print("################")
                print("RUNNING SCRIPT 2")
                print("################")

                call(["python3", script2, "-i=" + test_data_dir, "-a=" + test_anno_dir,
                        "-o=./testtemp2/", "-f=" + regex_config_dir+ file, "-e=False"])

                print("################")
                print("TESTING OUTPUTS")
                print("################")

                directory = os.fsencode("testtemp1")

                total_files = 0
                different_files = 0
                for f in os.listdir(directory):
                    filename = os.fsdecode(f)
                    if filename.endswith(".txt") and 'DS_Store.' not in filename:
                        total_files += 1
                        if not filecmp.cmp('testtemp1/' + filename, 'testtemp2/' + filename):
                            print(filename + " doesn't match for config file: " + file)
                            different_files += 1
                    else:
                        continue

                print(str(total_files - different_files) + " tests have passed successfully for config file: " + file)
                if different_files == 0:
                    print("NO ERRORS FOUND")
                else:
                    print(str(different_files) + " TESTS HAVE FAILED.")

                rmtree("./testtemp1/")
                rmtree("./testtemp2/")
                print("-------------------- FINISHED REGEX CONFIG TESTING: " + file + ' ----------------------')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhilter)
    unittest.TextTestRunner(verbosity=2).run(suite)

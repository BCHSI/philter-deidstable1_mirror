# Testing Philter
## Unit Test
We define three units to test Philter: blacklist, whitelist and regular expression. 

### Easy version testing
Easy version testing allows users to simply test if their newly editted script produces the same results as the old script does. The default configuration file used is philter_gamma.json and the default input data is i2b2_notes. To do this, run:
```
python3 test.py -m v script1.py script2.py
```
### User-specified input for version testing
There may also be the case where users would like to apply different configurations on the two scripts and input data other than the default one. To do this, run:
```
python3 test.py -m v -s1 script1.py -s2 script2.py (-c1 conf1.json) (-c2 conf2.json) (-i input_data)
```
Note that arguments in parentheses are optional. If they are not specified, the default options will be enabled. 
### Simply testing out outputs
When users already have a set of output that they would like to run a quick comparison on, run the following command:
```
python3 test.py -m v -o1 output1 -o2 output2
```

### Run unit tests

To run the tests just navigate to the tests/ directory type the following command, use -m to specify the testing mode ('w' for whitelist, 'b' for blacklist and 'r' for regular expresssion):
```
python3 test.py -m b script
```

## Add your own test cases
We created utilities for adding test cases so that you can use one or two command lines to add your own test cases easily. You also have the choice to delete the added test cases if the test cases are no longer needed. The utility also supports standard input for quick testing. 

1. Using existing configuration files
If the configuration file that you want to use already exists in the testing directory, the name of that configuration file will be the ID. Then run the following command:

```
python3 add_test.py -m TEST_MODE -i PATH_TO_TEST_DATA -g PATH_TO_GOLD_DATA -c ID
```

-TEST_MODE: ‘w’ for whitelist testing, ‘b’ for blacklist testing, ‘r’ for regex testing. Other inputs will result in errors.

-PATH_TO_TEST_DATA: the path to where your test input files are located. It can be a single txt file or a directory which contains several txt files. 

-PATH_TO_GOLD_DATA: the path to where the gold standard files are located. It can be a single txt file or a directory which contains several txt files. 

-ID: the file name of the configuration file that you want to use for testing. 

2. Adding new configuration files
If you want to add a new configuration file that does not exist in current testing directory, the first step is to add the configuration file and get its ID. To do that, run the following command:

```
python3 add_test.py TEST_MODE PATH_TO_CONFIG
```

-TEST_MODE: ‘w’ for whitelist testing, ‘b’ for blacklist testing, ‘r’ for regex testing. Other inputs will result in errors.

-PATH_TO_CONFIG: the path to where your configuration file is located. It needs to be a single json file. 

This will print out the ID associated with the newly added configuration file. Then you can use the same command above to add your test data:

```
python3 add_test.py -m TEST_MODE -i PATH_TO_TEST_DATA -g PATH_TO_GOLD_DATA -c ID
```
3. Quick testing via standard input
If you want to perform a quick testing and get feedback immediately, you can input your test data via standard input. To do so, run the following command:

``` 
python3 add_test.py -s True -m TEST_MODE -i TEST_STRING -g GOLD_STRING -c ID
```
This will create a test input file and a gold standard output file under the directory ID. 


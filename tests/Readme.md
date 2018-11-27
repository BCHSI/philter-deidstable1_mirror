# Testing Philter
## Unit Test
We define three units to test Philter: blacklist, whitelist and regular expression. 

### Testing structure


#### Run unit tests

To run the tests just navigate to the tests/ directory type the following command:
```
python3 test.py <main_script_path>
```
For example:
```
python3 test.py ../main.py
```
#### Add your own test cases
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


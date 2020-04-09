import pandas as pd
import subprocess
import numpy as np
import argparse
import time
import re

def make_nicknames_dict(nicknames, frequency):
	# Read nicknames file
	nicknames_df = pd.read_csv(nicknames, delimiter = ',', encoding="latin-1")
	# Initialize dictionary
	nicknames_dict = {}
	# Set cutoff for alias frequency
	cutoff_frequency = frequency
	# Loop through nicknames df and add keys/values to dict
	for i in range(0,nicknames_df.shape***REMOVED***0***REMOVED***):
		key = nicknames_df***REMOVED***'NAME'***REMOVED******REMOVED***i***REMOVED***
		value = nicknames_df***REMOVED***'ALIAS'***REMOVED******REMOVED***i***REMOVED***
		freq = nicknames_df***REMOVED***'ALIAS FREQ'***REMOVED******REMOVED***i***REMOVED***
		# 1. Check the cutoff frequency
		if freq > cutoff_frequency:
			# 2. Check whether key exists in dict
			if key in nicknames_dict:
				# If yes, add to list
				nicknames_dict***REMOVED***key***REMOVED***.append(value)
			else:
				# If no, add the key to the dict and create a new list
				nicknames_dict***REMOVED***key***REMOVED*** = ***REMOVED***value***REMOVED***
	# Make sure all values in the lists are unique
	for key in nicknames_dict:
		new_value = list(np.unique(nicknames_dict***REMOVED***key***REMOVED***))
		nicknames_dict***REMOVED***key***REMOVED*** = new_value
	return nicknames_dict

def merge_probes_and_nicknames(probes, nicknames_dict, outfile, lines):
	
	# Initialize output file and write header line
	with open(outfile, "w") as myfile:
		myfile.write('pat_or_provider'+'\t'+'person_id'+'\t'+'RDB_Deid_person_id'+'\t'+'phi_type'+'\t'+'phi_source_col'+'\t'+'value'+'\t'+'clean_value'+'\t'+'to_delete'+'\n')
	# Define smaller chunk size
	chunk_size = 1000

	#unclean_names = ***REMOVED******REMOVED***
	times = ***REMOVED******REMOVED***
	counter = 0
	# Iterate through entire probes file by chunks
	# Test command: df_chunk = next(pd.read_csv(probes, delimiter = '\t', encoding="latin-1", chunksize=chunk_size))
	for df_chunk in pd.read_csv(probes, delimiter = '\t', encoding="latin-1", chunksize=chunk_size): #, names=***REMOVED***'pat_or_provider','person_id','phi_type','phi_source_col','value','clean_value','RDB_Deid_person_id','to_delete'***REMOVED***):
		start_time = time.time()
		counter += 1
		
		# Keep track of % probes processed
		percent_total = ((100000*counter)/109829457)*100
# Initialize output file and write header line



		for index, row in df_chunk.iterrows():
			# print(row)
			phi_type = str(row***REMOVED***'phi_type'***REMOVED***)
			value = str(row***REMOVED***'clean_value'***REMOVED***)
			#dict_copy = copy.deepcopy(nicknames_dict)
			#print(value)
			# Restart nicknames list
			nicknames_list = ***REMOVED******REMOVED***
			# If this is a name, find all possible nicknames
			if phi_type == 'fname':
				# Convert to upper case
				name_upper = value.upper()
				#print(name_upper)
				# Check whether name in is nickname dictionary
				if name_upper in nicknames_dict:
					name_list = nicknames_dict***REMOVED***name_upper***REMOVED***
					for name in name_list:
						nicknames_list.append(name)
					#print(nicknames_list)
					nicknames_list.append(name_upper)
				# If it's not, just create a single-element list with the original name, uppercase for uniformity
				else:
					nicknames_list = ***REMOVED***name_upper***REMOVED***
				# Add each new nickname to the file
				#print(index)
				#print(nicknames_list)
				with open(outfile, "a") as myfile:
				    for name in nicknames_list:
				    	new_row = str(row***REMOVED***'pat_or_provider'***REMOVED***)+'\t'+str(row***REMOVED***'person_id'***REMOVED***)+'\t'+str(row***REMOVED***'RDB_Deid_person_id'***REMOVED***)+'\t'+str(row***REMOVED***'phi_type'***REMOVED***)+'\t'+str(row***REMOVED***'phi_source_col'***REMOVED***)+'\t'+str(row***REMOVED***'value'***REMOVED***)+'\t'+name+'\t'+str(row***REMOVED***'to_delete'***REMOVED***)+'\n'
				    	myfile.write(new_row)
				    	#print(name)
				#print('\n')
			# If this is not a first name, just add the row to the new file
			else: 
				# Create the string to add to probes file
				new_row = str(row***REMOVED***'pat_or_provider'***REMOVED***)+'\t'+str(row***REMOVED***'person_id'***REMOVED***)+'\t'+str(row***REMOVED***'RDB_Deid_person_id'***REMOVED***)+'\t'+str(row***REMOVED***'phi_type'***REMOVED***)+'\t'+str(row***REMOVED***'phi_source_col'***REMOVED***)+'\t'+str(row***REMOVED***'value'***REMOVED***)+'\t'+str(row***REMOVED***'clean_value'***REMOVED***)+'\t'+str(row***REMOVED***'to_delete'***REMOVED***)+'\n'
				# Write original line to new probes file
				#print(index)
				#print("non-name")
				with open(outfile, "a") as myfile:
				    myfile.write(new_row)		
	
		# After the chunk has finished processing, print progress to terminal
		elapsed_time = time.time() - start_time
		times.append(elapsed_time)
		average_time = sum(times)/counter
		time_remaining = (((lines/chunk_size)*average_time)-(average_time*counter))/60/60
		print(counter, "%.2f" % percent_total+'%', "%.2f" % elapsed_time + 's', "%.2f" % average_time + 's avg', '('+"%.2f" % time_remaining + 'hrs remaining'+')')



def main():
    # get input/output/filename
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--probes",
                    help="Path to the probe file that needs to merged with the nicknames list",
                    type=str)
    ap.add_argument("-n", "--nicknames",
                    help="Path to the file that contains name/nickname pairings",
                    type=str)
    ap.add_argument("-o", "--output",
                    help="Path to the file that will contain the merged probes and nicknames",
                    type=str)
    ap.add_argument("-f", "--frequency", default=0.20,
                    help="Float indicating the minimum frequency of an alias for inclusion in the dictionary",
                    type=float)
    args = ap.parse_args()

    probes = args.probes
    nicknames = args.nicknames
    outfile = args.output
    frequency = args.frequency

    # Make nicknames dict
    nicknames_dict = make_nicknames_dict(nicknames,frequency)

    # Get number of lines in file
    proc = subprocess.Popen(***REMOVED***'wc','-l',probes***REMOVED***, stdout=subprocess.PIPE)
    output = proc.stdout.read()
    lines = int(output.decode("utf-8").split(' ')***REMOVED***0***REMOVED***)
    
    # Run the probes/nicknames merge code
    merge_probes_and_nicknames(probes, nicknames_dict, outfile, lines)


if __name__ == "__main__":
    main()

# # Test filepaths:
# probes = '/data/notes/prb_files_2018_03/prb1.txt'
# nicknames = '/data/notes/nickname_files/American_English_Nicknames.csv'
# outfile = '/data/muenzenk/probe_tests/test_merge_probes_and_nicknames.txt'



# current_index = 0
# current_row = ''
# for index, row in df_chunk.iterrows():
# 	# print(row)
# 	phi_type = str(row***REMOVED***'phi_type'***REMOVED***)
# 	value = str(row***REMOVED***'value'***REMOVED***)
# 	#### Clean names ####
# 	if phi_type == 'fname' or phi_type == 'lname':
# 		current_index = index
# 		current_row = row
# 		break

# index = current_index
# row = current_row



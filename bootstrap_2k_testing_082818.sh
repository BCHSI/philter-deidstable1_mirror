#!/bin/bash

# To run: nohup ./bootstrap_2k_testing_082818.sh > 2k_testing_bootstrap_out.txt 2>&1 &


# Define process checking function: checks number of running processes, and decreases the counter by 1 if 
processcheck() {
# Get number of whitelist processes
numprocess=$(ps ux |grep python3 |grep -c -v grep)
# Is the number of processes less than oir max number of processes?
if [[ $numprocess -lt $maxprocess ]]
# If so, decrease the process number by one
then
    counter=$numprocess
fi
}


# Define max number of processes to use
maxprocess=13
# Initialize process counter
counter=0
# Define number of notes to sample
sample_size=1892
# Define number of bootstrap replications
bootstrap_replications=100
for (( i=1; i <= $bootstrap_replications; i=(($i+1))))
do
	# If counter is less than the max number of processes
	if [[ $counter -lt $maxprocess ]]
	then # run bootstrap	
		bootstrap_name='philter_paper_testingbatch2k_20180802_updated'$i
		source_dir='/data/muenzenk/batch_data/philter_paper_testingbatch2k_20180802_updated'

		# Make directories to hold inputs/outputs
		bootstrap_dir='/data/muenzenk/bootstrap_data/philter_paper_testingbatch2k_20180802_updated_tests/'$bootstrap_name
		mkdir $bootstrap_dir
		notes_dir=$bootstrap_dir'/ucsf_notes/'
		mkdir $notes_dir
		anno_dir=$bootstrap_dir'/ucsf_anno/'
		mkdir $anno_dir
		results_dir=$bootstrap_dir'/ucsf_results/'
		mkdir $results_dir
		coord_path=$bootstrap_dir'/coordinates.json'

		# Create file with randomly sampled note names -- sample from /data/muenzenk/batch_data/randomtrainbatch500_20180716/ucsf_notes
		bootstrap_file_list=$bootstrap_dir'/'$bootstrap_name'_files.txt'
		# Get random sample of 1000 with replacement

		ls -d $source_dir'/ucsf_notes/'*.txt| shuf -r -n $sample_size > $bootstrap_file_list

		# Move all the right files to their correct folders (move notes, anno)
		while read filename; do
			pre_filename=${filename#$source_dir'/ucsf_notes/'}
	    	filename_alone=${pre_filename%.txt*}
	    	cp $source_dir'/ucsf_notes/'$filename_alone* $notes_dir
	    	cp $source_dir'/ucsf_anno/'$filename_alone* $anno_dir
		done < $bootstrap_file_list
		# Run philter on these 100 notes in the background (provide option to limit number of cores)
		nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/final_pipeline_tests/test_names_regex_context.json -a $anno_dir -x /data/muenzenk/batch_data/philter_paper_testingbatch2k_20180802_updated/phi_notes_test_batch20180802.json -i $notes_dir -o $results_dir -c $coord_path --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output $bootstrap_dir'/' > '/data/muenzenk/bootstrap_data/philter_paper_testingbatch2k_20180802_updated_tests/results/'$bootstrap_name'_results.txt' 2>&1 &
        
        counter=$((counter+1))

	fi
    # If counter is equal to max processes, we need to wait until one process has finished to spawn another process
    if [[ $counter -eq $maxprocess ]]
    then
        while [[ $counter -eq $maxprocess ]]; do processcheck; sleep 5; done
    fi

done



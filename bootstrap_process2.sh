#!/bin/bash

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
maxprocess=25
# Initialize process counter
counter=0
# Define number of notes to sample
sample_size=428
# Define number of bootstrap replications
bootstrap_replications=100
for (( i=1; i <= $bootstrap_replications; i=(($i+1))))
do
	# If counter is less than the max number of processes
	if [[ $counter -lt $maxprocess ]]
	then # run bootstrap	
		bootstrap_name='randomtrainbatch500_20180716_bootstrap'$i
		source_dir='/data/muenzenk/batch_data/randomtrainbatch500_20180716'

		# Make directories to hold inputs/outputs
		bootstrap_dir='/data/muenzenk/bootstrap_data/randomtrainbatch500_20180716_tests/'$bootstrap_name
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
		nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/ucsf_pipeline18.json -a $anno_dir -x /data/muenzenk/batch_data/randomtrainbatch500_20180716/phi_notes_rtb20180716.json -i $notes_dir -o $results_dir -c $coord_path --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ > '/data/muenzenk/bootstrap_data/randomtrainbatch500_20180716_tests/results/'$bootstrap_name'_results.txt' 2>&1 &
        counter=$((counter+1))

	fi
    # If counter is equal to max processes, we need to wait until one process has finished to spawn another process
    if [[ $counter -eq $maxprocess ]]
    then
        while [[ $counter -eq $maxprocess ]]; do processcheck; sleep 5; done
    fi

done



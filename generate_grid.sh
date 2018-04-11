#!/bin/bash

# Loop through config files
#counter=1
for config in ./configs/black_configs/*.json
do
	stripped_name=${config%.json}
	stripped_name=${stripped_name##*/}
	newdir='./data_'$stripped_name
	mkdir $newdir
	outdir='./data_'$stripped_name'/i2b2_results'
	mkdir $outdir
	mkdir './data_'$stripped_name'/phi'
	cp ./data/i2b2_anno $newdir
	cp ./data/i2b2_notes $newdir
    nohup python3 main.py -f $config -o $outdir --stanfordner /data/stanford-ner/  -p true >> grid_results.txt 2>&1 &
    #counter=$((counter+1))
    continue
done


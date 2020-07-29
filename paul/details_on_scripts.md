# Details on my scripts
1. ```paul/gene_symbols/HGNC_symbols_to_json.py```
2. ```paul/gene_symbols/notes_mini_create.py```
3. ```paul/scripts/batch.py```
4. ```paul/scripts/unbatch.py```
5. ```paul/scripts/cleanup_verbose_out.py```
6. ```paul/scripts/compare_results.py```
7. ```paul/scripts/extract_from_xml.py```
8. ```paul/scripts/find_obscured_symbols.py```
9. ```paul/scripts/find_rescued_symbols.py```
10. ```paul/for_philter_beta/diffs_coords.py```
11. ```paul/for_philter_beta/get_stats.py```
12. ```paul/pathology/get_new_terms.py```
13. ```filters/regex/transform_gene_symbols.py```
14. ```filters/regex/transform_pathology_terms.py```
---
#### ```HGNC_symbols_to_json.py```
This script parses the HGNC download of gene identifiers and outputs a .json file containing every approved, alias, and previous gene symbol to use as a whitelist. The script uses regular expressions to extract the gene identifiers, and is tailored to parse a specific HGNC download.

#### ```notes_mini_create.py```
This is a very simple script which takes the first 1,000 lines of the NOTEEVENTS.csv file which is part of the MIMIC dataset and writes those lines to a new .txt file (I used this file as example notes before I got the shredded notes).

#### ```batch.py```
This script will walk through all the files in a directory (including nested dirs), and batch (move) them into groups in a new directory containing a variable number of files.
- ```-i```: the path to the directory containing the files to be batched.
- ```-o```: the path to the directory where the new batched files will go (can be the same as ```-i```)
- ```-n```: the number of files per batch (default is 1,000)

#### ```unbatch.py```
This script will take in a directory (or nested dirs) and move all the files in that directory to a single new location (yes, this could also be achieved using ```batch.py``` and setting ```-n``` to be greater than the existing number of files).
- ```-i```: the path to the directory containing the files to be moved
- ```-o```: the path to the directory where the files will be moved to

#### ```cleanup_verbose_out.py```
This script takes "verbose" (```-v```) output from Philter and re-formats it to be easier to read. It outputs to the file "ogfilename_transformed.txt".
- ```-i```: the path to Philter's output file (getting an output file is achieved by pointing stdout to a file, eg. ```python3 script.py > path/to/file/which/will/contain/std/out.txt```)

#### ```compare_results.py```
This script compares two Philter runs by reading output files in the "eval" directory, and extracting lines from the input text files for Philter to get context for each match. The default comparison only looks at the summary.json files, however, there are options to compare false positives, true positives, etc as well.
- ```-i```: the directory containing the text files which was input to Philter
- ```-d1```: the first directory which will be compared (typically the "control", or the dir which is being tested against)
- ```-d2```: the second directory which will be compared (typically the "testing" directory, or the dir to compare against the control)
- ```-o```: the options for comparing false positives, true positives—the options are any combination of ```fp```, ```tp```, ```fn```, and ```tn```.

#### ```extract_from_xml.py```
This script was designed for extracting the text from the i2b2 xml annotations (the i2b2 dataset only had xml files, so the text needed to be extracted from in between the ```<TEXT></TEXT>``` tags). I created this script so that it will extract the text in between any two tags—in case I needed to use it for something else later.
- ```-i```: the path to the directory containing the xml files
- ```-o```: the path to the directory where the extracted .txt files will go
- ```-t```: the tag which the text will be extracted from

#### ```find_obscured_symbols.py```
This script compares two sets of notes, original vs. annotated, to figure out which notes contain obscured gene symbols. It runs off a grep search for gene symbols of the notes (command provided below). It has an option to copy the files containing the gene symbols to a new directory.
- ```-o```: the path to the dir containing the original notes
- ```-a```: the path to the dir containing the annotated notes
- ```-g```: the path to the grep output file
- ```-s```: the list of common symbols which were grepped for (newline separated .txt file)
- ```-c```: option to copy or not copy the files. "copy" will copy the files, "keep" will not
- ```-d```: the path to the dir where the copied files will go

```bash
   grep -n -r -w -f common_symbols.txt ./dir/with/files/ > ./path/to/outputfile.txt
```

#### ```find_rescued_symbols.py```
This script compares two sets of notes, annotated without modifications vs. with modifications (in my case, without whitelists and safe regexes vs. with), to find the gene symbols which got rescued by the modifications. It will output the symbol, file path, line number, and context for each un-obscured symbol.
- ```-o```: the path to the dir containing the annotated notes _without_ modifications
- ```-a```: the path to the dir containing the annotated notes _with_ modifications
- ```-g```: the path to the grep output file (see ```find_obscured_symbols.py``` for the specific grep command)
- ```-s```: the list of common symbols which were grepped for (newline separated .txt file)

#### ```diffs_coords.py```
This script is for the beta version of Philter. It will read in the coordinates.json files for two different Philter runs and output the tags which exist in the first run but not in the second.
- ```-og```: the path to the coords.json file for the 1st (original) Philter run
- ```-wl```: the path to the coords.json file for the 2nd (for me whitelisted) Philter run

#### ```get_stats.py```
This script is also for the beta version of Philter, and it too reads the coordinates.json files from two different Philter runs. However, it will extract the "phi types" and the "non-phi filepaths", and output how many of each exist (for example, I used this to see how many times the gene symbols whitelist got used).
- ```-og```: the path to the coords.json file for the 1st (original) Philter run
- ```-wl```: the path to the coords.json file for the 2nd (for me whitelisted) Philter run

#### ```get_new_terms.py```
This script reads in two .tsv files (```stains_hgnc.tsv``` and ```stains_umls.tsv```), containing common pathology terms provided by Dima (Dmytro) Lituiev and appends all terms which match ```[A-Z0-9\-]``` to the current gene symbols whitelist (creating a new json file of course).
- ```-f1```: the path to the first .tsv file
- ```-f2```: the path to the second .tsv file
- ```-wl```: the path to the current gene symbols whitelist
- ```-f```: the format of the whitelist (options are "json" or "txt")

#### ```transform_gene_symbols.py```
This script searches all the regexes in the ```filters/regex``` directory and replaces any instances of ```"""+gene_symbols+r"""``` with the list of gene symbols I created. So instead of editing a regex with 2,000 lines of gene symbols, I can instead just have ```"""+gene_symbols+r"""``` in my regex and replace that once I'm done.

#### ```transform_pathology_terms.py```
This script also searches all the regexes in the ```filters/regex``` directory, but replaces any instances of ```"""+staging_terms+r"""``` with the list of staging terms I got.

Hope this was helpful!

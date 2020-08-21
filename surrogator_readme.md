# Surrogator README


## What is Surrogator?
Surrogator.py will read in i2b2 or Philter XML formatted notes
Then apply date shifts to any phi tagged as a date.
Next it will replace all appropriate PHI with the respective PHI Tag
Then it will output .txt files with the appropriate surrogates to the specified directory

You can test out surrogator by adding the following folders to the data/ directory
[Download the following](https://drive.google.com/drive/folders/1zAgsx832PrNgYQy5Q3a79cK9FQPQ7gXT?usp=sharing
 unzip surrogator and move to data/surrogator
- unzip notes metadata and move to data/notes_metadata/
- unzip i2b2_data.zip and move to data/surrogator/testing-PHI-Gold-fixed/

# Running Surrogator

## Running from command line

### Testing Surrogator
```bash
python surrogator.py -t True
```

### Running Surrogator in Production Mode:
```bash
python surrogator.py -p True
```

This will use the default input directory "data/i2b2_results"
and write the output surrogated notes into the directory "data/surrogator/philter_results_output/"


### Running Surrogator on Auto Philter'ed XML Notes and Manually Annotated XML Notes:

```bash
python surrogator.py -rp True -ri True -w True
```

This will use the default input and output directories for both Philter'ed and I2B2 notes. It will run the surrogator on both sets of notes, and compare the outputs to create the evaluation tables. 

### Overview of all command line arguments:
```
	"-i","--input_dir", default="data/i2b2_results", help="specifiy the input directory",type=str
	"-o","--output_dir", default="data/surrogator/philter_results_output/", help="specifiy the output directory", type=str
	"-ii","--gold_anno_input_dir", default="data/surrogator/testing-PHI-Gold-fixed", help="specifiy the input gold manually annotated directory",type=str
	"-io","--gold_anno_output_dir", default="data/surrogator/testing-PHI-Gold-fixed-output/", help="specifiy the gold manually annotated output directory",type=str
	"-rp","--rerun_philter", default=False, help="This will re-run the philter surrogating. It takes a while, so default is false",type=bool
	"-ri","--rerun_i2b2", default=False, help="This will re-run the manually annotated gold standard surrogating. It takes a while, so default is false", type=bool
	"-e","--evaluation", default=True, help="This will run the evaluation comparing surrogated manually gold annotated with surrogated auto philter notes",type=bool
	"-t","--test", default=False, help="This will run the test, using less files", type=bool
	"-w","--write_surrogated_files", default=False, help="This will write the surrogated notes.",type=bool
	"-p","--prod", default=False, help="This will run the production mode, using only Philtered notes and not running evaluation",type=bool
	"-verbose","--verbose", default=True, help="This will output helpful print statements and surrogator logs, but also increase the runtime of the program",type=bool
```

### Log files:
In addition to the outputted surrogated text files, there will be a number of log files produced:
	philter_results_output/counts_by_phi_type.csv
	philter_results_output/date_shift_eval.csv
	philter_results_output/shifted_dates.csv
	philter_results_output/surrogated_text.csv
	testing-PHI-Gold-fixed-output/counts_by_phi_type.csv
	testing-PHI-Gold-fixed-output/shifted_dates.csv
	testing-PHI-Gold-fixed-output/surrogated_text.csv

You can view an output of the above log files in [following google sheet](https://docs.google.com/spreadsheets/d/1I_uhXq3qycbR06iI8qSKJbz_UEk9gu805yCPtMSz7Bc/edit#gid=412781496) :

It contains all of the logs that are written out from surrogator for the most recent run over all of the I2B2 notes.
- Date Shift Evaluations
- Dates that Surrogator Failed to Parse
- Philter counts by PHI Type
- Surrogated Text Summaries

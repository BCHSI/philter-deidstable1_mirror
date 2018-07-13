# Surrogator README


## What is Surrogator?
Surrogator.py will read in i2b2 or Philter XML formatted notes
Then apply date shifts to any phi tagged as a date.
Next it will replace all appropriate PHI with the respective PHI Tag
Then it will output .txt files with the appropriate surrogates to the specified directory

You can test out surrogator by adding the following folders to the data/ directory
[Download the following](https://drive.google.com/drive/folders/1zAgsx832PrNgYQy5Q3a79cK9FQPQ7gXT?usp=sharing)
- unzip surrogator and move to data/surrogator
- unzip notes metadata and move to data/notes_metadata/
- unzip i2b2_data.zip and move to data/surrogator/testing-PHI-Gold-fixed/

# Running Philter

## Running from command line

###Testing Surrogator:
`python surrogator.py -t True`

###Running Surrogator in Production Mode:
`python surrogator.py -p True`

This will use the default input directory "data/i2b2_results"
and write the output surrogated notes into the directory "data/surrogator/philter_results_output/"


###Running Surrogator on Philter'ed I2B2 XML Notes and I2B2 Tagged XML:

`python surrogator.py -rp True -ri True -w True`

This will use the default input and output directories for both Philter'ed and I2B2 notes. It will run the surrogator on both sets of notes, and compare the outputs to create the evaluation tables. 

In addition to the outputted surrogated text files, there will be a number of log files produced:
	```
	philter_results_output/counts_by_phi_type.csv
	philter_results_output/date_shift_eval.csv
	philter_results_output/shifted_dates.csv
	philter_results_output/surrogated_text.csv
	testing-PHI-Gold-fixed-output/counts_by_phi_type.csv
	testing-PHI-Gold-fixed-output/shifted_dates.csv
	testing-PHI-Gold-fixed-output/surrogated_text.csv
	```
You can view an output of the above log files in [following google sheet](https://docs.google.com/spreadsheets/d/1I_uhXq3qycbR06iI8qSKJbz_UEk9gu805yCPtMSz7Bc/edit#gid=412781496) :

It contains all of the logs that are written out from surrogator for the most recent run over all of the I2B2 notes.
- Date Shift Evaluations
- Dates that Surrogator Failed to Parse
- Philter counts by PHI Type
- Surrogated Text Summaries

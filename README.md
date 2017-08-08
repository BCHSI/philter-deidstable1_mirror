# README


### What is PHI-REDUCER? 
The package and associated scripts provide an end-to-end pipeline for removing Protected Health Information from clinical notes (or other sensitive text documents) in a completely secure environment (a machine with no external connections or exposed ports). We use a combination of regular expressions, Part Of Speech (POS) and Entity Recognition (NER) tagging, and filtering through a whitelist to achieve nearly perfect Recall and generate clean, readable notes. Everything is written in straight python and the package will process any text file, regardless of structure. You can install with PIP (see below) and run with a single command-line argument. Parallelization of processesing can be infinitly divided across cores or machines. 

- Please note: we don't make any claims that running this software on your data will instantly produce HIPAA compliance. 

There are 3 core functions in the pipeline. We've also included 2 bonus, or convenience functions, because they have been important for our own development and work.

1. **annotation:** Annotate each word in a text file as either being PHI (if so, annotate the type of PHI) or not. This is useful to generate a ground-truth corpus for evaluation of phi-reduction software on your own files. 

2. **phi-reducer:** Pull in each note from a directory (nested directories are supported), maintain clean words and replace PHI words with a safe filtered word: **\*\*PHI\*\***, then write the 'phi-reduced' output to a new file with the original file name appended by '\_phi\_reduced'. Conveniently generates additional output files containing meta data from the run: 
	- number of files processed
	- number of instances of PHI that were filtered
	- list of filtered words
	- etc.

3. **eval:** Compares the outputs of **annotation.py** and **phi-reducer.py** to evaluate phi-reduction performance. Provides the True and False Positive words found, True and False Negative words found, Precision and Recall scores, etc. 
4. **infoextract (bonus script):** Extracts entity:value pairs (eg: alcohol\_use:rare or blood_pressure:130/90) from phi-reduced clinical notes and writes them to table. 
5. **randompick (bonus script):** Randomly select n-notes from a directory (can be nested).Useful to generate subsets of notes to annotate, evaluate performance, and identify terms that may be common only at your institution. 




 


# Installation

**Install phi-reducer**

```pip3 install phi-reducer```

### Dependencies
spacy package en: A pretrained model of the english language.
You can learn more about the model at the [spacy model documentation]("https://spacy.io/docs/usage/models") page. Language models are required for optimum performance. 

**Download the model:**

```python3 -m spacy download en ```

Note for Windows Users: This command must be run with admin previleges because it will create a *short-cut link* that let's you load a model by name.



# Run

**annotation**
```phi-annotation -i ~/some_dir/note_I_want_to_annotate.txt -o ~/dir_to_save_annotated_pickled_file_to/```

Arguments:

- ("-i", "--inputfile") = Path to the file you would like to annotate.
- ("-o", "--output")= Path to the directory where the annotated note will be saved.

**phi-reducer**
``` phi-reducer -i ./raw_notes_dir -r -o dir_to_write_to -p 124```

Arguments:

- ("-i", "--input") = Path to the directory or the file that contains the PHI note, the default is ./input_test/
- ("-r", "--recursive") = help="whether read files in the input folder recursively. Default = False. 
- ("-o", "--output") = Path to the directory that save the PHI-reduced note, the default is ./output_test/.
- ("-w", "--whitelist") = Path to the whitelist, the default is phireducer/whitelist.pkl
- ("-n", "--name") = The key word of the output file name, the default is *_phi_reduced.txt.
- ("-p", "--process") = The number of processes to run simultaneously, the default is 1.

**eval.py**
```phi-eval -p dir_containing_phi_notes -a dir_annotated_pkl.ano -o output_path```

Arguments:

- ("-p", "--phinote") = Path to the directory containing phi reduced notes (or a single file)
- ("-a", "--annotation") = Path to the annotated file
- ("-o", "--output") = Path to save the summary pkl and statistics text
- ("-r", "--recursive") = whether read files in the input folder recursively

**randompick**
```python3 ./randompick.py -i ./dir_to_sample_from/ -r -n 2 -o dir_to_copy_to```

Arguments:

- ("-i", "--input") = Path to the directory that contains the notes you would like to sample from.
- ("-r", "--recursive") = Whether to search through all sub-directories that exist in "i"
- ("-o", "--output") = Output path to the directory that will store the randomly picked notes.
- ("-n", "--number") = "How many files you want to pick?



# How it works
This should a reasonable overview of *exactly* what each script does

**Annotation Interface**
![Alt text](https://github.com/beaunorgeot/images_for_presentations/blob/master/annot_use.png?raw=true "annotation interface")


Once you have launched the annotation software using a given note as input, you will see that note displayed on your screen with each word having an index() on it's left and the phi-category currently assigned to the word on the right []. Each word is intially assigned to the non-phi category. Choose from the available commands to annotate your file for phi.

Command Options

- all: change the phi-category of all words in the document at the same time.
- range: select a range of word indices and then assign the same phi-category to all words in that range. Enter the index of the first word and hit RETURN.Enter the index of the last word and hit RETURN.
- select: select a list of word indices and then assign the same phi-category to all words in that list. Enter the index of each word, using spaces to separate each word index, hit RETURN when you have listed all desired word indices
- show: show the current phi-category of all words
- done: to finish annotating the current sentence and start the next one.
- exit: exit the script without saving

**phi-reducer**

![Alt text](https://github.com/beaunorgeot/images_for_presentations/blob/master/Whitelist_V2.png?raw=true "phi-reduction process")

**Example output for eval**

![Alt text](https://github.com/beaunorgeot/images_for_presentations/blob/master/eval%20result.PNG?raw=true "eval_output example")


**Example output table for infoextraction**

![Alt text](https://github.com/beaunorgeot/images_for_presentations/blob/master/infoext_from_phireduced_note.PNG?raw=true "info_extraction_csv example")

### Why did we build it?
Clinical notes capture rich information on the interaction between physicians, nurses, patients, and more. While this data holds the promise of uncovering valuable insights, it is also challenging to work with for numerous reasons. Extracting various forms of knowledge from Natural Language is difficult on it's own. However, attempts to even begin to mine this data on a large scale are severely hampered by the nature of the raw data, it's deeply personal. In order to allow more researchers to have access to this potentially transformative data, individual patient identifiers need to be removed in a way that presevers the content, context, and integrity of the raw note. 

De-Identification of clinical notes is certainly not a new topic, there are even machine learning competitions that are held to compare methods. Unfornuately these did not provide us with a viable approach to de-identify our own notes. First, the code from methods used in the competitions are often not available. 
Second, the notes used in public competitions don't reflect our notes very closely and therefore even methods that are publicly available did not perform nearly as well on our data as they did on the data used for the competitions (As noted by Ferrandez, 2012, BMC Medical Research Methodology who compared public methods on VA data). Additionally,our patient's privacy is paramount to us which meant we were unwilling to expose our data use any methods that required access to any url or external api call. Finally, our goal was to de-identify all 40 MILLION of our notes. There are multiple published approaches that are simply impractical from a run-time perspective at this scale. 

## Why a whitelist (aren't blacklists smaller and easier)?

Blacklists are certainly the norm, but they have some pretty large inherent problems. For starters, they present an unbounded problem: there are a nearly infinite number of words that could be PHI and that you'd therefore want to filter. For us, the difference between blacklists vs whitelists comes down to the *types* of errors that you're willing to make. Since blacklists are made of  PHI words and/or patterns, that means that when a mistake is made PHI is allowed through (Recall error). Whitelists on the other hand are made of non-PHI which means that when a mistake is made a non-PHI word gets filtered (Precision Error). We care more about recall for our own uses, and we think that high recall is also important to others that will use this software, so a whitelist was the sensible approach. 

### Results (current, unpublished)
- Our method on the only data that we care about (our own)
- Physionet results on our data
- Our method on the I2B2 public data set 

# Recommendations
- Search through filtered words for institution specific words to improve precision
- have a policy in place to report phi-leakage
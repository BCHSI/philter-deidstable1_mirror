If you use this software for any publication, please cite: Radhakrishnan, Lakshmi, et al. "A certified de-identification system for all clinical text documents for information extraction at scale." JAMIA open 6.3 (2023): ooad045. https://academic.oup.com/jamiaopen/article/6/3/ooad045/7219298

# README

![Alt text](https://github.com/beaunorgeot/images_for_presentations/blob/master/logo_v4.tif?raw=true "annotation interface")

### What is PHIlter? 
Philter is a command-line based clinical text de-identification software that removes protected health information (PHI) from any plain text file. The package and associated scripts provide an end-to-end pipeline for removing Protected Health Information from clinical notes (or other sensitive text documents) in a completely secure environment (a machine with no external connections or exposed ports). We use a combination of regular expressions, Part Of Speech (POS) and Entity Recognition (NER) tagging, and filtering through a whitelist to achieve nearly perfect Recall and generate clean, readable notes. Everything is written in straight python and the package will process any text file, regardless of structure. You can download/clone (see below) and run with a single command-line argument. Parallelization of processesing can be infinitly divided across cores or machines. 
The software has built-in evaluation capabilities and can compare Philter PHI-reduced notes with a corresponding set of ground truth annotations. However, annotations are not required to run Philter. The following steps may be used to 1) run Philter in the command line without ground truth annotations, or 2) generate Philter-compatible annotations and run Philter in evaluation mode using ground truth annotations. Although any set of notes and corresponding annotations may be used with Philter, the examples provided here will correspond to the I2B2 dataset, which Philter uses in its default configuration.

### Important
- Please note: we don't make any claims that running this software on your data will instantly produce HIPAA compliance. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

see: [BSD-3 LISCENCE](https://github.com/BCHSI/de-id_stable1/blob/develop/LICENSE)

# Installing Philter
Download or clone the project source code and switch to v1.0 tag. Run the commands below from the home directory.
## Installing Requirements
To install the Python requirements, run the following command:
```bash
pip3 install -r requirements.txt
```
# Running Philter
Before running Philter, make sure to familiarize yourself with the various options that may be used for any given Philter run:

### Flags:
**-h:**&nbsp; Show this help message and exit<br/>
**-i (input):**&nbsp; Path to the directory or the file that contains the PHI note, the default is ./data/i2b2_notes/<br/>
**-o (output):**&nbsp; Path to the directory to save PHI-reduced notes, the default is ./data/i2b2_results/<br/>
**-f (filters):**&nbsp; Path to the config file, the default is ./configs/philter_one.json.<br/>
**-s (surrogate_info):**&nbsp; Path to the tsv file that contains the surrogate info per note key<br/>
**-d (deid_filename):**&nbsp; When this is true, the pipeline saves the de-identified output using de-identified note ids for the filenames<br/>
**-k (dynamic_blacklist):**&nbsp; Path to the probes file, if path to file is absent dynamic blacklist does not get generated<br/>
**-m (mongodb):**&nbsp; When mongo config file is provided the pipeline will use mongodb to get input text, surrogation meta data and write out deid text<br/>
**-l (log):**&nbsp; When this is true, the pipeline prints and saves log in a subdirectory in each output directory<br/>
**-e (eval):**&nbsp; When this is true, the pipeline computes and saves statistics in a subdirectory in each output directory (see option -a)<br/>
**-a (anno):**&nbsp; Path to the directory or the file that contains the PHI annotation, the default is ./data/i2b2_xml/ (needs option -e True)<br/>
**-x (xml):**&nbsp; When this is true, the pipeline looks for xml files in the input directory and extracts the PHI information from the xml tags without running philter<br/>
**-v (verbose):**&nbsp;When verbose is set, will emit messages about script progress<br/>
**-b (batch):**&nbsp;Batch number to process<br/>
**-r (refdate):**&nbsp;Reference date for shifting dates (for patients > 90 y.o.)<br/>

## 0. Curating I2B2 XML Files
To remove non-HIPAA PHI annotations from the I2B2 XML files, run the following command:

**-i** Path to the directory that contains the original I2B2 xml files<br/>
**-o** Path to the directory where the curated files will be written<br/>

```bash
python improve_i2b2_notes.py -i data/i2b2_xml/ -o data/i2b2_xml_updated/
```
## 1. Running Philter WITHOUT evaluation (no ground-truth annotations required)
In this mode, the PHI will be redactd and the evaluation step will be skipped:

**a.** Make sure the input file(s) are in plain text format. If you are using the I2B2 dataset (or any other dataset in XML or other formats), the note text must be extracted from each original file and be saved in individual text files. Examples of properly formatted input files can be found in ./data/i2b2_notes/.

**b.** Store all input file(s) in the same directory, and create an output directory (if you want the PHI-reduced notes to be stored somewhere other than the default location).

**c.** Create a configuration file with specified filters (if you do not want to use the default configuration file).

**d.** Run Philter in the command line using either default or custom parameters.

Use the following command to run a single job:
```bash
python3 deidpipe.py -i ./data/i2b2_notes/ -o ./data/i2b2_results/ -f ./configs/philter_one.json 
```

To run multiple jobs simultaneously, all input notes handled by a single job must be located in separate directories to avoid cross-contamination between output files. For example, if you wanted to run Philter on 1000 notes simultaneously on two processes, the two input directories might look like:

1. ./data/batch1/500_input_notes_batch1/
2. ./data/batch2/500_input_notes_batch2/

In this example, the following two commands would be used to start running each job in the background:
```bash
nohup python3 main.py -i ./data/batch1/500_input_notes_batch2/ -o ./data/i2b2_results_test/ -f ./configs/philter_delta.json --prod=True > ./data/batch1/batch1_terminal_out.txt 2>&1 &

```
```bash
nohup python3 main.py -i ./data/batch2/500_input_notes_batch2/ -o ./data/i2b2_results_test/ -f ./configs/philter_delta.json --prod=True > ./data/batch2/batch2_terminal_out.txt 2>&1 &

```

## 2. Running Philter WITH evaluation (ground truth annotations required)

In this mode, PHI is redacted, and the evaluation step will be performed using the annotated notes provided by the user:

**a-c.** See Step 1a-c above

**d.** Run Philter in evaluation mode using the following command:

```bash
python3 deidpipe.py -i ./data/i2b2_notes/ -a ./data/i2b2_anno/ -o ./data/i2b2_results/ -f=./configs/philter_one.json -e True
```

By defult, this will output PHI-reduced notes (.txt format) in the specified output directory.


# How it works
This should a reasonable overview of *exactly* what each script does

**philter**

![Alt text](https://github.com/beaunorgeot/images_for_presentations/blob/master/flow_v2.tif?raw=true "phi-reduction process")


**Example Input and Output**
![Alt text](https://github.com/beaunorgeot/images_for_presentations/blob/master/deid_note_v2.tif?raw=true "eval_output example")

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

![Alt text](https://github.com/beaunorgeot/images_for_presentations/blob/master/performance_1.png?raw=true "info_extraction_csv example")

# Recommendations
- Search through filtered words for institution specific words to improve precision
- have a policy in place to report phi-leakage

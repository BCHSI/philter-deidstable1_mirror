If you use this software for any publication, please cite: Radhakrishnan et al. "[A certified de-identification system for all clinical text documents for information extraction at scale](https://doi.org/10.1093/jamiaopen/ooad045)" JAMIA Open 6.3 (2023): ooad045.

### Important
> [!WARNING]
> Please note: we don't make any claims that running this software on your data will instantly produce HIPAA compliance. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

see: [BSD-3 LICENSE](LICENSE)

# README

### What is PHIlter? 
Philter is a command-line based clinical text de-identification software that removes protected health information (PHI) from any plain text file. The package and associated scripts provide an end-to-end pipeline for removing Protected Health Information from clinical notes (or other sensitive text documents) in a completely secure environment (a machine with no external connections or exposed ports). We use a combination of regular expressions, Part Of Speech (POS), and filtering through include and exclude lists to achieve nearly perfect Recall and generate clean, readable notes. Everything is written in straight python and the package will process any text file, regardless of structure. You can download/clone (see below) and run with a single command-line argument. Parallelization of processesing can be infinitly divided across cores or machines. 
The software has built-in evaluation capabilities and can compare Philter PHI-reduced notes with a corresponding set of ground truth annotations. However, annotations are not required to run Philter. The following steps may be used to 1) run Philter in the command line without ground truth annotations, or 2) generate Philter-compatible annotations and run Philter in evaluation mode using ground truth annotations. Although any set of notes and corresponding annotations may be used with Philter, the examples provided here will correspond to the I2B2 dataset, which Philter uses in its default configuration.



# Installing Philter
Download or clone the project source code and switch to v1.0 tag (or use the latest `develop` code if you feel adventurous). Run the commands below from the home directory.
## Installing Requirements
To install the Python requirements, run the following command:
```bash
pip3 install -r requirements.txt
```
# Running Philter
Before running Philter, make sure to familiarize yourself with the various options that may be used for any given Philter run:
```bash
python3 deidpipe.py -h
```
### Flags:
**-h:**&nbsp; Show this help message and exit<br/>
**-i (input_dir):**&nbsp; Path to the directory or the file that contains the PHI note<br/>
**-o (output_dir):**&nbsp; Path to the directory to save PHI-reduced notes<br/>
**-f (filters_config_file):**&nbsp; Path to the config file, the default is configs/philter_one.json<br/>
**-s (surrogate_info_file):**&nbsp; Path to the tsv file that contains the surrogate info per note key<br/>
**-d (True,False):**&nbsp; When this is true, the pipeline saves the de-identified output using de-identified note ids for the filenames, the default is True<br/>
**-k (known_pii_file):**&nbsp; Path to the probes file, if path to file is absent Dynamic Blocklist does not get generated<br/>
**-m (mongodb_config_file):**&nbsp; When mongo config file is provided the pipeline will use mongodb to get input text, surrogation meta data and write out deid text<br/>
**-l (True,False):**&nbsp; When this is true, the pipeline prints and saves log in a subdirectory in each output directory, the default is True<br/>
**-e (True,False):**&nbsp; When this is true, the pipeline computes and saves statistics in a subdirectory in each output directory (see option -a), the default is False<br/>
**-a (anno_dir):**&nbsp; Path to the directory or the file that contains the PHI annotation, the default is data/i2b2_xml/ (needs option -e True)<br/>
**-x (True,False):**&nbsp; When this is true, the pipeline looks for xml files in the input directory and extracts the PHI information from the xml tags without running Philter, the default is False<br/>
**-v:**&nbsp;When verbose is set, will emit messages about script progress<br/>
**-b (batch_num):**&nbsp;Batch number to process (needed for mongo usage)<br/>
**-r (ref_date):**&nbsp;Reference date for shifting birth dates for patients > 90 y.o., the default is date.today()<br/>

## 0. Curating I2B2 XML Files
Skip this step if you do not intend to use I2B2 data for evaluation. To remove non-HIPAA PHI annotations from the I2B2 XML files, run the following command:

**-i** Path to the directory that contains the original I2B2 xml files<br/>
**-o** Path to the directory where the curated files will be written<br/>

```bash
python improve_i2b2_notes.py -i data/i2b2_xml/ -o data/i2b2_xml_updated/
```
## 1. Running Philter WITHOUT evaluation (no ground-truth annotations required)
In this mode, the PHI will be redactd and the evaluation step will be skipped:

**a.** Make sure the input file(s) are in plain text format. If you are using the I2B2 dataset (or any other dataset in XML or other formats), the note text must be extracted from each original file and be saved in individual text files. Examples of properly formatted input files can be found in data/i2b2_notes/.

**b.** Store all input file(s) in the same directory, and create an output directory.

**c.** Create a configuration file with specified filters (if you do not want to use the default configuration file).

**d.** Run Philter in the command line using either default or custom parameters.

Use the following command to run a single job:
```bash
python3 deidpipe.py -i data/i2b2_notes/ -o data/i2b2_results/ -f configs/philter_one.json 
```

To run multiple jobs simultaneously, see [deidloop.py](deidloop.py)/[deidloop_mongo.py](deidloop_mongo.py) and [deidmaster.py](deidmaster.py)/[deidmaster_mongo.py](deidmaster_mongo.py)

## 2. Running Philter WITH evaluation (ground truth annotations required)

In this mode, PHI is redacted, and the evaluation step will be performed using the annotated notes provided by the user:

**a-c.** See Step 1a-c above

**d.** Run Philter in evaluation mode using the following command:
```bash
python3 deidpipe.py -i data/i2b2_notes/ -o data/i2b2_results/ -f configs/philter_one.json -e True -a data/i2b2_xml/ 
```
By defult, this will output PHI-reduced notes (.txt format) in the specified output directory.

## 3. Running Philter with Mongo I/O

This mode lets us use Mongo DB as the I/O for Philter runs. Here are the pre processing steps that needs to be completed before running Philter using Mongo.

**a.** Load the Notes meta data with structured mappings to Mongo. We have internally called it `note_info_map` collection.
```
{
        "_id" : ObjectId("5fde7677eaf0903792f48cd8"),
        "redact_date" : ISODate("2023-10-04T11:43:17.322Z"),
        "mrn" : "",
        "patient_ID" : "",
        "BirthDate" : "",
        "Deid_BirthDate" : "",
        "DeathDate" : null,
        "status" : "",
        "deid_turns_91_date" : "",
        "deid_date_offset_cdw" : "",
        "note_key" : "",
        "deid_note_key" : "",
        "note_type" : "Progress Notes”,
        "meta_md5" : "6c8c7a0697a1edfbd0d669d5d63d0afb",
        "philter_version" : “Philter One"
}
```

**b.** Load the Notes Text file to another collections called `raw_note_text`. For quick joins we have leveraged the mongo internal object_id as the primary key on both the collections to quickly link the note_text to the meta data.
```
{
        "_id" : ObjectId("5fde7677eaf0903792f48cd8"),
        "note_key" : "",
        "raw_note_text" : “”
}
```

**c.** Below are the list of associated collections we have to help with our monthly refresh cycles

`note_info_map` 	 Mongo Collection which contains the meta data and surrogate information<br/>
`raw_note_text` 
 Mongo Collection which contains the identified note text<br/>
`philtered_note_text` 
 Mongo Collection with the PHI redacted note text
```
{
       "_id" : ObjectId("5fde7677eaf0903792f48cd8"),
       "note_text” :””
}
```
`probes` 
 Mongo Collection with UCSF probes
```
{
        "_id" : ObjectId("6462acb791cef5bb442b10cd"),
        "person_id" : "",
        "ADDR" : [ "" ],
        "fname" : [ "" ],
        "lname" : [ "" ],
        "MRN" : [ "", "", "", "" ],
        "phone" : [ "" ],
        "ZIP" : [ "" ]
}
```
`status` 
 Mongo Collection with notes classified into Add, Update, Delete or Keep
```
{
        "_id" : ObjectId("5fde7677eaf0903792f48cd8"),
        "note_key_status" : "Keep",
        "update_date" : ISODate("2023-04-10T22:58:08.474Z"),
        "only_text_update" : false
}
```
`chunk` 
 Mongo Collection with details on the notes to be deidentified<br/>

**d.** Create a mongo config file. Here is a sample config file for your reference.
```
{
   "client": “localhost",
   "username": "",
   "password": "",
   "db": "100k_test_db",
   "collection_tmpmeta": "tmpmeta",
   "collection_tmpstatus": "tmpstatus",
   "collection_tmptext": "tmptext",
   "collection_meta_data": "note_info_map",
   "collection_status": "status",
   "collection_raw_note_text": "raw_note_text",
   "collection_deid_note_text": "philtered_note_text",
   "collection_chunk": "chunk",
   "collection_delta": "delta",
   "collection_log_batch_phi_count": "log_batch_phi_count",
   "collection_log_batch_summary": "log_batch_summary",
   "collection_log_detailed_batch_summary": "log_detailed_batch_summary",
   "collection_log_dynamic_blacklist": "log_dynamic_blacklist",
   "collection_log_failed_dates": "log_failed_dates",
   "collection_log_parsed_dates": "log_parsed_dates",
   "collection_log_phi_marked": "log_phi_marked",
   "collection_super_log": "log_super_log",
   "collection_user_meta": "user_facing_meta_data",
   "collection_probes": "probes",
   "collection_tmp_nk_patid": "tmp_note_key_pat",
   "known_phi": true,
   "philter_version": “Philter V1.0"
}
```

**e.** To run the philter parallel on multiple threads create the chunk table with the following fields. 
```
{
   "_id" : ObjectId(""),
   "patient_ID" : "",
   "url" : "",
   "batch" : 1
}
```

- The `_id` must correspond to the note object_id in the `note_meta_data` and `raw_notes_text` tables. This shows the script which note to de-identify. 
- The `patient_ID` field is used to pull the probes if you have them to help with de-identification.
- The `url` is the name of the server you are running the de-identification process on. This is required in case you are planning to run the de-identification process on multiple servers.
- The `batch` number is the same for a set of 1000 notes so that the algorithm knows to process those together in one thread.

**f.** Once we have the data loaded into mongo, chunk collection and a config file created we can use the following command to launch the runs.
```bash
python3 deidloop_mongo.py -t 4  --mongofile configs/mongo.json --philterconfig config/philter_one.json --superlog False --philter /path/to/philter/scripts/ > stdouterr.txt 2>&1 &
```
### Flags:
**-h, --help:** show this help message and exit<br/>
**--mongofile (MONGOFILE):** with mongo configuration Path to the mongo config file<br/>
**-t (THREADS), --threads (THREADS):** Number of parallel threads, the default is 1<br/>
**--philterconfig (PHILTERCONFIG):** Path to Philter program config files like philter_one.json<br/>
**--philter (PHILTER):**     Path to philter scripts<br/>
**--superlog [True, False]:**   When this is set, the pipeline
                        prints and saves a super log in mongo combining logs
                        of each batch<br/>
**-r (REFDATE), --refdate (REFDATE):**
                        Reference date for shifting dates (for patients > 90
                        y.o.)<br/>


## 4. Why did we build it?
Clinical notes capture rich information on the interaction between physicians, nurses, patients, and more. While this data holds the promise of uncovering valuable insights, it is also challenging to work with for numerous reasons. Extracting various forms of knowledge from Natural Language is difficult on it's own. However, attempts to even begin to mine this data on a large scale are severely hampered by the nature of the raw data, it's deeply personal. In order to allow more researchers to have access to this potentially transformative data, individual patient identifiers need to be removed in a way that presevers the content, context, and integrity of the raw note. 

De-Identification of clinical notes is certainly not a new topic, there are even machine learning competitions that are held to compare methods. Unfornuately these did not provide us with a viable approach to de-identify our own notes. First, the code from methods used in the competitions are often not available. 
Second, the notes used in public competitions don't reflect our notes very closely and therefore even methods that are publicly available did not perform nearly as well on our data as they did on the data used for the competitions (As noted by Ferrandez, 2012, BMC Medical Research Methodology who compared public methods on VA data). Additionally,our patient's privacy is paramount to us which meant we were unwilling to expose our data use any methods that required access to any url or external api call. Finally, our goal was to de-identify all 40 MILLION of our notes. There are multiple published approaches that are simply impractical from a run-time perspective at this scale. 

## Why a safelist (aren't blocklists smaller and easier)?

Blocklists are certainly the norm, but they have some pretty large inherent problems. For starters, they present an unbounded problem: there are a nearly infinite number of words that could be PHI and that you'd therefore want to filter. For us, the difference between blocklists vs safelists comes down to the *types* of errors that you're willing to make. Since blocklists are made of PHI words and/or patterns, that means that when a mistake is made PHI is allowed through (Recall error). Safelists on the other hand are made of non-PHI which means that when a mistake is made a non-PHI word gets filtered (Precision Error). We care more about recall for our own uses, and we think that high recall is also important to others that will use this software, so a safelist was the sensible approach. 

# Recommendations
- Search through filtered words for institution specific words to improve precision
- Have a policy in place to report PHI-leakage

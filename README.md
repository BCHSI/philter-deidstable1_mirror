# README

![Alt text](https://github.com/beaunorgeot/images_for_presentations/blob/master/logo_v4.tif?raw=true "annotation interface")

### What is PHIlter? 
The package and associated scripts provide an end-to-end pipeline for removing Protected Health Information from clinical notes (or other sensitive text documents) in a completely secure environment (a machine with no external connections or exposed ports). We use a combination of regular expressions, Part Of Speech (POS) and Entity Recognition (NER) tagging, and filtering through a whitelist to achieve nearly perfect Recall and generate clean, readable notes. Everything is written in straight python and the package will process any text file, regardless of structure. You can install with PIP (see below) and run with a single command-line argument. Parallelization of processesing can be infinitly divided across cores or machines. 

### Important
- Please note: we don't make any claims that running this software on your data will instantly produce HIPAA compliance. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

see: [MIT LISCENCE](https://opensource.org/licenses/MIT)

# Running Philter

## Production mode
```bash
python3 main.py -i "./data/i2b2_notes_test/" -o "./data/i2b2_results_test/" --prod=True
```
Notes - this production mode will avoid outputting unnecessary print statements, and will skip the evaluation steps

## Running from command line
```bash
python3 main.py -i=./data/i2b2_notes/ -a=./data/i2b2_anno/ -o=./data/i2b2_results/ -f=./configs/example.json
```


### Run a Stanford NER Taggger  (Warning, very slow)
#### Remove 'PERSON' configs/remove_person_tags.json
```json
python3 main.py -i=./data/i2b2_notes/ -a=./data/i2b2_anno/ -o=./data/i2b2_results/ -f=./configs/test_ner.json
```


### Run a Whitelist
#### Remove 'PERSON' configs/remove_person_tags.json
```json
python3 main.py -i=./data/i2b2_notes/ -a=./data/i2b2_anno/ -o=./data/i2b2_results/ -f=./configs/test_whitelist.json
```


### Run a Blacklist
#### Remove 'PERSON' configs/remove_person_tags.json
```json
python3 main.py -i=./data/i2b2_notes/ -a=./data/i2b2_anno/ -o=./data/i2b2_results/ -f=./configs/test_blacklist.json
```


### Run a Regex
#### Remove 'PERSON' configs/remove_person_tags.json
```json
python3 main.py -i=./data/i2b2_notes/ -a=./data/i2b2_anno/ -o=./data/i2b2_results/ -f=./configs/just_digits.json
```

### Run Multiple patterns
#### Remove PHI configs/example.json
```json
python3 main.py -i=./data/i2b2_notes/ -a=./data/i2b2_anno/ -o=./data/i2b2_results/ -f=./configs/example.json
```

# Features : Dynamic filtering

## Dynamic Filtering
Turn non-Protected Health information notes into annotation notes using a list of pattern recognizers. The types are configured as follows:

### Regex (remove all digits) 
#### patterns/remove_all_digits.json
```json
[
	{
		"title":"All Digits", 
		"type":"regex",
		"exclude":true,
		"filepath":"filters/regex/alldigits.txt",
		"notes":"Greedy catches anything with digits in it"
	}
]


```

### Whitelists / Blacklists (remove anything not in this dictionary, or keep anything in a dict)
#### patterns/keep_whitelist_remove_blacklist.json

Note the only difference in the config between a whitlist and a blacklist is the "exclude" 
value set to true / false. 

```json
[
	{
		"title":"Names Blacklist",
		"type":"set",
		"exclude":true,
		"filepath":"filters/blacklists/names_blacklist_common.pkl",
		"pos":[],
		"notes":""
	},
	{
		"title":"General Whitelist",
		"type":"set",
		"exclude":false,
		"filepath":"filters/whitelists/whitelist.pkl",
		"pos":[],
		"notes":"These are words we beleive are safe"
	},
]
```

### POS (Part of Speech Whitelist / Blacklist) Similar to above, but will only match NLTK tag types
see: [NLTK Tags](https://stackoverflow.com/a/38264311/1404663)
```json
[
	{
		"title":"Test Whitelist",
		"type":"set",
		"exclude":false,
		"filepath":"filters/whitelists/whitelist_2-28_2.json",
		"pos":[],
		"notes":"These are words we beleive are safe"
	}
]
```

### NER Tagging (Warning, very slow)
#### Remove 'PERSON' TAGS
```json
[	
	{
		"title":"Test NER",
		"type":"stanford_ner",
		"exclude":true,
		"pos":["PERSON"],
		"notes":"This should test that ner is working"
	}
]

```


# Installation

**Install philter**
```bash

//TODO, see RUN

```
<!-- 
```pip3 install philter```

### Dependencies
spacy package en: A pretrained model of the english language.
You can learn more about the model at the [spacy model documentation]("https://spacy.io/docs/usage/models") page. Language models are required for optimum performance. 

**Download the model:**

```python3 -m spacy download en ```

Note for Windows Users: This command must be run with admin previleges because it will create a *short-cut link* that let's you load a model by name.

 -->


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
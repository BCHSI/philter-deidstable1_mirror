# Who am I and what I worked on
I'm Paul, a high school summer intern who worked remotely at the UCSF Bakar Computational Health Sciences Institute in summer 2020 on Philter. Philter is a clinical de-identification software which removes protected health information (phi) from clinical notes to make the data in the notes more readily available to the scientific community. I worked on implementing whitelists and safe regexes for gene symbols and pathology terms to address the issue of Philter obscuring these symbols and terms. Gene symbols and pathology terms (eg. BRCA1) were obscured by Philter because the values have similarities to person names.

Whitelists get used near the end of the pipeline, after Philter has identified the phi. The whitelists might contain values which are actually phi, so running the whitelist at the end allows values to be identified as phi before they would have been incorrectly identified as safe by the whitelist. What whitelists do is prevent the "catch-all" at the end of the pipeline (which obscures all the identified phi without a type) from obscuring safe words which were tagged as phis without a type. Introducing gene symbols and pathology terms whitelists would theoretically prevent Philter from obscuring the gene symbols and pathology terms present in the clinical notes.

However, upon closer examination and testing, I discovered that multiple regular expressions earlier in the pipeline tagged the gene symbols with a type—which meant that the whitelist never had a chance to un-tag-as-phi the symbols. To fix this, I created a "safe" regex which I put into the pipeline ahead of the regexes which were obscuring gene symbols. This "safe" regex would get to the gene symbols ahead of the other regexes and mark them as safe. I used the same technique of creating a safe regex to address the incorrect obscuring of some pathology terms.

I also worked with David, my fellow summer intern, a little (it was his project) to create the correct xml annotations for the MIMIC notes. I only provided some advice and tested his results. The reason why I'm mentioning it is because having correct annotations is crucial to testing any sort of thing with Philter—they allow Philter to evaluate its performance. The annotations are in xml format, and contain for each phi in the clinical note the phi type, the actual value, the start and stop indices of the value(s), and an ID. For example, Philter, reading this annotation file, can identify actual phi it obscured (true positives), which values it obscured but were actually safe (false positives), etc, and calculate metrics about its performance. I needed annotations for my test set of notes in order to determine how much the whitelists/safe regexes helped.

If some of my scripts are confusing, check out [details_on_scripts.md](https://github.com/pauliwog/philter-ucsf/blob/master/paul/details_on_scripts.md)!
And here is [the change-log](https://github.com/pauliwog/philter-ucsf/blob/master/paul/CHANGE-LOG.md) which should have everything I added or modified.

# What I did

### Overview
**Setup**
1. Got access to and downloaded data (MIMIC, i2b2).
2. Downloaded and set up Philter-Beta.
3. Got Philter-Zeta and set up a python virtual environment.

**Gene symbols project**
1. Found, downloaded, extracted, and converted a list of gene symbols to create a whitelist.
2. Made a list of the most common gene symbols, then searched for and copied MIMIC notes containing a common gene symbol to use as a test set of notes for evaluating the whitelist.
3. Ran these MIMIC notes through Philter (without the whitelist), compared before and after to find obscured gene symbols, then separated the notes with the obscured gene symbols.
    - If I ran Philter on a note and it obscured the gene symbol(s) in that note, then running Philter with the whitelist would hopefully un-obscure those symbols.
    - Whether Philter un-obscured the symbols or not would tell me how well the whitelist was working.
4. Downloaded and set up newest version of Philter because the beta version was buggy when using xml annotations.
5. Realized a big problem with the whitelist approach and created a safe regex to catch gene symbols before they got obscured.
6. Merged my code with new latest version of Philter, then ran MIMIC notes with annotations through Philter, with and without the whitelist and regexes and determined that the whitelist + safe regexes did work (after a couple modifications) and did not impact recall! I then sent my code off to get tested on UCSF data.

**Pathology project**
1. Tried to find and download data ([mtsamples](https://www.mtsamples.com/)), decided to use the MIMIC gene symbols test set instead.
2. Created safe regexes or whitelists for staging terms, cassette (or slide) numbers, lymph nodes, and molecular markers.
3. Tested on MIMIC notes. Even though the notes didn't have the pathology terms I was trying to rescue, I could use the MIMIC notes to refine my regexes and make sure they didn't catch non-pathology terms.
4. Sent my code off to get tested on UCSF data.
5. Edit/modify my safe regexes/whitelists, test on UCSF data, rinse and repeat.


## A closer look at the setup
### 1
Obtained access to MIMIC and i2b2 data sets (I just followed the instructions on the site pages).
- [Link to MIMIC](https://mimic.physionet.org/gettingstarted/access/).
- [Link to i2b2](https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/#).

### 2
I forked and set up a repo of the beta version of Philter on GitHub, [link](https://github.com/BCHSI/philter-ucsf) to Philter-Beta and [my repo](https://github.com/pauliwog/philter-ucsf) (not a fork of beta version, but a copy of the latest version of Philter containing the scripts I used). Then I set up Terminal on my Mac with Homebrew, python, etc—here's how I did it.
1. Install command line tools: ```xcode-select --install```.
2. Install [Homebrew](https://brew.sh/): ```/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"```.
3. Update path for Homebrew : ```export PATH="/usr/local/opt/python/libexec/bin:$PATH"```.
4. Install python3, pip, setuptools, etc and create separate dir for python 3: ```brew install python3 && cp /usr/local/bin/python3 /usr/local/bin/python```.
5. Done! All the necessary tools have been installed, and python 3 is ready to be used. The commands ```python -V``` or ```python3 -V``` will display python versions. Use ```pip3 install <packagename>``` to install packages for python 3 (eg. ```pip3 install numpy```).

### 3
When I installed Philter-Zeta, it came with a virtual environment, but it didn't work properly for me—my local file paths differed. So I learned how to set up a virtual python environment (referencing [this handy article](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-macos)). Again, if you're following in my steps, here's how to set a virtual environment up.
1. ```cd ./the/proj/dir``` or ```mkdir ./the/proj/dir && cd ./the/proj/dir``` to get to the directory you want to create the virtual environment in.
2. ```python3 -m venv python_env``` creates the virtual environment (python_env will be a new directory created in the current directory). This command also sets up the basic directories and files in the virtual environment.
3. ```source python_env/bin/activate``` will activate the virtual environment. Now your command line prompt should look like this ```(python_env) computer-name:path/to/somewhere$```. To deactivate the virtual environment, just simply type ```deactivate```.


## A closer look at the gene symbols project
### 1
1. There's this really nice website, [genenames.org](https://www.genenames.org/) (called HGNC), which has an easy, customizable form for downloading gene data ([link to data form](https://biomart.genenames.org/martform/#!/default/HGNC?datasets=hgnc_gene_mart)). It takes the data from NCBI gene banks (or other places if you so choose). I downloaded all the gene symbols and names from NCBI to compile into a list, which included approved, alias, and previous symbols and names for each gene.
2. Once that was downloaded, I created a script ([HGNC_symbols_to_json.py](https://github.com/pauliwog/philter-ucsf/blob/master/paul/gene_symbols/HGNC_symbols_to_json.py)) to extract the gene symbols from the HGNC download and create a json file containing each symbol, in the correct format for Philter to use as a whitelist. This script read the HGNC list and used regex to extract the gene symbols from it (the regex is tailored to the HGNC formatting, so it wouldn't work for a different download).
3. Philter runs using a config file, which tells it what to do, and in what order. To get Philter to use the whitelist I created, I first duplicated the original config file and added a section at the bottom (more details in step 5) telling Philter to use the whitelist ([my test config file](https://github.com/pauliwog/philter-ucsf/blob/master/configs/philter_zeta_genes.json)). I chose to create a separate test config file because it is easy to switch between config files when running Philter (the ``` -f ./path/to/configs.json``` option).

### 2, 3, and 4
1. Next, I wanted a test set of data so I could see how well the whitelist did, so I compiled a list of 35 common gene symbols ([common_symbols.txt](https://github.com/pauliwog/philter-ucsf/blob/master/paul/common_symbols.txt)) to search for in the MIMIC notes.
2. I then searched for those symbols in all the MIMIC notes using the Unix ```grep``` command and copied the notes containing the common symbols into a new directory.
```bash
   grep -l -r -w -f common_symbols.txt ./path/to/dir/containing/notes/to/search/in/ > ./path/to/outputfile.txt
```
```bash
   for file in `cat ./path/to/outputfile.txt`; do cp "$file" ./dir/where/you/want/the/files/containing/the/gene/symbols/to/go/ ; done
```
3. After this was done, I ended up with ~20,000 notes, and running 20,000 notes through Philter all at once would take weeks on my laptop (and I didn't have enough memory anyway), so I created a short script ([batch.py](https://github.com/pauliwog/philter-ucsf/blob/master/paul/other_scripts/batch.py)) which took the notes and batched them into folders containing a variable number of notes each (I chose 1,000). I then ran these folders through original Philter (without the whitelist) five at a time. There's a reverse script to unbatch files which I created as well, [unbatch.py](https://github.com/pauliwog/philter-ucsf/blob/master/paul/other_scripts/unbatch.py). Here's the basic command I used to run Philter-Beta.
```bash
   python3 main.py -i ./path/to/input/dir/ -a ./path/to/anno/dir/ -o ./path/to/output/dir/ -f ./path/to/configfile.json -c ./path/to/coordsfile.json -e False > ./path/to/outputfile.txt
```
4. Next, I compared the before and after notes (before and after Philter annotations) to find the notes containing gene symbols obscured by Philter. These notes would become the test set for the whitelist. I originally designed my script which identified obscured gene symbols to use another grep search, so sorry if you are duplicating my process—you're going to need to do another grep :disappointed: (or you could write your own script).
```bash
   grep -n -r -w -f common_symbols.txt ./dir/with/files/ > ./path/to/anotheroutputfile.txt
```
5. Using my script ([find_obscured_symbols.py](https://github.com/pauliwog/philter-ucsf/blob/master/paul/other_scripts/find_obscured_symbols.py)) and the grep search from the previous step, I went through all the MIMIC notes I had annotated looking for notes containing obscured gene symbols. My script also has an option to copy the notes containing the symbols to a new directory, which I used. More details on the script can be found inside it (click the link above). _Original_ means the notes which are not annotated. _Annotated_ means the notes which have been run through Philter and have phi obscured with asterisks.
```bash
   python3 find_obscured_symbols.py -o ./path/to/dir/with/original/notes/ -a ./path/to/dir/with/annotated/notes/ -g ./path/to/grep/output/file/from/step/four.txt -s ./path/to/list/of/common_symbols.txt -c copy -d ./path/to/dir/where/notes/will/be/copied/to/
```
6. After trying for a while with Lakshmi's help to get Philter-Beta to accept the xml annotations so we could test the modifications, we decided to use the newest version of Philter instead, not wanting to mess too much with the beta version. This decision was also important because Philter-Zeta outputs more log and eval files, making it easier for me to assess how the whitelists and safe regexes performed.

### 5
As described at the very top (2nd and 3rd paragraphs), the gene symbols whitelist had been inserted into the config file near the very end. However, when I ran Philter with the whitelist on a test note, nothing changed. After some fiddling, Lakshmi told me to move the whitelist to the top of the config file and try again. This time, the gene symbols in the test note were not obscured! But...putting the whitelist at the beginning of the pipeline was dangerous, because the whitelist could catch real phi values and mark them as safe (false negatives) before the real phi could be caught by regular expressions later in the pipeline. So we definitely didn't want to put the whitelist at the front of the pipeline. It seemed like we had two other options, to edit the regexes catching the gene symbols, or to create a "safe" regex to tag gene symbols as safe.

The next logical step was to take a closer look at the regexes which were catching the symbols. To do so, I enabled the verbose option in Philter (```-v```) and added a print statement in philter.py, the main program. And when I subsequently ran Philter on several test notes, I found that multiple different regexes were catching the gene symbols :cry:. That meant to fix the problem I would have to edit multiple regexes. On top of that, some of them looked quite complicated.

So instead, I decided to create a safe regex, one that would catch the gene symbols and tell Philter "DON'T OBSCURE THESE." To do so, I ran a grep search on the test notes so I could look at all the instances of gene symbols and find patterns which could be used to identify a symbol. Using those patterns, I created a regular expression to catch the gene symbols and mark them as safe. However, the regex I used to represent a gene symbol, ```[A-Z][A-Z0-9\-]+```, would not exclusively match gene symbols. To fix this problem, I modified a piece of code a previous intern had written which would take regex containing a "variable" and replace that variable with a long list of something (in my case gene symbols)—much easier than editing a regular expression with 2000 lines of symbols! Here's the [transform_gene_symbols.py](https://github.com/pauliwog/philter-ucsf/blob/master/filters/regex/transform_gene_symbols.py) code, and the [regex with the variable](https://github.com/pauliwog/philter-ucsf/blob/master/filters/regex/gene_symbols/gene_symbols_safe_03.txt) and [without](https://github.com/pauliwog/philter-ucsf/blob/master/filters/regex/gene_symbols/gene_symbols_safe_03_transformed.txt).

### 6
I then tested my regex and whitelist on the MIMIC test set with annotations, modified my regex to be more specific, and eventually got everything working! However, we wanted to test my additions to Philter on the UCSF data using the latest code, so I created a [change-log](https://github.com/pauliwog/philter-ucsf/blob/master/paul/CHANGE-LOG.md) so Lakshmi could merge my additions to the latest code (which I didn't have access to). Once the merge was completed, Lakshmi tested it on the UCSF data. The results were...


## A closer look at the pathology terms project
### 1
Unfortunately, the MIMIC and i2b2 data sets didn't have any (or only very few) notes which contained the pathology terms which I would be attempting to recover. So, I went looking for more notes which had the pathology terms. Lakshmi had provided me with a website, [mtsamples.com](https://www.mtsamples.com/), but it only had eight pathology notes. I did some more searching and I didn't find anything better, which meant that once I was ready to test, the pathology regexes would have to be tested by Lakshmi on the UCSF notes. However, I could use the MIMIC test set I already had to refine my regexes before I tested on UCSF data.

### 2, 3, 4, and 5
When I first started looking at the pathology terms, Lakshmi had provided me with a couple examples for each type of term (cassette or slide numbers, staging terms, lymph nodes, and molecular markers). She also gave me two potential safe regexes for staging terms and cassette numbers. When I was testing the regexes/whitelists I used the MIMIC gene symbols test set, which allowed me to refine my regexes—I knew there were no pathology terms in the notes.
1. **Cassette or slide numbers.** [Link](https://github.com/pauliwog/philter-ucsf/blob/master/filters/regex/pathology/cassette_numbers_safe.txt) to safe regex. The provided regex was not super specific, but with some modifications to check that the match was not part of a date/time stamp I got it working. However, when Lakshmi tested my modifications on UCSF data, this regex ended up catching some phis like "suite A40", as "A40" could theoretically be a cassette number). My first idea was to modify the regex with a negative lookbehind (checking that "suite" or "room" is not before the match), but this proved to be extra-super-duper complicated—as variable length lookbehinds are not supported and alternatives did not work properly for my purpose. The next solution, it seemed, was to edit the regexes which were catching the cassette numbers. But when I ran Philter with verbose output, I couldn't find the cassette number matches anywhere in the output files. This meant that the cassette numbers were being caught by the catch-all (details in 2nd paragraph at the very top), so all I had to do was to move the safe regex to the bottom of the config pipeline. It would run after the location regexes—which would catch "suite A40"—and then prevent the catch-all from getting to the cassette numbers.
2. **Staging terms.** [Link](https://github.com/pauliwog/philter-ucsf/blob/master/filters/whitelists/whitelist_staging_terms.json) to whitelist. The provided regex wasn't bad—staging terms follow a pattern of characters, so it wasn't hard to create a regex to match them. But the complete list of staging terms was only 100 terms long, so I decided to create a whitelist to be sure that I was only matching staging terms. And because the staging terms were definitely unique and would never be phi (eg. pT4aN1aM1), this whitelist could go near the beginning of the pipeline without fear of mistakenly tagging a real phi as safe.
3. **Lymph nodes.** [Link](https://github.com/pauliwog/philter-ucsf/blob/master/filters/regex/pathology/lymph_nodes_safe.txt) to safe regex. Lymph nodes were pretty simple. As is obvious in the example below, the ```(11/16)``` following "lymph nodes" looks a lot like a date. In fact, it could actually be November 16th! Only having one example, I used my imagination to try to account for all the possibilities of these numbers, and created a safe regex which worked.
```
Metastatic  adenocarcinoma in eleven of sixteen lymph nodes (11/16).
```
4. **Molecular markers.** [Link](https://github.com/pauliwog/philter-ucsf/blob/master/filters/regex/pathology/molecular_markers_safe_transformed.txt) to safe regex. These were rather confusing. I was provided with two examples, one containing the protein "Ki-67", and the other "MLH1, MSH2, MSH6, and PMS2". Funnily enough, those four terms in the second note are all gene symbols. When I did some research to try to find a list or even more examples of molecular markers, I got a bunch of funny lists of proteins or polypeptides (whatever you want to call them). These lists often included gene symbols or molecular markers in the descriptions for the main term. The whole thing was rather confusing—there wasn't really a good definition of what a "molecular marker" was, and no definite lists of them (without more examples, we couldn't create a regex based on the surrounding context). So, in consultation with Lakshmi, I decided to reuse the gene symbols safe regex, although checking for different words surrounding the match—based on the two examples I had. I used the same replacing a variable with a list technique as well ([transform_pathology_terms.py](https://github.com/pauliwog/philter-ucsf/blob/master/filters/regex/transform_pathology_terms.py)). A next step for molecular markers would be to try to flesh out the list of terms more, perhaps using some of the lists provided below and adding some of the values found in the "name" column and the "description" column.
    - [Human Protein Reference Database](http://www.hprd.org/).
    - [Protein Atlas](https://www.proteinatlas.org/search).
    - [Peptide Atlas](http://www.peptideatlas.org/#).
    - [Uniprot](https://www.uniprot.org/uniprot/) (my favorite).

### Thats it!

I hope this is helpful—I had a lot of fun working on these projects!

Paul
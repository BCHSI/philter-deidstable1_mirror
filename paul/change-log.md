# This is a list of everything which I have modified or added

### Stuff I've added

**Files**
- ```configs/philter_zeta_test.json``` (my config test file)
- ```configs/philter_zeta_test_old.json``` (an older version of my config test file)
- ```configs/paths_to_update.txt``` (because I removed all the duplicate transformed regex files, I had to change some file paths in the config files, this file contains my stdout from MacOS Terminal when I manually checked to see which file paths I needed to change—don't worry if this is confusing, it was a very janky one-time solution)
- ```configs/update_filepaths.py``` (this script reads ```paths_to_update.txt``` and extracts all the file paths which I changed, and then applies the changes I needed to all the config files)
- ```filters/regex/transform_gene_symbols.py``` (modified version of ```transform_regex.py``` to transform gene symbols)
- ```filters/regex/transform_pathology.py``` (modified version of ```transform_regex.py``` to transform pathology terms)
- ```filters/whitelists/whitelist_gene_symbols.json``` (whitelist of gene symbols)
- ```filters/whitelists/whitelist_staging_terms.json``` (whitelist of staging terms)
- ```generate_dataset/staging_terms.txt``` (the .txt list of staging terms used to create a .json whitelist)
- ```generate_dataset/symbols.txt``` (the .txt list of gene symbols used to create a .json whitelist—updated script ```HGNC_symbols_to_json.py``` doesn't require transformation)

**Directories**
- ```data/``` (contains all the data I used for running Philter)
- ```paul/``` (contains most of my scripts which I created)
- ```deidproj/``` (my virtual python environment)
- ```filters/regex/gene_symbols/``` (the folder containing all the gene symbols safe regexes)
- ```filters/regex/pathology/``` (the folder containing all the pathology terms safe regexes)

### Stuff I've modified

- ```philter.py``` (added print statement on lines 490-491 in ```map_regex()```, possibly unknown comments elsewhere)
```
if __debug__ and self.verbose:
    print(m)
```
- ```generate_dataset/generate_modified_whitelist.py``` (modified slightly to read newline separated .txt files (I got an error))

### Change-log for regexes

Changed ```filters/regex/salutations/post_salutations_2chars.txt``` from
```
   \b(?<!M\.)(([A-Z]\.\s)?[A-Z]\'?[A-Z]?[\-aA-zZ]+(\,)?(\s[A-Z]{1,2}(.)?)?(\s[A-Z]{1,2}(.)?)?(\s[A-Z]\'?[A-Z]?[\-aA-zZ]+){1,2}(\s[A-Z]{1,2}(.)?)?|[A-Z]\.\s[a-zA-Z]+)((?=(\s|\,\s|\,)MD\sPhD\b)|(?=(\s|\,\s|\,)MD\b)|(?=(\s|\,\s|\,)NP\b)|(?=(\s|\,\s|\,)DO\b)|(?=(\s|\,\s|\,)RN\b)|(?=(\s|\,\s|\,)PA\b)|(?=(\s|\,\s|\,)PhD\b)|(?=(\s|\,\s|\,)OT\b)|(?=(\s|\,\s|\,)PT\b))
```
to
```
   \b(?<!M\.)(([A-Z]\.\s)?[A-Z]\'?[A-Z]?[\-aA-zZ]+(\,)?(\s[A-Z]{1,2}(.)?)?(\s[A-Z]{1,2}(.)?)?(\s[A-Z]\'?[A-Z]?[\-aA-zZ]+){1,2}(\s[A-Z]{1,2}(.)?)?|[A-Z]\.\s[a-zA-Z]+)((?=(\s|\,\s|\,)(MD|NP|DO|RN|PA|OT|PT)\b)|(?=(\s|\,\s|\,)PhD\b))
```

---

Changed ```filters/regex/addresses/pharmacy_#.txt``` from
```
   (?i)(?!your\s)(?!sent\sto\s)(?!to\syour\s)(?!notes\sto\s)(?!called\sto\s)(?!to\s)(?!by\s)(?!the\s)(?!per\s)(?!from\s)(?!another\s)\b(([A-Z][a-zA-Z]+\-)?([A-Z][a-zA-Z]+(\'s)?\s)?[A-Z][a-zA-Z]+(\s|\/))((pharmacy|walgreens|pharm))(\s#\d+)?\b
```
to
```
   (?i)(?!your\s)(?!sent\sto\s)(?!to\syour\s)(?!notes\sto\s)(?!called\sto\s)(?!to\s)(?!by\s)(?!the\s)(?!per\s)(?!from\s)(?!another\s)\b(([A-Z][a-zA-Z]+\-)?([A-Z][a-zA-Z]+(\'s)?\s)?[A-Z][a-zA-Z]+(\s|\/))((pharmacy|cvs|walgreens|pharm))(\s#\d+)?\b
```

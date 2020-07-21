# This is a list of everything which I have modified or added

### Stuff I've added

**Files**
- ```configs/philter_zeta_genes.json``` (my config test file)
- ```configs/paths_to_update.txt``` (because I removed all the duplicate "\_transformed" regex files, I had to change some file paths in the config files, this file contains my stdout from MacOS Terminal when I manually checked to see which file paths I needed to change—don't worry if this is confusing, it was a very janky one-time solution)
- ```configs/update_filepaths.py``` (this script reads ```paths_to_update.txt``` and extracts all the file paths which I changed, and then modifies those paths in all the config files)
- ```filters/regex/transform_gene_symbols.py``` (modified version of ```transform_regex.py``` to transform gene symbols)
- ```filters/regex/transform_pathology.py``` (modified version of ```transform_regex.py``` to transform pathology terms)
- ```filters/whitelists/whitelist_gene_symbols.json``` (whitelist of gene symbols)
- ```filters/whitelists/whitelist_staging_terms.json``` (whitelist of staging terms)
- ```generate_dataset/staging_terms.txt``` (the .txt list of staging terms used to create a .json whitelist)
- ```generate_dataset/symbols.txt``` (obsolete—the .txt list of gene symbols used to create a .json whitelist. The updated script ```HGNC_symbols_to_json.py``` doesn't require transformation from .txt to .json)

**Directories**
- ```data/``` (contains all the data I used for running Philter, and some scripts I created/used. This folder is not actually in this git repo, but here's [a link](https://github.com/pauliwog/philter-data) to it)
- ```paul/``` (contains all the scripts I created)
- ```filters/regex/gene_symbols/``` (the folder containing all the gene symbols safe regexes)
- ```filters/regex/pathology/``` (the folder containing all the pathology terms safe regexes)

### Stuff I've modified (additional modifications in the change-log for regexes at the bottom)

- ```philter.py``` (added print statement on lines 490-491 (Philter-Zeta) or 555-556 (newest version I had access to) in ```map_regex()```, possibly unknown comments elsewhere)
```
if __debug__ and self.verbose:
    print(m)
```
- ```configs/``` (some file paths in the config.json files which were using the duplicate "regex_transformed.txt" files, I removed the "\_transformed" part for the duplicates)
- ```configs/safe_regex.json``` (there was an extra comma at the bottom of this file, I deleted it)
- ```configs/age_regex_test_updated.json``` (the json file was formatted incorrectly—it was missing the "[" and "]" at the beginning and end)

### Other stuff which I'm not sure about
- ```generate_dataset/generate_modified_whitelist.py``` (this script will take a txt file and convert it to a json whitelist—I also modified it slightly to read newline separated .txt files—I got an error)
- [A link](https://docs.google.com/spreadsheets/d/1VAPUGfwussUGq8YE6B1NfRhOmuV5_I_BR4DMXHJtfXM/edit?usp=sharing) to details about the edits David and I made to the MIMIC notes (because of incorrect tags)

---
### Change-log for previously existing regexes
- ```filters/regex/addresses/room_#.txt```
- ```filters/regex/salutations/post_salutations_2chars.txt```
- ```filters/regex/addresses/pharmacy_#.txt```

---

Changed ```filters/regex/addresses/room_#.txt``` from
```
    \b((?i)[A-Z]\slevel(:)?\s)?((?i)room(:)?\s[a-z]+(\-)?\d+)\b
```
to
```
    (?i)\b((([A-Z]\s)?(level|lvl|floor|flr|fl|story|stry):?\s+[A-Z]?-?\d+\s)?(room|rm|suite|ste|apartment|aptment|apt)s?(\s+(number|num|nm)\.?)?:?(\,?\s+(and\s)?[A-Z]?-?\d+)+)\b
```

---

Changed ```filters/regex/salutations/post_salutations_2chars.txt``` from
```
   \b(?<!M\.)(([A-Z]\.\s)?[A-Z]\'?[A-Z]?[\-aA-zZ]+(\,)?(\s[A-Z]{1,2}(.)?)?(\s[A-Z]{1,2}(.)?)?(\s[A-Z]\'?[A-Z]?[\-aA-zZ]+){1,2}(\s[A-Z]{1,2}(.)?)?|[A-Z]\.\s[a-zA-Z]+)((?=(\s|\,\s|\,)MD\sPhD\b)|(?=(\s|\,\s|\,)MD\b)|(?=(\s|\,\s|\,)NP\b)|(?=(\s|\,\s|\,)DO\b)|(?=(\s|\,\s|\,)RN\b)|(?=(\s|\,\s|\,)PA\b)|(?=(\s|\,\s|\,)PhD\b)|(?=(\s|\,\s|\,)OT\b)|(?=(\s|\,\s|\,)PT\b))
```
to
```
   \b(?<!M\.)(([A-Z]\.\s)?[A-Z]\'?[A-Z]?[\-aA-zZ]+(\,)?(\s[A-Z]{1,2}(.)?)?(\s[A-Z]{1,2}(.)?)?(\s[A-Z]\'?[A-Z]?[\-aA-zZ]+){1,2}(\s[A-Z]{1,2}(.)?)?|[A-Z]\.\s[a-zA-Z]+)((?=(\s|\,\s|\,)(MD|NP|DO|RN|PA|OT|PT|PhD)\b))
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

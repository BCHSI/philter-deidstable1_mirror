# Installing and Running POS-taggers
## HUNPOS
### Installing Hunpos:
1. Move the executable hunpos-tag and en_wsj.model to your /Users/your_user_name/bin/ directory. 
2. Change the following of philter.py: 
self.ht = HunposTagger(path_to_model = 'Users/your_user_name/bin/en_wsj.model', path_to_bin = 'Users/your_user_name/bin/hunpos_tag')

Reference: https://github.com/mivoq/hunpos

Useful link for installing and setting it up: https://stackoverflow.com/questions/17408543/how-to-correctly-set-hunpos-tagger-in-nltk-for-pos-tagging-in-english
### Special handling:
- Input: Hunpos takes a list of tokens as input. Note that Hunpos does not accept newline characters in its input. Simply deleteing the newline characters may mess up the coordinates. Therefore, we need some placeholders for the newline characters. 
- Output: Hunpos produces a list of tuples as outupt: [(word_1, pos_1), (word_2, pos_2), ... (word_n, pos_n)]. This is the same as the output of NLTK, and no special handling is needed. 

## Spacy
Documentation: https://spacy.io/usage/linguistic-features

Spacy can be easily loaded by "import spacy". Note tha Spacy supports customized pipeline so that unnecessary functionalities such as NER and Parsing can be disabled. 
- Input: Spacy takes a string as input. Therefore, we need to either concatenate the list of tokens or directly pass a string. This is different from both HUNPOS and NLTK.

## Initial evaluation for comparing different POS-taggers
Besides directly comparing how using different POS-taggers affect the final precision and recall, this branch also contains code that produces more details to compare these POS-taggers. By turning on '-pos True' tag, Philter will flushes all the words that are assigned as the corresponding tags for whitelists or blacklists that include a "POS" field. Specifically, the following files will be produced for further analysis:

## Current Performance on I2B2 Dataset

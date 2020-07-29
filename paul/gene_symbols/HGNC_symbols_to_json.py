import re
import json

# create lists of symbols

with open("HGNC_gene_names.txt") as fin:
    approved_sym = re.findall('(?:Approved|Entry Withdrawn)\t(\S+)', fin.read())
    alias_sym = re.findall('(?:Approved|Entry Withdrawn)\t\S*\t[\S ]*\t(\S+)', fin.read())
    previous_sym = re.findall('(?:Approved|Entry Withdrawn)\t\S*\t[\S ]*\t\S*\t[\S ]*\t[\S ]*\t(\S+)', fin.read())

symbols = {} # dictionary to dump to json

# adds all symbols from lists to symbols dict

for item in approved_sym: # approved symbols
    symbols[item] = 1

for item in alias_sym: # alias symbols
    symbols[item] = 1

for item in previous_sym: # previous symbols
    symbols[item] = 1

# dump symbols dictionary to json file
with open("whitelist_gene_symbols.json", "w") as fout:
    json.dump(symbols, fout)

# IMPORTANT: Use HGNC_to_json.py to create a json whitelist instead of this script

import re
fin = open("HGNC-gene-names.txt")
fout = open("symbols.txt", "w")

# create lists of symbols

approved_sym = re.findall('(?:Approved|Entry Withdrawn)\t(\S+)', fin.read())
alias_sym = re.findall('(?:Approved|Entry Withdrawn)\t\S*\t[\S ]*\t(\S+)', fin.read())
previous_sym = re.findall('(?:Approved|Entry Withdrawn)\t\S*\t[\S ]*\t\S*\t[\S ]*\t[\S ]*\t(\S+)', fin.read())

# Outputs all symbols from HGNC-gene-names.txt
# Does not account for repeating symbols

for item in approved_sym: # Approved Symbols
    fout.write(item)
    fout.write("\n")
for item in alias_sym: # Alias Symbols
    fout.write(item)
    fout.write("\n")
for item in previous_sym: # Previous Symbols
    fout.write(item)
    fout.write("\n")

# Outputs all symbols from HGNC-gene-names.txt
# Accounts for repeating symbols

# l = []
# for item in approved_sym: # Approved Symbols
#     if item not in l:
#         l.append(item)
#         fout.write(item)
#         fout.write("\n")
# for item in alias_sym: # Alias Symbols
#     if item not in l:
#         l.append(item)
#         fout.write(item)
#         fout.write("\n")
# for item in previous_sym: # Previous Symbols
#     if item not in l:
#         l.append(item)
#         fout.write(item)
#         fout.write("\n")

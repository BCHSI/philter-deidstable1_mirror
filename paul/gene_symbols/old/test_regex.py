import re
import time

start_time = time.time()

with open("../../data/MIMIC/faked_notes/grep_search.txt") as fin:
    text = fin.read()

with open("../../filters/regex/gene_symbols/gene_symbols_safe_04_transformed.txt") as fin:
    regex = re.compile(fin.read())

matches = regex.findall(text)

with open("test_regex_out.txt", "w") as fout:
    for m in matches:
        fout.write(m)
        fout.write("\n")

print("completed in %s seconds" % (str(time.time() - start_time)))

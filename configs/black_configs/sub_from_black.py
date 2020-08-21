import sys
import json

def is_unicode(s):
    if isinstance(s, str):
        return False
    elif isinstance(s, unicode):
        return True
    else:
        print("not a string")

# Get current (non-subtracted) blacklist
current_blacklist = json.loads(open(sys.argv[1]).read(), encoding="latin-1")
current_blacklist_keys = list(current_blacklist.keys())

# Get list of words/terms to substract (extremely commonyl occuring words in notes that are almost never PHI)
with open(sys.argv[2]) as f:
	subtract_list = f.readlines()
subtract_list = [x.strip() for x in subtract_list]

# Strip characters from subtract words, double check that it is a string, and lower
subtract_list_cleaned = [re.split("\s+", re.sub(r"[^a-zA-Z0-9]+", " ", item)) for item in subtract_list]
subtract_list_flattened = [item for sublist in subtract_list_cleaned for item in sublist]
subtract_list_lowered = [str(item.lower()) for item in subtract_list_flattened]
# Remove empty strings and spaces
subtract_list_final = [x for x in subtract_list_lowered if x != '' and x != ' ' and len(x) > 1]

# Loop through list, check if in blacklist, if it is remove it
for item in subtract_list_final:
	if item in current_blacklist_keys:
		current_blacklist_keys.remove(item)


# Make sure that the character encoding is uniform
updated_blacklist_ascii = set()
for item in current_blacklist_keys:
    if is_unicode(item):
        new_item = unicodedata.normalize('NFD', item).encode('ascii', 'ignore')
        updated_blacklist_ascii.add(new_item)
    else:
        updated_blacklist_ascii.add(item)


updated_blacklist_dictionary = {}
for k in updated_blacklist_ascii:
    updated_blacklist_dictionary[k] = 1


json.dump(updated_blacklist_dictionary, open( "updated_blacklist.json", "w" ) )







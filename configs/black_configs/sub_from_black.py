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
current_blacklist = json.loads(open(sys.argv***REMOVED***1***REMOVED***).read(), encoding="latin-1")
current_blacklist_keys = list(current_blacklist.keys())

# Get list of words/terms to substract (extremely commonyl occuring words in notes that are almost never PHI)
with open(sys.argv***REMOVED***2***REMOVED***) as f:
	subtract_list = f.readlines()
subtract_list = ***REMOVED***x.strip() for x in subtract_list***REMOVED***

# Strip characters from subtract words, double check that it is a string, and lower
subtract_list_cleaned = ***REMOVED***re.split("\s+", re.sub(r"***REMOVED***^a-zA-Z0-9***REMOVED***+", " ", item)) for item in subtract_list***REMOVED***
subtract_list_flattened = ***REMOVED***item for sublist in subtract_list_cleaned for item in sublist***REMOVED***
subtract_list_lowered = ***REMOVED***str(item.lower()) for item in subtract_list_flattened***REMOVED***
# Remove empty strings and spaces
subtract_list_final = ***REMOVED***x for x in subtract_list_lowered if x != '' and x != ' ' and len(x) > 1***REMOVED***

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
    updated_blacklist_dictionary***REMOVED***k***REMOVED*** = 1


json.dump(updated_blacklist_dictionary, open( "updated_blacklist.json", "w" ) )







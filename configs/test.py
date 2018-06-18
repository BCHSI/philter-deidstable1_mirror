import json

original_blacklist = json.loads(open("/data/muenzenk/new_blacklists/names_blacklist_061418-1.json").read())
ucsf_names = json.loads(open("/data/muenzenk/new_blacklists/ucsf_probes_names.json").read())
whitelist = json.loads(open("whitelist_061418.json").read())


# Diff between blacklist and ucsf names
names_diff = []
for word in ucsf_names:
	if word not in original_blacklist and type(word) == str:
		names_diff.append(word)


names_diff_set = set(names_diff)
len(names_diff_set)

# Len: 470240


# Diff between ucsf-unique names and whitelist
whitelist_diff = []
for word in names_diff_set:
	if word not in whitelist:
		whitelist_diff.append(word)

whitelist_diff_set = set(whitelist_diff)

len(whitelist_diff_set)
# Len: 462234, about 8000 in whitelist


# New blacklist: original_blacklist + whitelist_diff
original_blacklist_set = set(original_blacklist)

new_blacklist = original_blacklist_set | whitelist_diff_set


# Original blacklist length: 242608
# New blacklist lengths: 704842


names_blacklist_dictionary = {}
for k in new_blacklist:
    names_blacklist_dictionary[k] = 1



json.dump(names_blacklist_dictionary, open("names_blacklist_061418-2.json", "w" ) )


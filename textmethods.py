import re

def get_clean(text, punctuation_matcher=re.compile(r"***REMOVED***^a-zA-Z0-9***REMOVED***")):
    # Use pre-process to split sentence by spaces AND symbols,
    # while preserving spaces in the split list
    lst = re.findall(r"***REMOVED***\w'***REMOVED***+",text)
    cleaned = ***REMOVED******REMOVED***
    for item in lst:
        if len(item) > 0:
            if item.isspace() == False:
                split_item = re.split("(\s+)", re.sub(punctuation_matcher,
                                                      " ", item))
                for elem in split_item:
                    if len(elem) > 0:
                        cleaned.append(elem)
    return cleaned


def get_tokens(string):
    tokens = {}
    str_split = get_clean(string)
    
    offset = 0
    for item in str_split:
        item_stripped = item.strip()
        if len(item_stripped) is 0:
            offset += len(item)
            continue
        token_start = string.find(item_stripped, offset)
        if token_start is -1:
            raise Exception("ERROR: cannot find token \"{0}\" ".format(item)
                            + "in \"{1}\" starting at {2}".format(string,
                                                                  offset))
        token_stop = token_start + len(item_stripped) - 1
        offset = token_stop + 1
        tokens.update({token_start:***REMOVED***token_stop,item_stripped***REMOVED***})
    
    return tokens

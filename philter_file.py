#!/usr/local/bin/python
from philter import filter_task
import sys, pickle
from nphilter.nphilter import NPhilter


if __name__ == "__main__":
    f = sys.argv[1]

    if f.endswith(".txt"):
	    foutpath  = sys.argv[2]
	    key_name = "phi_reduced"
	    whitelist = None

	    #instantiate a number philterer
	    NumPhilter = NPhilter({"debug":True, "regex":"nphilter/regex.json"})
	    NumPhilter.precompile(path="nphilter/") #precompile any patterns we've added

	    with open("whitelist.pkl", "rb") as fin:
	    	whitelist = pickle.load(fin)
	    if whitelist == None:
	    	print("Error, could not load whitelist")
	    	sys.exit(1)
	    filter_task(f, whitelist, foutpath, key_name, NumPhilter)




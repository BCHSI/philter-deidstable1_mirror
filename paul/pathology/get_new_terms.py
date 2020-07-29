# extracts terms which match [A-Z0-9\-] from two .tsv files provided by Dima (Dmytro) Lituiev

import re
import json
import argparse


# extracts and creates a dictionary or list (depending on whitelist format) of gene symbols
def extract(fin1, fin2):

    symbols_list = {} # list of new symbols

    with open(fin1) as fin:
        f1_text = fin.read()
    with open(fin2) as fin:
        f2_text = fin.read()

    symbols_pattern = re.compile("[A-Z][A-Z0-9\-]+") # regex for catching new terms

    f1_symbols = symbols_pattern.findall(f1_text) # get list of terms from file 1
    f2_symbols = symbols_pattern.findall(f2_text) # get list of terms from file 2

    for symbol in f1_symbols: # go through each symbol in file 1
        symbol = re.sub("(^-)(-$)", "", symbol) # remove hyphens from beginning or end of symbol
        if symbol not in symbols_list:
            symbols_list.append(symbol)

    for symbol in f2_symbols: # go through each symbol in file 2
        symbol = re.sub("(^-)(-$)", "", symbol) # remove hyphens from beginning or end of symbol
        if symbol not in symbols_list:
            symbols_list.append(symbol)

    # remove the titles of the columns which could match a gene symbol
    del symbols_list["HGNC"]
    del symbols_list["ID"]
    del symbols_list["CUI"]
    del symbols_list["AUI"]
    del symbols_list["STT"]
    del symbols_list["ISPREF"]
    del symbols_list["SAB"]
    del symbols_list["TTY"]

    return symbols_list


# appends the new symbols to the og list, writes the new list of everything to the new file
def append(symbols_list, wl_name, format):

    new_wl = wl_name[:-(len(format)+1)]+"_new."+format # create new whitelsit name

    with open(wl_name) as fin: # read in previous symbols
        if format == "json":
            big_list = json.loads(fin.read())
        elif format == "txt":
            big_list = fin.read().split()

    for symbol in symbols_list: # append new symbols to full list
        if symbol not in big_list:
            if format == "json":
                big_list[symbol] = 1
            elif format == "txt":
                big_list.append(symbol)


    with open(new_wl, "w") as fout: # write new list with everything to fout
        if format == "json":
            json.dump(big_list, fout)
        elif format == "txt":
            for symbol in big_list:
                fout.write(symbol)
                fout.write(" ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f1", "--file_1",
                    default="stains_hgnc.tsv",
                    help="""The path to the first file which gene symbols
                            will be extracted from. Default is
                            'stains_hgnc.tsv'.""",
                    type=str)
    ap.add_argument("-f2", "--file_2",
                    default="stains_umls.tsv",
                    help="""The path to the second file which gene symbols
                            will be extracted from. Default is
                            'stains_hgnc.tsv'.""",
                    type=str)
    ap.add_argument("-wl", "--whitelist",
                    default="../../filters/whitelists/whitelist_gene_symbols.json",
                    help="""The path to the whitelist which will be appended to.
                            Default is
                            '../../filters/whitelists/whitelist_gene_symbols.json'.""",
                    type=str)
    ap.add_argument("-f", "--whitelist_format",
                    default="json",
                    help="""The format of the whitelist (eg. json, txt).
                            Default is 'json'.""",
                    type=str)

    args = ap.parse_args()

    f1_name = args.file_1
    f2_name = args.file_2
    wl_name = args.whitelist
    format = args.whitelist_format

    if format != ("json" or "txt"):
        print("Please enter 'json' or 'txt' for the format, they are the only formats currently supported.")
        exit()

    symbols_list = extract(f1_name, f2_name)
    append(symbols_list, wl_name, format)

main()

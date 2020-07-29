import argparse
import time
import pandas as pd
from pandas.io.json import json_normalize


# read coords.json files to determine which tags were un-obscured and by what whitelist
def stats(finwl, finog):

    """
        set up dataframe containing original (without whitelist) data from coords
    """

    s = "\nReading '"+finog+"'..."
    print(s)
    df_og = pd.read_json(finog) # read in json file
    df_og = df_og.transpose() # transpose dataframe (switch rows and colums)

    for i in range(len(df_og)): # go through each row

        # unpack the nested json in the phi-tags and non-phi-tags into a dataframe
        phi_tag_data = pd.json_normalize(df_og.loc[:, "phi"].iloc[i])
        nonphi_tag_data = pd.json_normalize(df_og.loc[:, "non-phi"].iloc[i])

        # set the overall dataframe["phi"] and ["non-phi"] to the unpacked phi-tags dataframe
        df_og.iat[i, 1] = phi_tag_data
        df_og.iat[i, 2] = nonphi_tag_data

    """
        set up dataframe containing whitelist data from coords
    """

    s = "\nReading '"+finwl+"'..."
    print(s)
    df_wl = pd.read_json(finwl) # read in json file
    df_wl = df_wl.transpose() # transpose dataframe (switch rows and colums)

    for i in range(len(df_wl)): # go through each row

        # unpack the nested json in the phi-tags and non-phi-tags into a dataframe
        phi_tag_data = pd.json_normalize(df_wl.loc[:, "phi"].iloc[i])
        nonphi_tag_data = pd.json_normalize(df_wl.loc[:, "non-phi"].iloc[i])

        # set the overall dataframe["phi"] and ["non-phi"] to the unpacked phi-tags dataframe
        df_wl.iat[i, 1] = phi_tag_data
        df_wl.iat[i, 2] = nonphi_tag_data

    """
        go through each tag and check if it is in both original and whitelist coords
    """

    s = "\nFinding differences...\n"
    print(s)
    open("diffs_cords_out.txt", "w")
    doesexist = False # if no differences exist
    for i in range(len(df_og)): # go through each file

        # set variables to the "phi-tag" dataframe for the original and whitelist dataframe
        current_df_og = df_og.iloc[i, 1]
        current_df_wl = df_wl.iloc[i, 1]

        for j in range(len(current_df_og)): # go through each tag in the original "phi-tag" dataframe

            test = current_df_og.iloc[j,:4].values # set test to the current original tag

            # check to see whether test exists in the whitelist tags
            # if not than print the file name and tag
            if not (current_df_wl.iloc[:,:4] == test).all(axis='columns').any():
                doesexist = True
                s = "File name : '"+str(df_og.iloc[i].name)+"'\nTag [start, stop, word, phi-type] : "+str(test)+"\n"
                print(s) # output to stdout
                with open("diffs_cords_out.txt", "a") as fout: # output to file
                    fout.write(s)
                    fout.write("\n")

    if not doesexist: # if there are no differences
        s = "\nThere is no difference in the tags between the original and whitelist coordinates files."
        print(s)
        with open("diffs_cords_out.txt", "a") as fout: fout.write(s) # output to file


def main():
    help_str = """
        Reads coordinates.json files output by Philter and finds tags in the
        run without a whitelist but not in the whitelist run (the tags which
        were un-obscured because of the whitelist). Outputs to a stdout.
    """
    ap = argparse.ArgumentParser(description=help_str)
    ap.add_argument("-og", "--coords_original",
                    default="../../data/coords_original.json",
                    help="""The coordinates file for the Philter run without
                            the whitelist. Default is
                            '../../data/coords_original.json'.""",
                    type=str)
    ap.add_argument("-wl", "--coords_whitelist",
                    default="../../data/coords_whitelist.json",
                    help="""The coordinates file for the Philter run with the
                            whitelist. Default is
                            '../../data/coords_whitelist.json'.""",
                    type=str)

    args = ap.parse_args()

    cwl = args.coords_whitelist
    cog = args.coords_original

    start_time = time.time()

    stats(cwl, cog)

    print("\nCompleted in", time.time() - start_time, "seconds.\n")

main()

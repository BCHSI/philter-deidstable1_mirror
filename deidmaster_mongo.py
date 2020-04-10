import sys
import argparse
import distutils.util
import os
import random
from math import ceil
from subprocess import call
from collections import OrderedDict

# using OrderedDict for reproducability
servers = OrderedDict([('MCWLDEIDLAP701.ucsfmedicalcenter.org',24),
                       ('qcdeidlap702.ucsfmedicalcenter.org',14),
                       ('qcdeidlap703.ucsfmedicalcenter.org',14),
                       ('qcdeidlap705.ucsfmedicalcenter.org',14)])
random.seed(10101) #fix seed for reproducibility 


def get_args():

     help_str = """De-identify and surrogate all text files in mongo db and distribute processing to servers. Calls deidloop.py"""
     ap = argparse.ArgumentParser(description=help_str)

     ap.add_argument("--username", required=True,
                    help="The username used to ssh into the servers",
                    type=str)
     ap.add_argument("--philter", required=True,
                    help="Path to Philter program files like deidpipe.py",
                    type=str)
     ap.add_argument("--philterconfig", required=True,
                    help="philter config file",
                    type=str)
     ap.add_argument("--mongo", required=True,
                    help="Mongo config file",
                    type=str)
     ap.add_argument("--superlog", required=False, default=False,
                    help="True or False flag to let the program know if it needs to store superlog in mongo."
                    + " When this is set, the pipeline saves the"
                    + " super log in a log_super_log collection"
                    + " combining logs of each batch",
                    type=lambda x:bool(distutils.util.strtobool(x)))

     return ap.parse_args()

def send_jobs(servers, username, wrkDir, configfile, mongofile, suplog):
    # ssh into each server and pass respective subdirs chunk to deidloop
    for url, nthreads in servers.items():
        commandline = ("ssh -T {0}@{1}".format(username, url)
                       #+ " hostname && echo \""
                       + " cd " + wrkDir + "; /usr/bin/time nice /data/radhakrishnanl/deidproj/bin/python3 "
                       + os.path.join(wrkDir, "deidloop_mongo.py")
                       + " -t {0} ".format(nthreads)
                       + " --mongofile " + os.path.join(wrkDir, "configs/", mongofile)
                       + " --philterconfig " + os.path.join(wrkDir,"configs/",configfile)
                       + " --superlog " + str(suplog)
                       + " --philter " + str(wrkDir)
                       + " > " + os.path.join(wrkDir, "stdouterr_"+ url.split('.')[0] + ".txt")
                       + " 2>&1 &")
        print(commandline)
        call(commandline.split())

def main():

    args = get_args()
    send_jobs(servers, args.username, args.philter, args.philterconfig, args.mongo, args.superlog)

    return 0

if __name__ == "__main__":
    sys.exit(main())


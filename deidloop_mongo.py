"""
Code to script multithread instances of deidipipe.py
It creates a queue of directories. Each thread processes a directory.
"""
import sys
import argparse
import distutils.util
from queue import Queue
from threading import Thread
from subprocess import call
import time
from shutil import rmtree
import pandas
import numpy
import os
from logger import get_super_log
import json
import socket
from pymongo import MongoClient
from deidpipe import main_mongo
from argparse import Namespace

def get_args():
    # gets input/output/filename
    help_str = """De-identify and surrogate all text files in a set of folders using threads"""
    
    ap = argparse.ArgumentParser(description=help_str)

    ap.add_argument("--mongofile",
                    help="Path to the mongo config file",
                    type=str)
    ap.add_argument("-t", "--threads", default=1,
                    help="Number of parallel threads, the default is 1",
                    type=int)
    ap.add_argument("--philter",
                    help="Path to Philter program files like deidpipe.py",
                    type=str)
    ap.add_argument("--philterconfig",
                    help="Path to Philter program config files like philter_delta.json",
                    type=str)
    ap.add_argument("--superlog",
                    help="True or False option."
                    + " When this is set, the pipeline prints and saves a"
                    + " super log in mongo"
                    + " combining logs of each batch",
                    type=str)

    return ap.parse_args()

def read_mongo_config(mongofile):
    if not os.path.exists(mongofile):
       raise Exception("Filepath does not exist", mongofile)
    mongo_details = json.loads(open(mongofile,"r").read())
    return mongo_details    

def get_mongo_handle(mongo):
    client = MongoClient(mongo["client"])
    try:
        db = client['notes_deid_dev']
    except:
        print("Mongo Server not available")
    return db


def get_batch(mongo):
    db = get_mongo_handle(mongo)
    collection_chunk = db['chunk']
    server = socket.gethostname() + ".ucsfmedicalcenter.org"
    batch = collection_chunk.distinct('batch',{'url': server})
    return batch

def runDeidChunck(unit, q, philterFolder, philterConfig, db):
    """
    Function to instruct a thread to deid a directory.
    INPUTS:
        unit: Thread ID
        q: Tuple used to determine path to directory.
    """
    while True:
        # time for run
        t0 = time.time()
        '''
        # Tuple to determine path
        if len(q.get()) == 4:
           srcFolder, srcMeta, dstFolder, kpfile = q.get()
        else:
           srcFolder, srcMeta, dstFolder = q.get()
        # Build output directory
        os.makedirs(dstFolder, exist_ok=True)

        print(str(unit) + " src: " + srcFolder)
        print(str(unit) + " met: " + srcMeta)
        print(str(unit) + " dst: " + dstFolder)
        print(str(unit) + " cwd: " + philterFolder)

        # Run Deid (would be better to interface directly)
        try:
           kpfile
        except NameError:
           kpfile = None
        if kpfile is None:
           call(["python3", "-O", "deidpipe.py",
                 "-i", srcFolder,
                 "-o", dstFolder,
                 "-s", srcMeta,
                 "-d", "True",
                 "-f", "configs/philter_delta_holidays_added_dynamic_blklist.json",
                 "-l", "True"],
                 cwd=philterFolder)
        else:
            call(["python3", "-O", "deidpipe.py",
                 "-i", srcFolder,
                 "-o", dstFolder,
                 "-s", srcMeta,
                 "-d", "True",
                 "-f", "configs/philter_delta_holidays_added_dynamic_blklist.json",
                 "-k", kpfile,
                 "-l", "True"],
                 cwd=philterFolder)
        '''
        args = Namespace(anno='./data/i2b2_xml', batch=q.get(), deid_filename=True, dynamic_blacklist=None, eval=False, filters=philterConfig, input=None, log=True, mongodb=True, output=None, surrogate_info=None, verbose=False, xml=False)
        print(args)
        main_mongo(args,db,args.batch)
        # Print time elapsed for batch
        t = time.time() - t0
        print(str(unit) + " " + str(args.batch) + ": " + str(t) + " seconds")

        q.task_done()

def main():
    enclosure_queue = Queue()

    args = get_args()
    print("read args")

    # Set up some threads to fetch the enclosures (each thread deids a directory)
    print("starting {0} worker threads".format(args.threads))
    mongo = read_mongo_config(args.mongofile)
    db = get_mongo_handle(mongo)
    for unit in range(args.threads):
        worker = Thread(target=runDeidChunck,
                        args=(unit, enclosure_queue,
                              os.path.dirname(args.philter),args.philterconfig,db))
        worker.setDaemon(True)
        worker.start()


    list_of_batch_to_process = get_batch(mongo)    
    
    # Build queue
    for batch in list_of_batch_to_process:
       enclosure_queue.put(batch)

    # Now wait for the queue to be empty, indicating that we have
    # processed all of the notes
    print('*** Main thread waiting')
    enclosure_queue.join()
    print('*** Done')
    '''
    if args.superlog:
        # Once all the directories have been processed,
        # create a superlog that combines all logs in each output directory
        all_logs = []
        with open(args.imofile, 'r') as imo:
            for line in imo:
                parts = line.split()
                if len(parts) > 3:
                   idir, mfile, odir, kpfile = line.split()
                else:
                   idir, mfile, odir = line.split()

                all_logs.append(os.path.join(odir, "log",
                                             "detailed_batch_summary.csv"))
                all_logs.append(os.path.join(odir, "log",
                                             "known_phi.log"))

        # Create super log of batch summaries
        if all_logs != []:
            get_super_log(all_logs, os.path.join(args.superlog, "log"))
    '''
    return 0
if __name__ == "__main__":
    sys.exit(main())

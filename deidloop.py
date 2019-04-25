"""
Code to script multithread instances of deidipipe.py
It creates a queue of directories. Each thread processes a directory.
It copies the structure of the input in a new location, and renames files.
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

def get_args():
    # gets input/output/filename
    help_str = """De-identify and surrogate all text files in a set of folders using threads"""
    
    ap = argparse.ArgumentParser(description=help_str)

    ap.add_argument("--imofile",
                    help="Path to the file that contains the list of input"
                    + " folders, metafiles, output folders",
                    type=str)
    ap.add_argument("-t", "--threads", default=1,
                    help="Number of parallel threads, the default is 1",
                    type=int)
    ap.add_argument("--philter",
                    help="Path to Philter program files like deidpipe.py",
                    type=str)
    ap.add_argument("--superlog", 
                    help="Path to the folder for the super log."
                    + " When this is set, the pipeline prints and saves a"
                    + " super log in a subfolder log of the set folder"
                    + " combining logs of each output directory",
                    type=str)

    return ap.parse_args()


def runDeidChunck(unit, q, philterFolder):
    """
    Function to instruct a thread to deid a directory.
    INPUTS:
        unit: Thread ID
        q: Tuple used to determine path to directory.
    """
    while True:
        # time for run
        t0 = time.time()

        # Tuple to determine path
        srcFolder, srcMeta, dstFolder, kpfile = q.get()

        # Build output directory
        os.makedirs(dstFolder, exist_ok=True)

        print(str(unit) + " src: " + srcFolder)
        print(str(unit) + " met: " + srcMeta)
        print(str(unit) + " dst: " + dstFolder)
        print(str(unit) + " cwd: " + philterFolder)

        # Run Deid (would be better to interface directly)
        call(***REMOVED***"python3", "-O", "deidpipe.py", 
              "-i", srcFolder, 
              "-o", dstFolder, 
              "-s", srcMeta,
              "-d", "True", 
              "-f", "configs/philter_delta.json",
              "-k", kpfile,
              "-l", "True"***REMOVED***,
             cwd=philterFolder)


        # Print time elapsed for batch
        t = time.time() - t0
        print(str(unit) + " " + dstFolder + ": " + str(t) + " seconds")

        q.task_done()


def main():
    enclosure_queue = Queue()
    
    args = get_args()
    print("read args")
    
    # Set up some threads to fetch the enclosures (each thread deids a directory)
    print("starting {0} worker threads".format(args.threads))
    for unit in range(args.threads):
        worker = Thread(target=runDeidChunck,
                        args=(unit, enclosure_queue,
                              os.path.dirname(args.philter),))
        worker.setDaemon(True)
        worker.start()

    # Build queue
    with open(args.imofile, 'r') as imo:
        for line in imo:
            idir, mfile, odir, kpfile = line.split()
            enclosure_queue.put(***REMOVED***idir, mfile, odir, kpfile***REMOVED***)
    
    # Now wait for the queue to be empty, indicating that we have
    # processed all of the notes
    print('*** Main thread waiting')
    enclosure_queue.join()
    print('*** Done')

    if args.superlog:
        # Once all the directories have been processed,
        # create a superlog that combines all logs in each output directory
        all_logs = ***REMOVED******REMOVED***
        with open(args.imofile, 'r') as imo:
            for line in imo:
                idir, mfile, odir = line.split()
                all_logs.append(os.path.join(odir, "log",
                                             "detailed_batch_summary.csv"))

        # Create super log of batch summaries
        if all_logs != ***REMOVED******REMOVED***:
            get_super_log(all_logs, os.path.join(args.superlog, "log"))

    return 0

if __name__ == "__main__":
    sys.exit(main())





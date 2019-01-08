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
import csv 
import os


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
        srcFolder, srcMeta, dstFolder = q.get()

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
              "-l", "True"***REMOVED***,
             cwd=philterFolder)


        # Print time elapsed for batch
        t = time.time() - t0
        print(str(unit) + " " + dstFolder + ": " + str(t) + " seconds")

        q.task_done()


def get_super_log(all_logs, super_log_dir):
    
    #Path to csv summary of all files
    csv_summary_filepath = os.path.join(super_log_dir,
                                        'deidpipe_superlog_detailed.csv')
    #Path to txt summary of all files combined
    text_summary_filepath = os.path.join(super_log_dir,
                                         'deidpipe_superlog_summary.txt')

    os.makedirs(super_log_dir, exist_ok=True)

    # Create aggregated summary file
    if not os.path.isfile(csv_summary_filepath):
        with open(csv_summary_filepath,'w') as f:
            file_header = 'filename'+','+'file_size'+','+'total_tokens'+','+'phi_tokens'+','+'successfully_normalized'+','+'failed_normalized'+','+'successfully_surrogated'+','+'failed_surrogated'+'\n'
            f.write(file_header)
    
    # Append contents of all summaries to this file
    for log_file in all_logs:
        if not os.path.exists(log_file):
            print("log file missing: " + log_file)
            continue
        with open(log_file,'r') as f:
            with open(csv_summary_filepath,'a') as f1:
                next(f) # skip header line
                for line in f:
                    f1.write(line)

    summary = pandas.read_csv(csv_summary_filepath)

    # Batch size (all)
    number_of_notes = len(summary)

    # File size
    total_kb_processed = sum(summary***REMOVED***'file_size'***REMOVED***)/1000
    median_file_size = numpy.median(summary***REMOVED***'file_size'***REMOVED***)
    q2pt5_size,q97pt5_size = numpy.percentile(summary***REMOVED***'file_size'***REMOVED***,***REMOVED***2.5,97.5***REMOVED***)

    # Total tokens
    total_tokens = numpy.sum(summary***REMOVED***'total_tokens'***REMOVED***)
    median_tokens = numpy.median(summary***REMOVED***'total_tokens'***REMOVED***)
    q2pt5_tokens,q97pt5_tokens = numpy.percentile(summary***REMOVED***'total_tokens'***REMOVED***,***REMOVED***2.5,97.5***REMOVED***)

    # Total PHI tokens
    total_phi_tokens = numpy.sum(summary***REMOVED***'phi_tokens'***REMOVED***)
    median_phi_tokens = numpy.median(summary***REMOVED***'phi_tokens'***REMOVED***)
    q2pt5_phi_tokens,q97pt5_phi_tokens = numpy.percentile(summary***REMOVED***'phi_tokens'***REMOVED***,***REMOVED***2.5,97.5***REMOVED***)

    # Normalization
    successful_normalization = sum(summary***REMOVED***'successfully_normalized'***REMOVED***)
    failed_normalization = sum(summary***REMOVED***'failed_normalized'***REMOVED***)

    # Surrogation
    successful_surrogation = sum(summary***REMOVED***'successfully_surrogated'***REMOVED***)
    failed_surrogation = sum(summary***REMOVED***'failed_surrogated'***REMOVED***)


    with open(text_summary_filepath, "w") as f:
        f.write("TOTAL NOTES PROCESSED: "+str(number_of_notes)+'\n')
        f.write("TOTAL KB PROCESSED: "+str("%.2f"%total_kb_processed)+'\n')
        f.write("TOTAL TOKENS PROCESSED: "+str(total_tokens)+'\n')
        f.write("TOTAL PHI TOKENS PROCESSED: "+str(total_phi_tokens)+'\n')
        f.write('\n')
        f.write("MEDIAN FILESIZE (BYTES): "+str(median_file_size)+" (95% Percentile: "+str("%.2f"%q2pt5_size)+'-'+str("%.2f"%q97pt5_size)+')'+'\n')
        f.write("MEDIAN TOKENS PER NOTE: "+str(median_tokens)+" (95% Percentile: "+str("%.2f"%q2pt5_tokens)+'-'+str("%.2f"%q97pt5_tokens)+')'+'\n')
        f.write("MEDIAN PHI TOKENS PER NOTE: "+str(median_phi_tokens)+" (95% Percentile: "+str("%.2f"%q2pt5_phi_tokens)+'-'+str("%.2f"%q97pt5_phi_tokens)+')'+'\n')
        f.write('\n')
        f.write("DATES SUCCESSFULLY NORMALIZED: "+str(successful_normalization)+'\n')
        f.write("DATES FAILED TO NORMALIZE: "+str(failed_normalization)+'\n')
        f.write("DATES SUCCESSFULLY SURROGATED: "+str(successful_surrogation)+'\n')
        f.write("DATES FAILED TO SURROGATE: "+str(failed_surrogation)+'\n')  

        
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
            idir, mfile, odir = line.split()
            enclosure_queue.put(***REMOVED***idir, mfile, odir***REMOVED***)
    
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





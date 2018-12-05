"""
Code to script multithread instances of deidipipe.py
It creates a queue of directories. Each thread processes a directory.
It copies the structure of the input in a new location, and renames files.
"""
from queue import Queue
from threading import Thread
from subprocess import call
import time
from shutil import rmtree
import pandas
import numpy
import csv 
import os


# Set up some global variables
num_threads = 14
enclosure_queue = Queue()
srcBase = "/data/muenzenk/log_enhancements/log_test_environment/input/"
dstBase = "/data/muenzenk/log_enhancements/log_test_environment/output/"
mtaBase = "/data/muenzenk/log_enhancements/log_test_environment/input/"

def runDeidChunck(unit, q):
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
        #i,j,k = q.get()
        r = q.get()

        #Build path to notes, meta and output path
        srcFolder = r + '/'
        #srcFolder = os.path.join(r, d) + '/'
        srcMeta = os.path.join(mtaBase, os.path.relpath(srcFolder, srcBase),
                               "meta_data.txt")
        dstFolder = os.path.join(dstBase, os.path.relpath(srcFolder, srcBase)) + '/'

        # Build output directory
        os.makedirs(dstFolder, exist_ok=True)

        print(str(unit) + " src: " + srcFolder)
        print(str(unit) + " met: " + srcMeta)
        print(str(unit) + " dst: " + dstFolder)

        # Run Deid (would be better to interface directly)
        call(["python3", "-O", "deidpipe.py", 
              "-i", srcFolder, 
              "-o", dstFolder, 
              "-s", srcMeta,
              "-d", "True", 
              "-f", "configs/philter_delta.json",
              "-l", "True"])


        # Print time elapsed for batch
        t = time.time() - t0
        print(str(unit) + " " + dstFolder + ": " + str(t) + " seconds")

        q.task_done()


def get_super_log(all_logs, output_dir):
    
    super_log_dir = '/'.join(output_dir.split('/')[:-2])+'/log/'
    #Path to csv summary of all files
    csv_summary_filepath = super_log_dir+'deidpipe_superlog_detailed.csv'
    #Path to txt summary of all files combined
    text_summary_filepath = super_log_dir+'deidpipe_superlog_summary.txt'

    os.makedirs(super_log_dir, exist_ok=True)

    # Create aggregated summary file
    if not os.path.isfile(csv_summary_filepath):
        with open(csv_summary_filepath,'w') as f:
            file_header = 'filename'+','+'file_size'+','+'total_tokens'+','+'phi_tokens'+','+'successfully_normalized'+','+'failed_normalized'+','+'successfully_surrogated'+','+'failed_surrogated'+'\n'
            f.write(file_header)
    
    # Append conents of all summaries to this file
    for log_file in all_logs:
        with open(log_file,'r') as f:
            with open(csv_summary_filepath,'a') as f1:
                next(f) # skip header line
                for line in f:
                    f1.write(line)

    summary = pandas.read_csv(csv_summary_filepath)

    # Batch size (all)
    number_of_notes = len(summary)

    # File size
    total_kb_processed = sum(summary['file_size'])/1000
    median_file_size = numpy.median(summary['file_size'])
    q2pt5_size,q97pt5_size = numpy.percentile(summary['file_size'],[2.5,97.5])

    # Total tokens
    total_tokens = numpy.sum(summary['total_tokens'])
    median_tokens = numpy.median(summary['total_tokens'])
    q2pt5_tokens,q97pt5_tokens = numpy.percentile(summary['total_tokens'],[2.5,97.5])

    # Total PHI tokens
    total_phi_tokens = numpy.sum(summary['phi_tokens'])
    median_phi_tokens = numpy.median(summary['phi_tokens'])
    q2pt5_phi_tokens,q97pt5_phi_tokens = numpy.percentile(summary['phi_tokens'],[2.5,97.5])

    # Normalization
    successful_normalization = sum(summary['successfully_normalized'])
    failed_normalization = sum(summary['failed_normalized'])

    # Surrogation
    successful_surrogation = sum(summary['successfully_surrogated'])
    failed_surrogation = sum(summary['failed_surrogated'])


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


# Set up some threads to fetch the enclosures (each thread deids a directory)
for unit in range(num_threads):
    worker = Thread(target=runDeidChunck, args=(unit, enclosure_queue,))
    worker.setDaemon(True)
    worker.start()

# Build queue
for root, dirs, files in os.walk(srcBase):
    if not dirs: enclosure_queue.put(root)
        
# Now wait for the queue to be empty, indicating that we have
# processed all of the notes
print('*** Main thread waiting')
enclosure_queue.join()
print('*** Done')

# Once all the directories have been processed, create a superlog that combines
# all logs in each output directory

all_logs = []
for (dirpath, dirnames, filenames) in os.walk(dstBase):
    for filename in filenames:
        if filename == 'detailed_batch_summary.csv':
            all_logs.append(os.sep.join([dirpath, filename]))

# Create super log of batch summaries
if all_logs != []:
    get_super_log(all_logs,dstBase)







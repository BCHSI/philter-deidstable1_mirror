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
import os


# Set up some global variables
num_threads = 14
enclosure_queue = Queue()
srcBase = "/data/notes/shredded_notes/000/"
dstBase = "/data/schenkg/deid_notes_20180328/000/"
mtaBase = "/data/notes/meta_data_20180328/000/"

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
        srcMeta = os.path.join(mtaBase, os.path.relpath(srcFolder, srcBase), "meta_data.txt")
        dstFolder = os.path.join(dstBase, os.path.relpath(srcFolder, srcBase)) + '/'

        # Build output directory
        os.makedirs(dstFolder, exist_ok=True)

        print(str(unit) + " src: " + srcFolder)
        print(str(unit) + " met: " + srcMeta)
        print(str(unit) + " dst: " + dstFolder)

        # Run Deid (would be better to interface directly)
        call(***REMOVED***"python3", "-O", "deidpipe.py", 
              "-i", srcFolder, 
              "-o", dstFolder, 
              "-s", srcMeta, 
              "-f", "configs/philter_delta.json",
              "-l", "False"***REMOVED***)

        # Rename files (Keep if we have meta, otherwise toss--also toss log)
        # Also create map between note_key and deid_note_key
        mfile = open(srcMeta)
        head = mfile.readline()
        noteKey2deidNoteKey = dict()
        for line in mfile:
            line = line.split("\t")
            noteKey2deidNoteKey***REMOVED***line***REMOVED***0***REMOVED******REMOVED*** = line***REMOVED***2***REMOVED***

        # Iterate through output files
        filenames = os.listdir(dstFolder)
        for filename in filenames:
            # Keep if we have meta in dict
            try:
                noteKey = filename.strip("0")***REMOVED***:-9***REMOVED***
                deidNoteKey = noteKey2deidNoteKey***REMOVED***noteKey***REMOVED***
                os.rename(dstFolder + filename, dstFolder + deidNoteKey + ".txt")
            # Toss if we dont
            except KeyError:
                try:
                    os.remove(dstFolder + filename)
                except IsADirectoryError:
                    # Remove log
                    rmtree(dstFolder + filename)

        # Print time elapsed for batch
        t = time.time() - t0
        print(dstFolder + ": " + str(t) + " seconds")

        q.task_done()


# Set up some threads to fetch the enclosures (each thread deids a directory)
for unit in range(num_threads):
    worker = Thread(target=runDeidChunck, args=(unit, enclosure_queue,))
    worker.setDaemon(True)
    worker.start()

# Build queue
#for i in ***REMOVED***2***REMOVED***:
#    for j in range(0,400):
#        for k in range(0,10):
#            enclosure_queue.put((i,j,k))
for root, dirs, files in os.walk(srcBase):
    if not dirs: enclosure_queue.put(root)
    #print(os.path.join(root,d)) 
        
# Now wait for the queue to be empty, indicating that we have
# processed all of the notes
print('*** Main thread waiting')
enclosure_queue.join()
print('*** Done')

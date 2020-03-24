import sys
import argparse
import distutils.util
import os
import random
from math import ceil
from subprocess import call
from collections import OrderedDict

# using OrderedDict for reproducability
servers = OrderedDict(***REMOVED***('MCWLDEIDLAP701.ucsfmedicalcenter.org',24),
                       ('qcdeidlap702.ucsfmedicalcenter.org',14),
                       ('qcdeidlap703.ucsfmedicalcenter.org',14),
                       ('qcdeidlap705.ucsfmedicalcenter.org',14)***REMOVED***)
random.seed(10101) #fix seed for reproducibility 


def get_args():
    # gets input/output/filename
    help_str = """De-identify and surrogate all text files in a set of folders distributed to servers via ssh. Calls deidloop.py"""
    
    ap = argparse.ArgumentParser(description=help_str)

    ap.add_argument("--username", required=True,
                    help="The username used to ssh into the servers",
                    type=str)
    ap.add_argument("--philter", required=True,
                    help="Path to Philter program files like deidpipe.py",
                    type=str)
    ap.add_argument("-i", "--input", required=True,
                    help="Path to the file or directory that contains the list"
                    + " of input folders",
                    type=str)
    ap.add_argument("-o", "--output", required=True,
                    help="Path to the directory that the output notes are"
                    + " written to",
                    type=str)
    ap.add_argument("-s", "--surrogate", required=True,
                    help="Path to the directory that contains the metafiles"
                    + " (must have the same sub directory structure as input)",
                    type=str)
    ap.add_argument("--superlog", required=True,
                    help="Path to the folder for the super log."
                    + " When this is set, the pipeline prints and saves a"
                    + " super log in a subfolder log of the set folder"
                    + " combining logs of each output directory",
                    type=str)

    return ap.parse_args()



def _read_src_folders(srcList):
    # lists all subdirs in file srcList
    srcFolders = ***REMOVED******REMOVED***
    print("reading folder list from " + srcList)
    with open(srcList, 'r') as sl:
        for line in sl:
            srcFolders.append(os.path.join(line.strip(), ''))
    return srcFolders

def _walk_src_folders(srcBase):
    # lists all subdirs in dir srcBase
    srcFolders = ***REMOVED******REMOVED***
    print("walking through {0} (this can take a couple of minutes)".format(srcBase))
    for root, dirs, files in os.walk(srcBase):
        if not dirs:
            srcFolders.append(os.path.join(root, '')) # adds trailing slash
            #print("found dir {0}".format(root))
    return srcFolders

def _shuffle_src_folders(srcFolders):
    # shuffle subdirs list to balance out across servers
    print("shuffling {0} found subdirs".format(len(srcFolders)))
    random.shuffle(srcFolders)
    return srcFolders

def _list_metafiles_and_dst_folders(srcFolders, mtaBase, dstBase, srcBase=None):
    srcMetafiles = ***REMOVED******REMOVED***
    dstFolders = ***REMOVED******REMOVED***
    if not srcBase: srcBase = os.path.dirname(os.path.commonprefix(srcFolders)) # use os.path.commonpath(srcFolders) if you have python 3.5 or higher
    print("creating metafiles list from " + mtaBase
          + " and output subdirs list from " +  dstBase)
    for srcFolder in srcFolders:
        srcMetafiles.append(os.path.join(mtaBase, os.path.relpath(srcFolder,
                                                                  srcBase),
                                         "meta_data.txt"))
        dstFolders.append(os.path.join(dstBase, os.path.relpath(srcFolder,
                                                                srcBase),
                                       ''))
    return srcMetafiles, dstFolders

def create_imo_lists(srcPath, mtaBase, dstBase):
    if os.path.isdir(srcPath):
        srcFolders = _walk_src_folders(srcPath)
        srcBase = srcPath
    elif os.path.isfile(srcPath):
        srcFolders = _read_src_folders(srcPath)
        srcBase = os.path.dirname(os.path.commonprefix(srcFolders)) # use os.path.commonpath(srcFolders) if you have python 3.5 or higher
    else:
        return None

    srcFolders = _shuffle_src_folders(srcFolders)
    srcMetaFiles, dstFolders = _list_metafiles_and_dst_folders(srcFolders,
                                                               mtaBase, dstBase,
                                                               srcBase)
    return srcFolders, srcMetaFiles, dstFolders
    
def write_chunk_files(servers, srcFolders, srcMetafiles, dstFolders,
                      prefix="chunk_", extension="csv"):
    # split into chunks based on number_of_servers
    # & number_of_threads_per_each_server
    total_threads = sum(servers.values())
    chunk_len = ***REMOVED******REMOVED***
    chunks_fname = {}

    for url, nthreads in servers.items():
        subdirs_fraction = nthreads / total_threads
        chunk_len.append(ceil(subdirs_fraction * len(srcFolders)))

        if len(chunk_len) > 1:
            start = end
        else:
            start = 0
        end = sum(chunk_len***REMOVED***:-1***REMOVED***) + chunk_len***REMOVED***-1***REMOVED***

        chunk_srcFolders = srcFolders***REMOVED***start:end***REMOVED***
        chunk_srcMetafiles = srcMetafiles***REMOVED***start:end***REMOVED***
        chunk_dstFolders = dstFolders***REMOVED***start:end***REMOVED***
        
        chunks_fname***REMOVED***url***REMOVED*** = prefix + url.split('.')***REMOVED***0***REMOVED*** + "." + extension
        with open(chunks_fname***REMOVED***url***REMOVED***, 'w') as cf:
            for idir, mfile, odir in zip(chunk_srcFolders, chunk_srcMetafiles,
                                         chunk_dstFolders):
                cf.write("{0} {1} {2}\n".format(idir, mfile, odir))
                
    return chunks_fname

def scp_chunk_files(servers, username, wrkDir, chunks_fname):
    for url, nthreads in servers.items():
        print("copying imo chunk file to server " + url)
        os.system("scp {0} {1}@{2}:{3}".format(chunks_fname***REMOVED***url***REMOVED***, username,
                                               url, wrkDir))

def send_jobs(servers, username, wrkDir, chunks_fname, logBase):
    # ssh into each server and pass respective subdirs chunk to deidloop
    for url, nthreads in servers.items():
        commandline = ("ssh {0}@{1}".format(username, url)
                       #+ " hostname && echo \""
                       + " nohup /usr/bin/time nice python3 "
                       + os.path.join(wrkDir, "deidloop.py")
                       + " -t {0} ".format(nthreads)
                       + " --imofile " + os.path.join(wrkDir, chunks_fname***REMOVED***url***REMOVED***)
                       + " --philterfolder" + wrkDir
                       + " --superlog " + logBase
                       + " > " + os.path.join(wrkDir, "stdouterr_"
                                              + url.split('.')***REMOVED***0***REMOVED*** + ".txt")
                       + " 2>&1 &")
        print(commandline)
        #call(commandline.split())

# rsync deid'd notes back to master (or sync across servers)


def main():

    args = get_args()

    srcFolders, srcMetaFiles, dstFolders = create_imo_lists(args.input,
                                                            args.surrogate,
                                                            args.output)
    chunks_fname = write_chunk_files(servers,
                                     srcFolders, srcMetaFiles, dstFolders)
    
    scp_chunk_files(servers, args.username, args.philterfolder, chunks_fname)
    send_jobs(servers, args.username, args.philterfolder, chunks_fname, args.superlog)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

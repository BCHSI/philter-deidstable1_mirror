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
    ap.add_argument("-k", "--knownphi", required=True,
                    help="Path to the directory that contains the probesfiles"
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
    srcFolders = []
    print("reading folder list from " + srcList)
    with open(srcList, 'r') as sl:
        for line in sl:
            srcFolders.append(os.path.join(line.strip(), ''))
    return srcFolders

def _walk_src_folders(srcBase):
    # lists all subdirs in dir srcBase
    srcFolders = []
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

def _list_mfiles_dfolders_kpfiles(srcFolders, mtaBase, dstBase, kpBase,
                                  srcBase=None):
    srcMetafiles = []
    dstFolders = []
    kPhifiles = []
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
        kPhifiles.append(os.path.join(kpBase, os.path.relpath(srcFolder,
                                                              srcBase),
                                         "knownphi_data_dana_value.txt"))
    return srcMetafiles, dstFolders, kPhifiles

def create_imok_lists(srcPath, mtaBase, dstBase, kpBase):
    if os.path.isdir(srcPath):
        srcFolders = _walk_src_folders(srcPath)
        srcBase = srcPath
    elif os.path.isfile(srcPath):
        srcFolders = _read_src_folders(srcPath)
        srcBase = os.path.dirname(os.path.commonprefix(srcFolders)) # use os.path.commonpath(srcFolders) if you have python 3.5 or higher
    else:
        return None

    srcFolders = _shuffle_src_folders(srcFolders)
    metaFiles, dstFolders, kpFiles = _list_mfiles_dfolders_kpfiles(srcFolders,
                                                                   mtaBase,
                                                                   dstBase,
                                                                   kpBase,
                                                                   srcBase)
    return srcFolders, metaFiles, dstFolders, kpFiles
    
def write_chunk_files(servers, srcFolders, srcMetafiles, dstFolders, kPhifiles,
                      prefix="chunk_", extension="csv"):
    # split into chunks based on number_of_servers
    # & number_of_threads_per_each_server
    total_threads = sum(servers.values())
    chunk_len = []
    chunks_fname = {}

    for url, nthreads in servers.items():
        subdirs_fraction = nthreads / total_threads
        chunk_len.append(ceil(subdirs_fraction * len(srcFolders)))
        print("tothreads: {0} nthreads: {1} frac: {2} lenF: {3} lenC: {4}".format(total_threads, nthreads, subdirs_fraction, len(srcFolders), len(chunk_len)))
        if len(chunk_len) > 1:
            start = end
        else:
            start = 0
        end = sum(chunk_len[:-1]) + chunk_len[-1]
        print("start: {0} end: {1}".format(start, end))
        chunk_srcFolders = srcFolders[start:end]
        chunk_srcMetafiles = srcMetafiles[start:end]
        chunk_dstFolders = dstFolders[start:end]
        chunk_kPhifiles = kPhifiles[start:end]
        
        chunks_fname[url] = prefix + url.split('.')[0] + "." + extension
        with open(chunks_fname[url], 'w') as cf:
            for idir, mfile, odir, kfile in zip(chunk_srcFolders,
                                                chunk_srcMetafiles,
                                                chunk_dstFolders,
                                                chunk_kPhifiles):
                cf.write("{0} {1} {2} {3}\n".format(idir, mfile, odir, kfile))
                
    return chunks_fname

def scp_chunk_files(servers, username, wrkDir, chunks_fname):
    for url, nthreads in servers.items():
        print("copying imo chunk file to server " + url)
        os.system("scp {0} {1}@{2}:{3}".format(chunks_fname[url], username,
                                               url, wrkDir))

def send_jobs(servers, username, wrkDir, chunks_fname, logBase):
    # ssh into each server and pass respective subdirs chunk to deidloop
    for url, nthreads in servers.items():
        commandline = ("ssh {0}@{1}".format(username, url)
                       #+ " hostname && echo \""
                       + " nohup /usr/bin/time nice python3 "
                       + os.path.join(wrkDir, "deidloop.py")
                       + " -t {0} ".format(nthreads)
                       + " --imofile " + os.path.join(wrkDir, chunks_fname[url])
                       + " --philterfolder" + wrkDir
                       + " --superlog " + logBase
                       + " > " + os.path.join(wrkDir, "stdouterr_"
                                              + url.split('.')[0] + ".txt")
                       + " 2>&1 &")
        print(commandline)
        #call(commandline.split())

# rsync deid'd notes back to master (or sync across servers)


def main():

    args = get_args()

    sdirs, mfiles, ddirs, kfiles = create_imok_lists(args.input,
                                                     args.surrogate,
                                                     args.output,
                                                     args.knownphi)
    chunks_fname = write_chunk_files(servers, sdirs, mfiles, ddirs, kfiles)
    
    scp_chunk_files(servers, args.username, args.philterfolder, chunks_fname)
    send_jobs(servers, args.username, args.philterfolder, chunks_fname, args.superlog)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

import os
import random
from math import ceil
from subprocess import call

username = "schenkg"
servers = {'MCWLDEIDLAP701.ucsfmedicalcenter.org':24,
           'qcdeidlap702.ucsfmedicalcenter.org':14,
           'qcdeidlap703.ucsfmedicalcenter.org':14,
           'qcdeidlap705.ucsfmedicalcenter.org':14}

srcBase = "/data/notes/shredded_notes/"
srcList = "/data/shared/dir_list_shredded_notes.txt"
dstBase = "/data/schenkg/deid_notes_20180328_ttt/"
mtaBase = "/data/notes/meta_data_20180328/"
wrkDir = "/data/schenkg/pipeline/" #dstBase

# list all subdirs in srcBase
srcFolders = []
if not srcList: # slow
    print("walking through {0} (this can take a couple of minutes)".format(srcBase))
    for root, dirs, files in os.walk(srcBase):
        if not dirs:
            srcFolders.append(os.path.join(root, '')) # adds trailing slash
            #print("found dir {0}".format(root))
else:
    print("reading folder list from " + srcList)
    with open(srcList, 'r') as sl:
        for line in sl:
            srcFolders.append(os.path.join(line.strip(), ''))

    
# shuffle subdirs list to balance out across servers
print("shuffling {0} found subdirs".format(len(srcFolders)))
random.seed(10101) #fix seed for reproducibility 
random.shuffle(srcFolders)

srcMetafiles = []
dstFolders = []
print("creating metafiles list from " + mtaBase
      + " and output subdirs list from " +  dstBase)
for srcFolder in srcFolders:
    srcMetafiles.append(os.path.join(mtaBase, os.path.relpath(srcFolder,
                                                              srcBase),
                                     "meta_data.txt"))
    dstFolders.append(os.path.join(dstBase, os.path.relpath(srcFolder, srcBase),
                                   ''))

# split into chunks based on number_of_servers & number_of_threads_per_each_server
total_threads = sum(servers.values())
chunk_len = []
chunks_fname = {}
for url, nthreads in servers.items():
    subdirs_fraction = nthreads / total_threads
    chunk_len.append(ceil(subdirs_fraction * len(srcFolders)))
    if len(chunk_len) > 1:
        start = end
    else:
        start = 0
    end = sum(chunk_len[:-1]) + chunk_len[-1]
    chunk_srcFolders = srcFolders[start:end]
    chunk_srcMetafiles = srcMetafiles[start:end]
    chunk_dstFolders = dstFolders[start:end]
    chunks_fname[url] = "chunk_" + url.split('.')[0] + ".csv"
    with open(chunks_fname[url], 'w') as cf:
        for idir, mfile, odir in zip(chunk_srcFolders, chunk_srcMetafiles,
                                     chunk_dstFolders):
            cf.write("{0} {1} {2}\n".format(idir, mfile, odir))
    print("copying imo chunk file to server " + url)
    os.system("scp {0} {1}@{2}:{3}".format(chunks_fname[url], username, url,
                                           wrkDir))
    
# ssh into each server and pass respective subdirs chunk to deidloop
for url, nthreads in servers.items():
    commandline = ("ssh {0}@{1}".format(username, url)
                   #+ " hostname && echo \""
                   + " nohup /usr/bin/time nice python3 "
                   + os.path.join(wrkDir, "deidloop.py")
                   + " -t {0} ".format(nthreads)
                   + " --imofile " + os.path.join(wrkDir, chunks_fname[url])
                   + " --philter " + wrkDir
                   + " --superlog " + dstBase
                   + " > " + os.path.join(wrkDir, "stdouterr_"
                                          + url.split('.')[0] + ".txt")
                   + " 2>&1 &")
    print(commandline)
    call(commandline.split())

# rsync deid'd notes back to master (or sync across servers)

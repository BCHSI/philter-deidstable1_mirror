import os
import random
from math import ceil
from subprocess import call

username = "schenkg"
servers = {'MCWLDEIDLAP701.ucsfmedicalcenter.org':24,
           'qcdeidlap702.ucsfmedicalcenter.org':14,
           'qcdeidlap703.ucsfmedicalcenter.org':14}#,
           #'qcdeidlap705.ucsfmedicalcenter.org':14}

srcBase = "/data/notes/shredded_notes/000/000/000/"
dstBase = "/data/deid_notes_20180328/000/000/000/"
mtaBase = "/data/notes/meta_data_20180328/000/000/000/"
wrkDir = "/data/schenkg/" #dstBase

# list all subdirs in srcBase
srcFolders = []
print("walking through {0} (this can take a couple of minutes)".format(srcBase))
for root, dirs, files in os.walk(srcBase):
    if not dirs:
        srcFolders.append(root + '/')
        #print("found dir {0}".format(root))
    
# shuffle subdirs list to balance out across servers
print("shuffling {0} found subdirs".format(len(srcFolders)))
random.seed(10101) #fix seed for reproducibility 
random.shuffle(srcFolders)

srcMetafiles = []
dstFolders = []
print("creating metafiles list in {0} and output subdirs list in {1}".format(mtaBase, dstBase))
for srcFolder in srcFolders:
    srcMetafiles.append(os.path.join(mtaBase, os.path.relpath(srcFolder,
                                                              srcBase),
                                     "meta_data.txt"))
    dstFolders.append(os.path.join(dstBase,
                                   os.path.relpath(srcFolder, srcBase)) + '/')

# split into chunks based on number_of_servers & number_of_threads_per_each_server
total_threads = sum(servers.values())
chunk_len = []
chunks_srcFolders_fname = {}
chunks_srcMetafiles_fname = {}
chunks_dstFolders_fname = {}
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
    chunks_srcFolders_fname[url] = "srcfolders_" + url.split('.')[0] + ".txt"
    chunks_srcMetafiles_fname[url] = "srcmetafiles_" + url.split('.')[0] + ".txt"
    chunks_dstFolders_fname[url] = "dstfolders_" + url.split('.')[0] + ".txt"
    with open(chunks_srcFolders_fname[url], 'w') as cf:
        cf.write('\n'.join(chunk_srcFolders))
        cf.write('\n')
    with open(chunks_srcMetafiles_fname[url], 'w') as cf:
        cf.write('\n'.join(chunk_srcMetafiles))
        cf.write('\n')
    with open(chunks_dstFolders_fname[url], 'w') as cf:
        cf.write('\n'.join(chunk_dstFolders))
        cf.write('\n')
    # os.system("scp {0} {1} {2} {3}@{4}:{5}".format(chunks_srcFolders_fname[url], chunks_srcMetafiles_fname[url], chunks_dstFolders_fname[url],
    #                                                username, url, wrkDir))
    
# ssh into each server and pass respective subdirs chunk to deidloop
for url, nthreads in servers.items():
    commandline = "ssh {0}@{1} ".format(username, url) + "echo \"/usr/bin/time nice python3 {2}deidloop.py {1} {2}{3} {2}{4} {2}{5} > {2}stdouterr_{0}.txt 2>&1 &\"".format(url.split('.')[0], nthreads, wrkDir, chunks_srcFolders_fname[url], chunks_srcMetafiles_fname[url], chunks_dstFolders_fname[url])
    print(commandline)
    call(commandline.split())

# rsync deid'd notes back to master (or sync across servers)

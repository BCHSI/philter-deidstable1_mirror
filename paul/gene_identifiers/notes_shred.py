# Written by Hunter Mills

import os
import shutil

def note_batch_generator(outputdir, basedir='.', n=1000):
    gen = os.walk(basedir)
    i = 0
    j = 0
    for root, dirs, files in os.walk(basedir):
        for filename in files:
            if i == 0:
                shutil.rmtree(outputdir, ignore_errors=True)
                os.makedirs(outputdir)
            source = os.path.join(root, filename)
            destination = os.path.join(outputdir, filename)
            shutil.copyfile(source, destination)
            i += 1
            j += 1
            if i >= n:
                i = 0
                yield j
    yield j

gen = note_batch_generator(outputdir, path2mimic)

# next(gen)
# for batch in notes:
#   print(batch)

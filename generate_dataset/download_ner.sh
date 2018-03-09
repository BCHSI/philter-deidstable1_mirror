#!/bin/bash
wget "http://nlp.stanford.edu/software/stanford-ner-2014-06-16.zip"
unzip stanford-ner-2014-06-16.zip
mv stanford-ner-2014-06-16 stanford-ner
sudo mv stanford-ner /usr/local/
rm stanford-ner-2014-06-16.zip
rm -r stanford-ner
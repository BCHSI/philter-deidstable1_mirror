## philter-opt(imized)

### Main differences

1. Avoid unnecessary calls to the POS tagger by `map_set()` and `map_pos()`.
2. Avoid redundant tokenization in `map_set()` and `map_pos()`.
3. Eliminate POS computation by storing the POS data offline (to a file) and just load them each time Philter is run.

### How to run?

`python3 optimized/main_opt.py -i=./data/i2b2_notes/ -a=./data/i2b2_anno/ -o=./data/i2b2_results/ -f=./configs/philter_alpha.json -e=False`

## Evaluation 
 The evaluation script contains two parts: producing logs and evaluating the performance of the pipeline.

 ### Logs (Done)
 The pipeline will produce logs by default in the subdirectory "log" under the result directory. To turn of logging, add "-l False" to the command line arguments.
 The following logs will be generated to assist further development and analysis of Philter:
 1. phi_count.txt: this file contains the number of PHI captured by PHI categories. 
 2. failed_dates.json: this file contains the dates that are failed to be parsed for surrogation. 
 3. parsed_dates.json: this file contains the raw dates that are successfully parsed, the normalized dates, and the surrogated dates.
 4. phi_marked.json: this file contains all PHI that are marked by Philter and their associated categories.


 ### Evaluation (IP)
 Producing evaluation of the pipeline needs manually annotated gold standard notes and normalized dates as input. 
 #### Evaluate date surrogation
 The evaluation script compares the manually normalized dates with the dates that are normalized by Philter. 
 #### Evaluate PHI coverage
 The evaluation script compares the annotated notes with Philtered notes and produces the following matrices: 
 - True positive:
 - True negative:
 - False negative:
 - False positive:
 - Recall:
 - Precision:

 
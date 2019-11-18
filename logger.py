
import sys
import argparse
import pandas
import numpy
import os

def get_args():
    # gets input/output/filename
    help_str = """Create log files after one or multiple runs of deidpipe"""
    
    ap = argparse.ArgumentParser(description=help_str)

    ap.add_argument("--imofile",
                    help="Path to the file that contains the list of input"
                    + " folders, metafiles, output folders",
                    type=str)
    ap.add_argument("--superlog", 
                    help="Path to the folder for the super log."
                    + " When this is set, the pipeline prints and saves a"
                    + " super log in a subfolder log of the set folder"
                    + " combining logs of each output directory",
                    type=str)

    return ap.parse_args()


def get_super_log(all_logs, super_log_dir):
    
    #Path to csv summary of all files
    csv_summary_filepath = os.path.join(super_log_dir,
                                        'deidpipe_superlog_detailed.csv')
    #Path to txt summary of all files combined
    text_summary_filepath = os.path.join(super_log_dir,
                                         'deidpipe_superlog_summary.txt')
    #Path to dynamic blacklist superlog
    dynamic_blacklist_filepath = os.path.join(super_log_dir,
                                              'dynamic_blacklist_superlog.csv')
    os.makedirs(super_log_dir, exist_ok=True)

    # Create aggregated summary file
    if not os.path.isfile(csv_summary_filepath):
        with open(csv_summary_filepath, 'w',
                  errors='surrogateescape') as f:
            file_header = ('filename' + ',' + 'file_size' + ','
                           + 'total_tokens' + ',' + 'phi_tokens' + ','
                           + 'successfully_normalized' + ','
                           + 'failed_normalized' + ','
                           + 'successfully_surrogated' + ','
                           + 'failed_surrogated' + '\n')
            f.write(file_header)
    

    # Create aggregated dynamic blacklist file
    if not os.path.isfile(dynamic_blacklist_filepath):
        with open(dynamic_blacklist_filepath, 'w',
                  errors='surrogateescape') as f:
            file_header = ('filename' + "\t" + 'start' + "\t" + 'stop' + "\t"
                           + 'knownphi_token' + "\t" + 'context' + "\t"
                           + 'phi_type' + "\n")
            f.write(file_header)

    # Append contents of all summaries to this file
    for log_file in all_logs:
        if not os.path.exists(log_file):
            print("log file missing: " + log_file)
            continue
        with open(log_file,'r') as f:
            with open(csv_summary_filepath,'a') as f1:
                with open(dynamic_blacklist_filepath, 'a') as f2:
                    # Check if current log file is empty
                    if not os.stat(log_file).st_size == 0:
                        next(f) # skip header line
                        if 'dynamic_blacklist_summary.csv' in log_file:
                            for line in f:
                                f2.write(line)
                        else:
                            for line in f:
                                f1.write(line)

    summary = pandas.read_csv(csv_summary_filepath)

    # Batch size (all)
    number_of_notes = len(summary)

    # File size
    total_kb_processed = sum(summary***REMOVED***'file_size'***REMOVED***)/1000
    median_file_size = numpy.median(summary***REMOVED***'file_size'***REMOVED***)
    q2pt5_size,q97pt5_size = numpy.percentile(summary***REMOVED***'file_size'***REMOVED***,***REMOVED***2.5,97.5***REMOVED***)

    # Total tokens
    total_tokens = numpy.sum(summary***REMOVED***'total_tokens'***REMOVED***)
    median_tokens = numpy.median(summary***REMOVED***'total_tokens'***REMOVED***)
    q2pt5_tokens,q97pt5_tokens = numpy.percentile(summary***REMOVED***'total_tokens'***REMOVED***,***REMOVED***2.5,97.5***REMOVED***)

    # Total PHI tokens
    total_phi_tokens = numpy.sum(summary***REMOVED***'phi_tokens'***REMOVED***)
    median_phi_tokens = numpy.median(summary***REMOVED***'phi_tokens'***REMOVED***)
    q2pt5_phi_tokens,q97pt5_phi_tokens = numpy.percentile(summary***REMOVED***'phi_tokens'***REMOVED***,***REMOVED***2.5,97.5***REMOVED***)

    # Normalization
    successful_normalization = sum(summary***REMOVED***'successfully_normalized'***REMOVED***)
    failed_normalization = sum(summary***REMOVED***'failed_normalized'***REMOVED***)

    # Surrogation
    successful_surrogation = sum(summary***REMOVED***'successfully_surrogated'***REMOVED***)
    failed_surrogation = sum(summary***REMOVED***'failed_surrogated'***REMOVED***)


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


def create_log_files_list(imofile):
    all_logs = ***REMOVED******REMOVED***
    with open(imofile, 'r') as imo:
        for line in imo:
            parts = line.split()
            odir = parts***REMOVED***2***REMOVED***
            
            all_logs.append(os.path.join(odir, "log",
                                         "detailed_batch_summary.csv"))
            all_logs.append(os.path.join(odir, "log",
                                         "dynamic_blacklist_summary.csv"))
            
    return all_logs
        
def main():
        
    args = get_args()
    
    if args.superlog:
        # Once all the directories have been processed,
        # create a superlog that combines all logs in each output directory
        all_logs  = create_log_files_list(args.imofile)

        # Create super log of batch summaries
        if all_logs != ***REMOVED******REMOVED***:
            get_super_log(all_logs, os.path.join(args.superlog, "log"))

    return 0


if __name__ == "__main__":
    sys.exit(main())

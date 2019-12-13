
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
        
        if 'dynamic_blacklist_summary.csv' in log_file:
            fpath = dynamic_blacklist_filepath
        elif 'detailed_batch_summary.csv' in log_file:
            fpath = csv_summary_filepath
        else:
            raise Exception("Unknown logfile: ", log_file)

        with open(log_file, 'r', errors='surrogateescape') as f:
            next(f, None) # skip header line
            with open(fpath, 'a', errors='surrogateescape') as f1:
                for line in f:
                    f1.write(line)

    summary = pandas.read_csv(csv_summary_filepath)

    # Batch size (all)
    number_of_notes = len(summary)

    # File size
    total_kb_processed = sum(summary['file_size'])/1000
    median_file_size = numpy.median(summary['file_size'])
    q2pt5_size,q97pt5_size = numpy.percentile(summary['file_size'],[2.5,97.5])

    # Total tokens
    total_tokens = numpy.sum(summary['total_tokens'])
    median_tokens = numpy.median(summary['total_tokens'])
    q2pt5_tokens,q97pt5_tokens = numpy.percentile(summary['total_tokens'],[2.5,97.5])

    # Total PHI tokens
    total_phi_tokens = numpy.sum(summary['phi_tokens'])
    median_phi_tokens = numpy.median(summary['phi_tokens'])
    q2pt5_phi_tokens,q97pt5_phi_tokens = numpy.percentile(summary['phi_tokens'],[2.5,97.5])

    # Normalization
    successful_normalization = sum(summary['successfully_normalized'])
    failed_normalization = sum(summary['failed_normalized'])

    # Surrogation
    successful_surrogation = sum(summary['successfully_surrogated'])
    failed_surrogation = sum(summary['failed_surrogated'])

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
    all_logs = []
    with open(imofile, 'r') as imo:
        for line in imo:
            parts = line.split()
            odir = parts[2]
            
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
        if all_logs != []:
            get_super_log(all_logs, os.path.join(args.superlog, "log"))

    return 0


if __name__ == "__main__":
    sys.exit(main())

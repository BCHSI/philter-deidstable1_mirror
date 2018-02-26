import pandas as pd
import numpy as np

phi = pd.read_table('/media/DataHD/PHI_probes/phi_probe.txt', skiprows=1,
                    names = ***REMOVED***'pat_or_provider', 'person_id','phi_type', 'source_id', 'clean_value'***REMOVED***,
                   sep='\s+')

print phi.shape

ucsf_fnames_all = phi.loc***REMOVED***phi***REMOVED***'phi_type'***REMOVED*** == 'fname'***REMOVED***

ucsf_lnames_all = phi.loc***REMOVED***phi***REMOVED***'phi_type'***REMOVED*** == 'lname'***REMOVED***


#ucsf_fnames_all.loc***REMOVED***-1***REMOVED*** = ***REMOVED***'pat', 3, 'fname',46, 0.5***REMOVED*** # adding a row
#ucsf_fnames_all.index = ucsf_fnames_all.index +1 # shifting index 
#ucsf_fnames_all = ucsf_fnames_all.sort_index() #update

ucsf_fnames_all***REMOVED***'clean_value'***REMOVED*** = ucsf_fnames_all***REMOVED***'clean_value'***REMOVED***.str.lower()
ucsf_lnames_all***REMOVED***'clean_value'***REMOVED*** = ucsf_lnames_all***REMOVED***'clean_value'***REMOVED***.str.lower()
#ucsf_fnames_all.head()



ucsf_fnames_all = ucsf_fnames_all.dropna(how='any')
ucsf_lnames_all = ucsf_lnames_all.dropna(how='any')

ucsf_fnames_all***REMOVED***'word_len'***REMOVED*** = ucsf_fnames_all.clean_value.apply(lambda x: len(x))
ucsf_lnames_all***REMOVED***'word_len'***REMOVED*** = ucsf_lnames_all.clean_value.apply(lambda x: len(x))

#ucsf_fnames_all.head()

n=3
ucsf_fnames_all = ucsf_fnames_all.loc***REMOVED***ucsf_fnames_all***REMOVED***'word_len'***REMOVED*** >= n***REMOVED***
ucsf_lnames_all = ucsf_lnames_all.loc***REMOVED***ucsf_lnames_all***REMOVED***'word_len'***REMOVED*** >= n***REMOVED***



s=10
ucsf_fnames_count = pd.DataFrame(ucsf_fnames_all.clean_value.value_counts().reset_index())

ucsf_fnames_count.columns = ***REMOVED***'name','count'***REMOVED***
ucsf_fnames_count = ucsf_fnames_count.loc***REMOVED***ucsf_fnames_count***REMOVED***'count'***REMOVED*** >= s***REMOVED***
ucsf_lnames_count = pd.DataFrame(ucsf_lnames_all.clean_value.value_counts().reset_index())

ucsf_lnames_count.columns = ***REMOVED***'name','count'***REMOVED***
ucsf_lnames_count = ucsf_lnames_count.loc***REMOVED***ucsf_lnames_count***REMOVED***'count'***REMOVED*** >= s***REMOVED***


ucsf_fnames_count.to_csv('ucsf_fnames_count.tsv', index=False, sep='\t')
ucsf_lnames_count.to_csv('ucsf_lnames_count.tsv', index=False, sep='\t')
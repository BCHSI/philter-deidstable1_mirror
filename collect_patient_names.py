import pandas as pd
import numpy as np

phi = pd.read_table('/media/DataHD/PHI_probes/phi_probe.txt', skiprows=1,
                    names = ['pat_or_provider', 'person_id','phi_type', 'source_id', 'clean_value'],
                   sep='\s+')

print phi.shape

ucsf_fnames_all = phi.loc[phi['phi_type'] == 'fname']

ucsf_lnames_all = phi.loc[phi['phi_type'] == 'lname']


#ucsf_fnames_all.loc[-1] = ['pat', 3, 'fname',46, 0.5] # adding a row
#ucsf_fnames_all.index = ucsf_fnames_all.index +1 # shifting index 
#ucsf_fnames_all = ucsf_fnames_all.sort_index() #update

ucsf_fnames_all['clean_value'] = ucsf_fnames_all['clean_value'].str.lower()
ucsf_lnames_all['clean_value'] = ucsf_lnames_all['clean_value'].str.lower()
#ucsf_fnames_all.head()



ucsf_fnames_all = ucsf_fnames_all.dropna(how='any')
ucsf_lnames_all = ucsf_lnames_all.dropna(how='any')

ucsf_fnames_all['word_len'] = ucsf_fnames_all.clean_value.apply(lambda x: len(x))
ucsf_lnames_all['word_len'] = ucsf_lnames_all.clean_value.apply(lambda x: len(x))

#ucsf_fnames_all.head()

n=3
ucsf_fnames_all = ucsf_fnames_all.loc[ucsf_fnames_all['word_len'] >= n]
ucsf_lnames_all = ucsf_lnames_all.loc[ucsf_lnames_all['word_len'] >= n]



s=10
ucsf_fnames_count = pd.DataFrame(ucsf_fnames_all.clean_value.value_counts().reset_index())

ucsf_fnames_count.columns = ['name','count']
ucsf_fnames_count = ucsf_fnames_count.loc[ucsf_fnames_count['count'] >= s]
ucsf_lnames_count = pd.DataFrame(ucsf_lnames_all.clean_value.value_counts().reset_index())

ucsf_lnames_count.columns = ['name','count']
ucsf_lnames_count = ucsf_lnames_count.loc[ucsf_lnames_count['count'] >= s]


ucsf_fnames_count.to_csv('ucsf_fnames_count.tsv', index=False, sep='\t')
ucsf_lnames_count.to_csv('ucsf_lnames_count.tsv', index=False, sep='\t')
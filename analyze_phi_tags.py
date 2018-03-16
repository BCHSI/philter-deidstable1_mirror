"""
TODO: 
Gets the PHI tag associated with each false negative

"""

import json
import re
import nltk
from nltk import word_tokenize

# Load PHI notes
phi = json.loads(open("./data/phi_notes.json", "r").read())


# Load summary file
summary = json.loads(open("./data/phi/summary.json").read())

all_doctor_phi = 0
all_hospital_phi = 0
all_country_phi = 0
all_age_phi = 0
all_username_phi = 0
all_city_phi = 0
all_state_phi = 0
all_zip_phi = 0
all_medicalrecord_phi = 0
all_patient_phi = 0
all_street_phi = 0
all_profession_phi = 0
all_idnum_phi = 0
all_organization_phi = 0
all_phone_phi = 0
all_location_other_phi = 0
all_date_phi = 0
all_email_phi = 0
all_fax_phi = 0
all_device_phi = 0
all_unspecified_phi = 0
# Get number of phi in each category
for file in phi:
	anno_file = phi[file]
	phi_dict = anno_file['phi']
	for item in phi_dict:		
		if item['TYPE'] == 'DOCTOR':
			all_doctor_phi += 1		
		if item['TYPE'] == 'HOSPITAL':
			all_hospital_phi += 1
		if item['TYPE'] == 'COUNTRY':
			all_country_phi += 1
		if item['TYPE'] == 'AGE':
			all_age_phi += 1
		if item['TYPE'] == 'USERNAME':
			all_username_phi += 1
		if item['TYPE'] == 'CITY':
			all_city_phi += 1
		if item['TYPE'] == 'STATE':
			all_state_phi += 1
		if item['TYPE'] == 'ZIP':
			all_zip_phi += 1
		if item['TYPE'] == 'MEDICALRECORD':
			all_medicalrecord_phi += 1
		if item['TYPE'] == 'PATIENT':
			all_patient_phi += 1
		if item['TYPE'] == 'STREET':
			all_street_phi += 1
		if item['TYPE'] == 'PROFESSION':
			all_profession_phi += 1
		if item['TYPE'] == 'IDNUM':
			all_idnum_phi += 1
		if item['TYPE'] == 'ORGANIZATION':
			all_organization_phi += 1
		if item['TYPE'] == 'PHONE':
			all_phone_phi += 1
		if item['TYPE'] == 'LOCATION-OTHER':
			all_location_other_phi += 1
		if item['TYPE'] == 'DATE':
			all_date_phi += 1
		if item['TYPE'] == 'EMAIL':
			all_email_phi += 1
		if item['TYPE'] == 'FAX':
			all_fax_phi += 1
		if item['TYPE'] == 'DEVICE':
			all_device_phi += 1

# Create dictionary to hold fn tags
fn_tags = {}

# Loop through all filenames in summary
for fn in summary['summary_by_file']:
	current_summary =  summary['summary_by_file'][fn]
	# Get corresponding info in phi_notes
	note_name = fn.split('/')[3]
	anno_name = note_name.split('.')[0] + ".xml"
	phi_list = phi[anno_name]['phi']
	# Loop through all FNs
	if current_summary['false_negatives'] != [] and current_summary['false_negatives'] != [""]:
		fn_tags[anno_name] = {}
		for false_negative in current_summary['false_negatives']:
			tokenized_fn = word_tokenize(false_negative)
			for item in tokenized_fn:
				if len(item) > 1:
					if item not in ['','.',',','(',')','#',"'s"]:
						if item in fn_tags[anno_name]:
							fn_tags[anno_name][item][1] += 1
						else:
							fn_tags[anno_name][item] = ['new',1]
					for phi_dict in phi_list:
						fn_tag = phi_dict['TYPE']
						if item in word_tokenize(phi_dict['text']) and item not in ['','.',',','(',')','#',"'s"]: # or (len(item) <4 and phi_dict['text'] in item and item not in ['','.',',','(',')']):
							fn_tags[anno_name][item][0] = fn_tag


phi_tag_lists = {}
for fn2 in fn_tags:
	counter = 0
	keys = list(fn_tags[fn2].keys())
	for subdict in fn_tags[fn2]:
		if fn_tags[fn2][subdict][0] not in phi_tag_lists:
			phi_tag_lists[fn_tags[fn2][subdict][0]] = [keys[counter]]
		else:
			phi_tag_lists[fn_tags[fn2][subdict][0]].append(keys[counter])
		counter += 1			

phi_tag_counts = {'DATE': 0, 'HOSPITAL': 0, 'DOCTOR': 0, 'CITY': 0, 'STATE': 0, 'AGE': 0, 'COUNTRY': 0, 'PATIENT': 0, 'MEDICALRECORD': 0, 'IDNUM': 0, 'USERNAME': 0, 'STREET': 0, 'ZIP': 0, 'PHONE': 0, 'PROFESSION': 0, 'ORGANIZATION': 0, 'LOCATION-OTHER': 0, 'FAX': 0, 'DEVICE': 0, 'EMAIL': 0}
for key in phi_tag_lists:
	phi_tag_counts[key] = len(phi_tag_lists[key])


recall_dict = {}
recall_dict['DOCTOR Recall'] = (all_doctor_phi-phi_tag_counts['DOCTOR'])/all_doctor_phi
recall_dict['HOSPITAL Recall'] = (all_hospital_phi-phi_tag_counts['HOSPITAL'])/all_hospital_phi
recall_dict['COUNTRY Recall'] = (all_country_phi-phi_tag_counts['COUNTRY'])/all_country_phi
recall_dict['AGE Recall'] = (all_age_phi-phi_tag_counts['AGE'])/all_age_phi
recall_dict['USERNAME Recall'] = (all_username_phi-phi_tag_counts['USERNAME'])/all_username_phi
recall_dict['CITY Recall'] = (all_city_phi-phi_tag_counts['CITY'])/all_city_phi
recall_dict['STATE Recall'] = (all_state_phi-phi_tag_counts['STATE'])/all_state_phi
recall_dict['ZIP Recall'] = (all_zip_phi-phi_tag_counts['ZIP'])/all_zip_phi
recall_dict['MEDICALRECORD Recall'] = (all_medicalrecord_phi-phi_tag_counts['MEDICALRECORD'])/all_medicalrecord_phi
recall_dict['PATIENT Recall'] = (all_patient_phi-phi_tag_counts['PATIENT'])/all_patient_phi
recall_dict['STREET Recall'] = (all_street_phi-phi_tag_counts['STREET'])/all_street_phi
recall_dict['PROFESSION Recall'] = (all_profession_phi-phi_tag_counts['PROFESSION'])/all_profession_phi
recall_dict['IDNUM Recall'] = (all_idnum_phi-phi_tag_counts['IDNUM'])/all_idnum_phi
recall_dict['ORGANIZATION Recall'] = (all_organization_phi-phi_tag_counts['ORGANIZATION'])/all_organization_phi
recall_dict['PHONE Recall'] = (all_phone_phi-phi_tag_counts['PHONE'])/all_phone_phi
recall_dict['LOCATION-OTHER Recall'] = (all_location_other_phi-phi_tag_counts['LOCATION-OTHER'])/all_location_other_phi
recall_dict['DATE Recall'] = (all_date_phi-phi_tag_counts['DATE'])/all_date_phi
recall_dict['EMAIL Recall'] = (all_email_phi-phi_tag_counts['EMAIL'])/all_email_phi
recall_dict['FAX Recall'] = (all_fax_phi-phi_tag_counts['FAX'])/all_fax_phi
recall_dict['DEVICE Recall'] = (all_device_phi-phi_tag_counts['DEVICE'])/all_device_phi

# Get totals for PHI in all notes


json.dump([fn_tags, phi_tag_lists, phi_tag_counts, recall_dict], open("data/phi_tags.json", "w"), indent=4)



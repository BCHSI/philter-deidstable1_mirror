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
all_unspecified_phi = 0
# Get number of phi in each category
for file in phi:
	anno_file = phi***REMOVED***file***REMOVED***
	phi_dict = anno_file***REMOVED***'phi'***REMOVED***
	for item in phi_dict:		
		if item***REMOVED***'TYPE'***REMOVED*** == 'DOCTOR':
			all_doctor_phi += 1		
		if item***REMOVED***'TYPE'***REMOVED*** == 'HOSPITAL':
			all_hospital_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'COUNTRY':
			all_country_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'AGE':
			all_age_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'USERNAME':
			all_username_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'CITY':
			all_city_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'STATE':
			all_state_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'ZIP':
			all_zip_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'MEDICALRECORD':
			all_medicalrecord_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'PATIENT':
			all_patient_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'STREET':
			all_street_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'PROFESSION':
			all_profession_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'IDNUM':
			all_idnum_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'ORGANIZATION':
			all_organization_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'PHONE':
			all_phone_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'LOCATION-OTHER':
			all_location_other_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'DATE':
			all_date_phi += 1
		if item***REMOVED***'TYPE'***REMOVED*** == 'EMAIL':
			all_email_phi += 1

# Create dictionary to hold fn tags
fn_tags = {}

# Loop through all filenames in summary
for fn in summary***REMOVED***'summary_by_file'***REMOVED***:
	current_summary =  summary***REMOVED***'summary_by_file'***REMOVED******REMOVED***fn***REMOVED***
	# Get corresponding info in phi_notes
	note_name = fn.split('/')***REMOVED***3***REMOVED***
	anno_name = note_name.split('.')***REMOVED***0***REMOVED*** + ".xml"
	phi_list = phi***REMOVED***anno_name***REMOVED******REMOVED***'phi'***REMOVED***
	# Loop through all FNs
	if current_summary***REMOVED***'false_negatives'***REMOVED*** != ***REMOVED******REMOVED*** and current_summary***REMOVED***'false_negatives'***REMOVED*** != ***REMOVED***""***REMOVED***:
		fn_tags***REMOVED***anno_name***REMOVED*** = {}
		for false_negative in current_summary***REMOVED***'false_negatives'***REMOVED***:
			tokenized_fn = word_tokenize(false_negative)
			for item in tokenized_fn:
				if len(item) > 1:
					if item not in ***REMOVED***'','.',',','(',')','#',"'s"***REMOVED***:
						if item in fn_tags***REMOVED***anno_name***REMOVED***:
							fn_tags***REMOVED***anno_name***REMOVED******REMOVED***item***REMOVED******REMOVED***1***REMOVED*** += 1
						else:
							fn_tags***REMOVED***anno_name***REMOVED******REMOVED***item***REMOVED*** = ***REMOVED***'new',1***REMOVED***
					for phi_dict in phi_list:
						fn_tag = phi_dict***REMOVED***'TYPE'***REMOVED***
						if item in word_tokenize(phi_dict***REMOVED***'text'***REMOVED***) and item not in ***REMOVED***'','.',',','(',')','#',"'s"***REMOVED***: # or (len(item) <4 and phi_dict***REMOVED***'text'***REMOVED*** in item and item not in ***REMOVED***'','.',',','(',')'***REMOVED***):
							fn_tags***REMOVED***anno_name***REMOVED******REMOVED***item***REMOVED******REMOVED***0***REMOVED*** = fn_tag


phi_tag_lists = {}
for fn2 in fn_tags:
	counter = 0
	keys = list(fn_tags***REMOVED***fn2***REMOVED***.keys())
	for subdict in fn_tags***REMOVED***fn2***REMOVED***:
		if fn_tags***REMOVED***fn2***REMOVED******REMOVED***subdict***REMOVED******REMOVED***0***REMOVED*** not in phi_tag_lists:
			phi_tag_lists***REMOVED***fn_tags***REMOVED***fn2***REMOVED******REMOVED***subdict***REMOVED******REMOVED***0***REMOVED******REMOVED*** = ***REMOVED***keys***REMOVED***counter***REMOVED******REMOVED***
		else:
			phi_tag_lists***REMOVED***fn_tags***REMOVED***fn2***REMOVED******REMOVED***subdict***REMOVED******REMOVED***0***REMOVED******REMOVED***.append(keys***REMOVED***counter***REMOVED***)
		counter += 1			

phi_tag_counts = {}
for key in phi_tag_lists:
	phi_tag_counts***REMOVED***key***REMOVED*** = len(phi_tag_lists***REMOVED***key***REMOVED***)


recall_dict = {}
recall_dict***REMOVED***'DOCTOR Recall'***REMOVED*** = (all_doctor_phi-phi_tag_counts***REMOVED***'DOCTOR'***REMOVED***)/all_doctor_phi
recall_dict***REMOVED***'HOSPITAL Recall'***REMOVED*** = (all_hospital_phi-phi_tag_counts***REMOVED***'HOSPITAL'***REMOVED***)/all_hospital_phi
recall_dict***REMOVED***'COUNTRY Recall'***REMOVED*** = (all_country_phi-phi_tag_counts***REMOVED***'COUNTRY'***REMOVED***)/all_country_phi
recall_dict***REMOVED***'USERNAME Recall'***REMOVED*** = (all_username_phi-phi_tag_counts***REMOVED***'USERNAME'***REMOVED***)/all_username_phi
recall_dict***REMOVED***'CITY Recall'***REMOVED*** = (all_city_phi-phi_tag_counts***REMOVED***'CITY'***REMOVED***)/all_city_phi
recall_dict***REMOVED***'STATE Recall'***REMOVED*** = (all_state_phi-phi_tag_counts***REMOVED***'STATE'***REMOVED***)/all_state_phi
recall_dict***REMOVED***'ZIP Recall'***REMOVED*** = (all_zip_phi-phi_tag_counts***REMOVED***'ZIP'***REMOVED***)/all_zip_phi
recall_dict***REMOVED***'MEDICALRECORD Recall'***REMOVED*** = (all_medicalrecord_phi-phi_tag_counts***REMOVED***'MEDICALRECORD'***REMOVED***)/all_medicalrecord_phi
recall_dict***REMOVED***'PATIENT Recall'***REMOVED*** = (all_patient_phi-phi_tag_counts***REMOVED***'PATIENT'***REMOVED***)/all_patient_phi
recall_dict***REMOVED***'STREET Recall'***REMOVED*** = (all_street_phi-phi_tag_counts***REMOVED***'STREET'***REMOVED***)/all_street_phi
recall_dict***REMOVED***'PROFESSION Recall'***REMOVED*** = (all_profession_phi-phi_tag_counts***REMOVED***'PROFESSION'***REMOVED***)/all_profession_phi
recall_dict***REMOVED***'IDNUM Recall'***REMOVED*** = (all_idnum_phi-phi_tag_counts***REMOVED***'IDNUM'***REMOVED***)/all_idnum_phi
recall_dict***REMOVED***'ORGANIZATION Recall'***REMOVED*** = (all_organization_phi-phi_tag_counts***REMOVED***'ORGANIZATION'***REMOVED***)/all_organization_phi
recall_dict***REMOVED***'LOCATION-OTHER Recall'***REMOVED*** = (all_location_other_phi-phi_tag_counts***REMOVED***'LOCATION-OTHER'***REMOVED***)/all_location_other_phi
recall_dict***REMOVED***'DATE Recall'***REMOVED*** = (all_date_phi-phi_tag_counts***REMOVED***'DATE'***REMOVED***)/all_date_phi
recall_dict***REMOVED***'EMAIL Recall'***REMOVED*** = (all_email_phi-phi_tag_counts***REMOVED***'EMAIL'***REMOVED***)/all_email_phi


# Get totals for PHI in all notes


json.dump(***REMOVED***fn_tags, phi_tag_lists, phi_tag_counts, recall_dict***REMOVED***, open("data/phi_tags.json", "w"), indent=4)



import pickle
import json
import os


def getcategory(summary, anno_path):
	'''
	return FN's category
	input:
	summary: dict[filename: dict[false_negative, false_positive, ture_positive]]
	anno_path: path to the annotation files
	output:
	FN_category: list["FN type"]
	FN_dict: dict[type:[FNs]]
	'''
	# summary_path = 'summary_dict.pkl'
	# anno_path = '/media/DataHD/philter-annotations/pooneh/pooneh-done'

	FN_dict = {'Name FN':[], 'Location FN':[], 'Date FN':[], 'Contact FN':[], 'ID FN':[], 'Age(>90) FN':[], 'Other FN':[],
				'True Negatives':[], 'True Positives':[], 'False Positives':[]}

	category_dict = {'0':'TN', '1':'TP', '2':'FP', 'n':'Name FN', 'l':'Location FN', 'd':'Date FN',
	                 'c':'Contact FN', 'i':'ID FN', 'a':'Age(>90) FN', 'o':'Other FN'}


	for (anno_file, results_dict) in summary.items():
		finpath = os.path.join(anno_path, anno_file + '.ano')
		# Load annotation
		if os.path.isfile(finpath):
			with open(finpath, 'rb') as fin:
			    anno = pickle.load(fin)
			
			# Get plain anno text
			anno_text = [item[0] for item in anno]

			for i in range(0, len(anno)):
				word = anno[i][0]
				word_category = anno[i][1]
				
				# Get word context
				if i > 4 and i < (len(anno)-4):
					phi_context = ' '.join(anno_text[i-4:i+5])
				elif i > 4 and i > (len(anno)-4):
				    phi_context = ' '.join(anno_text[i-4:])
				elif i < 4 and i < (len(anno)-4):
				    phi_context = ' '.join(anno_text[0:i+5])

				if word_category == '0':
					FN_dict['True Negatives'].append(word)
				if word_category == '1':
					FN_dict['True Positives'].append(word)
				if word_category == '2':
					FN_dict['False Positives'].append(word)
				if word_category == 'n':
					FN_dict['Name FN'].append(word)
					print(word, phi_context)
				if word_category == 'l':
					FN_dict['Location FN'].append(word)
					print(word, phi_context)
				if word_category == 'd':
					FN_dict['Date FN'].append(word)
					print(word, phi_context)
				if word_category == 'c':
					FN_dict['Contact FN'].append(word)
					print(word, phi_context)
				if word_category == 'i':
					FN_dict['ID FN'].append(word)
					print(word, phi_context)
				if word_category == 'a':
					FN_dict['Age FN'].append(word)
					print(word, phi_context)
				if word_category == 'o':
					FN_dict['Other FN'].append(word)
					print(word, phi_context)		        

	return FN_dict

def main():
	summary_path = input("where is summary?>")
	with open(summary_path, 'rb') as fin:
		summary = pickle.load(fin)
	anno_path = input("where are annotations?>")
	FN_dict = getcategory(summary, anno_path)

	with open('FN_dict.json', 'w') as fout:
		json.dump(FN_dict, fout)


if __name__ == "__main__":
	main()
			






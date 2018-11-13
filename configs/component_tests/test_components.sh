# Exclude regex
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_exclude_regex_only.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/exclude_regex_only/ -c /data/muenzenk/component_tests/exclude_regex_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/exclude_regex_only/ > /data/muenzenk/component_tests/exclude_regex_only_results.txt 2>&1 &

# Names blacklist
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_names_blacklist_only.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/names_blacklist_only/ -c /data/muenzenk/component_tests/names_blacklist_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/names_blacklist_only/ > /data/muenzenk/component_tests/names_blacklist_only_results.txt 2>&1 &


# Address Blacklist
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_address_blacklist_only.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/address_blacklist_only/ -c /data/muenzenk/component_tests/address_blacklist_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/address_blacklist_only/ > /data/muenzenk/component_tests/address_blacklist_only_results.txt 2>&1 &


# Whitelist
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_whitelist_only.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/whitelist_only/ -c /data/muenzenk/component_tests/whitelist_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/whitelist_only/ > /data/muenzenk/component_tests/whitelist_only_results.txt 2>&1 &


# Exclude regex + names blacklist
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_ER_NB.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/ER_NB_only/ -c /data/muenzenk/component_tests/ER_NB_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/ER_NB_only/ > /data/muenzenk/component_tests/ER_NB_only_results.txt 2>&1 &


# Exclude regex + names blacklist + address blacklist
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_ER_NB_AB.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/ER_NB_AB_only/ -c /data/muenzenk/component_tests/ER_NB_AB_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/ER_NB_AB_only/ > /data/muenzenk/component_tests/ER_NB_AB_only_results.txt 2>&1 &


# Exclude regex + names blacklist + address blacklist + whitelist
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_ER_NB_AB_WL.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/ER_NB_AB_WL_only/ -c /data/muenzenk/component_tests/ER_NB_AB_WL_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/ER_NB_AB_WL_only/ > /data/muenzenk/component_tests/ER_NB_AB_WL_only_results.txt 2>&1 &


# Exclude regex + names blacklist + address blacklist + whitelist + initials regex
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_ER_NB_AB_WL_IR.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/ER_NB_AB_WL_IR_only/ -c /data/muenzenk/component_tests/ER_NB_AB_WL_IR_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/ER_NB_AB_WL_IR_only/ > /data/muenzenk/component_tests/ER_NB_AB_WL_IR_only_results.txt 2>&1 &


# Exclude regex + names blacklist + address blacklist + whitelist + initials regex + safe regex
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_ER_NB_AB_WL_IR_SR.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/ER_NB_AB_WL_IR_SR_only/ -c /data/muenzenk/component_tests/ER_NB_AB_WL_IR_SR_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/ER_NB_AB_WL_IR_SR_only/ > /data/muenzenk/component_tests/ER_NB_AB_WL_IR_SR_only_results.txt 2>&1 &


# Exclude regex + names blacklist + address blacklist + whitelist + initials regex + safe regex + extra whitelists
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_ER_NB_AB_WL_IR_SR_EW.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/ER_NB_AB_WL_IR_SR_EW_only/ -c /data/muenzenk/component_tests/ER_NB_AB_WL_IR_SR_EW_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/ER_NB_AB_WL_IR_SR_EW_only/ > /data/muenzenk/component_tests/ER_NB_AB_WL_IR_SR_EW_only_results.txt 2>&1 &






# Exclude regex + names blacklist + whitelist + initials regex + safe regex
nohup python3 main.py -f /data/muenzenk/de-id_stable1/configs/component_tests/philter_gamma_ER_NB_WL_IR_SR.json -a /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_anno/ -x /data/muenzenk/batch_data/combined_102_110_r1_r2/phi_notes_b102b110r1r2.json -i /data/muenzenk/batch_data/combined_102_110_r1_r2/ucsf_notes/ -o /data/muenzenk/component_tests/ER_NB_WL_IR_SR_only/ -c /data/muenzenk/component_tests/ER_NB_WL_IR_SR_only/coordinates.json --ucsfformat True --stanfordner /data/muenzenk/stanford-ner/ --eval_output /data/muenzenk/component_tests/ER_NB_WL_IR_SR_only/ > /data/muenzenk/component_tests/ER_NB_WL_IR_SR_only_results.txt 2>&1 &

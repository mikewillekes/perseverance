from config import config
from dossier import load_gpt_cleaned_diagnoses, load_dossiers
from icd import load_icd_entities_generator
import numpy as np


# print("\n\nIs Probable")
# print('============================')
# for diagnosis in load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE):
#     if diagnosis.is_probable and diagnosis.clean_field_diagnosis_french:
#         print(f'{diagnosis.raw_field_diagnosis_french} > {diagnosis.clean_field_diagnosis_french}')

# print("\n\nTo Eliminate")
# print('============================')
# for diagnosis in load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE):
#     if diagnosis.to_eliminate and diagnosis.clean_field_diagnosis_french:
#         print(f'{diagnosis.raw_field_diagnosis_french} > {diagnosis.clean_field_diagnosis_french}')

# print("\n\nTo Investigate")
# print('============================')
# for diagnosis in load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE):
#     if diagnosis.to_investigate and diagnosis.clean_field_diagnosis_french:
#         print(f'{diagnosis.raw_field_diagnosis_french} > {diagnosis.clean_field_diagnosis_french}')

# print("\n\nShorthand")
# print('============================')
# for diagnosis in load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE):
#     if diagnosis.shorthand and diagnosis.clean_field_diagnosis_french:
#         print(f'"{diagnosis.shorthand}","{diagnosis.raw_field_diagnosis_french}","{diagnosis.clean_field_diagnosis_french}"')


# print("\n\nLongest Diagnosis")
# print('============================')
# dossiers = load_dossiers(config.DOSSIERS_FILE)
# print(f'Dossiers: {len(dossiers)}')
# longest_diagnosis_record = max(dossiers, key=lambda x: len(x.clean_diagnosis))
# print(f'Longest Diagnosis: {len(longest_diagnosis_record.clean_diagnosis)} {longest_diagnosis_record.clean_diagnosis}')

print("\n\nAll Cleaned Diagnoses")
print('============================')

# Load GPT Cleaned Diagnosis
cleaned_diagnosis = [d for d in load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE)] 

# Create diagnosis lookup index
diagnosis_lookup_by_clean = {diag.clean_field_diagnosis_french: diag for diag in cleaned_diagnosis}

unique_diagnosis = list(diagnosis_lookup_by_clean.keys())
unique_diagnosis.sort()

for diagnosis in unique_diagnosis:
    print(f'{diagnosis}\t{diagnosis_lookup_by_clean[diagnosis].clean_field_diagnosis_english}')
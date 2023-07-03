from config import config
from dossier import load_gpt_cleaned_diagnoses
from icd import load_icd_entities_generator

from collections import defaultdict

# First - Collect embeddings for Field Diagnoses
unique_gpt_cleaned_diagnoses = []

for diagnosis in load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE):
    if diagnosis.clean_field_diagnosis_french and diagnosis.embeddings:
        unique_gpt_cleaned_diagnoses.append(diagnosis.clean_field_diagnosis_french)


unique_gpt_cleaned_diagnoses = list(set(unique_gpt_cleaned_diagnoses))
unique_gpt_cleaned_diagnoses.sort()

for d in unique_gpt_cleaned_diagnoses:
    print(d)

print(f'Unique Diagnoses: {len(unique_gpt_cleaned_diagnoses)}')
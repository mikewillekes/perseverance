from config import config
from config import columns

from dossier import load_gpt_cleaned_diagnoses, load_gpt_cleaned_prescriptions, load_dossiers, Dossier, GPTCleanedDiagnosis
import numpy as np
from typing import List
import pandas as pd

# Load Dossiers
dossiers = load_dossiers(config.DOSSIERS_FILE)

# Load GPT Cleaned Prescriptions
cleaned_prescriptions = [p for p in load_gpt_cleaned_prescriptions(config.GPT_CLEANED_PRESCRIPTIONS_FILE)]

# Create a prescription index
prescription_lookup = {(p.patient_id, p.raw_prescription): p.medication for p in cleaned_prescriptions}

# Load GPT Cleaned Diagnosis
cleaned_diagnosis = [d for d in load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE)] 

# Create diagnosis lookup index
diagnosis_lookup_by_raw = {diag.raw_field_diagnosis_french: diag for diag in cleaned_diagnosis}
diagnosis_lookup_by_clean = {diag.clean_field_diagnosis_french: diag for diag in cleaned_diagnosis}

# Manually correct / override two errors that the LLM seems to have introduced
# 'inappetence' and 'fievre typhoide' are *NOT* in GPT cleaned diagnosis, even through they're
# in the source dossier file. We think the LLM didn't leave these raw fields alone
diagnosis_lookup_by_raw['inappetence'] = diagnosis_lookup_by_raw['ianppetence']
diagnosis_lookup_by_raw['fievre typhoide'] = diagnosis_lookup_by_raw['fievre tyfoide']

# Copy the corresponding cleaned diagnosis into the Dossier
for dossier in dossiers:
    for diagnosis in dossier.clean_diagnosis:

        if diagnosis in diagnosis_lookup_by_raw:
            dossier.gpt_cleaned_diagnosis.append(diagnosis_lookup_by_raw[diagnosis])
        
        elif diagnosis in diagnosis_lookup_by_clean:
            dossier.gpt_cleaned_diagnosis.append(diagnosis_lookup_by_clean[diagnosis])

        else:
            print(f'{diagnosis} not found from dossier {dossier.id}')


longest_diagnosis_record = max(dossiers, key=lambda x: len(x.clean_diagnosis))
max_diagnosis_len = len(longest_diagnosis_record.clean_diagnosis)

longest_prescription_record = max(dossiers, key=lambda x: len(x.clean_prescription))
max_prescription_len = len(longest_diagnosis_record.clean_prescription)

def flatten_dossier(dossier: Dossier) -> dict:
    flat_data = {
        columns.ID_COL: dossier.id,
        columns.SYMPTOMS_COL: dossier.raw_symptoms,
        columns.DIAGNOSIS_COL: dossier.raw_diagnosis,
        columns.PRESCRIPTION_COL: dossier.raw_prescription
    }

    #
    # Pandas will be smart enough to explicitly dynamically expand columns based
    # as the number of diagnoses grow, but I want to be very explicit about the 
    # ordering
    #

    for i in range(0, max_diagnosis_len):

        if i < len(dossier.clean_diagnosis):
            prefix = f'gpt_cleaned_diagnosis_{i}_'
            
            flat_data[f'standard_cleaned_diagnosis_{i}'] = dossier.clean_diagnosis[i]

            flat_data[prefix + 'french'] = dossier.gpt_cleaned_diagnosis[i].clean_field_diagnosis_french
            flat_data[prefix + 'english'] = dossier.gpt_cleaned_diagnosis[i].clean_field_diagnosis_english
            flat_data[prefix + 'shorthand'] = dossier.gpt_cleaned_diagnosis[i].shorthand
            flat_data[prefix + 'is_probable'] = dossier.gpt_cleaned_diagnosis[i].is_probable
            flat_data[prefix + 'to_investigate'] = dossier.gpt_cleaned_diagnosis[i].to_investigate
            flat_data[prefix + 'to_eliminate'] = dossier.gpt_cleaned_diagnosis[i].to_eliminate

        else:
            prefix = f'gpt_cleaned_diagnosis_{i}_'
            
            flat_data[f'standard_cleaned_diagnosis_{i}'] = ''

            flat_data[prefix + 'french'] = ''
            flat_data[prefix + 'english'] = ''
            flat_data[prefix + 'shorthand'] = ''
            flat_data[prefix + 'is_probable'] = ''
            flat_data[prefix + 'to_investigate'] = ''
            flat_data[prefix + 'to_eliminate'] = ''


    for i in range(0, max_prescription_len):

        if i < len(dossier.clean_prescription):
            prefix = f'gpt_cleaned_medication_{i}_'

            if (str(dossier.id), dossier.clean_prescription[i]) in prescription_lookup:
                flat_data[prefix + 'french'] = prescription_lookup[(str(dossier.id), dossier.clean_prescription[i])]
            else:
                flat_data[prefix + 'french'] = dossier.clean_prescription[i]

        else:
            prefix = f'gpt_cleaned_medication_{i}_'
            flat_data[prefix + 'french'] = ''

    return flat_data

# Flatten the data and create a DataFrame
flattened_data = [flatten_dossier(dossier) for dossier in dossiers]
df = pd.DataFrame(flattened_data)

print(df.head(10))
print(df.columns)
#df.head(100).to_excel('data/EXPORT.xlsx', index=False, engine='openpyxl')

df.to_excel('data/EXPORT.xlsx', index=False, engine='openpyxl')

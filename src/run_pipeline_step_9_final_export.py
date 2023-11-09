import json
from config import config
from config import columns

from dossier import load_gpt_cleaned_diagnoses, load_gpt_cleaned_prescriptions, load_dossiers, Dossier, GPTCleanedDiagnosis
import numpy as np
from typing import List
import pandas as pd
import unicodedata


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

# Manually correct / override subtle errors that the LLM seems to have introduced
# ie. 'inappetence' and 'fievre typhoide' are *NOT* in GPT cleaned diagnosis, even through they're
# in the source dossier file.
# 
# We think the LLM made changes to the RAW field, even though the prompt explicitly instructed 
# the LLM to 'pass-thru' this RAW field value 
diagnosis_lookup_by_raw['inappetence'] = diagnosis_lookup_by_raw['ianppetence']
diagnosis_lookup_by_raw['fievre typhoide'] = diagnosis_lookup_by_raw['fievre tyfoide']
diagnosis_lookup_by_raw['diarrhee aigu'] = diagnosis_lookup_by_raw['diarrhee aigue']

# Copy the corresponding cleaned diagnosis into the Dossier
for dossier in dossiers:
    for diagnosis in dossier.clean_diagnosis:

        if diagnosis in diagnosis_lookup_by_raw:
            dossier.gpt_cleaned_diagnosis.append(diagnosis_lookup_by_raw[diagnosis])
        
        elif diagnosis in diagnosis_lookup_by_clean:
            dossier.gpt_cleaned_diagnosis.append(diagnosis_lookup_by_clean[diagnosis])

        else:
            print(f'{diagnosis} not found from dossier {dossier.id}')

#
# We now have a Dossier list with GPT cleaned Diagnoses and GPT Cleaned prescriptions merged in!
#

# Load Post-hoc Cleanup file.  This spreadsheet is to manually correct two failure scenarios:
#  1. Diagnosis field actually contains a prescription
#  2. Diagnosis field contains multiple diagnoses 
posthoc_cleanup_df = pd.read_excel(config.POST_HOC_CLEANUP_FILE)
filtered_posthoc_cleanup_df = posthoc_cleanup_df[
                                posthoc_cleanup_df['medication_french'].notna() |   
                                posthoc_cleanup_df['corrected_comma_delimited_diagnosis_french'].notna() |   
                                posthoc_cleanup_df['corrected_comma_delimited_diagnosis_english'].notna()]

filtered_posthoc_cleanup_df = filtered_posthoc_cleanup_df.copy()

#print(filtered_posthoc_cleanup_df.head(10))

# We need to do some manual correcting.

for dossier in dossiers:
    
    posthoc_standard_cleaned_diagnosis = []
    posthoc_gpt_cleaned_diagnosis = []
    posthoc_cleaned_prescriptions = []
    count = 0

    # Each dossier can have multiple diagnoses
    for standard_cleaned_diagnosis, gpt_cleaned_diagnosis in zip(dossier.clean_diagnosis, dossier.gpt_cleaned_diagnosis):
        matching_row = filtered_posthoc_cleanup_df.loc[filtered_posthoc_cleanup_df['french_diagnosis'] == gpt_cleaned_diagnosis.clean_field_diagnosis_french]
        if matching_row.empty:
            # No cleanup needed for this diagnosis
            posthoc_gpt_cleaned_diagnosis.append(gpt_cleaned_diagnosis)
            posthoc_standard_cleaned_diagnosis.append(standard_cleaned_diagnosis)

        else:
            # The diagnosis has to be manually cleaned-up from our 'post-hoc cleanup' file
            count = count + 1

            if matching_row['corrected_comma_delimited_diagnosis_french'].any() and matching_row['corrected_comma_delimited_diagnosis_english'].any():
                # A single diagnosis string (i.e. "abcès dentaire, gastrite") actually represents 2 or more diagnoses
                for f, e in zip(
                    matching_row['corrected_comma_delimited_diagnosis_french'].iloc[0].split(','),
                    matching_row['corrected_comma_delimited_diagnosis_english'].iloc[0].split(',')):

                    posthoc_gpt_cleaned_diagnosis.append(GPTCleanedDiagnosis(
                        raw_field_diagnosis_french = gpt_cleaned_diagnosis.raw_field_diagnosis_french,
                        clean_field_diagnosis_french = f.strip(),
                        clean_field_diagnosis_english = e.strip(),
                        shorthand = gpt_cleaned_diagnosis.shorthand,
                        is_probable = gpt_cleaned_diagnosis.is_probable,
                        to_investigate = gpt_cleaned_diagnosis.to_investigate,
                        to_eliminate = gpt_cleaned_diagnosis.to_eliminate
                    ))

                    posthoc_standard_cleaned_diagnosis.append(standard_cleaned_diagnosis)
            
            if matching_row['medication_french'].any():

                # Some string cleanup to match how Prescriptions are captured by GPT 
                prescription = matching_row['medication_french'].iloc[0]

                # Capitalize first letter
                prescription = prescription.capitalize()

                # fold unicode to ascii
                prescription = ''.join(char for char in unicodedata.normalize('NFD', prescription) if unicodedata.category(char) != 'Mn')

                posthoc_cleaned_prescriptions.append(prescription)

                
    if count > 0:
        print(f'\n======\n{dossier.id}')
        for d in dossier.gpt_cleaned_diagnosis:
            print(f'ORIG: {d}')
        for d in posthoc_gpt_cleaned_diagnosis:
            print(f'NEW:  {d}')
        for p in posthoc_cleaned_prescriptions:
            print(f'NEW:  {p}')
        
        # There was at least one post-hoc cleanup record, 
        # adjust the original Dossier record
        dossier.clean_diagnosis = posthoc_standard_cleaned_diagnosis
        dossier.gpt_cleaned_diagnosis = posthoc_gpt_cleaned_diagnosis

        # in the rare cases where the original dossier had no prescriptions
        # the list will have one empty element. If we extend after that
        # empty element, the positioning in the final dataset will be off-by-one.
        if posthoc_cleaned_prescriptions:
            dossier.clean_prescription = [s for s in dossier.clean_prescription if s]
            dossier.clean_prescription.extend(posthoc_cleaned_prescriptions)
            dossier.clean_prescription = list(set(dossier.clean_prescription))

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

# Copy some columns from the source dataset into the destination
original_raw_df = pd.read_excel(config.DATA_FILE)

df.insert(1, value=original_raw_df['Date'], column='Date')
df.insert(2, value=original_raw_df['_1INFORMATIONSGÉNÉRALES_Département'], column='_1INFORMATIONSGÉNÉRALES_Département')
df.insert(3, value=original_raw_df['_1INFORMATIONSGÉNÉRALES_Commune2_Label'], column='_1INFORMATIONSGÉNÉRALES_Commune2_Label')
df.insert(4, value=original_raw_df['_1INFORMATIONSGÉNÉRALES_ÂgeenAnnée'], column='Dat_1INFORMATIONSGÉNÉRALES_ÂgeenAnnéee')
df.insert(5, value=original_raw_df['_1INFORMATIONSGÉNÉRALES_ÂgeenMois'], column='_1INFORMATIONSGÉNÉRALES_ÂgeenMois')
df.insert(6, value=original_raw_df['_1INFORMATIONSGÉNÉRALES_Sexe'], column='_1INFORMATIONSGÉNÉRALES_Sexe')

print(df.head(10))
print(df.columns)
#df.head(100).to_excel('data/EXPORT.xlsx', index=False, engine='openpyxl')

df.to_excel('data/EXPORT.xlsx', index=False, engine='openpyxl')

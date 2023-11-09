import pandas as pd
from datetime import datetime
import string
import re
import unicodedata

from config import config
from config import columns
from dossier import Dossier, save_dossiers

# Load .xlsx into the dataframe
raw_df = pd.read_excel(config.DATA_FILE)

# filter to only the columns we care about
df = raw_df[[columns.ID_COL, 
             columns.SYMPTOMS_COL,
             columns.DIAGNOSIS_COL,
             columns.PRESCRIPTION_COL]].copy()

# fill in NaNs with empty strings
df[columns.SYMPTOMS_COL].fillna('', inplace=True)
df[columns.DIAGNOSIS_COL].fillna('', inplace=True)
df[columns.PRESCRIPTION_COL].fillna('', inplace=True)

# Load the CSV file of manually corrected overrides
manually_corrected_df = pd.read_csv(config.MANUALLY_CORRECTED_FILE)
manually_corrected_df['MP_raw_diagnosis'].fillna('', inplace=True)

def normalize_diagnosis(raw_diagnosis):
    # the input column may contain multiple entries separated
    # by a newline. Gather all values into a new list
    diagnosis = raw_diagnosis.split('\n')

    # replace all punctuation with whitespace
    diagnosis = [''.join(char if char not in string.punctuation else ' ' for char in value) for value in diagnosis]

    # strip leading and trailing whitespace
    diagnosis = [value.strip() for value in diagnosis]

    # lowercase
    diagnosis = [value.lower() for value in diagnosis]

    # remove empty records
    diagnosis = [value for value in diagnosis if value]

    # normalize whitespace
    diagnosis = [' '.join(value.split()) for value in diagnosis]

    # fold unicode to ascii
    diagnosis = [''.join(char for char in unicodedata.normalize('NFD', value) if unicodedata.category(char) != 'Mn') for value in diagnosis]

    return diagnosis


def normalize_symptoms(raw_symptoms):
    # the input column may contain multiple entries separated
    # by a newline. Gather all values into a new list
    symptoms = raw_symptoms.split('\n')
    return symptoms


def normalize_prescription(raw_prescription):
    # the input column may contain multiple entries separated
    # by a newline. Gather all values into a new list
    prescription = raw_prescription.split('\n')
    return prescription


dossiers = []

for index, row in df.iterrows():

    dossier = Dossier(
                id=row[columns.ID_COL],
                raw_symptoms=row[columns.SYMPTOMS_COL],
                raw_diagnosis=row[columns.DIAGNOSIS_COL],
                raw_prescription=row[columns.PRESCRIPTION_COL],
                manual_diagnosis_overrides=[],
                clean_symptoms=normalize_symptoms(row[columns.SYMPTOMS_COL]),
                clean_diagnosis=normalize_diagnosis(row[columns.DIAGNOSIS_COL]),
                clean_prescription=normalize_prescription(row[columns.PRESCRIPTION_COL]),
                gpt_cleaned_diagnosis=[])

    #
    # The Manual Diagnosis over-rides is read-in from a Spreadsheet.
    # 
    # We did a first-pass of the end to end pipeline and identified ~400 
    # unique diagnoses values where the LLM could not make sense of the 
    # medical shorthand:
    #
    #   'original_diagnosis' --->  'new_manually_corrected_diagnosis'
    #   'hbp a investigue'   --->  'hyperplasie bénigne de la prostate a investigue'   
    # 
    # Because a field record can have multiple recorded diagnoses (Clinical Impression) values,
    # it's not a simple find and replace.  
    #
    for original_diagnosis in dossier.clean_diagnosis:
        
        matching_df = manually_corrected_df.loc[manually_corrected_df['raw_diagnosis'] == original_diagnosis]
        if matching_df.empty:
            # there is no manual correction for this diagnosis
            dossier.manual_diagnosis_overrides.append('')

        else:

            # there is a manual correction for this diagnosis;
            # clean the text using the same process as the raw incoming value,
            # and record it in the overrides list
            override = matching_df.iloc[0]['MP_raw_diagnosis']
            if override:
                dossier.manual_diagnosis_overrides.append(normalize_diagnosis(override)[0])
            else:
                # Override could be an empty string if manual annotators were unable to correct it
                dossier.manual_diagnosis_overrides.append('')

    
    # we now have two lists like this:
    #   clean_list = ['duck', 'cow', 'sheep', 'dog']
    #   override_list = ['goose', '', '', '']
    #
    # where override_list has a non-empty entry if it overrides the corresponding value from clean_list.
    # 
    # Zip the two lists together:
    #    clean_list = ['goose', 'cow', 'sheep', 'dog']
    
    dossier.clean_diagnosis = [override if override else cleaned for cleaned, override in zip(dossier.clean_diagnosis, dossier.manual_diagnosis_overrides)]

    dossiers.append(dossier)

save_dossiers(config.DOSSIERS_FILE, dossiers)

# Some summary info

print(f'Total records {len(dossiers)}')

dossiers_with_overrides = [dossier for dossier in dossiers if len([override for override in dossier.manual_diagnosis_overrides if override])]
print(f'Count of records with at least one manually-corrected diagnosis: {len(dossiers_with_overrides)}')

unique_diagnosis = list(set([d for dossier in dossiers for d in dossier.clean_diagnosis]))
unique_diagnosis.sort()
# for d in unique_diagnosis:
#     print(d)
print(f'Unique diagnosis values: {len(unique_diagnosis)}')



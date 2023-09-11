import pandas as pd
from datetime import datetime
import string
import re
import unicodedata

from config import config
from config import columns
from dossier import Dossier


#
# Count the number of unique diagnoses in the source data.
#

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

def normalize_diagnosis(raw_diagnosis):
    # the input column may contain multiple entries separated
    # by a newline. Gather all values into a new list
    diagnosis = raw_diagnosis.split('\n')

    # Only "Clean up" we do here is lowercase.
    diagnosis = [value.lower() for value in diagnosis]

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


# For fun, count the raw number of unique diagnosis fields with now cleaning
raw_diagnosis_values = set()
for index, row in df.iterrows():
    raw_diagnosis_values.add(row[columns.DIAGNOSIS_COL])

raw_prescription_values = set()
for index, row in df.iterrows():
    raw_prescription_values.add(row[columns.PRESCRIPTION_COL])


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

    dossiers.append(dossier)

unique_diagnosis = list(set([d for dossier in dossiers for d in dossier.clean_diagnosis]))
unique_diagnosis.sort()

for d in unique_diagnosis:
    print(d)

print(f'Total records {len(dossiers)}')
print(f'Raw Diagnoses: {len(raw_diagnosis_values)}')
print(f'Unique Diagnoses: {len(unique_diagnosis)}')
print(f'Raw Prescriptions: {len(raw_prescription_values)}')

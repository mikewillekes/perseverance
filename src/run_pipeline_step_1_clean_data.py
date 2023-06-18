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
             columns.DATE_COL,
             columns.SYMPTOMS_COL,
             columns.DIAGNOSIS_COL]].copy()

# fill in NaNs with empty strings
df[columns.SYMPTOMS_COL].fillna('', inplace=True)
df[columns.DIAGNOSIS_COL].fillna('', inplace=True)


def normalize_diagnosis(raw_diagnosis):
    # the input column may contain multiple entries separated
    # by a newline. Gather all values into a new list
    diagnosis = raw_diagnosis.split('\n')
    return diagnosis


def normalize_symptoms(raw_symptoms):
    # the input column may contain multiple entries separated
    # by a newline. Gather all values into a new list
    symptoms = raw_symptoms.split('\n')
    return symptoms


dossiers = []

for index, row in df.iterrows():
    dossiers.append(
            Dossier(
                id=row[columns.ID_COL],
                date=row[columns.DATE_COL].to_pydatetime(),
                raw_symptoms=row[columns.SYMPTOMS_COL],
                raw_diagnosis=row[columns.DIAGNOSIS_COL],
                symptoms=normalize_symptoms(row[columns.SYMPTOMS_COL]),
                diagnosis=normalize_diagnosis(row[columns.DIAGNOSIS_COL])
                ))


save_dossiers('data/dossiers.jsonl', dossiers)



 #               date=datetime.strptime(row[columns.DATE_COL], '%d/%m/%Y'),

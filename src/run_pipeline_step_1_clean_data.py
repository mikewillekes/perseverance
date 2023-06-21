import pandas as pd
from datetime import datetime
import string
import re
import unicodedata

from thefuzz import fuzz
from thefuzz import process

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


def remove_a_invest(s):
    """Removes words starting with 'a invest' from a string."""
    return re.sub(r'\ba invest\w*\b', '', s).strip()


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

    # Remove all instances of 'a investigue' or 'a investiguer' (and variations)
    # because there are many diagnosis entries that are "anemia to be investigated" etc.
    diagnosis = [remove_a_invest(value) for value in diagnosis]

    # sort
    diagnosis.sort()

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

unique_diagnosis = list(set([d for dossier in dossiers for d in dossier.diagnosis]))
unique_diagnosis.sort()
for d in unique_diagnosis:
    print(d)
print(len(unique_diagnosis))

import pandas as pd
from datetime import datetime
import string
import re
import unicodedata

from thefuzz import fuzz
from thefuzz import process

from config import config
from config import columns
from dossier import Dossier, load_dossiers

dossiers = load_dossiers('data/dossiers.jsonl')

print(len(dossiers))

# unique_diagnosis = list(set([d for dossier in dossiers for d in dossier.diagnosis]))
# unique_diagnosis.sort()
# for d in unique_diagnosis:
#     print(d)
# print(len(unique_diagnosis))


# =================================

def group_strings(strings, threshold=90):
    """Groups strings based on their fuzzy match score.

    Parameters:
    strings (List[str]): The list of strings to be grouped.
    threshold (int): The score above which matches should be considered. Default is 90.

    Returns:
    Dict[str, List[str]]: A dictionary where the keys are canonical strings
        and the values are lists of the strings that were matched to them.
    """
    groups = []
    for string in strings:
        found = False
    
        # All these nested for loops... Not efficient at scale
        # (On^2) but fine for just a few thousand entries
        for group in groups:
            
            for existing in group:
                if fuzz.token_sort_ratio(string, existing) > threshold:
                    group.append(string)
                    found = True
                    break
            
            if found:
                break
    
        if not found:
            # String did not match within threshold against
            # any existing string in any group. Make a new
            # group with just this new String
            groups.append([string])
    
    return groups


unique_diagnosis = list(set([d for dossier in dossiers for d in dossier.diagnosis]))
unique_diagnosis.sort()

# Threshold of ~70 seems to group French medical conditions well 
groups = group_strings(unique_diagnosis, threshold=70)
sorted_groups = list(sorted(groups, key = len))

for group in sorted_groups:
    print(f'{len(group)}\t{", ".join(group)}')

print(len(sorted_groups))

import pandas as pd
from collections import defaultdict

from config import config
from icd import ICDEntity, save_icd_entities

def clean_title(t):
    # ICD Titles from the Linearization spreadsheet
    # have an implied hierarchy like this
    #
    #    - Parasitic diseases
    #    - - Malaria
    #    - - Nonintestinal protozoal diseases
    #
    # We're going to reconstruct that hierarchy in another
    # way, so strip the leading dashes and whitespace
    return t.lstrip('- ')   


# Load .xlsx into the dataframe
raw_df = pd.read_excel(config.ICD_LINEARIZATION_FILE)
df = raw_df.fillna('')

# Iterate through the dataframe and grab BlockId and Title to use as
# key and value in a Dictionary
blocks = defaultdict(str)


for index, row in df.iterrows():
    block = row['BlockId']
    if block:
        title = clean_title(row['Title'])
        blocks[block] = title


# 
# Now, build up a list of ICD-11 entries that we'll for embedding
#
entities = []
for index, row in df.iterrows():

    code = row['Code']
    # Exclude:
    #    V  'Supplementary sections for functioning assessment'
    #    X  'Extension codes'
    if not code or code.startswith(('V','X')):
        continue

    # Up to 5 levels of Grouping, identified by
    # reference to "BlockXXXX" in columns Grouping1..Grouping5
    grouping = ''
    grouping_depth = 0
    
    g1 = row['Grouping1']
    if g1:
        grouping = blocks[g1]
        grouping_depth = 1

    g2 = row['Grouping2']
    if g2:
        grouping = grouping + ' > ' + blocks[g2]
        grouping_depth = 2

    g3 = row['Grouping3']
    if g3:
        grouping = grouping + ' > ' + blocks[g3]
        grouping_depth = 3

    g4 = row['Grouping4']
    if g4:
        grouping = grouping + ' > ' + blocks[g4]
        grouping_depth = 4

    g5 = row['Grouping5']
    if g5:
        grouping = grouping + ' > ' + blocks[g5]
        grouping_depth = 5

    entities.append(
            ICDEntity(
                code=code,
                title=clean_title(row['Title']),
                grouping_depth=grouping_depth,
                is_leaf=row['isLeaf'],
                grouping=grouping,
                embeddings=[]
                ))


save_icd_entities(config.ICD_ENTITIES_FILE, entities)


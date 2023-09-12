import os
import json
import re
from collections import defaultdict
import time

from config import config
from config import columns
from dossier import Dossier, load_dossiers, GPTCleanedDiagnosis, save_gpt_cleaned_diagnoses
from serde.json import from_json

from langchain.llms import OpenAI
llm = OpenAI(model_name='gpt-4',
             temperature=0.3,
             max_tokens=2500,
             openai_api_key=os.getenv("OPENAI_API_KEY"))

#
# Print out some summary stats about the previous pipeline stages
#
dossiers = load_dossiers(config.DOSSIERS_FILE)
print(f'Dossiers: {len(dossiers)}')

unique_diagnoses = list(set([d for dossier in dossiers for d in dossier.clean_diagnosis]))
unique_diagnoses.sort()
print(f'Unique Diagnoses: {len(unique_diagnoses)}')

def build_prompt(diagnoses):
     # Very naive templating using %%SOME_STRING%% 
    with open('prompts/clean_diagnosis.txt', 'r') as fin:
        content = fin.read()

        values = '\n'.join(['\t' + d for d in diagnoses])
        return content.replace('%%DIAGNOSIS%%' , values)

#
# Iterate through the diagnosis list in chunks, using OpenAI to clean
# and normalize each diagnosis
#
CHUNK_SIZE = 10
for i in range(0, len(unique_diagnoses), CHUNK_SIZE):

    time.sleep(0.5)
    chunk = unique_diagnoses[i:i+CHUNK_SIZE]
    prompt = build_prompt(chunk)
    print(f'Chunk [{i+1}..{i+CHUNK_SIZE}]: {", ".join(chunk)}')

    # Call the LLM to complete the prompt
    completion = llm(prompt)

    # Result will be something like this
    # [
    #        {
    #            "raw_field_diagnosis_french": "abces du cuir chevelure",
    #            "clean_field_diagnosis_french": "abcès du cuir chevelu",
    #            "shorthand": "",
    #            "is_probable": false,
    #            "to_investigate": false,
    #            "to_eliminate": false
    #        },
    # ]
    # 
    gpt_cleaned_diagnoses = []

    for item in json.loads(completion):
        diagnosis = from_json(GPTCleanedDiagnosis, json.dumps(item))
        gpt_cleaned_diagnoses.append(diagnosis)

    save_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE, gpt_cleaned_diagnoses)

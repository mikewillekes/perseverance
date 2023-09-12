import os
import json
import re
from collections import defaultdict
import time

from config import config
from config import columns
from dossier import Dossier, load_dossiers, GPTCleanedPrescription, save_gpt_cleaned_prescriptions
from serde.json import from_json

from langchain.llms import OpenAI
llm = OpenAI(model_name='gpt-3.5-turbo',
             temperature=0.3,
             max_tokens=3000,
             openai_api_key=os.getenv("OPENAI_API_KEY"))

#
# Print out some summary stats about the previous pipeline stages
#
dossiers = load_dossiers(config.DOSSIERS_FILE)
print(f'Dossiers: {len(dossiers)}')

unique_prescriptions = list(set([d for dossier in dossiers for d in dossier.clean_prescription]))
unique_prescriptions.sort()
print(f'Unique Prescriptions: {len(unique_prescriptions)}')

def build_prompt(dossiers):
     # Very naive templating using %%SOME_STRING%% 
    with open('prompts/clean_prescription.txt', 'r') as fin:
        content = fin.read()

        values = []
        for dossier in dossiers:
            id = dossier.id
            for prescription in dossier.clean_prescription:
                values.append(f'"{id}", "{prescription}"')
        
        return content.replace('%%PRESCRIPTION%%', '\n'.join(values))

#
# Iterate through the diagnosis list in chunks, using OpenAI to clean
# and normalize each diagnosis
#
CHUNK_SIZE = 10
for i in range(0, len(dossiers), CHUNK_SIZE):

    time.sleep(0.05)
    chunk = dossiers[i:i+CHUNK_SIZE]
    prompt = build_prompt(chunk)
    print(f'Chunk [{i+1}..{i+CHUNK_SIZE}]: {", ".join([str(c.id) for c in chunk])}')

    # Call the LLM to complete the prompt
    completion = llm(prompt)

    # Result will be something like this
    # [
    #     {
    #         "raw_prescription": "Lisinopril 10mg q/j",
    #         "medication": "Lisinopril"
    #     },
    #     {
    #         "raw_prescription": "Amlodipine 10mg q/j",
    #         "medication": "Amlodipine"
    #     },
    #     {
    #         "raw_prescription": "Omeprazol 20mg BID",
    #         "medication": "Omeprazole"
    #     },
    #     {
    #         "raw_prescription": "Amoxicilline 500mg TID",
    #         "medication": "Amoxicillin"
    #     },
    #     {
    #         "raw_prescription": "Metronidazole 500mg TID",
    #         "medication": "Metronidazole"
    #     }
    # ]}
    # 
    gpt_cleaned_prescriptions = []

    for item in json.loads(completion):
        record = from_json(GPTCleanedPrescription, json.dumps(item))
        gpt_cleaned_prescriptions.append(record)

    save_gpt_cleaned_prescriptions(config.GPT_CLEANED_PRESCRIPTIONS_FILE, gpt_cleaned_prescriptions)

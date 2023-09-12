import os
import json
import re
from collections import defaultdict
import time

from config import config
from config import columns
from dossier import Dossier, load_dossiers, save_gpt_cleaned_prescriptions
from serde.json import from_json

from langchain.llms import OpenAI
llm = OpenAI(model_name='gpt-3.5-turbo',
             temperature=1.0,
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

        values = '\n'.join([str(d.clean_prescription) for d in dossiers])
        return content.replace('%%PRESCRIPTION%%' , values)

#
# Iterate through the diagnosis list in chunks, using OpenAI to clean
# and normalize each diagnosis
#
CHUNK_SIZE = 1
for i in range(0, len(dossiers), CHUNK_SIZE):

    time.sleep(0.05)
    chunk = dossiers[i:i+CHUNK_SIZE]
    prompt = build_prompt(chunk)
    print(f'Chunk [{i+1}..{i+CHUNK_SIZE}]: {", ".join([str(c.id) for c in chunk])}')

    # Call the LLM to complete the prompt
    completion = llm(prompt)

    # Result will be something like this
    #   {"prescription": ["Lisinopril", "Amlodipine", "Omeprazole", "Amoxicilline", "Metronidazole"]}
    #   {"prescription": ["Paracetamol", "B complex"]}
    #   {"prescription": ["Amoxicilline", "Paracetamol"]}
    #   {"prescription": ["B complex", "Omeprazole"]}
    #   {"prescription": ["Omeprazole", "Enalapril"]}
    #   {"prescription": ["Augmentin", "Fusigen"]}
    #   {"prescription": ["Paracetamol"]}
    #   {"prescription": ["Prednisone", "Augmentin"]}
    #   {"prescription": ["Paracetamol", "Galocur"]}
    #   {"prescription": ["Amoxicilline", "Metronidazole", "Omeprazole"]}
    #   {"prescription": ["Augmentin", "Brupal"]}
    # 
    gpt_cleaned_prescriptions = []

    for index, item in enumerate(completion.split('\n')):
        
        dossier = chunk[index]
        record = {'id':dossier.id, 'prescription':dossier.clean_prescription, 'gpt_cleaned_prescription':json.loads(item)['prescription']}
        print(record)
        gpt_cleaned_prescriptions.append(json.dumps(record) + '\n')

    save_gpt_cleaned_prescriptions(config.GPT_CLEANED_PRESCRIPTIONS_FILE, gpt_cleaned_prescriptions)

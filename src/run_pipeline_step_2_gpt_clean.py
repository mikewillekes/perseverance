import os
import openai
import json
import re
from collections import defaultdict

from config import config
from config import columns
from dossier import Dossier, load_dossiers, GPTCleanedDiagnosis, save_gpt_cleaned_diagnoses
from serde.json import from_json


openai.api_key = os.getenv("OPENAI_API_KEY")

dossiers = load_dossiers('data/dossiers.jsonl')
print(f'Dossiers: {len(dossiers)}')

unique_diagnoses = list(set([d for dossier in dossiers for d in dossier.diagnoses]))
unique_diagnoses.sort()
print(f'Unique Diagnoses: {len(unique_diagnoses)}')


def build_prompt(diagnoses):
    
    values = '\n'.join(['\t' + d for d in diagnoses])
    
    return f'''You are a French-speaking medical doctor reviewing notes from a community clinic held in a rural community in a resource poor country following an earthquake.
    
Some of the patients seen have afflictions related to the earthquake, but many have visited the clinic simply because there limited other health-care options and this was their opportunity to see a doctor.

The data has been transcribed from hand written notes, so there is a high likelihood of transcription errors and spelling errors. Your goal is to clean the data by correcting these errors.  Here is a collection of "Field Diagnosis" values in French:

{values}

For each input Field Diagnosis, make a correction:

- Correct any likely spelling or transcription error
- If you encounter an acronym or shorthand such as: agu, hta, sd, ic sd; do not modify the term or attempt to expand
- Do not rephrase or expand medical shorthand or acronyms. return your answer in the following JSON format:

Return the answer as JSON in the following format:
[
    {{
        "raw_field_diagnosis_french": "the first Field Diagnosis value in French",
        "clean_field_diagnosis_french": "the first corrected value in French"
    }},
    {{
         "raw_field_diagnosis_french": "the second Field Diagnosis value in French",
        "clean_field_diagnosis_french": "the second corrected value in French"
    }}
]
No preamble. Just return JSON.
'''

#
# Iterate through the diagnosis list in chunks, using OpenAI to clean
# and normalize each diagnosis
#
CHUNK_SIZE = 5
for i in range(0, len(unique_diagnoses), CHUNK_SIZE):

    chunk = unique_diagnoses[i:i+CHUNK_SIZE]
    prompt = build_prompt(chunk)
    print(f'Chunk [{i+1}..{i+CHUNK_SIZE}]: {", ".join(chunk)}')

    # # OpenAI API call (SLOOOOOOOW)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=3000,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )

    # remove the substring "Answer: " from the bigger response string
    answer = response['choices'][0]['text']
    gpt_cleaned_chunk = re.sub(r'^\s*Answer:\s*', '', answer)

    # Result will be something like this
    # [
    #     {
    #         "raw_field_diagnosis_french": "hta de diabete",
    #         "clean_field_diagnosis_french": "Hypertension artérielle du diabète",
    #         "clean_field_diagnosis_english": "Diabetic hypertension",
    #         "reason" : "Expanded acronym HTA (Hypertension Artérielle) to Hypertension Artérielle du diabète"
    #     }
    # ]
    # 
    gpt_cleaned_diagnoses = []

    for item in json.loads(gpt_cleaned_chunk):
        diagnosis = from_json(GPTCleanedDiagnosis, json.dumps(item))
        gpt_cleaned_diagnoses.append(diagnosis)
        
    save_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE, gpt_cleaned_diagnoses)


# map_of_gpt_cleaned_diagnoses = defaultdict(dict)

# # Collect into a map-of-lists so it's easier to match-up with the original dossiers
# for item in json.loads(gpt_cleaned_chunk):
#     key = item['raw_field_diagnosis_french']
#     map_of_gpt_cleaned_diagnoses[key] = item

# for key, value in map_of_gpt_cleaned_diagnoses.items():
#     print('==============================')
#     print(f'Key: {key}')
#     for item in value:
#         print(item)

# unique_gpt_cleaned_diagnoses = list(set([d['clean_field_diagnosis_french'] for d in map_of_gpt_cleaned_diagnoses.values()]))
# unique_gpt_cleaned_diagnoses.sort()

# print(f'Unique Diagnoses: {len(unique_gpt_cleaned_diagnoses)}')
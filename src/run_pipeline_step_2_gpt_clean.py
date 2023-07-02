import os
import json
import re
from collections import defaultdict

from config import config
from config import columns
from dossier import Dossier, load_dossiers, GPTCleanedDiagnosis, save_gpt_cleaned_diagnoses
from serde.json import from_json

from langchain.llms import OpenAI
llm = OpenAI(model_name='text-davinci-003',
             temperature=0.3,
             max_tokens=2000,
             openai_api_key=os.getenv("OPENAI_API_KEY"))


from langchain.embeddings import OpenAIEmbeddings
embed = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

#
# Print out some summary stats about the previous pipeline stages
#
dossiers = load_dossiers(config.DOSSIERS_FILE)
print(f'Dossiers: {len(dossiers)}')

unique_diagnoses = list(set([d for dossier in dossiers for d in dossier.diagnoses]))
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

    chunk = unique_diagnoses[i:i+CHUNK_SIZE]
    prompt = build_prompt(chunk)
    print(f'Chunk [{i+1}..{i+CHUNK_SIZE}]: {", ".join(chunk)}')

    # Call the LLM to complete the prompt
    completion = llm(prompt)

    # # remove the substring "Answer: " from the bigger response string
    # answer = response['choices'][0]['text']
    # gpt_cleaned_chunk = re.sub(r'^\s*Answer:\s*', '', answer)

    # Result will be something like this
    # [
    #        {
    #            "raw_field_diagnosis_french": "abces du cuir chevelure",
    #            "clean_field_diagnosis_french": "abcès du cuir chevelu",
    #            "shorthand": "",
    #            "is_probable": false,
    #            "to_investigate": false,
    #            "to_eliminate": false,
    #            "embeddings": []
    #        },
    # ]
    # 
    gpt_cleaned_diagnoses = []

    for item in json.loads(completion):
        diagnosis = from_json(GPTCleanedDiagnosis, json.dumps(item))

        # Embed the Cleaned Diagnosis (guard against an empty cleaned string)
        if (diagnosis.clean_field_diagnosis_french):
            diagnosis.embeddings = embed.embed_query(diagnosis.clean_field_diagnosis_french)

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
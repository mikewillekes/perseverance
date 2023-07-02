import os
import json
from collections import defaultdict

from config import config
from icd import ICDEntity, load_icd_entities_batch, save_icd_entity

from langchain.embeddings import OpenAIEmbeddings
embed = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

#
# Print out some summary stats about the previous pipeline stages
#
entities = load_icd_entities_batch(config.ICD_ENTITIES_FILE)
print(f'ICD Entities: {len(entities)}')

CHUNK_SIZE = 100
for i in range(0, len(entities), CHUNK_SIZE):

    chunk = entities[i:i+CHUNK_SIZE]
    texts = [c.title for c in chunk]
    print(f'Chunk [{i+1}..{i+CHUNK_SIZE}]: {", ".join([c.code for c in chunk])}')

    # Embed
    chunk_embeddings = embed.embed_documents(texts)

    # Each Nth item in chunk_embeddings corresponds to the 
    # Nth icd entity in that chunk.
    for j in range(0, len(chunk)):
        chunk[j].embeddings = chunk_embeddings[j]
        save_icd_entity(config.ICD_ENTITIES_FILE_EMBEDDING, chunk[j])
    
    if i > 500:
        break

    # embed.e

    #     # Embed the Cleaned Diagnosis (guard against an empty cleaned string)
    #     if (diagnosis.clean_field_diagnosis_french):
    #         diagnosis.embeddings = embed.embed_query(diagnosis.clean_field_diagnosis_french)

    #     gpt_cleaned_diagnoses.append(diagnosis)
        
    # save_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE, gpt_cleaned_diagnoses)


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
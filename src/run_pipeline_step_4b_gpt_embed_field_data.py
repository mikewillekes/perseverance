import os
import json
import re
from collections import defaultdict
import time

from config import config
from config import columns
from dossier import GPTCleanedDiagnosis, DiagnosisEmbedding, load_gpt_cleaned_diagnoses, save_diagnosis_embedding
from serde.json import from_json

from langchain.embeddings import OpenAIEmbeddings
embed = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"), model='text-embedding-ada-002')

#
# Print out some summary stats about the previous pipeline stages
#
diagnoses = load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE)

unique_diagnoses = list(set([d.clean_field_diagnosis_english for d in diagnoses]))
unique_diagnoses.sort()

for d in unique_diagnoses:
    print(d)
print(len(unique_diagnoses))

#
# Iterate through the diagnosis list in chunks, using OpenAI to clean
# and normalize each diagnosis
#
CHUNK_SIZE = 250
for i in range(0, len(unique_diagnoses), CHUNK_SIZE):

    chunk = unique_diagnoses[i:i+CHUNK_SIZE]
    texts = [f'{c}' for c in chunk]
    
    print(f'Chunk [{i+1}..{i+CHUNK_SIZE}]: {", ".join([c for c in chunk])}')

    # Embed
    chunk_embeddings = embed.embed_documents(texts)

    # Each Nth item in chunk_embeddings corresponds to the 
    # Nth diagnosis in that chunk.
    for j in range(0, len(chunk)):
        e = DiagnosisEmbedding(clean_field_diagnosis_english=chunk[j],
                           embedding=chunk_embeddings[j])

        save_diagnosis_embedding(config.DIAGNOSIS_EMBEDDINGS_FILE, e)
import os
import json
from collections import defaultdict

from config import config
from icd import ICDEntity, load_icd_entities_batch, save_icd_entity

from langchain.embeddings import OpenAIEmbeddings
embed = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"), model='text-embedding-ada-002')

#
# Print out some summary stats about the previous pipeline stages
#
entities = load_icd_entities_batch(config.ICD_ENTITIES_FILE)
print(f'ICD Entities: {len(entities)}')

CHUNK_SIZE = 250
for i in range(0, len(entities), CHUNK_SIZE):

    chunk = entities[i:i+CHUNK_SIZE]
    texts = [f'{c.title}' for c in chunk]
    
    print(f'Chunk [{i+1}..{i+CHUNK_SIZE}]: {", ".join([c.code for c in chunk])}')

    # Embed
    chunk_embeddings = embed.embed_documents(texts)

    # Each Nth item in chunk_embeddings corresponds to the 
    # Nth icd entity in that chunk.
    for j in range(0, len(chunk)):
        chunk[j].embeddings = chunk_embeddings[j]
        save_icd_entity(config.ICD_ENTITIES_FILE_EMBEDDING, chunk[j])
    
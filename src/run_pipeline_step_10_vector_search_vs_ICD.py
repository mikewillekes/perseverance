from config import config
from icd import load_icd_entities_generator
import pandas as pd
import numpy as np
import os

from docarray import DocList
from docarray.documents import TextDoc
from docarray.typing import NdArray
from docarray.index import InMemoryExactNNIndex


from langchain.embeddings import OpenAIEmbeddings
embed = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"), model='text-embedding-ada-002')


# Prepare the in-memory nearest neighbor index
class MyDoc(TextDoc):
    embedding: NdArray[1536]

db = InMemoryExactNNIndex[MyDoc]()
docs = DocList[MyDoc]()


# Load the CSV file of unique diagnoses
# NOTE: even though there's already code in place to do this 
# (/perseverance/src/run_pipeline_step_6_vector_search.py)
# we can't rely on the `gpt_cleaned_diagnosis` data file because
# there were last-minute manual corrections applied in the final
# export step.  
# 
# So we must load all unique diagnoses from a CSV extracted from the final 
# export spreadsheet, re-embed and compare with the ICD11 embeddings
df = pd.read_csv(config.UNIQUE_DIAGNOSES_FOR_ICD_MATCHING_FILE, header=None)

#df = df.head(20)
unique_diagnoses = df[0].to_list()

#
# Load ICD 11 embeddings from disk 
#
for entity in load_icd_entities_generator(config.ICD_ENTITIES_FILE_EMBEDDING):

    # In an attempt to be as specific as possible, consider only the 'is_leaf' entities

    if entity.is_leaf:
        docs.append(MyDoc(text=f'{entity.code}: {entity.title}', embedding=np.array(entity.embeddings)))
db.index(docs)

# List of Lists that will be our final dataframe
vector_search_candidates = []

#
# Iterate through the diagnosis list in chunks, using OpenAI to embed the diagnosis
# and then match against the ICD11 embeddings
#
CHUNK_SIZE = 50
for i in range(0, len(unique_diagnoses), CHUNK_SIZE):

    chunk = unique_diagnoses[i:i+CHUNK_SIZE]
    texts = [f'{c}' for c in chunk]
    
    print(f'Chunk [{i+1}..{i+CHUNK_SIZE}]: {", ".join([c for c in chunk])}')

    # Embed
    chunk_embeddings = embed.embed_documents(texts)

    # Each Nth item in chunk_embeddings corresponds to the 
    # Nth diagnosis in that chunk.
    for j in range(0, len(chunk)):

        candidates = []
        
        diagnosis_text = chunk[j]
        diagnosis_embeddings = chunk_embeddings[j]

        # ANN search vs ICD embeddings
        query = MyDoc(text=diagnosis_text, embedding=np.array(diagnosis_embeddings))
        candidates.append(diagnosis_text)
        
        MAX_RESULTS = 10

        matches, scores = db.find(query, search_field='embedding', limit=MAX_RESULTS)

        for i in range(0, len(matches)):
            if scores[i] > 0.8:
                candidates.append(f'{matches[i].text}')

        vector_search_candidates.append(candidates)

# Build the final DF
df = pd.DataFrame(vector_search_candidates)
df.to_excel('data/Vector Search ICD Candidates.xlsx', index=False, engine='openpyxl')





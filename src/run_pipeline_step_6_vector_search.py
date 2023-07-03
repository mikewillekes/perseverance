from config import config
from dossier import load_gpt_cleaned_diagnoses
from icd import load_icd_entities_generator
import numpy as np

from docarray import DocList
from docarray.documents import TextDoc
from docarray.typing import NdArray
from docarray.index import InMemoryExactNNIndex


class MyDoc(TextDoc):
    embedding: NdArray[1536]

db = InMemoryExactNNIndex[MyDoc]()
docs = DocList[MyDoc]()


for entity in load_icd_entities_generator(config.ICD_ENTITIES_FILE_EMBEDDING):
    docs.append(MyDoc(text=f'{entity.code}: {entity.title}', embedding=np.array(entity.embeddings)))
db.index(docs)


for diagnosis in load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE):
    if diagnosis.clean_field_diagnosis_french and diagnosis.embeddings:
        print('============================')
        query = MyDoc(text=diagnosis.clean_field_diagnosis_english, embedding=np.array(diagnosis.embeddings))
        print(f'QUERY: {diagnosis.clean_field_diagnosis_english}')
        
        MAX_RESULTS = 10

        matches, scores = db.find(query, search_field='embedding', limit=MAX_RESULTS)

        for i in range(0, len(matches)):
            print(f'\t{matches[i].text} : {scores[i]}')


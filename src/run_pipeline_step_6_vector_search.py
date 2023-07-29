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
    # Because of the rough field notes, just consider "top level" items like
    #   "code":"1C1D","title":"Yaws"
    # not
    #   "code":"1C1D.0","title":"Primary yaws"
    #   "code":"1C1D.1","title":"Secondary yaws"
    #   "code":"1C1D.2","title":"Tertiary yaws"
    #   "code":"1C1D.3","title":"Latent yaws"
    #
    #if '.' not in entity.code:
    docs.append(MyDoc(text=f'{entity.code}: {entity.title}', embedding=np.array(entity.embeddings)))
db.index(docs)

all_diagnoses = []

for diagnosis in load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE):
    if diagnosis.clean_field_diagnosis_french and diagnosis.embeddings:
        print('============================')
        query = MyDoc(text=diagnosis.clean_field_diagnosis_english, embedding=np.array(diagnosis.embeddings))
        print(f'QUERY: {diagnosis.clean_field_diagnosis_english}')
        
        MAX_RESULTS = 50

        matches, scores = db.find(query, search_field='embedding', limit=MAX_RESULTS)

        for i in range(0, len(matches)):
            if scores[i] > 0.8:
                print(f'\t{matches[i].text} : {scores[i]}')

        all_diagnoses.append(diagnosis.clean_field_diagnosis_english)

unique_diagnoses = list(set(all_diagnoses))
unique_diagnoses.sort()

for d in unique_diagnoses:
    print(d)
print(len(unique_diagnoses))
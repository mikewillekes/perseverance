# =========================
# Raw input documents / spreadsheets
DATA_FILE = 'data/Complete anonymized data set_Pers Project.xlsx'

# Downloaded from https://icd.who.int/browse11/Downloads/Download?fileName=simpletabulation.zip in July 1, 2023
ICD_LINEARIZATION_FILE = 'data/simpletabulation.xlsx'

ICD_ENTITIES_FILE = 'data/icd_entities_text_only.jsonl'
ICD_ENTITIES_FILE_EMBEDDING = 'data/icd_entities_with_embeddings.jsonl'

# Working / intermediate files
DOSSIERS_FILE = 'data/dossiers.jsonl'
GPT_CLEANED_DIAGNOSES_FILE = 'data/gpt_cleaned_diagnoses.jsonl'
DIAGNOSIS_EMBEDDINGS_FILE = 'data/gpt_diagnosis_embeddings.jsonl'

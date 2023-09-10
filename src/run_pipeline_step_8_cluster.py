from config import config
from dossier import load_diagnosis_embeddings_batch

import pandas as pd
import numpy as np
from hdbscan import HDBSCAN

titles = []
embeddings = []

for diagnosis in load_diagnosis_embeddings_batch(config.DIAGNOSIS_EMBEDDINGS_FILE):
    titles.append(diagnosis.clean_field_diagnosis_english)
    embeddings.append(diagnosis.embedding)

hdbscan = HDBSCAN(min_cluster_size=2, min_samples=1)
clusters = hdbscan.fit_predict(embeddings)

for i, cluster in enumerate(clusters):
    print(f"{cluster}\t\t{titles[i]}")
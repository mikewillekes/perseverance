from config import config
from dossier import load_gpt_cleaned_diagnoses

import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
import plotly.express as px


titles = []
embeddings = []

for diagnosis in load_gpt_cleaned_diagnoses(config.GPT_CLEANED_DIAGNOSES_FILE):
    titles.append(diagnosis.clean_field_diagnosis_french)
    embeddings.append(diagnosis.embeddings)

tsne = TSNE(n_components=2, random_state=42)
embeddings_tsne = tsne.fit_transform(np.array(embeddings))

# Create a DataFrame with the t-SNE embeddings and titles
data = {
    'x': embeddings_tsne[:, 0],
    'y': embeddings_tsne[:, 1],
    'title': titles
}
df = pd.DataFrame(data)

# Create an interactive scatter plot with plotly
fig = px.scatter(
    df, x='x', y='y', text='title',
    title="Diagnosis Embeddings"
)

# Customize the plot
fig.update_traces(textposition='top center')
fig.update_layout(
    hovermode='closest',
    xaxis=dict(title='Dimension 1'),
    yaxis=dict(title='Dimension 2')
)

# Show the plot
fig.show()

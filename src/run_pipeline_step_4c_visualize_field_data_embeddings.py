from config import config
from dossier import load_diagnosis_embeddings_batch

import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
import plotly.express as px


titles = []
embeddings = []

for diagnosis in load_diagnosis_embeddings_batch(config.DIAGNOSIS_EMBEDDINGS_FILE):
    titles.append(diagnosis.clean_field_diagnosis_english)
    embeddings.append(diagnosis.embedding)

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

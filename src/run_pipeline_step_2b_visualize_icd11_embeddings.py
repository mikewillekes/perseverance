from config import config
from icd import load_icd_entities_generator, ICDEntity

import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
import plotly.express as px


titles = []
embeddings = []
series = []
hover = []

for entity in load_icd_entities_generator(config.ICD_ENTITIES_FILE_EMBEDDING):
    if entity.grouping_depth == 1:
        titles.append(entity.code)
        embeddings.append(entity.embeddings)
        series.append(f'ICD {entity.code[0]}')
        hover.append(f'{entity.code}: {entity.title}')

tsne = TSNE(n_components=2, random_state=42)
embeddings_tsne = tsne.fit_transform(np.array(embeddings))

# Create a DataFrame with the t-SNE embeddings and titles
data = {
    'x': embeddings_tsne[:, 0],
    'y': embeddings_tsne[:, 1],
    'title': titles,
    'series': series,
    'hover': hover
}
df = pd.DataFrame(data)

# Create an interactive scatter plot with plotly
fig = px.scatter(
    df,
    x='x',
    y='y',
    text='title',
    color='series',
    hover_data='hover',
    title='Perseverance Project Diagnosis Embeddings'
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

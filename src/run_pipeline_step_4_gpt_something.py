from config import config
from config import columns
from dossier import Dossier, load_dossiers
from diagnosis_clusters import load_clusters

dossiers = load_dossiers(config.DOSSIERS_FILE)
print(f'Dossiers: {len(dossiers)}')

clusters = load_clusters(config.CLUSTERS_FILE)
print(f'Clusters: {len(clusters)}')


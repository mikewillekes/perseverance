from thefuzz import fuzz
from thefuzz import process

from config import config
from config import columns
from dossier import Dossier, load_dossiers
from diagnosis_clusters import save_clusters

dossiers = load_dossiers('data/dossiers.jsonl')
print(len(dossiers))


def cluster_strings(strings, threshold=90):

    clusters = []
    for string in strings:
        found = False
    
        # All these nested for loops... Not efficient at scale
        # (On^2) but fine for just a few thousand entries
        for cluster in clusters:
            
            for existing in cluster:
                if fuzz.token_sort_ratio(string, existing) > threshold:
                    cluster.append(string)
                    found = True
                    break
            
            if found:
                break
    
        if not found:
            # String did not match within threshold against
            # any existing string in any cluster. Make a new
            # cluster with just this new String
            clusters.append([string])
    
    return clusters


unique_diagnosis = list(set([d for dossier in dossiers for d in dossier.diagnosis]))
unique_diagnosis.sort()

# Threshold of ~70 seems to group French medical conditions well 
clusters = cluster_strings(unique_diagnosis, threshold=70)
sorted_clusters = list(sorted(clusters, key=len, reverse=True))

save_clusters('data/clusters.txt', sorted_clusters)
print(len(sorted_clusters))



import json
import pickle
import itertools
from kneed import KneeLocator
import matplotlib.pyplot as plt
from properties import data_path 
from scipy.cluster import hierarchy

def cohesion_score(X, labels):
	cohesion = [0] * len(set(labels))
	for c, cluster in enumerate(set(labels)):
		cluster_points = [i for i, _ in enumerate(labels) if labels[i] == cluster]
		cohesion[c] = sum([X[i][j] * X[i][j] for i, j in itertools.combinations(cluster_points, 2)]) / len(cluster_points)
	return sum(cohesion) / len(cohesion)

labels = pickle.load(open(data_path + 'distance_matrix_labels.pickle', 'rb'))
distances = pickle.load(open(data_path + 'distance_matrix_sparse_full.pickle', 'rb'))
sdistances = pickle.load(open(data_path + 'distance_matrix_dense_full.pickle', 'rb'))
sdistances_comment = pickle.load(open(data_path + 'distance_matrix_dense_comment.pickle', 'rb'))

cluster_range = list(range(50, 3001, 10))
totalcohc = []

Z = hierarchy.linkage(distances, method='average')
for n_clusters in cluster_range:
	t = Z[-(n_clusters - 0), 2]
	C = hierarchy.fcluster(Z, t=t, criterion='distance')  
	print("Number of clusters: " + str(len(set(C))), end='\t')
	# Compute cohesion score based on comment distance matrix 
	cohc = cohesion_score(sdistances_comment, C)
	totalcohc.append(cohc)
	print("Cohesion (C): " + str(cohc))

stats = {"SSE": totalcohc, "INDEXES": cluster_range}
with open(data_path + 'clustering_stats.json', 'w') as outfile:
	json.dump(stats, outfile, indent=3)

# Find optimal number of clusters using Kneedle method
with open(data_path + 'clustering_stats.json') as infile:
	stats = json.load(infile)

INDEXES = stats["INDEXES"]
SSE = stats["SSE"]

# An alternative to this is presented here:
# https://dataplatform.cloud.ibm.com/analytics/notebooks/54d79c2a-f155-40ec-93ec-ed05b58afa39/view?access_token=6d8ec910cf2a1b3901c721fcb94638563cd646fe14400fecbb76cea6aaae2fb1
# Both methods provide the same result
kn = KneeLocator(INDEXES, SSE, S=1.0, curve='convex', direction='decreasing')

print(kn.knee)

plt.figure(figsize=(5, 3.5))
plt.plot(INDEXES, SSE, '.-')
plt.axvline(x=kn.knee, color='#ff7f0e', linestyle='--')
plt.xlabel('Number of Clusters')
plt.ylabel('SSE')
plt.tight_layout()
plt.savefig('clusters-vs-sse.pdf')
plt.show()

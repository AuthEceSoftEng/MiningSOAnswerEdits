import csv
import pickle
from properties import data_path
from collections import defaultdict
from scipy.cluster import hierarchy

labels = pickle.load(open(data_path + 'distance_matrix_labels.pickle', 'rb'))
distances = pickle.load(open(data_path + 'distance_matrix_sparse_full.pickle', 'rb'))
sdistances = pickle.load(open(data_path + 'distance_matrix_dense_full.pickle', 'rb'))
sdistances_comment = pickle.load(open(data_path + 'distance_matrix_dense_comment.pickle', 'rb'))
print("Done loading!")

Z = hierarchy.linkage(distances, method='average')
n_clusters = 390
t = Z[-(n_clusters - 0), 2]
C = hierarchy.fcluster(Z, t=t, criterion='distance')  
print("Done clustering!")
print("Number of clusters: " + str(len(set(C))))

with open(data_path + 'clusters.txt', 'w') as outfile:
	for label, cluster in zip(labels, C):
		outfile.write(str(label) + ';' + str(cluster) + '\n')

# Find the comments of each cluster
with open(data_path + 'filtered_similarity_matrix.csv', 'r', encoding='utf-8') as data:
	h = {header: hn for hn, header in enumerate(next(data).strip().split(';'))}
	lines = {}
	indexes = []
	for line in csv.reader(data, dialect='excel', delimiter=';'):
		IdOne, IdTwo = int(line[0]), int(line[1])
		if IdOne <= IdTwo:
			row = [int(line[0])] + [int(line[1])] + [float(l.strip()) for l in line[2:]]
			if len(indexes) == 0 or row[h["IdOne"]] != indexes[-1]:
				indexes.append(row[h["IdOne"]])
			lines[(row[h["IdOne"]], row[h["IdTwo"]])] = 1 - row[h["CommentScore"]]
	
with open(data_path + 'edit_differences.csv', 'r', encoding='utf-8') as diff:
	next(diff)
	comments = {}
	for line in csv.reader(diff, dialect='excel', delimiter='\t'):
		comments[int(line[2])] = line[3]

with open(data_path + 'clusters.txt', 'r') as data:
	clusters_temp = {}
	for line in csv.reader(data, dialect='excel', delimiter=';'):
		clusters_temp[int(line[0])] = int(line[1])

clusters = defaultdict(list)
for i in range(max(clusters_temp.values())):
	for key, value in clusters_temp.items():
		if i == value:
			clusters[i].append(key)

sorted_clusters = list(sorted(clusters, key=lambda x: len(clusters[x]), reverse=True))

# Find the 5 most representative comments of each cluster based on mean distance from all cluster comments
with open(data_path + 'cluster_names.txt', 'w', encoding='utf-8') as outfile:
	outfile.write("Total clusters: " + str(len(clusters)) + '\n')
	for cluster_id in sorted_clusters:
		cluster_points = clusters[cluster_id]
		mdist = {}
		for i in cluster_points:
			mdist[int(i)] = sum([lines.get((int(i), int(j)), 1) for j in cluster_points if i != j]) / len(cluster_points)
		sorted_points = list(sorted(mdist, key=lambda x: mdist[x]))
		outfile.write(str(cluster_id) + "\t" + str(len(clusters[cluster_id])) + '\t')
		outfile.write(', '.join([comments[i] for i in sorted_points][:5]) + '\n')


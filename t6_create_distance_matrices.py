import csv
import pickle
from properties import data_path

scores = ["CommentScore", "TextAdditionsScore", "TextDeletionsScore", "CodeAdditionsScore", "CodeDeletionsScore", "CodeSequenceAdditionsScore", "CodeSequenceDeletionsScore"]
avg = lambda x: sum(x) / len(x)

with open(data_path + 'filtered_similarity_matrix.csv', 'r', encoding='utf-8') as data:
	h = {header: hn for hn, header in enumerate(next(data).strip().split(';'))}
	lines = {}
	lines_comment = {}
	indexes = []
	for f, line in enumerate(csv.reader(data, dialect='excel', delimiter=';')):
		row = [int(line[0])] + [int(line[1])] + [float(l.strip()) for l in line[2:]]
		if len(indexes) == 0 or row[h["IdOne"]] != indexes[-1]:
			indexes.append(row[h["IdOne"]])
		lines[(row[h["IdOne"]], row[h["IdTwo"]])] = 1 - avg([row[h[score]] for score in scores[1:7]])
		lines_comment[(row[h["IdOne"]], row[h["IdTwo"]])] = 1 - row[h["CommentScore"]]
		if f % 8000 == 0:
			print("%d%%" % (100 * f / 822157))
print("Done loading!")
print(len(indexes))

# Create distance matrix as in https://stackoverflow.com/a/36867493
sdistances = []
sdistances_comment = []
for i in range(len(indexes)):
	sdistances.append([0] * len(indexes))
	sdistances_comment.append([0] * len(indexes))
	for j in range(len(indexes)):
		sdistances[-1][j] = lines.get((indexes[i], indexes[j]), lines.get((indexes[j], indexes[i]), 1))
		sdistances_comment[-1][j] = lines_comment.get((indexes[i], indexes[j]), lines_comment.get((indexes[j], indexes[i]), 1))
	if i % 100 == 0:
		print("%d%%" % (100 * i / len(indexes)))

# Create upper triangular distance matrix as in https://stackoverflow.com/a/36867493
keys, values = [], []
for i in range(len(indexes)):
	for j in range(i + 1, len(indexes)):
		keys.append((indexes[i], indexes[j]))
		values.append(lines.pop((indexes[i], indexes[j]), 1))
	if i % 100 == 0:
		print("%d%%" % (100 * i / len(indexes)))

# Create condensed distance matrix https://stackoverflow.com/a/51678381
sorted_keys, distances = keys, values
labels = sorted(set([key[0] for key in sorted_keys] + [sorted_keys[-1][-1]]))

pickle.dump(labels, open(data_path + 'distance_matrix_labels.pickle', 'wb'))
pickle.dump(distances, open(data_path + 'distance_matrix_sparse_full.pickle', 'wb'))
pickle.dump(sdistances, open(data_path + 'distance_matrix_dense_full.pickle', 'wb'))
pickle.dump(sdistances_comment, open(data_path + 'distance_matrix_dense_comment.pickle', 'wb'))
print("Done preprocessing!")

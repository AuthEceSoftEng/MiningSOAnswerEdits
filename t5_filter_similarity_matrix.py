import csv
from properties import data_path 

# Keep 100 most similar edits for each edit
scores = ["TextAdditionsScore", "TextDeletionsScore", "CodeAdditionsScore", "CodeDeletionsScore", "CodeSequenceAdditionsScore", "CodeSequenceDeletionsScore"]
distance = lambda row: sum([row[h[score]] for score in scores]) / len(scores)
with open(data_path + 'filtered_similarity_matrix.csv', 'w', encoding='utf-8') as outdata:
	current_row_id, current_row_similar = -1, []
	with open(data_path + 'similarity_matrix.csv', 'r', encoding='utf-8') as data:
		firstline = next(data).strip()
		h = {header: hn for hn, header in enumerate(firstline.split(';'))}
		outdata.write(firstline + '\n')
		for linecount, line in enumerate(csv.reader(data, dialect='excel', delimiter=';')):
			row = [int(line[0])] + [int(line[1])] + [float(l.strip()) for l in line[2:]]
			if row[h["IdOne"]] < row[h["IdTwo"]]:
				if current_row_id == -1:
					current_row_id = row[h["IdOne"]]
				if current_row_id == row[h["IdOne"]]:
					current_row_similar.append(row)
				else:
					# Write 100 most similar edits to disk
					for row_to_write in list(sorted(current_row_similar, key=distance, reverse=True))[:100]:
						a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12 = row_to_write
						outdata.write("%d;%d;%.5f;%.5f;%.5f;%.5f;%.5f;%.5f;%.5f;%.5f;%.5f;%.5f\n" % (a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12))
					# Update current row
					current_row_id, current_row_similar = row[h["IdOne"]], []
			if linecount % 600000 == 0:
				print("%d%%" % (100 * linecount / 66623231))
				outdata.flush()

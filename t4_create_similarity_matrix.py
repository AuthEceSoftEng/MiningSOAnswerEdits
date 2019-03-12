import csv
from properties import data_path
from helpers import model_exists, create_model, load_model, execute_model, cos_sim, lcs_scores

lines = []
with open(data_path + 'edit_differences.csv', 'r', encoding='utf-8') as diff:
	linenum = 0
	headers = {header: h for h, header in enumerate(next(diff)[1:].strip().split('\t'))}
	for line in csv.reader(diff, dialect='excel', delimiter='\t'):
		lines.append([line[1], line[2], line[3], line[4], line[5], line[6], line[7], [s for s in line[8][1:-1].split(', ')], [s for s in line[8][1:-1].split(', ')], \
					line[10], line[11], [s for s in line[12][1:-1].split(', ')], line[13], line[14], line[15], line[16], [s for s in line[17][1:-1].split(', ')], [s for s in line[18][1:-1].split(', ')]])
		linenum += 1
		if linenum % 500 == 0:
			print("%d%%" % (100 * linenum / 8273))

indexes = [line[headers['IdAfter']] for line in lines]  # Keep IdAfter as the id
comments = [line[headers['Comment']] for line in lines]
texts = [line[headers['TextBefore']] for line in lines]
textdiffs = [line[headers['TextAdditions']] for line in lines]
textdiffsd = [line[headers['TextDeletions']] for line in lines]
codes = [line[headers['CodeBefore']] for line in lines]
codediffs = [line[headers['CodeAdditions']] for line in lines]
codediffsd = [line[headers['CodeDeletions']] for line in lines]
codesequences = [line[headers['CodeSequenceBefore']] for line in lines]
codesequencediffs = [line[headers['CodeSequenceAdditions']] for line in lines]
codesequencediffsd = [line[headers['CodeSequenceDeletions']] for line in lines]

# Create the models if they do not exist
if not model_exists('tfidf_comments'):
	create_model('tfidf_comments', [line[headers['Comment']] for line in lines])

if not model_exists('tfidf_texts'):
	create_model('tfidf_texts', [line[headers['TextBefore']] + ' ' + line[headers['TextAdditions']] + ' ' + line[headers['TextDeletions']] for line in lines])

if not model_exists('tfidf_codes'):
	create_model('tfidf_codes', [line[headers['CodeBefore']] + ' ' + line[headers['CodeAdditions']] + ' ' + line[headers['CodeDeletions']] for line in lines])

# Load the models
comment_vectorizer = load_model('tfidf_comments')
comment_tfidf_model = execute_model(comment_vectorizer, comments)

text_vectorizer = load_model('tfidf_texts')
text_tfidf_model = execute_model(text_vectorizer, texts)
text_diff_tfidf_model = execute_model(text_vectorizer, textdiffs)
text_diff_tfidf_modeld = execute_model(text_vectorizer, textdiffsd)

code_vectorizer = load_model('tfidf_codes')
code_tfidf_model = execute_model(code_vectorizer, codes)
code_diff_tfidf_model = execute_model(code_vectorizer, codediffs)
code_diff_tfidf_modeld = execute_model(code_vectorizer, codediffsd)

# Compute cosine similarity for comment, text, code and lcs score for codesequence
with open(data_path + 'similarity_matrix.csv', 'w', encoding='utf-8') as outfile_cs:
	outfile_cs.write('IdOne;IdTwo;CommentScore;TextBeforeScore;TextAdditionsScore;TextDeletionsScore;CodeBeforeScore;CodeAdditionsScore;CodeDeletionsScore;CodeSequenceBeforeScore;CodeSequenceAdditionsScore;CodeSequenceDeletionsScore\n')
	for i, line in enumerate(lines):
		ind = line[headers['IdAfter']]
		if i % 100 == 0:
			outfile_cs.flush()
			print("Processing %d out of %d" % (i, len(lines)))
		
		comment_score = cos_sim(comment_tfidf_model, i)

		text_score = cos_sim(text_tfidf_model, i)
		textdiff_score = cos_sim(text_diff_tfidf_model, i)
		textdiff_scored = cos_sim(text_diff_tfidf_modeld, i)

		code_score = cos_sim(code_tfidf_model, i)
		codediff_score = cos_sim(code_diff_tfidf_model, i)
		codediff_scored = cos_sim(code_diff_tfidf_modeld, i)

		codesequence_score = lcs_scores(codesequences, i)
		codesequencediff_score = lcs_scores(codesequencediffs, i)
		codesequencediff_scored = lcs_scores(codesequencediffsd, i)

		for j, a, b, c, d, e, f, g, h, i, k in zip(indexes, comment_score, text_score, textdiff_score, textdiff_scored, code_score, codediff_score, codediff_scored, codesequence_score, codesequencediff_score, codesequencediff_scored):
			if a > 0 or b > 0 or c > 0 or d > 0 or e > 0 or f > 0 or g > 0 or h > 0 or i > 0 or k > 0:
				outfile_cs.write("%s;%s;%.5f;%.5f;%.5f;%.5f;%.5f;%.5f;%.5f;%.5f;%.5f;%.5f\n" % (ind, j, a, b, c, d, e, f, g, h, i, k))

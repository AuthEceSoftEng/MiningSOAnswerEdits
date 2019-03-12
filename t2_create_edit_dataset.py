import csv
import codecs
import pandas as pd
from sequenceextractor import SequenceExtractor
from properties import data_path, sequence_extractor_path

sequence_extractor = SequenceExtractor(sequence_extractor_path)

with codecs.open(data_path + 'answer_posts_with_edits.csv', 'r', encoding='utf-8') as data:
	linenum = 0
	lines = {}
	headers = {header: h for h, header in enumerate(next(data)[1:].strip().split('\t'))}
	for line in csv.reader(data, dialect='excel', delimiter='\t'):
		lines[line[1]] = line[1:]
		linenum += 1
		if linenum % 10000 == 0:
			print("%d%%" % (100 * linenum / 423240))
print("Done reading data")

diff = []
counter = 0

for i, row in lines.items():
	counter += 1
	if counter % 1000 == 0:
		print("Processing %d out of %d" % (counter, len(lines)))
	j = row[headers['PredPostHistoryId']].strip('.0')
	# Check if predhistoryid exist in data so as to compare with
	# and filter out also comments with less or equal than 10 characters and less or equal than 2 words
	if (not row[headers['Comment']].endswith('characters in body')) and \
			(not row[headers['Comment']].endswith('character in body')) and \
			(not row[headers['Comment']] == 'edited body') and \
			(not "format" in row[headers['Comment']]) and \
			(not "Format" in row[headers['Comment']]) and \
			(not "Rollback" in row[headers['Comment']]) and \
			(not "stackoverflow.com" in row[headers['Comment']]) and \
			(not "typo" in row[headers['Comment']]) and \
			(len(row[headers['Comment']]) > 10) and \
			(len(row[headers['Comment']].split()) > 2) and \
			(j in lines) and (j != ''):
		rowi, rowj = row, lines[j]
	
		com1 = rowi[headers['Comment']]
		text1 = rowi[headers['Text']]
		try:
			codetype1 = sequence_extractor.parse_snippet(rowi[headers['Code']])
			code1 = rowi[headers['Code']]
		except:
			codetype1 = -1
			code1 = ''
		
		text2 = rowj[headers['Text']]
		try:
			codetype2 = sequence_extractor.parse_snippet(rowj[headers['Code']])
			code2 = rowj[headers['Code']]
		except:
			codetype2 = -1
			code2 = ''
		
		# Check if code block has some codetype from sequence extractor
		if (not(codetype1 == -1 or codetype1 == '[]')) and (not(codetype2 == -1 or codetype2 == '[]')):
			diff.append([j, i, com1, text2, text1, code2, code1, codetype2, codetype1])

diff = pd.DataFrame.from_records(diff, columns=['IdBefore', 'IdAfter', 'Comment', 'TextBefore', 'TextAfter', 'CodeBefore', 'CodeAfter', 'CodeSequenceBefore', 'CodeSequenceAfter'])

diff.to_csv(data_path + 'edits.csv', sep='\t', encoding='utf-8')


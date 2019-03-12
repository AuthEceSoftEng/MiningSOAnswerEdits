import csv
import codecs
import pandas as pd
from properties import data_path
from helpers import process_text, listdiff

diff = []
with codecs.open(data_path + 'edits.csv', 'r', encoding='utf-8') as data:
	linenum = 0
	headers = {header: h for h, header in enumerate(next(data)[1:].strip().split('\t'))}
	for line in csv.reader(data, dialect='excel', delimiter='\t'):
		diff.append([int(line[1]), int(line[2])] + line[3:])
		linenum += 1
		if linenum % 1000 == 0:
			print("%d%%" % (100 * linenum / 32085))
print("Done reading data")

counter = 0
newdiff = []
for i, row in enumerate(diff):
	counter += 1
	if counter % 1000 == 0:
		print("Processing %d out of %d" % (counter, len(diff)))

	try: 
		# Tokenize text, code, codesequence (before and after the edit) and save the differences 
		tokensTextBefore = process_text(row[headers['TextBefore']], False, False, False)
		tokensTextAfter = process_text(row[headers['TextAfter']], False, False, False)
		tokensTextDiff = listdiff(tokensTextBefore, tokensTextAfter)
		row.append('[' + ', '.join(tokensTextDiff) + ']')

		row[headers['TextBefore']] = ' '.join(tokensTextBefore)
		row[headers['TextAfter']] = ' '.join(tokensTextAfter)
		
		tokensCodeBefore = process_text(row[headers['CodeBefore']], False, False, False)
		tokensCodeAfter = process_text(row[headers['CodeAfter']], False, False, False)
		tokensCodeDiff = listdiff(tokensCodeBefore, tokensCodeAfter)
		row.append('[' + ', '.join(tokensCodeDiff) + ']')

		row[headers['CodeBefore']] = ' '.join(tokensCodeBefore)
		row[headers['CodeAfter']] = ' '.join(tokensCodeAfter)
		
		codeSequenceBefore = [s.strip() for s in row[headers['CodeSequenceBefore']][1:-1].split(', ') if s]
		codeSequenceAfter = [s.strip() for s in row[headers['CodeSequenceAfter']][1:-1].split(', ') if s]
		codeSequenceDiff = listdiff(codeSequenceBefore, codeSequenceAfter)
		
		if len(codeSequenceDiff) < 1:  # Filter out edits without code differences (at least 1 command)
			continue
		row.append('[' + ', '.join(codeSequenceDiff) + ']')

		row[headers['CodeSequenceBefore']] = '[' + ', '.join(codeSequenceBefore) + ']'
		row[headers['CodeSequenceAfter']] = '[' + ', '.join(codeSequenceAfter) + ']'

		# Save additions(+) and deletions(-) 
		row.append(' '.join([t[2:] for t in tokensTextDiff if t.startswith('+')]))
		row.append(' '.join([t[2:] for t in tokensTextDiff if t.startswith('-')]))
		row.append(' '.join([t[2:] for t in tokensCodeDiff if t.startswith('+')]))
		row.append(' '.join([t[2:] for t in tokensCodeDiff if t.startswith('-')]))
		row.append('[' + ', '.join([t[2:] for t in codeSequenceDiff if t.startswith('+')]) + ']')
		row.append('[' + ', '.join([t[2:] for t in codeSequenceDiff if t.startswith('-')]) + ']')

		newdiff.append(row)
	except:
		pass

newdiff = pd.DataFrame.from_records(newdiff, columns=['IdBefore', 'IdAfter', 'Comment', 'TextBefore', 'TextAfter', 'CodeBefore', 'CodeAfter', 'CodeSequenceBefore', 'CodeSequenceAfter', \
		'TextDiff', 'CodeDiff', 'CodeSequenceDiff', 'TextAdditions', 'TextDeletions', 'CodeAdditions', 'CodeDeletions', 'CodeSequenceAdditions', 'CodeSequenceDeletions'])

newdiff.to_csv(data_path + 'edit_differences.csv', sep='\t', encoding='utf-8')

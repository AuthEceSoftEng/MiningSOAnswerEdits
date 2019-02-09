import os
import gzip
from shutil import copyfile
from properties import data_dump_original_path, data_dump_final_path

# Copy non-data files
for filename in os.listdir(data_dump_original_path):
	if filename.endswith('.sql') or filename.endswith('.md'):
		copyfile(data_dump_original_path + filename, data_dump_final_path + filename)

# Find all java question ids
questionids = set()
with gzip.open(data_dump_original_path + 'Posts.xml.gz', 'rt', encoding='utf-8') as theinput:
	for line in theinput:
		if line.startswith('  <row'):
			PostTypeId = line.split(' PostTypeId="')[-1].split('"')[0]
			if PostTypeId == "1":
				Tags = line.split(' Tags="')[-1].split('"')[0]
				Tags = Tags.split('&gt;&lt;')
				if len(Tags) > 1:
					Tags = [Tags[0][4:]] + Tags[1:-1] + [Tags[-1][:-4]]
				else:
					Tags = [Tags[0][4:-4]]
				if 'java' in Tags:
					Id = line.split(' Id="')[-1].split('"')[0]
					questionids.add(Id)

# Write all java posts (questions and answers) to file
with gzip.open(data_dump_final_path + 'Posts.xml.gz', 'wt', encoding='utf-8') as myfile:
	myfile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
	myfile.write("<posts>\n")
	with gzip.open(data_dump_original_path + 'Posts.xml.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line.startswith('  <row'):
				PostTypeId = line.split(' PostTypeId="')[-1].split('"')[0]
				if PostTypeId == "1":
					Id = line.split(' Id="')[-1].split('"')[0]
					if Id in questionids:
						myfile.write(line)
				else:
					ParentId = line.split(' ParentId="')[-1].split('"')[0]
					if ParentId in questionids:
						myfile.write(line)
	myfile.write("</posts>")

# Find all java post ids (questions and answers) and all user ids of these posts, and keep also tag counts
postids = set()
userids = set()
tagcounts = {}
with gzip.open(data_dump_final_path + 'Posts.xml.gz', 'rt', encoding='utf-8') as theinput:
	for line in theinput:
		if line.startswith('  <row'):
			if ' Id' in line:
				postids.add(line.split(' Id="')[-1].split('"')[0])
			if ' OwnerUserId' in line:
				userids.add(line.split(' OwnerUserId="')[-1].split('"')[0])
			if ' LastEditorUserId' in line:
				userids.add(line.split(' LastEditorUserId="')[-1].split('"')[0])
			if ' Tags="' in line:
				Tags = line.split(' Tags="')[-1].split('"')[0]
				Tags = [tag[:-4] for tag in Tags[4:].split("&lt;")]
				for tag in Tags:
					if tag not in tagcounts:
						tagcounts[tag] = 0
					tagcounts[tag] += 1

# Write all comments of java posts to file and find all user ids of these comments
with gzip.open(data_dump_final_path + 'Comments.xml.gz', 'wt', encoding='utf-8') as myfile:
	myfile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
	myfile.write("<comments>\n")
	with gzip.open(data_dump_original_path + 'Comments.xml.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line.startswith('  <row'):
				PostId = line.split(' PostId="')[-1].split('"')[0]
				if PostId in postids:
					myfile.write(line)
					if ' UserId' in line:
						userids.add(line.split(' UserId="')[-1].split('"')[0])
	myfile.write("</comments>")

# Write all users of java posts and comments to file
with gzip.open(data_dump_final_path + 'Users.xml.gz', 'wt', encoding='utf-8') as myfile:
	myfile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
	myfile.write("<users>\n")
	with gzip.open(data_dump_original_path + 'Users.xml.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line.startswith('  <row'):
				AccountId = line.split(' AccountId="')[-1].split('"')[0]
				if AccountId in userids:
					myfile.write(line)
	myfile.write("</users>")

# Write all votes of java posts to file
with gzip.open(data_dump_final_path + 'Votes.xml.gz', 'wt', encoding='utf-8') as myfile:
	myfile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
	myfile.write("<votes>\n")
	with gzip.open(data_dump_original_path + 'Votes.xml.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line.startswith('  <row'):
				PostId = line.split(' PostId="')[-1].split('"')[0]
				if PostId in postids:
					myfile.write(line)
	myfile.write("</votes>")

# Write all postlinks of java posts to file
with gzip.open(data_dump_final_path + 'PostLinks.xml.gz', 'wt', encoding='utf-8') as myfile:
	myfile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
	myfile.write("<postlinks>\n")
	with gzip.open(data_dump_original_path + 'PostLinks.xml.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line.startswith('  <row'):
				PostId = line.split(' PostId="')[-1].split('"')[0]
				RelatedPostId = line.split(' RelatedPostId="')[-1].split('"')[0]
				if PostId in postids and RelatedPostId in postids:
					myfile.write(line)
	myfile.write("</postlinks>")

# Write all badges of users of java posts and comments to file
with gzip.open(data_dump_final_path + 'Badges.xml.gz', 'wt', encoding='utf-8') as myfile:
	myfile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
	myfile.write("<badges>\n")
	with gzip.open(data_dump_original_path + 'Badges.xml.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line.startswith('  <row'):
				UserId = line.split(' UserId="')[-1].split('"')[0]
				if UserId in userids:
					myfile.write(line)
	myfile.write("</badges>")

# Write the history of java posts to file
with gzip.open(data_dump_final_path + 'PostHistory.xml.gz', 'wt', encoding='utf-8') as myfile:
	myfile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
	myfile.write("<posthistory>\n")
	with gzip.open(data_dump_original_path + 'PostHistory.xml.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line.startswith('  <row'):
				PostId = line.split(' PostId="')[-1].split('"')[0]
				if PostId in postids:
					myfile.write(line)
	myfile.write("</posthistory>")

# Write the tags of java posts and their counts to file
with gzip.open(data_dump_final_path + 'Tags.xml.gz', 'wt', encoding='utf-8') as myfile:
	myfile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
	myfile.write("<tags>\n")
	with gzip.open(data_dump_original_path + 'Tags.xml.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line.startswith('  <row'):
				TagName = line.split(' TagName="')[-1].split('"')[0]
				if TagName in tagcounts:
					left = line.split(' Count="')[0] + ' Count="'
					right = '" ExcerptPostId' + line.split(' Count="')[-1].split('" ExcerptPostId')[-1]
					line = left + str(tagcounts[TagName]) + right
					myfile.write(line)
	myfile.write("</tags>")

# Write the post references of java posts to file
with gzip.open(data_dump_final_path + 'PostReferenceGH.csv.gz', 'wt', encoding='utf-8') as myfile:
	with gzip.open(data_dump_original_path + 'PostReferenceGH.csv.gz', 'rt', encoding='utf-8') as theinput:
		myfile.write(theinput.readline())
		for line in theinput:
			if line:
				PostId = line.split(',')[7]
				if PostId in postids:
					myfile.write(line)

# Write the comment urls of java posts to file
with gzip.open(data_dump_final_path + 'CommentUrl.csv.gz', 'wt', encoding='utf-8') as myfile:
	with gzip.open(data_dump_original_path + 'CommentUrl.csv.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line:
				PostId = line.split(',')[1]
				if PostId in postids:
					myfile.write(line)

# Write the post version of java posts to file
with gzip.open(data_dump_final_path + 'PostVersion.csv.gz', 'wt', encoding='utf-8') as myfile:
	with gzip.open(data_dump_original_path + 'PostVersion.csv.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line:
				PostId = line.split(',')[1]
				if PostId in postids:
					myfile.write(line)

# Write the title version of java posts to file
with gzip.open(data_dump_final_path + 'TitleVersion.csv.gz', 'wt', encoding='utf-8') as myfile:
	with gzip.open(data_dump_original_path + 'TitleVersion.csv.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line:
				PostId = line.split(',')[1]
				if PostId in postids:
					myfile.write(line)

# Write the post version url of java posts to file
with gzip.open(data_dump_final_path + 'PostVersionUrl.csv.gz', 'wt', encoding='utf-8') as myfile:
	with gzip.open(data_dump_original_path + 'PostVersionUrl.csv.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line:
				PostId = line.split(',')[1]
				if PostId in postids:
					myfile.write(line)

# Write the post block version of java posts to file
with gzip.open(data_dump_final_path + 'PostBlockVersion.csv.gz', 'wt', encoding='utf-8') as myfile:
	with gzip.open(data_dump_original_path + 'PostBlockVersion.csv.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line:
				PostId = line.split(',')[2]
				if PostId in postids:
					myfile.write(line)

# Write the post block diff of java posts to file
with gzip.open(data_dump_final_path + 'PostBlockDiff.csv.gz', 'wt', encoding='utf-8') as myfile:
	with gzip.open(data_dump_original_path + 'PostBlockDiff.csv.gz', 'rt', encoding='utf-8') as theinput:
		for line in theinput:
			if line:
				PostId = line.split(',')[1]
				if PostId in postids:
					myfile.write(line)



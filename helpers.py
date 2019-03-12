import os
import re
import pickle
import string
from difflib import Differ
from nltk import word_tokenize
from properties import data_path
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def camel_case_split(identifier):
	matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
	return [m.group(0).lower() for m in matches]

def listdiff(first, second): # computes second - first
	res = Differ().compare(first, second)
	return [r for r in res if r.startswith('+') or r.startswith('-')]

def process_text(text, stem = True, removestopwords = True, splitcamelcase = True):
	text = text.translate({ord(c): ' ' for c in string.punctuation})
	tokens = word_tokenize(text)
	if splitcamelcase:
		tokens = [camel_case_split(t) for t in tokens]
		tokens = [item for sublist in tokens for item in sublist]

	if removestopwords:
		tokens = [t for t in tokens if t not in stopwords.words('english')]

	if stem:
		stemmer = PorterStemmer()
		tokens = [stemmer.stem(t) for t in tokens]

	return tokens

def cos_sim(X, i):
	return cosine_similarity(X[i], X)[0]

def lcs_score(a, b):
	if len(a) == 0 or len(b) == 0:
		return 0
	table = [[0] * (len(b) + 1) for _ in iter(range(len(a) + 1))]
	for i, ca in enumerate(a, 1):
		for j, cb in enumerate(b, 1):
			table[i][j] = (
				table[i - 1][j - 1] + 1 if ca == cb else
				max(table[i][j - 1], table[i - 1][j]))
	return 2 * table[-1][-1] / (len(a) + len(b))

def lcs_scores(X, i, indexes_to_keep = None):
	return [lcs_score(cs, X[i]) for cs in X] if indexes_to_keep == None else [lcs_score(cs, X[i]) if indexes_to_keep[j] else 0 for j, cs in enumerate(X)]

def create_model(model_name, texts):
	vectorizer = TfidfVectorizer(tokenizer=process_text, max_df=0.5, min_df=10, lowercase=True)
	tfidf_model = vectorizer.fit(texts)
	pickle.dump(vectorizer, open(data_path + model_name + ".pkl","wb"))

def model_exists(model_name):
	return os.path.exists(data_path + model_name + ".pkl")

def load_model(model_name):
	return pickle.load(open(data_path + model_name + ".pkl", 'rb'))

def execute_model(vectorizer, texts):
	return vectorizer.transform(texts)

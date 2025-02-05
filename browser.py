import json
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from math import log
from nltk.corpus import stopwords

# Load necessary data
def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# Load indexes
brand_index = load_json('data_3/brand_index.json')
description_index = load_json('data_3/description_index.json')
origin_index = load_json('data_3/origin_index.json')
origin_synonyms = load_json('data_3/origin_synonyms.json')
reviews_index = load_json('data_3/reviews_index.json')
title_index = load_json('data_3/title_index.json')

# Get stopwords from NLTK
def get_stopwords():
    return set(stopwords.words('english'))

# Initialize the stemmer
stemmer = PorterStemmer()

# Tokenize a text
def tokenize(text):
    # Remove non-alphanumeric characters (except spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Tokenize the text
    tokens = word_tokenize(text.lower())  # Convert to lowercase
    return tokens

# Normalize text
def normalize_text(tokens):
    # Apply stemming
    normalized_tokens = [stemmer.stem(token) for token in tokens]
    return normalized_tokens

# Expand query using synonyms
def expand_query(query_tokens, synonym_dict):
    expanded = set(query_tokens)
    for token in query_tokens:
        if token in synonym_dict:
            expanded.update(synonym_dict[token])
    return list(expanded)


# Filter documents by tokens
def filter_documents(index, query_tokens, match_all=False):
    relevant_docs = set()
    for token in query_tokens:
        if token in index:
            if not match_all:
                relevant_docs.update(index[token])
            else:
                if not relevant_docs:
                    relevant_docs = set(index[token])
                else:
                    relevant_docs.intersection_update(index[token])
    return list(relevant_docs)


# BM25 ranking
class BM25:
    def __init__(self, index, k1=1.5, b=0.75):
        self.index = index
        self.k1 = k1
        self.b = b
        self.doc_lengths = {doc: sum(len(self.index[tok].get(doc, [])) for tok in self.index) for doc in
                            index.get(next(iter(index)), [])}
        self.avg_doc_length = sum(self.doc_lengths.values()) / len(self.doc_lengths) if self.doc_lengths else 1
        self.N = len(self.doc_lengths)

    def score(self, doc, query_tokens):
        score = 0
        for token in query_tokens:
            if token in self.index:
                df = len(self.index[token])
                idf = log((self.N - df + 0.5) / (df + 0.5) + 1)
                tf = len(self.index[token].get(doc, []))
                doc_length = self.doc_lengths.get(doc, 1)
                score += idf * ((tf * (self.k1 + 1)) / (
                            tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))))
        return score


# Search function
def search(query):
    query_tokens = tokenize(query)
    expanded_query = expand_query(query_tokens, origin_synonyms)
    filtered_docs = filter_documents(description_index, expanded_query) + filter_documents(title_index, expanded_query)
    bm25 = BM25(description_index)
    scored_docs = {doc: bm25.score(doc, expanded_query) for doc in filtered_docs}
    ranked_results = sorted(scored_docs.items(), key=lambda x: x[1], reverse=True)

    # Format results
    results = [{"title": doc, "score": score} for doc, score in ranked_results]
    return {
        "total_documents": len(description_index),
        "filtered_documents": len(filtered_docs),
        "results": results
    }


# Example usage
query = "chocolates"
print(json.dumps(search(query), indent=4))

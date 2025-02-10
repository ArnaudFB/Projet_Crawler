import json
import re
import string

import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from math import log
from nltk.corpus import stopwords

def load_json(filename):
    """Load JSON file."""
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# Load indexes
brand_index = load_json('data_3/brand_index.json')
description_index = load_json('data_3/description_index.json')
origin_index = load_json('data_3/origin_index.json')
origin_synonyms = load_json('data_3/origin_synonyms.json')
review_index = load_json('data_3/reviews_index.json')
title_index = load_json('data_3/title_index.json')

def load_jsonl(filepath):
    """Load JSONL file and return a list of dictionaries."""
    with open(filepath, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]

products_data = load_jsonl('data_3/products.jsonl')
rearranged_data = load_jsonl('data_3/rearranged_products.jsonl')

indexes = {
    "brand_index": brand_index,
    "description_index": description_index,
    "origin_index": origin_index,
    "review_index": "data_2/review_index.json",
    "title_index": title_index
}


def get_stopwords():
    """Get stopwords from NLTK."""
    return set(stopwords.words('english'))

# Initialize the stemmer
stemmer = PorterStemmer()

def tokenize(text):
    """Tokenize a text by removing punctuation and converting to lowercase."""
    # Remove non-alphanumeric characters (except spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Tokenize the text
    tokens = word_tokenize(text.lower())  # Convert to lowercase

    stopwords = get_stopwords()
    punctuation = set(string.punctuation)

    clean_tokens = [token for token in tokens if token not in stopwords and token not in punctuation]
    return clean_tokens

def expand_query(query_tokens, synonym_dict):
    """Expand query tokens using synonyms."""
    expanded = set(query_tokens)
    for token in query_tokens:
        if token in synonym_dict:
            expanded.update(synonym_dict[token])
    return list(expanded)

def filter_documents(index, query_tokens, match_all=False):
    """Filter documents by tokens in the index."""
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

def calc_doc_length(products):
    """Calculate the doc length for each doc (title + description)."""
    doc_lengths = {}
    for product in products:
        url = product['url']
        title = product.get('title', '')
        description = product.get('description', '')
        doc_lengths[url] = len(tokenize(title)) + len(tokenize(description))
    return doc_lengths

def get_token_frequency(token, url):
    """Calculate token frequency (with weights) in a document for some indexes."""

    weights = {
        "title_index": 5,
        "description_index": 3,
        "origin_index": 1,
        "brand_index": 2
    }

    total_freq = 0

    for field, index in indexes.items():
        if token not in index:
            continue

        value = index[token]
        # Can be a dict or a list depending on the current index
        if isinstance(value, dict):
            freq = len(value.get(url, []))
        elif isinstance(value, list):
            freq = 1 if url in value else 0
        else:
            freq = 0

        weight = weights.get(field, 1)  # Apply field weight
        total_freq += freq * weight

    return total_freq

# BM25 ranking
class BM25:
    def __init__(self, indexes, k1=1.5, b=0.75):
        self.indexes = indexes
        self.k1 = k1
        self.b = b
        self.doc_lengths = calc_doc_length(products_data)
        self.avg_doc_length = sum(self.doc_lengths.values()) / len(self.doc_lengths) if self.doc_lengths else 1
        self.N = len(self.doc_lengths)

    def score(self, doc, query_tokens):
        score = 0
        docs = set()
        for field, index in self.indexes.items():
            for token in query_tokens:
                if token in index:
                    value = index[token]
                    # Can be a dict or a list depending on the current index
                    if isinstance(value, dict):
                        docs.update(value.keys())
                    elif isinstance(value, list):
                        docs.update(value)
                    else:
                        pass
                    df = len(docs)
                    idf = log((self.N - df + 0.5) / (df + 0.5) + 1)
                    tf = get_token_frequency(token, doc)
                    doc_length = self.doc_lengths.get(doc, 1)
                    score += idf * ((tf * (self.k1 + 1)) / (
                                tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))))
        return score

def get_bonus_review(url):
    """Add a bonus if good review on URL."""
    mean_mark = review_index[url].get("mean_mark", 0)
    return mean_mark / 5


def exact_title_match(query_tokens, url):
    """Add a bonus if exact title match."""
    title = products_data[url].get("title", "")
    tokens = set(tokenize(title))
    query_tokens = set(query_tokens)
    return 1 if query_tokens == tokens and len(tokens)>0 else 0

def calculate_final_score(query_tokens, url, alpha=1, beta=.5, gamma=1.5):
    """Calculate final score for a given URL."""
    bm25 = BM25(indexes)
    bm25_score = bm25.score(url, query_tokens)
    review_score = get_bonus_review(url)
    exact_title_score = exact_title_match(query_tokens, url)
    return alpha*bm25_score + beta*review_score + gamma*exact_title_score

def get_tile_from_url(url):
    """Get tile from URL."""
    for product in products_data:
        if product["url"] == url:
            return product["title"]

def get_description_from_url(url):
    """Get description from URL."""
    for product in products_data:
        if product["url"] == url:
            return product["description"]

# Search function
def search(query):
    """Search for products based on a query."""
    query_tokens = tokenize(query)
    expanded_query = expand_query(query_tokens, origin_synonyms)
    filtered_docs = filter_documents(description_index, expanded_query) + filter_documents(title_index, expanded_query)
    bm25 = BM25(indexes, k1=1.5, b=0.75)
    scored_docs = {doc: bm25.score(doc, expanded_query) for doc in filtered_docs}
    ranked_results = sorted(scored_docs.items(), key=lambda x: x[1], reverse=True)
    # Format results
    results = [{"Titre": get_tile_from_url(doc), "URL": doc, "Description":get_description_from_url(doc), "score": score} for doc, score in ranked_results]

    return {
        "total_documents": len(description_index),
        "filtered_documents": len(filtered_docs),
        "results": results
    }


# Example usage
query = ("Classic leather sneakers")
print(json.dumps(search(query), indent=4))

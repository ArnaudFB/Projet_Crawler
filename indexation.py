import json
import re
from collections import defaultdict
import string
import os


# Load JSONL file
def load_jsonl(filepath):
    """Load JSONL file and return a list of dictionaries."""
    with open(filepath, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


# Extract product ID and variant from URL
def extract_product_id(url):
    """Extract product ID and variant from a URL."""
    match = re.search(r"https?://[^/]+/product/(\d+)(?:\?variant=(\w+-?\w+))?", url)
    return match.groups() if match else (None, None)


# Tokenize text
def tokenize(text):
    """Tokenize text by removing punctuation and converting to lowercase."""
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return [word for word in text.split() if word not in STOPWORDS]


# Build inverted index (stores URLs instead of doc IDs)
def build_inverted_index(documents, field):
    """Build inverted index for a given field in documents."""
    index = defaultdict(set)
    for doc in documents:
        words = tokenize(doc.get(field, ""))
        for word in words:
            index[word].add(doc["url"])
    return index


# Build positional index
def build_positional_index(documents, field):
    """Build positional index for a given field in documents."""
    index = defaultdict(lambda: defaultdict(list))
    for doc in documents:
        words = tokenize(doc.get(field, ""))
        for pos, word in enumerate(words):
            index[word][doc["url"]].append(pos)
    return index


# Create review index
def build_review_index(documents):
    """Build review index for a given field in documents."""
    index = {}
    for doc in documents:
        reviews = doc.get("product_reviews", [])
        if reviews:
            scores = [r.get("rating", 0) for r in reviews]
            index[doc["url"]] = {
                "total_reviews": len(scores),
                "average_rating": sum(scores) / len(scores),
                "last_rating": scores[-1]
            }
    return index

# Build features list
def build_features_list(documents):
    """Build features list for a given field in documents."""
    features_list = []
    for doc in documents:
        features = doc.get("product_features", {})
        for feature in features:
            features_list.append(feature)
    return features_list

# Build feature index
def build_feature_index(documents, feature):
    """Build feature index for a given feature in documents."""
    index = defaultdict(set)
    for doc in documents:
        features = doc.get("product_features", {}).get(feature, "")
        if features != "":
            index[features].add(doc["url"])
    return index


# Save and load index
def save_index(index, filename):
    """Save index to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({k: list(v) if isinstance(v, set) else v for k, v in index.items()}, f, indent=4)


def load_index(filename):
    """Load index from a JSON file."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# Main execution
if __name__ == "__main__":
    filepath = "products.jsonl"  # Updated to correct JSONL file
    documents = load_jsonl(filepath)

    STOPWORDS = {"the", "a", "an", "in", "on", "for", "and", "to", "of", "with"}  # Example stopwords
    combined_json = {
        "flavors_index.json": ["flavor_index.json", "flavors_index.json"],
        "care_instructions_index.json": ["care instructions_index.json", "care_instructions_index.json"],
        "sizes_index.json": ["size_index.json", "sizes_index.json"]
    }

    title_index = build_inverted_index(documents, "title")
    description_index = build_inverted_index(documents, "description")
    positional_title_index = build_positional_index(documents, "title")
    positional_description_index = build_positional_index(documents, "description")
    review_index = build_review_index(documents)

    features_list = build_features_list(documents)
    for feature in features_list:
        feature_index = build_feature_index(documents, feature)
        save_index(feature_index, f"{feature}_index.json")

    for key, value in combined_json.items():
        python_objects = []
        for json_file in value:
            with open(json_file, "r") as f:
                python_objects.append(json.load(f))

        # Dump all the Python objects into a single JSON file.
        with open(key, "w") as f:
            json.dump(python_objects, f, indent=4)


    save_index(title_index, "title_index.json")
    save_index(description_index, "description_index.json")
    save_index(positional_title_index, "positional_title_index.json")
    save_index(positional_description_index, "positional_description_index.json")
    save_index(review_index, "review_index.json")

    print("Indexing complete! Saved all indexes.")
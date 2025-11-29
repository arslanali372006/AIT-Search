# src/search_demo.py

import json
from typing import List

# Load lexicon
with open("search_engine/index/lexicon.json", "r", encoding="utf-8") as f:
    word_to_id = json.load(f)

# Load forward index
with open("search_engine/index/forward_index.json", "r", encoding="utf-8") as f:
    forward_index = json.load(f)

# Load inverted index
with open("search_engine/index/inverted_index.json", "r", encoding="utf-8") as f:
    inverted_index = json.load(f)

def search(query: str) -> List[str]:
    """
    Return list of document IDs that contain all words in the query.
    """
    words = query.lower().split()
    word_ids = [word_to_id.get(w) for w in words if w in word_to_id]

    if not word_ids:
        return []

    # Start with the first word's documents
    result_docs = set(inverted_index.get(str(word_ids[0]), []))

    # Intersect with the rest
    for wid in word_ids[1:]:
        result_docs &= set(inverted_index.get(str(wid), []))

    return list(result_docs)

if __name__ == "__main__":
    while True:
        query = input("\nEnter your search query (or 'exit' to quit): ")
        if query.lower() == "exit":
            break
        results = search(query)
        if results:
            print(f"Documents containing all words: {results}")
        else:
            print("No documents found for this query.")

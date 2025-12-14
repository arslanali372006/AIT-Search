# src/semantic.py
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

TOKENIZED_DIR = os.path.join(BASE_DIR, "sample_data", "tokenized")
EMBEDDINGS_DIR = os.path.join(BASE_DIR, "sample_data", "embeddings")
EMBED_FILE = os.path.join(EMBEDDINGS_DIR, "doc_embeddings.json")

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")



def build_embeddings():
    """
    Builds document embeddings from tokenized docs.
    Run ONCE.
    """
    embeddings = {}

    files = os.listdir(TOKENIZED_DIR)
    print(f"Building embeddings for {len(files)} documents...")

    for fname in files:
        path = os.path.join(TOKENIZED_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        tokens = data.get("tokens", [])
        if not tokens:
            continue

        text = " ".join(tokens)
        vector = model.encode(text).tolist()

        doc_id = fname.replace(".json", "")
        embeddings[doc_id] = vector

    with open(EMBED_FILE, "w", encoding="utf-8") as f:
        json.dump(embeddings, f)

    print("✅ Semantic embeddings built.")


def load_embeddings():
    with open(EMBED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def semantic_search(query: str, top_k: int = 10):
    """
    Perform semantic search using cosine similarity.
    """
    embeddings = load_embeddings()

    query_vec = model.encode(query).reshape(1, -1)

    results = []
    for doc_id, vec in embeddings.items():
        doc_vec = np.array(vec).reshape(1, -1)
        score = cosine_similarity(query_vec, doc_vec)[0][0]
        results.append((doc_id, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    build_embeddings()

# src/semantic.py
import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

TOKENIZED_DIR = os.path.join(BASE_DIR, "index", "tokenized")
EMBEDDINGS_DIR = os.path.join(BASE_DIR, "index", "embeddings")
GLOVE_PATH = os.path.join(BASE_DIR, "index", "glove", "glove.6B.100d.txt")  # Downloaded separately
EMBEDDING_DIM = 100

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# =========================
# LOAD GLOVE
# =========================

def load_glove(path=GLOVE_PATH):
    """
    Load pre-trained GloVe embeddings.
    """
    glove = {}
    print("Loading GloVe embeddings...")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            values = line.strip().split()
            word = values[0]
            vector = np.asarray(values[1:], dtype="float32")
            glove[word] = vector
    print(f"Loaded {len(glove)} word vectors.")
    return glove

# =========================
# VECTOR BUILDING
# =========================

def average_embedding(tokens, glove):
    """
    Compute average word embedding for a document or query.
    """
    vectors = [glove[t] for t in tokens if t in glove]
    if not vectors:
        return None
    return np.mean(vectors, axis=0)

# =========================
# BUILD DOCUMENT EMBEDDINGS
# =========================

def build_embeddings():
    """
    Build semantic embeddings for all tokenized documents.
    Each document stored as a separate .npy file for scalability.
    """
    glove = load_glove()
    files = os.listdir(TOKENIZED_DIR)
    print(f"Building embeddings for {len(files)} documents...")

    processed = 0
    for fname in files:
        if not fname.endswith(".json"):
            continue

        doc_id = fname.replace(".json", "")
        out_path = os.path.join(EMBEDDINGS_DIR, f"{doc_id}.npy")

        # Skip if already built
        if os.path.exists(out_path):
            continue

        with open(os.path.join(TOKENIZED_DIR, fname), "r", encoding="utf-8") as f:
            tokens = json.load(f).get("tokens", [])

        vec = average_embedding(tokens, glove)
        if vec is not None:
            np.save(out_path, vec)

        processed += 1

        if processed % 1000 == 0:
            print(f"Processed {processed} documents...")

    print(f"\n✅ Semantic embeddings built for {processed} documents.")

# =========================
# LOAD ALL EMBEDDINGS
# =========================

def load_all_embeddings():
    """
    Load all document embeddings into memory.
    Returns a dict: {doc_id: np.array(vector)}
    """
    embeddings = {}
    files = [f for f in os.listdir(EMBEDDINGS_DIR) if f.endswith(".npy")]
    total = len(files)
    print(f"Loading {total} document embeddings...")

    for i, fname in enumerate(files, start=1):
        doc_id = fname.replace(".npy", "")
        embeddings[doc_id] = np.load(os.path.join(EMBEDDINGS_DIR, fname))
        
        # Show progress every 1000 docs
        if i % 1000 == 0 or i == total:
            print(f"Loaded {i}/{total} embeddings")

    print("✅ All embeddings loaded into memory.")
    return embeddings

# =========================
# SEMANTIC SEARCH
# =========================

def semantic_search_query(query, top_k=10, glove=None, preloaded_embeddings=None):
    """
    Perform semantic search using cosine similarity.
    query: string
    top_k: number of results to return
    preloaded_embeddings: optional dict of doc_id -> vector
    """
    # glove = load_glove()
    query_tokens = query.lower().split()
    query_vec = average_embedding(query_tokens, glove)
    if query_vec is None:
        print("No valid embeddings found for the query.")
        return []

    results = []
    embeddings = preloaded_embeddings

    for doc_id, doc_vec in embeddings.items():
        score = cosine_similarity(query_vec.reshape(1, -1), doc_vec.reshape(1, -1))[0][0]
        results.append((doc_id, float(score)))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]

# =========================
# CLI TEST
# =========================

if __name__ == "__main__":
    print("1. Build embeddings")
    print("2. Semantic search")
    choice = input("Choice: ")

    if choice == "1":
        build_embeddings()
    elif choice == "2":
        query = input("Enter query: ")
        embeddings = load_all_embeddings()
        results = semantic_search_query(query, preloaded_embeddings=embeddings)
        print("\nSemantic Results:")
        for doc_id, score in results:
            print(f"{doc_id}  (score={score:.4f})")
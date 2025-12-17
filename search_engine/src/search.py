# src/search.py
from barrels import barrel_manager
from lexicon import lexicon
from autocomplete import get_autocomplete_suggestions
from semantic import semantic_search_query

def single_word_search(word):
    """Return list of (docID, score) tuples for a single word."""
    word_id = lexicon.get_id(word)
    if word_id == 0:
        print(f"Word '{word}' not in lexicon.")
        return []

    barrel_id = barrel_manager.get_barrel_id(word_id)
    barrel_data = barrel_manager.load_barrel(barrel_id)

    postings = barrel_data.get(word_id, [])

    if not postings:
        print(f"WordID {word_id} for '{word}' not found in barrel {barrel_id}.")
        return []

    # Old barrels: list of docIDs → score = 1
    if isinstance(postings, list):
        results = {doc_id: 1 for doc_id in postings}
    # New barrels: dict with positions → score = len(positions)
    elif isinstance(postings, dict):
        results = {doc_id: len(pos_list) for doc_id, pos_list in postings.items()}
    else:
        results = {}

    # Return sorted list by score descending
    return sorted(results.items(), key=lambda x: x[1], reverse=True)


def multi_word_search(query):
    """Return docs that match all words (AND search)."""
    words = query.lower().split()
    if not words:
        return []

    # Get results for first word
    results = dict(single_word_search(words[0]))
    if not results:
        return []

    # Intersect with other words
    for word in words[1:]:
        word_results = dict(single_word_search(word))
        results = {doc: score for doc, score in results.items() if doc in word_results}
        if not results:
            break

    return sorted(results.items(), key=lambda x: x[1], reverse=True)


def semantic_search(query, glove, embeddings, top_k):
    results = semantic_search_query(query, top_k=top_k, glove=glove, preloaded_embeddings=embeddings)
    if not results:
        print("No semantic results.")
        return

    print("\nSemantic Results:")
    for doc_id, score in results:
        print(f"{doc_id}  (score={score:.4f})")


def autocomplete_words(prefix, top_n=10):
    """Return autocomplete suggestions for a prefix."""
    return get_autocomplete_suggestions(prefix, top_n)
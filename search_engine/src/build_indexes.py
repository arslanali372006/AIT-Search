# src/build_indexes.py

import os
import json
from lexicon import Lexicon
from forward_index import ForwardIndex
from inverted_index import InvertedIndex

TOKENIZED_DIR = "search_engine/sample_data/tokenized/"

# 1. Load tokenized documents
tokenized_docs = {}
for filename in os.listdir(TOKENIZED_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(TOKENIZED_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            tokenized_docs[filename.replace(".json","")] = data.get("tokens", [])

print(f"Loaded {len(tokenized_docs)} tokenized documents.")

# 2. Build lexicon
lex = Lexicon()
lex.build(list(tokenized_docs.values()))
lex.save()
print(f"Lexicon saved. {len(lex.word_to_id)} unique words.")

# 3. Build forward index
fwd = ForwardIndex()
fwd.build(tokenized_docs, lex)
fwd.save()
print(f"Forward index saved. {len(fwd.index)} documents indexed.")

# 4. Build inverted index
inv = InvertedIndex()
inv.build(fwd.index)
inv.save()
print(f"Inverted index saved. {len(inv.index)} unique word IDs mapped.")

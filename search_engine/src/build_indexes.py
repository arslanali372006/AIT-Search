# src/build_indexes.py

import os
import json
from lexicon import Lexicon
from forward_index import ForwardIndex
from inverted_index import InvertedIndex

TOKENIZED_DIR = "search_engine/data/tokenized/"

tokenized_docs = {}

files = [f for f in os.listdir(TOKENIZED_DIR) if f.endswith(".json")]
total = len(files)


print(f"Loading {total} tokenized documents...")

for i, filename in enumerate(files, start=1):
    filepath = os.path.join(TOKENIZED_DIR, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.loads(f.read())

    tokenized_docs[filename[:-5]] = data.get("tokens", [])

    if i % 1000 == 0:
        print(f"Loaded {i} documents")

print(f"Loaded {len(tokenized_docs)} tokenized documents.")

# 2. Build lexicon
lex = Lexicon()
lex.build(list(tokenized_docs.values()))
lex.save("search_engine/data/lexicon.json")
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

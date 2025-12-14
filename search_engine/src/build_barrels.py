# src/build_barrel.py

import json
import os
from barrels import Barrel

INVERTED_INDEX_PATH = "search_engine/index/inverted_index.json"

barrel = Barrel(barrel_dir="search_engine/index/barrels", barrel_size=100000)

# Load inverted index
with open(INVERTED_INDEX_PATH, "r", encoding="utf-8") as f:
    inverted_index = json.load(f)

print(f"Loaded inverted index with {len(inverted_index)} words.")

# Step 1: clear directory
for fname in os.listdir(barrel.barrel_dir):
    fpath = os.path.join(barrel.barrel_dir, fname)
    if os.path.isfile(fpath):
        os.remove(fpath)

print("Old barrels cleared.\n")

# Step 2: In-memory barrel groups
barrel_groups = {}  # barrel_id -> {word: posting_list}

total_words = len(inverted_index)

for i, (wid_str, doc_ids) in enumerate(inverted_index.items(), start=1):
    wid = int(wid_str)
    bid = barrel.get_barrel_id(wid)

    if bid not in barrel_groups:
        barrel_groups[bid] = {}

    barrel_groups[bid][wid] = doc_ids

    # Progress every 50,000 words (fast)
    if i % 50000 == 0:
        print(f"Grouped {i}/{total_words} words ({i/total_words:.2%})")

print("Finished grouping into barrels.")

# Step 3: write each barrel once
for bid, data in barrel_groups.items():
    barrel.save_barrel(bid, data)
    print(f"Saved barrel {bid} with {len(data)} entries")

print("\nAll barrels built successfully (FAST MODE).")

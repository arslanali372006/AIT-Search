# src/inverted_index.py

import json
import os
from typing import Dict, List

class InvertedIndex:
    """
    wordID → [docIDs]
    """
    def __init__(self):
        self.index: Dict[int, List[str]] = {}

    def build(self, forward_index: Dict[str, Dict[int, int]]) -> None:
        for doc_id, word_freq in forward_index.items():
            for wid in word_freq.keys():
                if wid not in self.index:
                    self.index[wid] = []
                self.index[wid].append(doc_id)

    def save(self, path: str = "search_engine/index/inverted_index.json") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2)

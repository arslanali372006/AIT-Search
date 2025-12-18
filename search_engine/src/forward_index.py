# src/forward_index.py

import json
import os
from typing import Dict, List

class ForwardIndex:
    """
    Document → {wordID: frequency}
    """
    def __init__(self):
        self.index: Dict[str, Dict[int, int]] = {}

    def build(self, tokenized_docs: Dict[str, List[str]], lexicon) -> None:
        for doc_id, tokens in tokenized_docs.items():
            word_freq = {}
            for token in tokens:
                wid = lexicon.get_id(token)
                if wid:
                    word_freq[wid] = word_freq.get(wid, 0) + 1
            self.index[doc_id] = word_freq

    def save(self, path: str = "search_engine/data/forward_index.json") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2)

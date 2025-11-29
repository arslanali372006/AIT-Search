# src/lexicon.py

import json
import os
from typing import Dict, List

class Lexicon:
    """
    Manages mapping: word -> wordID.
    """
    def __init__(self):
        self.word_to_id: Dict[str, int] = {}
        self.id_to_word: Dict[int, str] = {}

    def build(self, token_lists: List[List[str]]) -> None:
        """
        Build lexicon from list of token lists.
        """
        all_tokens = set(token for tokens in token_lists for token in tokens)
        for idx, word in enumerate(sorted(all_tokens), start=1):
            self.word_to_id[word] = idx
            self.id_to_word[idx] = word

    def get_id(self, word: str) -> int:
        return self.word_to_id.get(word, 0)

    def get_word(self, idx: int) -> str:
        return self.id_to_word.get(idx, "")

    def save(self, path: str = "search_engine/index/lexicon.json") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.word_to_id, f, indent=2)

    def load(self, path: str = "search_engine/index/lexicon.json") -> None:
        with open(path, "r", encoding="utf-8") as f:
            self.word_to_id = json.load(f)
        self.id_to_word = {idx: word for word, idx in self.word_to_id.items()}

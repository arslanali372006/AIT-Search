# src/lexicon.py

import json
import os
import re
from typing import Dict, List

class Lexicon:
    """
    Manages mapping: word -> wordID.
    Only clean words (letters only, length 2-50) are included.
    """

    def __init__(self):
        self.word_to_id: Dict[str, int] = {}
        self.id_to_word: Dict[int, str] = {}
        self._next_id = 1  # Track next available ID

    def _is_valid_word(self, word: str) -> bool:
        return re.fullmatch(r"[a-z]{2,50}", word) is not None

    def build(self, token_lists: List[List[str]]) -> None:
        all_tokens = set(
            token for tokens in token_lists
            for token in tokens
            if self._is_valid_word(token)
        )
        for word in sorted(all_tokens):
            if word not in self.word_to_id:
                self.word_to_id[word] = self._next_id
                self.id_to_word[self._next_id] = word
                self._next_id += 1

    def get_id(self, word: str) -> int:
        return self.word_to_id.get(word, 0)

    def get_word(self, idx: int) -> str:
        return self.id_to_word.get(idx, "")

    def size(self) -> int:
        return len(self.word_to_id)

    def save(self, path: str = None) -> None:
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "..", "index", "lexicon.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.word_to_id, f, indent=2)

    def load(self, path: str = None) -> None:
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "..", "data", "lexicon.json")
        path = os.path.abspath(path)
        if not os.path.exists(path):
            print(f"Lexicon file not found at {path}. Starting empty lexicon.")
            return
        with open(path, "r", encoding="utf-8") as f:
            loaded_dict = json.load(f)
        self.word_to_id = {}
        self.id_to_word = {}
        for word, id_str in loaded_dict.items():
            word_id = int(id_str)
            self.word_to_id[word] = word_id
            self.id_to_word[word_id] = word
        self._next_id = max(self.id_to_word.keys(), default=0) + 1

# Create global instance
lexicon = Lexicon()
lexicon.load()

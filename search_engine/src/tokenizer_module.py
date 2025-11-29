# tokenizer_module.py

import re
from typing import List

class Tokenizer:
    """
    Tokenizes raw text into a list of clean words (tokens) suitable for indexing.
    """

    def __init__(self, remove_stopwords: bool = False):
        self.stopwords = set([
            "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "of", "for", 
            "with", "is", "are", "was", "were", "be", "been", "being", "by", "as", "from"
        ]) if remove_stopwords else set()
    
    def tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = text.split()
        if self.stopwords:
            tokens = [t for t in tokens if t not in self.stopwords]
        return tokens

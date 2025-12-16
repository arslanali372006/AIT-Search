# tokenizer_module.py

import re
from typing import List


class Tokenizer:
    """
    Tokenizes raw text into a list of clean, indexable tokens.
    Designed for large scientific / PMC-style corpora.
    """

    def __init__(
        self,
        remove_stopwords: bool = True,
        min_len: int = 2,
        max_len: int = 25
    ):
        self.min_len = min_len
        self.max_len = max_len

        self.stopwords = {
            "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
            "of", "for", "with", "is", "are", "was", "were", "be", "been",
            "being", "by", "as", "from", "that", "this", "these", "those",
            "we", "our", "their", "it", "its", "can", "may", "might", "also"
        } if remove_stopwords else set()

        # Match words containing letters, digits, and hyphens
        self.token_pattern = re.compile(r"[a-z0-9\-]+")

    def _is_gibberish(self, token: str) -> bool:
        """
        Heuristics to reject non-linguistic or harmful tokens.
        """

        # Length filtering
        if len(token) < self.min_len or len(token) > self.max_len:
            return True

        # Reject pure numbers
        if token.isdigit():
            return True

        # Reject repeated-character garbage (e.g., aaaaaaaa, bbbbb)
        if len(set(token)) <= 2 and len(token) > 5:
            return True

        return False

    def _normalize(self, token: str) -> str:
        """
        Normalize token while preserving semantic identity.
        """
        # Remove hyphens but keep meaning: covid-19 -> covid19
        token = token.replace("-", "")
        return token

    def tokenize(self, text: str) -> List[str]:
        """
        Convert raw text into a cleaned list of tokens.
        """
        if not text:
            return []

        text = text.lower()

        # Extract candidate tokens
        raw_tokens = self.token_pattern.findall(text)

        tokens: List[str] = []
        for token in raw_tokens:
            token = self._normalize(token)

            if token in self.stopwords:
                continue

            if self._is_gibberish(token):
                continue

            tokens.append(token)

        return tokens

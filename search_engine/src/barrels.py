# src/barrels.py

import json
import os
from typing import Dict, List


class Barrel:
    """
    Manages writing and reading of barrels.
    
    A barrel is simply:
        barrel_k.json = {
            wordID: [docID, docID...]
        }
        where k is the number of current barrel
    """

    def __init__(self, barrel_dir: str = "search_engine/index/barrels", barrel_size: int = 100000):
        """
        barrel_size = number of wordIDs per barrel
        """
        self.barrel_dir = barrel_dir
        self.barrel_size = barrel_size

        os.makedirs(self.barrel_dir, exist_ok=True)

    def get_barrel_id(self, word_id: int) -> int:
        """
        Determine which barrel a wordID belongs to.
        Example: barrel_size = 10000
            wordID 1-9999 → barrel_0
            wordID 10000-19999 → barrel_1
        """
        return (word_id - 1) // self.barrel_size

    def get_barrel_path(self, barrel_id: int) -> str:
        return os.path.join(self.barrel_dir, f"barrel_{barrel_id}.json")

    def load_barrel(self, barrel_id: int) -> Dict[int, List[str]]:
        """
        Load a single barrel file; return empty dict if not present.
        """
        path = self.get_barrel_path(barrel_id)
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_barrel(self, barrel_id: int, data: Dict[int, List[str]]) -> None:
        """
        Save a barrel to disk.
        """
        path = self.get_barrel_path(barrel_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_docID(self, word_id: int, doc_id: str) -> None:
        """
        Append a docID to the correct barrel for a given wordID.
        """
        barrel_id = self.get_barrel_id(word_id)
        barrel = self.load_barrel(barrel_id)

        if word_id not in barrel:
            barrel[word_id] = []

        barrel[word_id].append(doc_id)

        self.save_barrel(barrel_id, barrel)

# src/barrels.py
import json
import os
from typing import Dict, List, Union

class Barrel:
    """
    Manages reading and writing of barrels.
    
    Supports:
    - Old barrels: wordID → [docID, docID, ...]
    - New barrels: wordID → {docID: [pos1, pos2, ...], ...}
    """

    def __init__(self, barrel_dir: str = None, barrel_size: int = 100000):
        if barrel_dir is None:
            barrel_dir = os.path.join(os.path.dirname(__file__), "..", "index", "barrels")
        self.barrel_dir = barrel_dir
        self.barrel_size = barrel_size
        os.makedirs(self.barrel_dir, exist_ok=True)

    def get_barrel_id(self, word_id: int) -> int:
        """Return which barrel a wordID belongs to."""
        return (word_id - 1) // self.barrel_size

    def get_barrel_path(self, barrel_id: int) -> str:
        return os.path.join(self.barrel_dir, f"barrel_{barrel_id}.json")

    def load_barrel(self, barrel_id: int) -> Dict[int, Union[List[str], Dict[str, List[int]]]]:
        """Load a barrel; keys are ints, values can be list or dict."""
        path = self.get_barrel_path(barrel_id)
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Convert keys to int for safe lookup
        return {int(k): v for k, v in data.items()}

    def save_barrel(self, barrel_id: int, data: Dict[int, Union[List[str], Dict[str, List[int]]]]) -> None:
        path = self.get_barrel_path(barrel_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_docID(self, word_id: int, doc_id: str, position: int = None) -> None:
        """
        Add a docID and optional position to the correct barrel.
        If position is None, store as old-style list of docIDs.
        """
        barrel_id = self.get_barrel_id(word_id)
        barrel = self.load_barrel(barrel_id)

        if word_id not in barrel:
            barrel[word_id] = [] if position is None else {}

        if position is None:
            if doc_id not in barrel[word_id]:
                barrel[word_id].append(doc_id)
        else:
            if doc_id not in barrel[word_id]:
                barrel[word_id][doc_id] = []
            barrel[word_id][doc_id].append(position)

        self.save_barrel(barrel_id, barrel)


# Global barrel manager
barrel_manager = Barrel()



# src/parser.py

import json
import os
from typing import List, Dict

class Document:
    """Represents a single document."""
    def __init__(self, paper_id: str, title: str, abstract: str, body_text: str):
        self.paper_id = paper_id
        self.title = title
        self.abstract = abstract
        self.body_text = body_text

class Parser:
    """Parses JSON documents from a folder."""
    def __init__(self, folder_path: str = "search_engine/sample_data/sample_json"):
        self.folder_path = folder_path
        self.documents: List[Document] = []

    def parse(self) -> List[Document]:
        """Parse all JSON files in the folder."""
        files = [f for f in os.listdir(self.folder_path) if f.endswith(".json")]
        for file_name in files:
            path = os.path.join(self.folder_path, file_name)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                doc = Document(
                    paper_id=data.get("paper_id", ""),
                    title=data.get("title", ""),
                    abstract=data.get("abstract", ""),
                    body_text=data.get("body_text", "")
                )
                self.documents.append(doc)
        return self.documents

if __name__ == "__main__":
    parser = Parser()
    docs = parser.parse()
    for doc in docs:
        print(f"Doc ID: {doc.paper_id}")
        print(f"Title: {doc.title}")
        print(f"Abstract: {doc.abstract}")
        print(f"Body: {doc.body_text[:100]}...")  # show first 100 chars
        print("="*50)

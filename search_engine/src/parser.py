# src/parser.py

import json
import os
from typing import List


class Document:
    def __init__(self, paper_id: str, title: str, abstract: str, body_text: str):
        self.paper_id = paper_id
        self.title = title
        self.abstract = abstract
        self.body_text = body_text


def extract_text(field):
    """
    Extract text from a field that may be:
    - string
    - list of {text: "..."}
    """
    if isinstance(field, str):
        return field

    if isinstance(field, list):
        texts = []
        for item in field:
            if isinstance(item, dict) and "text" in item:
                texts.append(item["text"])
        return " ".join(texts)

    return ""


def parse_documents(folder_path: str) -> List[Document]:
    documents = []

    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".json")])

    for file_name in files:
        path = os.path.join(folder_path, file_name)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to load {file_name}: {e}")
            continue

        paper_id = data.get("paper_id", os.path.splitext(file_name)[0])
        title = data.get("title", "")

        abstract = extract_text(data.get("abstract", []))
        body_text = extract_text(data.get("body_text", []))

        documents.append(Document(
            paper_id=paper_id,
            title=title,
            abstract=abstract,
            body_text=body_text
        ))

    return documents

if __name__ == "__main__":
    folder_path = "search_engine/sample_data/sample_json"
    docs = parse_documents(folder_path)

    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".json")])

    print("-" * 60)
    
    for doc, file_name in zip(docs, files):
        print("File:", file_name)
        print("ID:", doc.paper_id)
        print("Title:", doc.title[:100])
        print("Abstract:", doc.abstract[:200])
        print("Body:", doc.body_text[:300])
        print("-" * 60)


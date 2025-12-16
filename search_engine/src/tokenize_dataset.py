# search_engine/src/tokenize_dataset.py

import os
import json
from tokenizer_module import Tokenizer

DATA_DIR = "search_engine/sample_data/sample_json/"
OUTPUT_DIR = "search_engine/sample_data/tokenized/"

tokenizer = Tokenizer(remove_stopwords=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_text(field):
    if isinstance(field, str):
        return field
    if isinstance(field, list):
        return " ".join(
            item["text"] for item in field
            if isinstance(item, dict) and "text" in item
        )
    return ""


for filename in os.listdir(DATA_DIR):
    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = " ".join([
        extract_text(data.get("title", "")),
        extract_text(data.get("abstract", [])),
        extract_text(data.get("body_text", []))
    ])

    tokens = tokenizer.tokenize(text)

    output_path = os.path.join(OUTPUT_DIR, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"tokens": tokens}, f, indent=2)

    print(f"Processed {filename}: {len(tokens)} tokens")

# search_engine/src/tokenize_dataset.py

import os
import json
from tokenizer_module import Tokenizer  # Make sure tokenizer_module.py is in the same folder

# Folder where your sample JSON files are
DATA_DIR = "search_engine/sample_data/sample_json/"

# Output folder for tokenized results
OUTPUT_DIR = "search_engine/sample_data/tokenized/"

# Initialize tokenizer (remove_stopwords=True if you want)
tokenizer = Tokenizer(remove_stopwords=True)

# Make sure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Process each JSON file
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(DATA_DIR, filename)

        # Read JSON content
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Combine all string fields into one text
        text_parts = []
        for value in data.values():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                # If list contains strings, join them
                text_parts.extend([str(v) for v in value if isinstance(v, str)])
            elif isinstance(value, dict):
                # Flatten dict values recursively if needed
                text_parts.extend([str(v) for v in value.values() if isinstance(v, str)])
        text = " ".join(text_parts)

        # Tokenize
        tokens = tokenizer.tokenize(text)

        # Print tokens
        print(f"\nTokens for {filename}:")
        print(tokens)

        # Save tokenized output
        output_path = os.path.join(OUTPUT_DIR, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"tokens": tokens}, f, indent=2)

        print(f"Processed {filename}: {len(tokens)} tokens")

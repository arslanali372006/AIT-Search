import os
import json

# Base folder containing JSON files
base_folder = "search_engine/data/json/document_parser"

# Folders to process
json_folders = ["pmc_json", "pdf_json"]

# In-memory document storage: {doc_id: text}
documents = {}

total_chars = 0
total_docs = 0

for folder in json_folders:
    folder_path = os.path.join(base_folder, folder)
    if not os.path.isdir(folder_path):
        print(f"Folder not found: {folder_path}, skipping...")
        continue

    files = os.listdir(folder_path)
    if not files:
        print(f"No files in folder: {folder_path}, skipping...")
        continue

    print(f"\nProcessing folder: {folder_path} ({len(files)} files)")

    for filename in files:
        file_path = os.path.join(folder_path, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
            continue

        # Extract text from common keys
        text = ""
        if "body_text" in data:
            if isinstance(data["body_text"], list):
                text = " ".join([p.get("text", "") for p in data["body_text"]])
            else:
                text = str(data["body_text"])
        elif "text" in data:
            text = str(data["text"])
        elif "abstract" in data:
            text = str(data["abstract"])
        else:
            # fallback: dump entire JSON
            text = json.dumps(data)

        # Use filename (without extension) as document ID
        doc_id = os.path.splitext(filename)[0]

        documents[doc_id] = text
        total_docs += 1
        total_chars += len(text)

        # Optional: print first few excerpts for verification
        if total_docs <= 10:
            print(f"\nDoc ID: {doc_id}")
            print("Excerpt:", text[:300])

print("\n=== Summary ===")
print(f"Total documents indexed: {total_docs}")
print(f"Average document length: {total_chars // total_docs if total_docs else 0} characters")

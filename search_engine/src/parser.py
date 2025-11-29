import json
import os
from typing import Dict, Generator, Tuple

class DocumentParser:
    """
    Reads CORD-19 JSON FILES and extracts:
        - paperID
        - title
        - abstract text
        - body text
        - back matter

    Returns clean text for indexing.
    """

    def __init__(self, json_root: str):
        self.json_root = json_root

    def iter_documents(self) -> Generator[Tuple[str, str], None, None]:
        """
        Iterates through all the JSON files inside:
            json_root/pdf_json/
            json_root/pmc_json/

        Yields:
            (doc_id, full_text)
        """

        folders = ["pdf_json", "pmc_json"]

        for folder in folders:
            folder_path = os.path.join(self.json_root, folder)

            # FIX 1: Correct directory existence check
            if not os.path.isdir(folder_path):
                continue

            # FIX 2: Correct iteration through files
            for filename in os.listdir(folder_path):
                if not filename.endswith(".json"):
                    continue

                fpath = os.path.join(folder_path, filename)

                try:
                    with open(fpath, "r") as f:
                        data = json.load(f)
                except Exception:
                    # skip unreadable/corrupt json
                    continue

                # FIX 3: safer filename fallback
                doc_id = data.get("paper_id", filename.replace(".json", ""))

                text = self.extract_text(data)

                if text.strip():
                    yield (doc_id, text)

    def extract_text(self, data: Dict) -> str:
        """Extract the title, abstract, body text, and back matter."""

        parts = []

        # Title
        title = data.get("metadata", {}).get("title", "")
        parts.append(title)

        # Abstract
        for item in data.get("abstract", []):
            t = item.get("text", "")
            if t:
                parts.append(t)

        # Body Text
        for item in data.get("body_text", []):
            t = item.get("text", "")
            if t:
                parts.append(t)

        # Back Matter
        for item in data.get("back_matter", []):
            t = item.get("text", "")
            if t:
                parts.append(t)

        return "\n".join(parts)
